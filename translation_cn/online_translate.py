#!/cc/bin/python

import argparse
import os
import random
import re
import requests
import sys
import time

# from bs4 import BeautifulSoup
from docutils import nodes
from docutils.core import publish_doctree
from pathlib import Path
from termcolor import colored, cprint
from urllib import parse

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


cn_char = re.compile(r'[\u4e00-\u9fa5“”（）…—！《》，。：、]')  # 匹配汉字
embed_code = re.compile(r'(``.*?``)')  # 匹配内嵌命令: ``cmd``
refered = re.compile(r'(`.*?`)')  # 匹配引言: `quoted`

DEBUG = False

# make selenium enviroment global
BROWSER = None
SELENIUM_PREPARED = False
LAST_RESULT: str = ''  # 翻译的上一个结果。程序输入太快，结果回来慢，取得太快就会得到上一个结果。

# TODO this set not work
docutils_settings_overrides = {
    'ignore_unknown_directives': True
}


def clear_line():
    os.system('echo -en "\\r\\e[K\\e[0m"')


def debug(words):
    if not DEBUG:
        return
    print(colored('DEBUG: ', color='red'), end='')
    print(words)

def err(words):
    print(colored('ERROR: ', color='red', attrs=['bold']), end='')
    print(words)

def p_green(words):
    cprint(words, color='green', attrs=['bold'])


def apply_fixes(old_txt, new_txt):
    '''
    apply our fixes, to reduce manual works
    old_txt, new_txt are both text, before translate and translated.
    '''
    old_paragraphs = [e for e in old_txt.split('\n\n') if e]
    new_paragraphs = [e for e in new_txt.split('\n\n') if e]
    if len(old_paragraphs) != len(new_paragraphs):
        err('翻译前和翻译后的段数不一样，放弃修正。')

    fixed = []
    for old, new in zip(old_paragraphs, new_paragraphs):
        # cmdline
        if old.endswith('::'):
            new += ' ::'

        # command, ` quoted

        # TODO fix needed, docutils removed `` when parse
        # command, `` quoted; add removed chars
        quoted = embed_code.findall(old)
        quoted = [s.lstrip('``') for s in quoted if s]
        quoted = [s.rstrip('``') for s in quoted if s]
        for old_quoted in quoted:
            new = new.replace(old_quoted, '``' + old_quoted + '``')

        fixed.append(new)

    return '\n\n'.join(fixed)


def apply_terms(txt):
    'apply our terms table'
    terms = {
        # long first, replaced text is colored, next match will fail.
        # to replace: replaced
        '请运行以下命令': '执行下列命令',
        '请运行下列命令': '执行下列命令',

        '以下': '下列',
        '刮擦': '扫描',  # scrape
        '特定': '指定',

        '您': '你',

        # terms
        '擦除代码': '纠删码',
        '群集': '集群',
    }

    for old, new in terms.items():
        if old in txt:
            new = colored(new, color='yellow')
            txt = txt.replace(old, new)

    return txt


def get_rst_nodes(fpath):  # noqa

    def section_to_paragraph(section, parent_section=None, depth=0):
        '''
        section is consists of numbers of paragraphs, so flatten sections,
        to paragraphs.
        depth: recursive depth, for debug
        '''
        # this is "paragraph"
        if section.tagname == 'paragraph':
            return [section]

        # flat "section"
        depth += 1
        ps = []
        subs = section.traverse()
        # debug(f'depth={depth}, section={subs}')
        for sub in subs:
            # The first element (section) in traverse() is itself.
            if sub == parent_section:
                continue

            if sub.tagname == 'paragraph' and not isinstance(sub.parent, nodes.system_message):
                ps.append(sub)
            elif sub.tagname == 'section':
                ps += section_to_paragraph(sub, parent_section=sub, depth=depth)
        return ps

    parts = publish_doctree(source=fpath.open('r', encoding='utf-8').read(),
                            settings=None,
                            settings_overrides=docutils_settings_overrides)
    paragraphs = []
    for p in parts:
        paragraphs += section_to_paragraph(p, depth=0)

    # dedup
    ps = []
    for p in paragraphs:
        if p not in ps:
            ps.append(p)
    # debug(f'dedup: {len(paragraphs)} -> {len(ps)}')

    # debug
    '''
    for n in ps:
        # print(n.tagname, '\t', n.astext())

        # cprint(n.tagname, color='green')
        # cprint(str(type(n)), color='red')
        print(n.astext(), '\n')
    '''

    return ps


def prepare_selenium():
    global BROWSER, SELENIUM_PREPARED
    print('preparing selenium ... ', end='', flush=True)

    # DeepL API的URL
    # url = "https://www.deepl.com/zh/translator#en/zh-hans/" + parse.quote(txt)
    url = "https://www.deepl.com/zh/translator#en/zh-hans/"
    # debug(url)

    # start firefox browser
    options = webdriver.FirefoxOptions()
    options.binary_location = '/usr/bin/firefox-bin'
    BROWSER = webdriver.Firefox(options=options)

    BROWSER.get(url)
    BROWSER.implicitly_wait(10)

    SELENIUM_PREPARED = True  # noqa
    clear_line()
    return BROWSER


def translate_via_deepl_json(txt):
    print('translating via json API ... ', end='', flush=True)
    # json style
    url = 'https://www2.deepl.com/jsonrpc?method=LMT_handle_jobs'
    data = {
        "id": 9020140,
        "jsonrpc": "2.0",
        "method": "LMT_handle_jobs",
        "params": {
            "commonJobParams": {
                "browserType": 1,
                "mode": "translate",
                "quality": "normal",
                "regionalVariant": "zh-Hans",
                "termbase": {
                    "dictionary": "Erasure-coded\t纠删码\nFully Qualified Domain Name\t全资域名\nPrimary affinity\t主亲和性\nRESTful\t符合 REST 规范的\ncluster\t集群\nmonitor\t监视器\nplacement group\t归置组\npool\t存储池\nscrub\t洗刷\nweb\t网页"
                },
                "textType": "plaintext"
            },
            "jobs": [
                {
                    "kind": "default",
                    "preferred_num_beams": 1,
                    "raw_en_context_after": [],
                    "raw_en_context_before": [],
                    "sentences": [
                        {
                            "id": 1,
                            "prefix": "",
                            "text": txt,
                        }
                    ]
                }
            ],
            "lang": {
                "preference": {
                    "default": "default",
                    "weight": {}
                },
                "source_lang_computed": "EN",
                "target_lang": "ZH"
            },
        }
    }
    # response sample
    '''
    response_json = {
        "jsonrpc": "2.0",
        "id": 9020140,
        "result": {
            "translations": [
                {
                    "beams": [
                        {
                            "sentences": [
                                {
                                    "text": "Ceph 跟踪哪些硬件存储设备（如 HDD、SSD）被哪些守护进程占用，并收集这些设备的健康指标，以便提供工具来预测和/或自动应对硬件故障。",
                                    "ids": [1]
                                }
                            ],
                            "num_symbols": 45,
                            "rephrase_variant": {
                                "name": "D5jrG5dVNnRrxxHKJd5W1BV9NvsiQrbVZmf78A=="
                            }
                        }
                    ],
                    "quality": "normal"
                }
            ],
            "target_lang": "ZH",
            "source_lang": "EN",
            "source_lang_is_confident": false,
            "detectedLanguages": {}
        }
    }

    # multiple paragraphs
    req =
    response_json = {
        "jsonrpc": "2.0",
        "id": 9020143,
        "result": {
            "translations": [
                {
                    "beams": [
                        {
                            "sentences": [
                                {
                                    "text": "Ceph 指标的主要来源是每个 Ceph 守护进程暴露的性能计数器。",
                                    "ids": [1]
                                }
                            ],
                            "num_symbols": 22,
                            "rephrase_variant": {
                                "name": "fXHia+1yQjA7bJKYlMla2C53eBbpr0K3s2+x2w=="
                            }
                        }
                    ],
                    "quality": "normal"
                },
                {
                    "beams": [
                        {
                            "sentences": [
                                {
                                    "text": "Perf 计数器是本地 Ceph 监视器数据",
                                    "glossary_highlights": [
                                        {
                                            "tag_l1": "monitor",
                                            "tag_l2": "监视器",
                                            "highlight_chr_ranges": [
                                                [17, 20]
                                            ]
                                        }
                                    ],
                                    "ids": [2]
                                }
                            ],
                            "num_symbols": 14,
                            "rephrase_variant": {
                                "name": "gRMJopO78GO0afa3GzMydiwD+wF6ZVe43P41Ew=="
                            }
                        }
                    ],
                    "quality": "normal"
                },
                {
                    "beams": [
                        {
                            "sentences": [
                                {
                                    "text": "性能计数器由 Ceph 输出程序守护进程转换为标准 Prometheus 指标。",
                                    "ids": [3]
                                }
                            ],
                            "num_symbols": 22,
                            "rephrase_variant": {
                                "name": "FtIaLOmOK6WbhrODdS0JkWpyCrU2+85rUAa0rw=="
                            }
                        }
                    ],
                    "quality": "normal"
                },
                {
                    "beams": [
                        {
                            "sentences": [
                                {
                                    "text": "该守护进程在每个 Ceph 集群主机上运行，并暴露一个指标终点，在该终点上，主机中运行的所有 Ceph 守护进程暴露的所有性能计数器都以 Prometheus 指标的形式发布。",
                                    "glossary_highlights": [
                                        {
                                            "tag_l1": "cluster",
                                            "tag_l2": "集群",
                                            "highlight_chr_ranges": [
                                                [14, 16]
                                            ]
                                        }
                                    ],
                                    "ids": [
                                        4
                                    ]
                                }
                            ],
                            "num_symbols": 54,
                            "rephrase_variant": {
                                "name": "uofJj1nOV2e1cKWXwSwF+c6hZgoSdvxFtcaLiw=="
                            }
                        }
                    ],
                    "quality": "normal"
                }
            ],
            "target_lang": "ZH",
            "source_lang": "EN",
            "source_lang_is_confident": false,
            "detectedLanguages": {}
        }
    }
    '''

    headers = {
        # "Accept-Encoding": "gzip, deflate, br, zstd",
        # "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.6,en-US;q=0.4,bo;q=0.2",
        "Connection": "keep-alive",
        "Content-type": "application/json",
        # "Cookie": "dapUid=3015b91f-ddb9-46be-adc1-c63cf5b09d09; releaseGroups=17791.AAEXP-15863.1.1_10551.DAL-1134.2.2_17337.AAEXP-15413.2.1_14962.CLAB-51.2.3_17789.AAEXP-15861.1.1_17404.AAEXP-15480.1.1_17731.AAEXP-15803.2.1_17415.AAEXP-15491.1.1_17273.CEX-696.1.1_13134.DF-3988.2.1_16753.DF-4044.2.3_17394.AAEXP-15470.1.1_17368.AAEXP-15444.1.1_17750.AAEXP-15822.1.1_8393.DPAY-3431.2.2_17743.AAEXP-15815.2.1_8776.DM-1442.2.2_17419.AAEXP-15495.1.1_17377.AAEXP-15453.2.1_17756.AAEXP-15828.1.1_17356.AAEXP-15432.2.1_17391.AAEXP-15467.1.1_17734.AAEXP-15806.1.1_17272.WTT-1298.1.1_17744.AAEXP-15816.2.1_17383.AAEXP-15459.1.1_13135.DF-4076.2.2_17379.AAEXP-15455.1.1_16358.WDW-677.2.2_17418.AAEXP-15494.1.1_17732.AAEXP-15804.1.1_17372.AAEXP-15448.1.1_13132.DM-1798.2.2_17357.AAEXP-15433.2.1_17729.AAEXP-15801.1.1_17740.AAEXP-15812.1.1_220.DF-1925.1.9_17361.AAEXP-15437.2.1_17765.AAEXP-15837.1.1_12500.DF-3968.2.2_17753.AAEXP-15825.1.1_17399.AAEXP-15475.1.1_4121.WDW-356.2.5_17416.AAEXP-15492.1.1_17348.AAEXP-15424.1.1_17363.AAEXP-15439.2.1_17266.WDW-885.1.1_17403.AAEXP-15479.1.1_13915.WDW-713.2.2_5562.DWFA-732.2.2_17417.AAEXP-15493.1.1_17773.AAEXP-15845.1.1_14528.WDW-673.1.1_15497.SEO-1114.2.2_14526.RI-246.2.6_17764.AAEXP-15836.1.1_17398.AAEXP-15474.1.1_17737.AAEXP-15809.2.1_16022.DEM-1456.2.7_17761.AAEXP-15833.1.1_10550.DWFA-884.2.2_17776.AAEXP-15848.1.1_14531.CEX-630.2.2_13564.DF-4046.2.3_2455.DPAY-2828.2.2_17390.AAEXP-15466.1.1_17354.AAEXP-15430.2.1_17271.DF-4240.1.1_17268.CEX-937.2.1_17406.AAEXP-15482.1.1_3961.B2B-663.2.3_17786.AAEXP-15858.1.1_14056.DF-4050.2.2_17770.AAEXP-15842.1.1_17752.AAEXP-15824.1.1_10382.DF-3962.2.2_17358.AAEXP-15434.1.1_11549.DM-1149.2.2_17788.AAEXP-15860.1.1_17350.AAEXP-15426.1.1_17420.AAEXP-15496.1.1_17342.AAEXP-15418.2.1_17741.AAEXP-15813.2.1_17779.AAEXP-15851.1.1_17749.AAEXP-15821.2.1_16055.CEX-741.1.1_14097.DM-1916.2.2_17387.AAEXP-15463.1.1_12891.TACO-234.2.3_17360.AAEXP-15436.2.1_9824.AP-523.2.3_14299.WDW-558.2.2_17397.AAEXP-15473.1.1_17385.AAEXP-15461.1.1_17381.AAEXP-15457.1.1_7759.DWFA-814.2.2_17783.AAEXP-15855.1.1_17774.AAEXP-15846.1.1_17386.AAEXP-15462.1.1_17758.AAEXP-15830.1.1_17345.AAEXP-15421.2.1_17344.AAEXP-15420.2.1_17384.AAEXP-15460.1.1_17352.AAEXP-15428.2.1_17782.AAEXP-15854.1.1_3613.WDW-267.2.2_13870.DF-4078.2.2_17408.AAEXP-15484.1.1_5030.B2B-444.2.7_6402.DWFA-716.2.3_16419.CEX-879.2.2_8287.TC-1035.2.5_17365.AAEXP-15441.1.1_17422.AAEXP-15498.1.1_17336.AAEXP-15412.1.1_17780.AAEXP-15852.1.1_16451.CEX-856.2.1_17746.AAEXP-15818.1.1_17373.AAEXP-15449.1.1_17771.AAEXP-15843.1.1_17375.AAEXP-15451.2.1_12498.DM-1867.2.3_17424.AAEXP-15500.1.1_17367.AAEXP-15443.1.1_14960.CEX-685.2.2_17339.AAEXP-15415.1.1_17747.AAEXP-15819.2.1_17392.AAEXP-15468.1.1_17755.AAEXP-15827.2.1_17359.AAEXP-15435.2.1_16420.CEX-736.2.2_17423.AAEXP-15499.1.1_17393.AAEXP-15469.1.1_12687.TACO-153.2.2_17388.AAEXP-15464.1.1_17410.AAEXP-15486.1.1_13176.B2B-1035.2.1_17735.AAEXP-15807.1.1_17413.AAEXP-15489.1.1_17304.WTT-1552.2.1_17364.AAEXP-15440.2.1_17738.AAEXP-15810.2.1_17767.AAEXP-15839.1.1_17409.AAEXP-15485.1.1_17389.AAEXP-15465.1.1_14961.CEX-501.2.2_7616.DWFA-777.2.2_17777.AAEXP-15849.1.1_17362.AAEXP-15438.1.1_14958.DF-4137.1.2_17421.AAEXP-15497.2.1_17340.AAEXP-15416.1.1_13871.CLAB-46.2.3_17414.AAEXP-15490.1.1_17785.AAEXP-15857.1.1_13913.TACO-235.2.2_15509.CEX-697.2.2_17768.AAEXP-15840.1.1_17267.WTT-1556.2.1_17759.AAEXP-15831.1.1_17762.AAEXP-15834.1.1_17353.AAEXP-15429.2.1; LMTBID=v2|72ca196e-cd8b-493c-91dc-86691b561765|d0a5ffe313861f7104b6f29b6c224bda; privacySettings=%7B%22v%22%3A2%2C%22t%22%3A1732665600%2C%22m%22%3A%22LAX%22%2C%22consent%22%3A%5B%22NECESSARY%22%2C%22PERFORMANCE%22%2C%22COMFORT%22%2C%22MARKETING%22%5D%7D; dapVn=206; _fwb=143mtwFPb3OUXZ3ulzU5k1o.1728826232232; _ga_66CXJP77N5=GS1.1.1735122687.3.0.1735122687.0.0.539602297; FPID=FPID2.2.qJbL6PKu93rO4XwhiGr0IUcsKfy5IqNdkkoQod3fJL0%3D.1728826233; speechToTextConsent=%7B%22anonymous%22%3Atrue%7D; _ga=GA1.1.1665477459.1732803529; _gcl_au=1.1.382903823.1733672143; INGRESSCOOKIE=93c6d7fbcb1cfd22d75854469f59d47a|a6d4ac311669391fc997a6a267dc91c0; userCountry=CN; dl_session=fa.a92fe1dd-2aaf-4b00-be88-81f9ebf168df; dapGid=0RYYVReijCaTo1N1tdRRGIO1mgmOG-QQzhRnjRkZvtaRURHmMd-v8juENhLUC_OyH2RRnehQT-DGNyBeRLxFNA; verifiedBot=false; dapSid=%7B%22sid%22%3A%22447a8b55-0243-4a79-9ba9-6fda7899a0b6%22%2C%22lastUpdate%22%3A1736849320%7D",
        "Host": "www2.deepl.com",
        "Origin": "https://www.deepl.com",
        "Referer": "https://www.deepl.com/zh/translator",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    }

    try:
        # json style
        response = requests.post(url, headers=headers, json=data)
        clear_line()
        if response.status_code == 200:
            json = response.json()
            translated = json['result']['translations']
            translated = translated[0]['beams']
            translated = translated[0]['sentences']
            translated = translated[0]['text']
            return translated
        elif response.status_code == 429:  # too many requests, too frequently
            print('Got response status_code 429 ... ', end='', flush=True)
            secs = response.headers.get('Retry-After')
            if not secs:
                # debug('No Retry-After in response headers')  # yes, do not have
                secs = 0
            wait_a_while(secs=secs)  # get time from response
            return translate_via_deepl_json(txt)
        else:
            err(f"请求失败，状态码: {response.status_code}")
            sys.exit(1)
    except requests.RequestException as e:
        err(f"发生请求异常: {e}")
    except Exception as e:
        err(f"发生未知异常: {e}")
    return None


def translate_via_deepl_selenium(txt):
    global BROWSER, SELENIUM_PREPARED, LAST_RESULT

    print('translating via selenium ... ', end='', flush=True)
    if not (SELENIUM_PREPARED and BROWSER):
        prepare_selenium()

    # input
    # CSS_SELECTOR 获取: 在浏览器开发调试界面（检查）、找到对应文本框，点右键，
    # 复制 -> CSS选择器
    input_box = BROWSER.find_element(By.CSS_SELECTOR, 'd-textarea.min-h-0 > div:nth-child(1)')
    if hasattr(input_box, 'text') and input_box.text:
        # debug('"input_box" has content, cleared')
        input_box.clear()  # 清空输入框
    input_box.send_keys(txt)
    BROWSER.implicitly_wait(10)

    # get result
    result = BROWSER.find_element(By.CSS_SELECTOR, '.last\\:grow > div:nth-child(1)')
    # wait for result
    wait_time = 0
    while True:
        # debug(f'\rcurrent result, before compare: {result.text}')
        if hasattr(result, 'text') and \
                cn_char.search(result.text) and \
                result.text != LAST_RESULT:
            # fake click 'CopyToClipboardMedium'
            btn = BROWSER.find_element(By.CSS_SELECTOR, 'button[data-testid="translator-target-toolbar-copy"]')
            btn.click()
            LAST_RESULT = result.text  # record new result
            break
        wait_time += 1
        print(f'\rwaited {wait_time} seconds for translated result ... ', end='', flush=True)
        time.sleep(1)

    clear_line()
    # debug(f'translate_via_deepl_selenium() got result: {result.text}')
    # import ipdb; ipdb.set_trace()
    # breakpoint()
    return result.text


def translation_file(fpath):
    global args

    if not isinstance(fpath, Path):
        fpath = Path(fpath)
    if not fpath.exists():
        err(f'文件不存在: {fpath}')
        return

    print(f'正在逐段翻译文件: {fpath}')

    paragraphs = get_rst_nodes(fpath)

    for p in paragraphs:
        p = p.astext()
        p = p.replace('\n', ' ')

        # feature: only list contents got from rst file
        if args.l:
            print(f'{p}\n')
            continue

        print(f'原文: {p}')

        # ignore already translated.
        if cn_char.search(p):
            p_green('已翻译\n')
            continue

        # skip short rows.
        if p.count(' ') <= 3:
            p_green('短句已跳过\n')
            continue

        p_green('译文:')
        # translate_via_deepl_selenium is slower than translate_via_deepl_json
        # but it won't run into 429 error.
        # tp = translate_via_deepl_selenium(p) or translate_via_deepl_json(p)
        tp = translate_via_deepl_selenium(p)
        tp = apply_fixes(p, tp)
        tp = apply_terms(tp)
        print(f'{tp}\n')

        # If do not wait a while, we may get 429 error.
        wait_a_while()


def wait_a_while(secs=None):
    secs = secs if secs else random.randint(10, 60)
    while secs >= 0:
        print(f'wait for {secs} seconds before next action ... ', end='', flush=True)
        time.sleep(1)
        secs -= 1
        clear_line()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='提取 rst 文件里需要翻译的内容，并用 deepl.com 翻译')

    parser.add_argument('file_path', metavar='str', nargs='*', type=str,
        help='要翻译的文件')
    parser.add_argument('-l', action=argparse.BooleanOptionalAction, default=False,
        help='仅罗列提取出的段落，不去翻译')

    parser.add_argument('--debug', action=argparse.BooleanOptionalAction, default=False,
        help='调试模式；默认关闭')
    args = parser.parse_args()

    DEBUG = True if args.debug else False
    debug(f'args = {args}')

    if args.file_path:
        try:
            translation_file(args.file_path[0])
        except KeyboardInterrupt:
            pass
        finally:
            BROWSER.close()
    else:
        parser.print_help()

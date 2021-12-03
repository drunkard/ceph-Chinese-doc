#!/usr/bin/python3

import os
import pandas as pd
import path
import re


doc_cn = '/git/DRUNKARD/ceph-Chinese-doc'
doc_en = '/git/ceph/doc'

LEN_DIFF_THRESHOLD = 5  # 译文和原文行数差别大于此值才显示
DIFF_ALIGN = 51     # 等号对齐列数
IGNORE_FILES = [
    # plain file
    'grep_words.sh',
    'README.md',    # empty file in ceph/doc as placeholder
    'README.rst',
    'vi_two_files.sh',

    # directory
    '.git',
    'scripts/__pycache__',
    'translation_cn',
    'zh_options',
]

# 翻译进度，需要统计的子系统列表
SUBSYS = [
    # 'api',
    'cephadm',
    'cephfs',
    'ceph-volume',
    # 'dev',
    'install',
    'jaegertracing',
    'man',
    'mgr',
    # 'mon',
    'rados',
    'radosgw',
    'rbd',
    'security',
    'start',
]
# Single file to debug, will be ignored if it's empty
FILEP = ''


def compare_file_existency():
    cnfl = _get_file_list(doc_cn, relpath=True)
    enfl = _get_file_list(doc_en, relpath=True)
    cn_uniq, en_uniq = [], []
    # print(cnfl)
    for c in cnfl:
        if c not in enfl:
            cn_uniq.append(c)
    for e in enfl:
        if e not in cnfl:
            en_uniq.append(e)
    # 去重
    cn_uniq, en_uniq = sorted(list(set(cn_uniq))), sorted(list(set(en_uniq)))
    cn_uniq = [str(f) for f in cn_uniq]
    en_uniq = [str(f) for f in en_uniq]
    print("译文和原文文件差异：")
    print('    译文版独有文件：{}\n    原文版独有文件：{}\n'.format(cn_uniq or '无', en_uniq or '无'))


def compare_file_length():
    cnfl = _get_file_list(doc_cn, relpath=True)
    enfl = _get_file_list(doc_en, relpath=True)
    fl = [cf for cf in cnfl
          if cf in enfl and
          (cf.endswith('.rst') or cf.endswith('.conf'))]
    print('"译文"和"原文"共有文件行数差别（行数差大于 {} 的）：'.format(LEN_DIFF_THRESHOLD))
    for f in fl:
        cn, en = _file_row_counts(doc_cn, f), _file_row_counts(doc_en, f)
        d = abs(cn - en)
        if d > LEN_DIFF_THRESHOLD:
            ss = '{} - {}'.format(cn, en)
            # 文件名缩进4， 行数相减右对齐，然后 = ，然后结果左对齐。
            print('    {} {:>{diff_align}} === {:}'
                  .format(f.ljust(DIFF_ALIGN), ss, d, diff_align=(DIFF_ALIGN / 3.1)))
    print()


def count_file_progress(f):
    ''' 单个文件的翻译进度 '''
    cn, total = 0, 0
    with open(f) as fo:
        for line in fo.readlines():
            total += 1
            if is_translated(line):
                cn += 1
    return (cn, total)


def _file_row_counts(*file_names):
    return len(open(os.path.join(*file_names)).readlines())


def _get_file_list(directory, only_rst=False, relpath=False):
    """
    返回一目录下的所有普通文件列表，递归，排序好。

    only_rst 是否只要 .rst 结尾的文件；
    relpath 是否返回相对于 <directory> 的路径；
    """
    p = path.Path(directory)
    if not p.exists():
        print('Not exists, please check work directory: {}'.format(p))
        os.exit(127)
    if not p.isdir():
        print('Not directory, please fix in code: {}'.format(p))
        os.exit(2)
    fl = p.walkfiles('*.rst') if only_rst else p.walkfiles()
    if relpath:
        fl = [f.relpath(directory) for f in fl]
    # Exclude files in IGNORE_FILES
    efl = []
    for f in fl:
        should_ignore = False
        for bname in IGNORE_FILES:
            if f.startswith(bname):
                should_ignore = True
                break
        if not should_ignore:
            efl.append(f)
    return sorted(efl)


def is_translated(line):
    '''
    比较规则：
    按行比较，有汉字就视作翻译了；
    以 [a-zA-Z] 打头的才计算；
    空行、[.-`*#:\] 、\s\t 打头的不算；
    '''
    cn_char = re.compile(r'[\u4e00-\u9fa5“”（）…—！《》，。：]')  # 匹配汉字
    starts = re.compile(r'^[\.\-=~_\^+|`*#:\(\)\[\]\\\s\t\"\'0-9]')  # 匹配行首
    if not line:  # 空行
        return True
    if cn_char.search(line) or starts.match(line):
        return True
    if FILEP:
        print(line, end='')  # debug, to catch exceptions of re expr
    return False


def to_pct(a, b):
    return '{}%'.format(round(a / b * 100, 2))


def translate_progress():
    # 统计结果暂存
    progress = pd.DataFrame(columns=['subsys', 'file', 'translated', 'total', 'pct'])
    # TODO: left align 'file' when show_all
    # pd.style.set_properties(**{'text-align': 'left'})\
    #     .set_table_styles([ dict(selector='th', props=[('text-align', 'left')]) ])
    idx = 0
    print('Progress by subsys:')
    for subsys in SUBSYS:
        print('{:<36}'.format(f'    counting subsys {subsys}/'), end='')
        files = _get_file_list(subsys, only_rst=True)
        for f in files:
            trans, total = count_file_progress(f)
            progress.loc[idx] = [subsys, f, trans, total, trans / total]
            idx += 1
        subsys_prog = progress[progress.subsys == subsys]
        r = subsys_prog.agg({'translated': sum, 'total': sum})
        print(to_pct(r.translated, r.total))

    # 总进度
    tp = progress.agg({'translated': sum, 'total': sum})
    print('Overall progress: \t\t{}'.format(to_pct(tp.translated, tp.total)))

    print('\nProgress by file: \n',
          progress.where(progress.pct != 1)\
          .sort_values('pct', ascending=False)\
          .dropna()\
          .head(50))


if __name__ == "__main__":
    compare_file_existency()
    compare_file_length()

    if FILEP:
        print(FILEP, count_file_progress(FILEP))
    else:
        # DataFrame 显示所有数据
        # pd.set_option('display.max_rows', 100)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # pd.set_option('display.max_colwidth', None)
        translate_progress()

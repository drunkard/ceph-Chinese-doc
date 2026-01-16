#!/cc/bin/python3

import argparse
import numpy as np
import os
import pandas as pd
import path
import re
import sys
from termcolor import colored, cprint

usage = f'''Counts file existence, row amount diffs, translated percentage.
Without files specified, counts all files.

Usage: {sys.argv[0]} [subsystem|subdir file_to_count ...]
'''

doc_cn = '/git/ceph-Chinese-doc'
doc_en = '/git/ceph/doc'

LEN_DIFF_THRESHOLD = 5  # 译文和原文行数差别大于此值才显示
DIFF_ALIGN = 51     # 等号对齐列数
EN_COLS = 80        # 英文版列数
IGNORE_FILES = [
    # plain file
    'grep_words.sh',
    'qa',
    'README.md',    # empty file in ceph/doc as placeholder
    'README.rst',
    'vim',

    # directory
    '.git',
    'translation_cn',
    'zh_options',
]

# 翻译进度，需要统计的子系统列表
SUBSYS = [
    # for newbie
    'start',
    'install',

    # core features
    'rados',
    'radosgw',
    'rbd',
    'cephfs',
    'man',
    # 'options',  # TODO 提取文档中的配置选项，然后解析这些选项描述信息的翻译情况

    # admin tools
    'cephadm',
    'ceph-volume',
    'mgr',
    # 'mon',
    # 'nvmeof',

    'monitoring',
    'hardware-monitoring',
    'jaegertracing',

    # for advanced users
    # 'api',
    # 'changelog',
    # 'dev',
    # 'releases',
    'security',
]
# flip original/translation when debug, mainly for seeing what translated looks like
FLIP = False  # TODO move to QA_SCOPE=='file' + '-a'

# 统计结果暂存
TP_COLUMNS = ['subsys', 'file', 'original', 'translated', 'total', 'pct', 'row_diff(cn-en)']
# remove column 'file', and remove '(cn-en)' in 'row_diff(cn-en)'
TP_COLUMNS_SHOW = ', '.join(
    [c.replace('(cn-en)', '') for c in TP_COLUMNS if c != 'file'])
TP = pd.DataFrame(columns=TP_COLUMNS)
# TP.style.format({'file': {'text-align': 'left'}})
# TP.style.set_properties(**{'text-align': 'left'})\
#     .set_table_styles([ dict(selector='th', props=[('text-align', 'left')]) ])

# Display related
OVERALL_SHOW_AMOUNT = 20  # TODO remove this, use args.n instead.
QA_SCOPE = 'all'  # could be: all / subsys / file

DEBUG = False


def debug(words, temp_enable=False):
    '''temp_enable: useful if debug just one place'''
    global args
    if DEBUG or args.debug or temp_enable:
        cprint(f'DEBUG: {words}', color='red')

def debug_stat(si):
    'si: Stat instance'
    attrs = [
        'f', 'line',
        # 'linen', 'linep',
        'indent', 'indentn1', 'indentn2',
        'i', 'imax',
        'done', 'total',
        # 'lines', 'done_idxs',
    ]
    print(dict((a, getattr(si, a)) for a in attrs))

def err(words):
    cprint(words, color='red', attrs=['bold'])

def warn(words):
    cprint(words, color='yellow')

def hdr(words):
    'print header line'
    cprint(words, color='cyan', attrs=['bold'])


class Stat(object):
    """
    This is translation stat of a single file.
    All stats saved in this object instance, and functions operates on it.
    """
    def __init__(self, file_path):
        self.f = file_path  # current processing file
        self.lines = self.file_lines()  # all cleaned lines, shouldn't change anymore

        self.i = self.get_idx_init()    # current index
        self.imax_default = len(self.lines) - 1
        self.imax = self.get_idx_max()  # rows of this file

        self.done = 0   # translated
        self.done_idxs = []
        self.total = 0  # total lines of file

    def clean_lines(self, ctx):
        # clean up first
        r = []
        for line in ctx:
            line = line.rstrip('\n')    # remove \n
            line = line.rstrip(' ')     # remove spaces, end of row
            r.append(line)
        return r

    def file_lines(self):
        with open(self.f) as fo:
            return self.clean_lines(fo.readlines())

    def get_idx_init(self):
        if not self.is_man:
            return -1
        # Ignore contents of whole 'Synopsis/提纲' section in man pages, that
        # is contents from head of file, to 描述/Description section title,
        # this code sets self.i (start index) as start point of counting.
        for w in ['描述', 'Description']:  # section header as flag.
            if (i := index_of_element(w, self.lines)) is not None:
                return i + 1
        print(f'WARN: been here, there may have bug in is_man() or get_idx_init(), file: {self.f}')
        return -1

    def get_idx_max(self):
        if not self.is_man:
            return self.imax_default
        # ignore 'See also' or '参考' section
        for w in ['参考', 'See also']:
            if (i := index_of_element(w, self.lines)) is not None:
                return i - 1
        # This man page do not have 'See also' section, return the defaults
        return self.imax_default

    def get_line(self, down=0):
        "return requested line, down means index is self.i+down"
        if (self.i + down) <= self.imax_default:
            return self.lines[self.i + down]
        return None

    def ignore_line(self):
        # File specific cases.
        # ignore quoted line
        fs = ['health-messages.rst', ]
        if self.f.name in fs and \
                self.line.lstrip().startswith('"') and \
                self.line.lstrip().endswith('"'):
            return True
        return ignore_one_line(self.line)

    @property
    def in_ignored_block(self):
        "Wether current line in is_ignore_blk()"
        pass  # TODO

    @property
    def indent(self):
        return get_indent(self.line, lineno=(self.i + 1))

    @property
    def indentn1(self):
        # indent of next line
        return get_indent(self.linen)

    @property
    def indentn2(self):
        # indent of next 2 line
        return get_indent(self.get_line(down=2))

    @property
    def is_man(self):
        "Check if this is man pages"
        if 'man/8/' in self.f:
            return True
        return False

    @property
    def line(self):
        # current line
        if self.i == -1:
            return None  # not started yet
        return self.lines[self.i]

    @property
    def linen(self):
        # next line
        return self.get_line(down=1)

    @property
    def linep(self):
        # previous line
        return self.lines[self.i - 1]

    @property
    def original(self):
        return self.total - self.done

    def record(self):
        'record current line as translated'
        self.done += 1
        self.done_idxs.append(self.i)

    @property
    def row_diff(self):
        return file_rows(doc_cn, self.f) - file_rows(doc_en, self.f)


def compare_file_existency():
    cnfl = _get_file_list(doc_cn, relpath=True)
    enfl = _get_file_list(doc_en, relpath=True)
    cn_uniq, en_uniq = [], []
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


def compare_file_length(files=None):
    "arg files: None or list."
    ignore_threshold = False  # show result, ignore LEN_DIFF_THRESHOLD
    if files:
        fl = files
        ignore_threshold = True
    else:
        cnfl = _get_file_list(doc_cn, relpath=True)
        enfl = _get_file_list(doc_en, relpath=True)
        fl = [cf for cf in cnfl
            if cf in enfl and
            (cf.endswith('.rst') or cf.endswith('.conf'))]
    print('"译文"和"原文"共有文件行数差别（行数差大于 {} 的）：'.format(LEN_DIFF_THRESHOLD))
    eqs = []
    for f in fl:
        cn, en = file_rows(doc_cn, f), file_rows(doc_en, f)
        d = cn - en
        if d == 0:
            eqs.append(f)
        elif ignore_threshold or abs(d) > LEN_DIFF_THRESHOLD:
            ss = '{} - {}'.format(cn, en)
            # 文件名缩进4， 行数相减右对齐，然后 = ，然后结果左对齐。
            print('    {} {:>{diff_align}} === {:}'
                  .format(f.ljust(DIFF_ALIGN), ss, d, diff_align=(DIFF_ALIGN / 3.1)))
    if eqs and len(FILES) >= 1:
        print('行数相同的：', end='')
        for f in eqs:
            print(str(f), end=' ')
        print()
    print()


def count_file_progress(f):  # noqa
    ''' 单个文件的翻译进度 '''
    global S
    S = Stat(f)
    # debug_stat(S)

    # section to ignore, one transaction once, so reuse this flag
    blk_flag = 0
    blk_indent = 0

    while S.i < S.imax:
        # debug_stat(S)
        # if 331 < S.i < 341: debug_stat(S)
        S.i += 1

        # if 88<S.i<93: debug(f'{S.i}: blk_flag={blk_flag} S.indent={S.indent} blk_indent={blk_indent} line="{S.line}"', 1)
        if S.ignore_line():
            continue

        # ignore table translation.
        if is_table(S):
            continue

        if is_ignore_blk(S.line):
            blk_flag = 1
            # init new block
            # Assume this block should be ignored, the next / next 2 row must
            # be indented.
            # If S.linen not exists, get_indent(S.linen) would be None, so fill
            # 0 as last fix.
            blk_indent = S.indentn1 or S.indentn2 or 0
            if blk_indent == 0:
                blk_flag = 0  # ignore role block ended, maybe on-line role.
            elif blk_indent > 8:
                # with ditaa, the first row maybe indented too much, and
                # won't align with following rows, so cut it to the least: 3.
                blk_indent = 3
            if not is_cmd(S.line):
                # For code block, no matter blk_indent ==/!= 0, this row should ignore.
                # For cmd block, the row contains '::' counts.
                continue

        if is_blank_row(S.line):
            if blk_flag >= 1:
                blk_flag += 1
            continue  # don't count blank line
        # blk_indent != 0, check if it changed
        # if 88<S.i<92: debug(f'{S.i}: blk_flag={blk_flag} S.indent={S.indent} blk_indent={blk_indent} line="{S.line}"', 1)
        # if S.i==91: debug(S.line, 1)

        if blk_flag >= 1 and S.indent >= blk_indent:
            # still indented as command, ignore it
            continue
        else:
            if blk_flag > 2:  # got 2 blank rows, cmd block maybe ended
                blk_flag = 0
                blk_indent = 0

        S.total += 1

        if is_translated(S.line):
            # Show un-translated lines
            if FLIP: print('{:<3}:'.format(S.i + 1), S.line)

            S.record()
            continue
    return S


def count_files(files):
    global TP
    for f in files:
        debug(f'processing file: {f}')
        subsys = str(f.splitall()[1])
        try:
            S = count_file_progress(f)
        except Exception as e:
            err(f'Got error with file: {f}')
            raise e
        # debug('got data of: {f}:')
        # print(' '*3, [subsys, f, S.original, S.done, S.total, to_pct(S.done, S.total), S.row_diff])  # debug
        TP.loc[f] = [subsys, f, S.original, S.done, S.total, to_pct(S.done, S.total), S.row_diff]


def file_rows(*paths):
    "count file rows"
    with open(os.path.join(*paths)) as f:
        return len(f.readlines())


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
    if not p.is_dir():
        print('Not directory, please fix in code: {}'.format(p))
        os.exit(2)
    fl = p.walkfiles('*.rst') if only_rst else p.walkfiles()
    if relpath:
        fl = [f.relpath(directory) for f in fl]
    # Exclude files in IGNORE_FILES
    efl = []
    for f in fl:
        # Drop python cache files.
        if f.endswith('.pyc'):
            continue

        should_ignore = False
        for bname in IGNORE_FILES:
            if f.startswith(bname):
                should_ignore = True
                break
        if not should_ignore:
            efl.append(f)
    return sorted(efl)


def get_indent(line, lineno=None):
    '''
    获取一行的缩进数量
    lineno: 本行的行号
    '''
    if line is None:
        return None

    # Only show this warn when doing one file.
    if '\t' in line and lineno and FLIP:
        warn(f'Has TAB in line {lineno}: {line}')

    return len(line) - len(line.lstrip())


def hl_pct(x):
    c = 'green' if x > 90 else 'white'
    return colored(x, color=c)


def hl_row_diff(x):
    if abs(x) > LEN_DIFF_THRESHOLD:
        c = 'red'
    else:
        c = 'white'
    # debug(f'x type is: {type(x)}, value={x}')
    if x == np.nan:
        x = 0
    return colored(int(x) if x != 0 else '', color=c)


def hook_check_errors():
    '检查文档里的常见错误'
    raise NotImplementedError('尚未实现: 检查文档里的常见错误')


def hook_linkcheck():
    '''
    Check if link works, it's just a hook of:
        cd /git/ceph && ./admin/zh_build-doc linkcheck
    '''
    os.chdir('/git/ceph')

    cmd = './admin/zh_build-doc linkcheck'
    cprint(f'执行命令: {cmd}', color='white', attrs=['bold'])
    os.system(cmd)


def hook_yaml_files():
    pass


def index_of_element(e, list_):
    "return index of specified element, None if not matched"
    try:
        return list_.index(e)
    except ValueError:
        pass
    return None


def is_ignore_blk(line, indent=0):
    '''
    args:
        line - line to check, if this is start of section that should ignore.
        indent - the min indent of this section.
    '''
    if is_code_blk(line):
        # print('is_ignore_blk:', line)
        return True

    # Command should be ignored
    # if the following paragraph is command, 0=not, 1=enter, 2=end
    # Decides if it's cmd by counting the leading spaces, reset blk_flag=0
    # if indent changed.
    if is_cmd(line):
        return True

    return False


def is_blank_row(line):
    br = re.compile(r'\s+')
    if not line or br.fullmatch(line):
        return True
    return False


def is_cmd(line):
    if not line.startswith('.. ') and line.endswith('::'):
        return True
    # There's file specific cases.
    if S.f.name == 'cephfs-shell.rst' and line.endswith('：'):
        return True
    return False


def is_code_blk(line):
    '''If matched the rst role, it needs two more blank row to end this block.
    '''
    roles = [
        # Never skip these roles.
        # 'topic', 'tip', 'note', 'caution', 'warning', 'important', 'DANGER',
        # 'sidebar',
        # TODO ignore the term row in 'glossary', explaination below it counts.
        'code', 'code-block', 'prompt',
        'py:class', 'py:currentmodule',
        'ditaa', 'graphviz', 'image', 'raw',
        'list-table',  # will be rendered as table
        'toctree', 'literalinclude',
        'autoclass', 'automethod', 'automodule',
        '|---|   unicode',
    ]
    for role in roles:
        if line.count(f'.. {role}::') > 0:
            return True
    return False


def is_table(stat_instance):
    '''
    table like this:

    ================ =============== =============== =================
     Previous State   Current State   Uptime Update   Downtime Update
    ================ =============== =============== =================
     Available        Available       +diff time      no update
     Available        Unavailable     +diff time      no update
     Unavailable      Available       +diff time      no update
     Unavailable      Unavailable     no update       +diff time
    ================ =============== =============== =================

    If matched as table, the pointer "Stat.i" will move to end of table.
    '''
    # 正则表达式，一行里只有等号和空格，且等号和空格都必须存在
    # table_bar = re.compile(r'^[=\s]+$')
    table_bar = re.compile(r'^(?=.*=)(?=.*\s)[=\s]+$')

    # 如果匹配到表头，就一直往下，找齐3个表头
    if stat_instance.line.startswith('=') and table_bar.fullmatch(stat_instance.line):
        bar_cnt = 1
        debug(f'line {stat_instance.i + 1}: matched table bar, bar_cnt={bar_cnt}')
        while bar_cnt < 3:
            stat_instance.i += 1
            if stat_instance.line.startswith('=') and table_bar.fullmatch(stat_instance.line):
                bar_cnt += 1
                debug(f'line {stat_instance.i + 1}: matched table bar, in loop; bar_cnt={bar_cnt}')

        return True

    return False


def is_title(si, idx=None, main_title=False):
    '''
    check if current line is title, if the next line is all syms
    si = Stat instance, idx is current index
    main_title: there's the same syms in previous and next line.
    '''
    if idx is not None:
        linep = si.lines[idx - 1]
        linen = si.lines[idx + 1]
    else:
        linep = si.linep
        linen = si.linen
    if main_title:
        if is_title_sym(linep) and is_title_sym(linen):
            return True
    else:
        if linen is not None and is_title_sym(linen):
            return True
    return False


def is_title_sym(line):
    title_syms = ['=', '-', '`', '\'', '.', '~', '*', '+', '_', '^']
    for sym in title_syms:
        # they are 0 for blank lines, so exclude 0
        if line.count(sym) == len(line) != 0:
            return True
    return False


def is_translated(line=None):
    '''
    比较规则：
    按行比较，有汉字就视作翻译了；
    以 [a-zA-Z] 打头的才计算；
    空行、[.-`*#:\\] 、\\s\\t 打头的不算；
    '''
    global args, FLIP

    def false_return(line):
        # debug, to catch exceptions of re expr
        if len(FILES) == 1 and not FLIP:
            print('{:<3}:'.format(S.i + 1), line)
        return False

    global S
    line = line or S.line
    cn_char = re.compile(r'[\u4e00-\u9fa5“”（）…—！《》，。：；、]')  # 匹配汉字
    if cn_char.search(line):
        if args.a and QA_SCOPE == 'file':
            cprint('{:<3}: {}'.format(S.i + 1, line), color='green')
        return True
    if is_title(S):
        if line.count(' ') <= 2:
            # treat short title (less than 3 words) as translated, do not check
            return True
        else:
            return false_return(line)  # count in long titles

    # ignore short rows, too many symbols in them.
    if len(line) < (EN_COLS / 3) or line.strip(' ').count(' ') <= 1:
        # print('{:<3}:'.format(S.i + 1), line)  # debug, what translated row looks like
        # if 36<=S.i<=37: debug(line, 1)
        return True

    return false_return(line)


def ignore_one_line(line):  # noqa
    '''我们只统计需要翻译的，所以以下忽略掉：
    空行，包括只含有空格的行；
    注释行；
    标题下的那行符号 [=\\-~_`'\\.\\*\\+\\^]+
    命令行、终端内容（暂时未实现）；
    ditaa 图；
    '''

    # ignore links
    if line.startswith('.. _') and (line.endswith(':') or line.count(': ') == 1):
        return True
    if line.count('`') == 2 and line.endswith('`_'):  # is hyperlink, could ignore
        return True

    # ignore command, whole line is command
    # For numbered line, there's "#. " or " * " at lead of row.
    if (line.startswith('``') or ('``' in line and line.index('``') <= 4)) \
            and (line.endswith('``') or line.endswith('*')):
        return True

    # ignore comment
    # TODO ignore comment block, starts with '.. ', ends with non-space started row
    if line.startswith('.. ') and line.count('::') == 0:
        return True

    # ignore table
    if (line.startswith('+-') and line.endswith('-+')) or \
            (line.startswith('|') and line.endswith('|')) or \
            (line.startswith('+=') and line.endswith('=+')):
        return True

    # ignore title symbol line
    if is_title_sym(line):
        return True

    # man page specific
    if line.startswith('|'):
        return True
    if line.startswith(':command:') or line.startswith(':orphan:'):
        return True

    # ignore some rst roles, just this row, following still counts
    roles = [
        'confval', 'program', 'option', 'describe',
        'deprecated', 'versionadded', 'versionchanged',
        'index', 'contents',
        'highlight', 'autodoxygenfile',
        'ceph_releases', 'ceph_timeline',
    ]
    for role in roles:
        if line.count(f'.. {role}::') > 0:
            return True
    # if idx==91: debug(line, 1)
    return False


def merge_lines():
    '把输入的多行文本合并成一行'
    lines = []

    hdr('输入的多行内容将合并成单行。')
    print('  n 下一轮；\n  q 结束并退出。\n请输入：')
    while True:
        line = input()
        if line == 'n':  # means finish inputs, start next round of inputs
            os.system('clear -x')
            err('输入结束')
            break
        elif line == 'q':
            sys.exit(0)  # exit whole feature

        lines.append(line)

    # remove multiple newlines in end
    debug(lines)
    while lines and lines[-1].strip() == '':
        lines.pop()

    hdr('合并后的行:')
    for line in lines:
        line = line.strip()
        line = line.replace('  ', ' ')
        if line:
            line = colored(line.strip() + ' ', color='green', attrs=['bold'])
            print(line, end='')
        else:
            print('\n')  # leave one blank row
    print('\n')
    # cprint(' ' * os.get_terminal_size()[0], on_color='on_green')  # screen split bar
    merge_lines()  # next round inputs


def parse_arg_files(args):
    global QA_SCOPE
    # Single file(s)/subsys to debug, will be ignored if it's empty
    FILES = []
    if args.paths:
        paths = [path.Path(p) for p in args.paths]
        if all([p.is_dir() for p in paths]):
            QA_SCOPE = 'subsys'
        elif all([p.is_file() for p in paths]):
            QA_SCOPE = 'file'
        else:
            # maybe it's mixed of files and dirs, just ignore that, be simple.
            QA_SCOPE = 'all'
        FILES = path_to_files(args.paths)
    else:
        QA_SCOPE = 'all'
    debug(f'parse_arg_files(): QA_SCOPE={QA_SCOPE}  FILES = {FILES}')
    return FILES


def path_to_files(paths):
    '''Check path types of all element in 'paths', grab files for directories'''
    # debug(f'path_to_files() arg: {paths}')
    files = []
    for p in paths:
        p = remove_prefix_path(p)

        p = path.Path(p)
        if p.is_dir():
            files += _get_file_list(p, only_rst=True)
        elif p.is_file():
            files.append(p)
        elif not p.exists():
            cprint(f'Error: file not exists: {p}', color='red')
            sys.exit(127)
        else:
            raise TypeError(f'Unknown file type: {p} type= {type(p)} cwd= {p.cwd()}')
    # debug(f'path_to_files() result: {files}')
    return files


def remove_prefix_path(fpath):
    "remove prefix of path, the input path is pasted from regular paths."
    pattern = r'^[ab]/'
    if re.findall(r'^[ab]/', fpath):
        fpath = re.sub(r'^[ab]/', '', fpath)

    pattern = '^doc/'
    if re.findall(pattern, fpath):
        fpath = re.sub(pattern, '', fpath)

    pattern = '^doc-en/'
    if re.findall(pattern, fpath):
        fpath = re.sub(pattern, '', fpath)

    pattern = f'^{doc_en}-zh/'
    if re.findall(pattern, fpath):
        fpath = re.sub(pattern, '', fpath)

    pattern = f'^/data{doc_en}/'
    if re.findall(pattern, fpath):
        fpath = re.sub(pattern, '', fpath)

    return fpath


def show_DataFrame_files(TP):
    # 单行
    if len(FILES) == 1:
        print(TP)
        return

    # 多行
    # 修饰
    # remove rows which: pct == 100%
    if args.sd or (args.sort_by_column and args.sort_by_column != ['row_diff']):
        pass
    elif OVERALL_SHOW_AMOUNT != 0:
        # remove rows which: pct == 100%
        # .where 只是筛选出了符合条件的，然后它们的值都被设置成了 np.nan ，
        # dropna() 再删除这些数值为 np.nan 的行
        TP = TP.where(TP.pct != 100).dropna()

    # debug
    # debug(TP)
    '''
    with pd.option_context(
        'display.colheader_justify', 'center',  # left/center/right
        'display.max_rows', None,
    ):
        print(TP.isna())
        print(TP)
    '''

    TP['pct'] = TP['pct'].apply(hl_pct)  # highlight pct
    TP['row_diff(cn-en)'] = TP['row_diff(cn-en)'].apply(hl_row_diff)  # highlight row_diff
    TP = TP.astype({
        "original": "int32",
        "translated": "int32",
        "total": "int32"
    })
    # style = TP.style.set_properties(subset=['pct', 'row_diff(cn-en)'], **{'text-align': 'right'})\
    #     .set_table_styles([ dict(selector='th', props=[('text-align', 'right')] ) ])
    # import ipdb; ipdb.set_trace()

    # 打印
    with pd.option_context(
        'display.colheader_justify', 'center',  # left/center/right
        'display.max_rows', OVERALL_SHOW_AMOUNT or None,
    ):
        # 这里不能直接打印，直接 print(TP) 会打印首尾，中间是 ...
        # 而我要的效果是打印前 X 条。
        # -1 / None 表示打印所有； 0 就不打印了，不是我要的效果。
        print(TP.head(OVERALL_SHOW_AMOUNT or None))
    # print(TP.where(TP.pct != 100).sort_values('original').dropna().head(OVERALL_SHOW_AMOUNT))


def sort_DataFrame(df):
    global args
    if args.sort_by_column:
        sort_col = args.sort_by_column[0]
        # small fix, "()" causes trouble in shell.
        if sort_col == 'row_diff':
            sort_col = 'row_diff(cn-en)'
    else:
        sort_col = 'pct'  # default sort column

    # '--sd' option gets high priority
    if args.sd:
        sort_col = 'row_diff(cn-en)'

    # 升序/降序
    ascending = False if args.r else True

    # 没指定任何排序选项时
    if not any([args.sort_by_column, args.r, args.sd]):
        sort_col, ascending = 'pct', False

    # last check
    if sort_col not in TP_COLUMNS:
        err(f'指定的排序列不存在: {sort_col}, 可用的有: {TP_COLUMNS_SHOW}')
        sys.exit(2)

    debug(f'sort option: sort_col={sort_col} ascending={ascending}')
    # debug(df.describe())
    df = df.sort_values(by=sort_col, ascending=ascending)  # ascending 升序
    return df


def to_pct(a, b):
    if a == b == 0:  # All zero, nothing to process, treat as done.
        # When count on specified subsys, others is absent, so should be 0.
        return 100.00 if QA_SCOPE == 'all' else 0
    return round(a / b * 100, 2)


def translate_progress(files=None):
    global QA_SCOPE
    global TP  # pandas DataFrame, translation progress
    if files:
        count_files(files)
    else:
        for subsys in SUBSYS:
            files = _get_file_list(subsys, only_rst=True)
            count_files(files)

    # debug(f'translate_progress(): QA_SCOPE={QA_SCOPE}  FILES = {FILES}')

    # show progress overall
    if QA_SCOPE == 'all':
        tp = TP.agg({'original': sum, 'translated': sum, 'total': sum})
        print('Overall progress:   {}% ({} of {} rows to translate)'
            .format(to_pct(tp.translated, tp.total), tp.original, tp.total))

    # show subsys progress
    # Only show when there's more than one subsys.
    if QA_SCOPE == 'all' or (QA_SCOPE == 'subsys' and len(args.paths) > 1):
        print('Progress by subsys:')
        for subsys in SUBSYS:
            subsys_prog = TP[TP.subsys == subsys]
            r = subsys_prog.agg({'translated': sum, 'total': sum})
            print('{:<26}{}%'.format(f'    {subsys}/', to_pct(r.translated, r.total)))

    # show progress by file
    print(F'Progress by file (near finished {OVERALL_SHOW_AMOUNT} files):')
    TP.set_index('file')
    TP = TP.drop('file', axis=1)
    TP = sort_DataFrame(TP)
    show_DataFrame_files(TP)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=usage)
    parser.add_argument('--debug', action=argparse.BooleanOptionalAction, default=False,
        help='调试模式；默认关闭')

    # Show all file's progress, include done files
    # When show one file's progress, also show translated row, in green.
    parser.add_argument('-a', action=argparse.BooleanOptionalAction, default=False,
        help='显示所有文件的进度，包括已完成文件的，相当于 "-n 0"； 查看单个文件时表示：显示已翻译的内容；')
    parser.add_argument('-n', action='store', default=OVERALL_SHOW_AMOUNT, type=int,
        help=f'显示整体翻译进度时，最后的表格里展示多少个文件，0 显示所有。默认 {OVERALL_SHOW_AMOUNT}')
    # Sort reverse
    parser.add_argument('-r', action=argparse.BooleanOptionalAction, default=False,
        help='反向排序，默认升序')
    # Sort 'Progress by file' by specified column
    parser.add_argument('-s', action='store', dest='sort_by_column', nargs=1,
        help=f'按指定列排序，支持的列有： {TP_COLUMNS_SHOW}')
    parser.add_argument('--sd', action='store_true', default=False,
        help='"-s row_diff" 的快捷方式')


    # Filter out wrong tags in rst file, like ".. note:", which is actually
    # comment but intended to be a NOTE block.
    parser.add_argument('--ce', action='store_true', default=False,
        help='Check Errors, 检查常见的文档书写、格式错误；')

    parser.add_argument('--linkcheck', action='store_true', default=False,
        help='检查链接是否有效')

    # yaml features:
    # check/compare yaml option files.
    # Option: update my copy with program.
    # Get 'desc' of specified option name, from raw file.
    parser.add_argument('--yaml', action='store_true', default=False,
        help='比较配置选项文件，即 *.yaml.in 文件')

    parser.add_argument('-m', action='store_true', default=False,
        help='把输入的多行文本合并成一行，以便粘贴到翻译软件。附加功能。')


    parser.add_argument('paths', nargs='*', type=str,
        help='要翻译的文件')

    args = parser.parse_args()
    debug(f'args = {args}')

    if args.ce:
        hook_check_errors()
        sys.exit()
    elif args.linkcheck:
        hook_linkcheck()
        sys.exit()
    elif args.yaml:
        hook_yaml_files()
    elif args.m:
        merge_lines()
        sys.exit(0)

    FILES = parse_arg_files(args)

    if args.n != OVERALL_SHOW_AMOUNT:
        OVERALL_SHOW_AMOUNT = args.n

    # 效果一样
    if args.a:
        OVERALL_SHOW_AMOUNT = 0

    if not FILES:
        parser.print_help()
        print()

        # Don't run this when processes specified files
        compare_file_existency()

    # compare_file_length(files=FILES)  # TODO as option

    translate_progress(files=FILES)

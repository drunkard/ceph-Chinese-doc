#!/cc/bin/python3

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
    'hardware-monitoring',
    'install',
    'jaegertracing',
    'man',
    'mgr',
    # 'mon',
    'monitoring',
    # 'nvmeof',
    'rados',
    'radosgw',
    'rbd',
    'security',
    'start',
    # 'options',  # TODO 提取文档中的配置选项，然后解析这些选项描述信息的翻译情况
]
# flip original/translation when debug, mainly for seeing what translated looks like
FLIP = False  # TODO rename to ONE_FILE__VERBOSE

# 统计结果暂存
TP = pd.DataFrame(
    columns=['subsys', 'file', 'original', 'translated', 'total', 'pct', 'row_diff(cn-en)'],
)
# TP.style.format({'file': {'text-align': 'left'}})
# TODO: left align 'file' when show_all
# TP.style.set_properties(**{'text-align': 'left'})\
#     .set_table_styles([ dict(selector='th', props=[('text-align', 'left')]) ])

# Display related
OVERALL_SHOW_AMOUNT = 30


DEBUG = False

def debug(words, temp_enable=False):
    '''temp_enable: useful if debug just one place'''
    if DEBUG or temp_enable:
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
        subsys = str(f.splitall()[1])
        debug(f'processing file: {f}')
        try:
            S = count_file_progress(f)
        except Exception as e:
            print(f'Got error with file: {f}')
            raise e
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
        msg_warn(f'Has TAB in line {lineno}: {line}')

    return len(line) - len(line.lstrip())


def hl_pct(x):
    c = 'green' if x > 90 else 'white'
    return colored(x, color=c)


def hl_row_diff(x):
    if abs(x) > LEN_DIFF_THRESHOLD:
        c = 'red'
    else:
        c = 'white'
    return colored(int(x) if x != 0 else '', color=c)


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
    ]
    for role in roles:
        if line.count(f'.. {role}::') > 0:
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
    def false_return(line):
        # debug, to catch exceptions of re expr
        if len(FILES) == 1 and not FLIP:
            print('{:<3}:'.format(S.i + 1), line)
        return False

    global S
    line = line or S.line
    cn_char = re.compile(r'[\u4e00-\u9fa5“”（）…—！《》，。：、]')  # 匹配汉字
    if cn_char.search(line):
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


def msg_warn(words):
    cprint(words, color='yellow')


def path_to_files(paths):
    '''Check path types of all element in 'paths', grab files for directories'''
    files = []
    for p in paths:
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
    return files


def to_pct(a, b):
    if a == b == 0:  # All zero, nothing to process, treat as done.
        return 100.00
    return round(a / b * 100, 2)


def translate_progress(files=None):
    global TP  # pandas DataFrame, translation progress
    if files:
        count_files(files)
    else:
        print('Progress by subsys:')
        for subsys in SUBSYS:
            print('{:<26}'.format(f'    {subsys}/'), end='')
            files = _get_file_list(subsys, only_rst=True)
            count_files(files)
            subsys_prog = TP[TP.subsys == subsys]
            r = subsys_prog.agg({'translated': sum, 'total': sum})
            print('{}%'.format(to_pct(r.translated, r.total)))

    # Progress overall
    tp = TP.agg({'original': sum, 'translated': sum, 'total': sum})
    print('Overall progress:   {}% ({} of {} to translate)'
          .format(to_pct(tp.translated, tp.total), tp.original, tp.total))

    # Progress by file
    TP.set_index('file')
    TP = TP.drop('file', axis=1)
    TP = TP.sort_values('pct', ascending=False)
    print(F'Progress by file (near finished {OVERALL_SHOW_AMOUNT} files):')
    if len(FILES) == 1:
        print(TP)
    else:
        TP = TP.where(TP.pct != 100).dropna()  # remove completed
        TP['pct'] = TP['pct'].apply(hl_pct)  # highlight pct
        TP['row_diff(cn-en)'] = TP['row_diff(cn-en)'].apply(hl_row_diff)  # highlight row_diff
        TP = TP.astype({"original": "int32", "translated": "int32", "total": "int32"})
        # style = TP.style.set_properties(subset=['pct', 'row_diff(cn-en)'], **{'text-align': 'right'})\
        #     .set_table_styles([ dict(selector='th', props=[('text-align', 'right')] ) ])
        # import ipdb; ipdb.set_trace()
        with pd.option_context('display.colheader_justify','right'):
            print(TP.head(OVERALL_SHOW_AMOUNT))
        # print(TP.where(TP.pct != 100).sort_values('original').dropna().head(OVERALL_SHOW_AMOUNT))


if __name__ == "__main__":
    # Single file(s)/subsys to debug, will be ignored if it's empty
    FILES = path_to_files(sys.argv[1:]) if len(sys.argv) >= 2 else []

    # TODO move to argparse
    # Show all file's progress, include done files

    if not FILES:
        print(usage)

        # Don't run this when processes specified files
        compare_file_existency()

    # compare_file_length(files=FILES)

    # DataFrame 显示所有数据
    # pd.set_option('display.max_rows', 100)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', None)
    # pd.set_option('display.max_colwidth', None)
    translate_progress(files=FILES)
    # TODO exit_code = 0 if pct == 1 else original, or total of original ?

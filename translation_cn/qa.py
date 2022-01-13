#!/cc/bin/python3

import os
import pandas as pd
import path
import re
import sys

usage = '''Counts file existence, row amount diffs, translated percentage.
Without files specified, counts all files.
Usage: {} [file_to_count ...]\n'''.format(sys.argv[0])

doc_cn = '/git/DRUNKARD/ceph-Chinese-doc'
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

# 统计结果暂存
TP = pd.DataFrame(columns=['subsys', 'file', 'translated', 'total', 'pct'])
# TODO: left align 'file' when show_all
# pd.style.set_properties(**{'text-align': 'left'})\
#     .set_table_styles([ dict(selector='th', props=[('text-align', 'left')]) ])
IDX = 0  # index for pandas.DataFrame
RN = 0  # current row number


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
    show_anyway = False  # show result, ignore LEN_DIFF_THRESHOLD
    if files:
        fl = files
        show_anyway = True
    else:
        cnfl = _get_file_list(doc_cn, relpath=True)
        enfl = _get_file_list(doc_en, relpath=True)
        fl = [cf for cf in cnfl
            if cf in enfl and
            (cf.endswith('.rst') or cf.endswith('.conf'))]
    print('"译文"和"原文"共有文件行数差别（行数差大于 {} 的）：'.format(LEN_DIFF_THRESHOLD))
    eqs = []
    for f in fl:
        cn, en = _file_row_counts(doc_cn, f), _file_row_counts(doc_en, f)
        d = cn - en
        if d == 0:
            eqs.append(f)
        elif abs(d) > LEN_DIFF_THRESHOLD or show_anyway:
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
    # TODO rewrite in list() instead of file.readlines()
    cn, total = 0, 0
    global RN
    with open(f) as fo:
        # Command should be ignored
        # if the following paragraph is command, 0=not, 1=enter, 2=end
        # Decides if it's cmd by counting the leading spaces, reset cmd_flag=0
        # if indent changed.
        cmd_flag = 0
        cmd_indent = 0

        # Decide if this section is code/role, co-used by code/role
        # 0=not, 1=yes, >=3 end
        code_flag = 0
        trans_flag = True  # to count title, some title not translated

        # ignore 'Synopsis' section in man pages
        man_synopsis = 1 if 'man' in f.splitall() else 0

        # count titles, 0=ignore, 1=count in
        # Ignore titles, treat all of them as translated.
        count_titles = 0
        # TODO has bug, fix it

        for line in fo.readlines():
            RN += 1
            # clean up first
            line = line.rstrip('\n')    # remove \n
            line = line.rstrip(' ')     # remove spaces

            # There's file specific cases.
            if line.endswith('::') or \
                    (f.name == 'cephfs-shell.rst' and line.endswith('：')):
                cmd_flag = 1
                cmd_indent = 0  # init new cmd block
            if is_code(line):
                code_flag += 1
            if man_synopsis > 0:
                if line in ['描述', 'Description']:  # section header as flag.
                    # Synopsis section finished, turn this flag off.
                    man_synopsis = 0
                    continue
                if line in ['提纲', 'Synopsis']:  # section header as flag.
                    man_synopsis = 2
                if man_synopsis == 2:
                    continue
            if is_blank_row(line):
                if cmd_flag >= 1:
                    cmd_flag += 1
                if code_flag >= 1:
                    code_flag += 1
                continue  # don't count blank line
            # if RN >= 45: print(f'RN={RN} cmd_flag={cmd_flag} cmd_indent={cmd_indent}')  # debug
            # if RN >= 45: print(f'RN={RN} code_flag={code_flag} trans_flag={trans_flag}')  # debug
            if cmd_flag >= 2:
                if cmd_indent == 0:
                    cmd_indent = get_indent(line)
                    continue
                # cmd_indent != 0, check if it changed
                if get_indent(line) >= cmd_indent:
                    # still indented as command, ignore it
                    continue
                else:
                    if cmd_flag > 2:  # got 2 blank rows, cmd block maybe ended
                        cmd_flag = 0
                        cmd_indent = 0
            if is_ignored(line):
                continue
            if code_flag >= 1:
                if get_indent(line) >= 3:  # not blank row, but indented
                    continue
                elif code_flag >= 3:
                    code_flag = 0
            total += 1
            # print(f'ttt trans_flag={trans_flag}', line)
            if trans_flag == False and is_title(line):
                trans_flag = True
                cn += count_titles
                total += -(count_titles + 1)  # remove counted title row
                continue
            # print('ddd', cmd_indent, get_indent(line), line)  # debug
            if is_translated(line):
                cn += 1
                trans_flag = True
                continue
            else:
                trans_flag = False
    return (cn, total)


def count_files(files):
    global IDX, TP
    for f in files:
        subsys = str(f.splitall()[1])
        trans, total = count_file_progress(f)
        TP.loc[IDX] = [subsys, f, trans, total, to_pct(trans, total)]
        IDX += 1


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


def get_indent(line):
    '获取一行的缩进数量'
    return len(line) - len(line.lstrip())


def is_blank_row(line):
    br = re.compile(r'\s+')
    if not line or br.fullmatch(line):
        return True
    return False


def is_code(line):
    '''If matched the rst role, it needs two more blank row to end this block.
    '''
    # TODO split needed, some roles should be ignored.
    roles = [
        # Never skip these roles.
        # 'topic', 'tip', 'note', 'caution', 'warning', 'important', 'DANGER',
        # 'sidebar',
        # 'describe',  # Just ignore this row, in is_ignored()
        # Just ignore THE row, following still counts, see is_ignored()
        # 'confval', 'program', 'option',
        'code', 'code-block', 'prompt',
        'ditaa', 'image',
        'deprecated', 'versionadded', 'versionchanged',
        'index', 'toctree',
    ]
    for role in roles:
        if line.count(f'.. {role}::') > 0:
            return True
    return False


def is_title(line):
    syms = ['=', '-', '`', '\'', '.', '~', '*', '+', '_', '^']
    for sym in syms:
        # print('is_title', RN, line, '{} vs {}'.format(line.count(sym), len(line)))  # debug
        if line.count(sym) == len(line):
            return True
    return False


def is_translated(line):
    '''
    比较规则：
    按行比较，有汉字就视作翻译了；
    以 [a-zA-Z] 打头的才计算；
    空行、[.-`*#:\] 、\s\t 打头的不算；
    '''
    cn_char = re.compile(r'[\u4e00-\u9fa5“”（）…—！《》，。：、]')  # 匹配汉字
    if cn_char.search(line):
        return True
    # do not ignore long row starts with spaces, but not command
    if len(line) < (EN_COLS / 3) and not is_title(line):
        # ignore short rows, too many symbols in them.
        # print('{:<3}:'.format(RN), line)  # debug, what translated row looks like
        return True
    if len(FILES) == 1: print('{:<3}:'.format(RN), line)  # debug, to catch exceptions of re expr
    return False


def is_ignored(line):
    '''我们只统计需要翻译的，所以以下忽略掉：

    空行，包括只含有空格的行；
    注释行；
    标题下的那行符号 [=\-~_`'\.\*\+\^]+
    命令行、终端内容（暂时未实现）；
    ditaa 图；
    '''
    # ignore links
    if line.startswith('.. _') and (line.endswith(':') or line.count(': ') == 1):
        return True
    if line.count('`') == 2 and line.endswith('`_'):  # is hyperlink, could ignore
        return True
    # ignore comment
    comment = re.compile(r'^\.\.\ [a-zA-Z]')
    if comment.match(line) and not (line.count(':: ') == 1 or line.endswith('::')):
        # print('comment debug:', get_indent(line), line)
        return True
    # ignore table
    if (line.startswith('+-') and line.endswith('-+')) or \
            (line.startswith('|') and line.endswith('|')):
        return True
    # ignore some rst roles, just this row, following still counts
    roles = [
        'confval', 'program', 'option',
        'describe',
        'highlight',
    ]
    for role in roles:
        if line.count(f'.. {role}::') > 0:
            return True
    return False


def man_ignore(line):
    if line.startswith('|'):
        return True
    if line.startswith(':command:'):
        return True
    return False


def path_to_files(paths):
    '''Check path types of all element in 'paths', grab files for directories'''
    files = []
    for p in paths:
        p = path.Path(p)
        if p.isdir():
            files += _get_file_list(p, only_rst=True)
        elif p.isfile():
            files.append(p)
        else:
            raise TypeError(f'Unknown file type: {p} type= {type(p)} cwd= {p.getcwd()}')
    return files


def to_pct(a, b):
    return round(a / b * 100, 2)


def translate_progress(files=None):
    global TP
    if files:
        count_files(files)
    else:
        print('Progress by subsys:')
        for subsys in SUBSYS:
            print('{:<20}'.format(f'    {subsys}/'), end='')
            files = _get_file_list(subsys, only_rst=True)
            count_files(files)
            subsys_prog = TP[TP.subsys == subsys]
            r = subsys_prog.agg({'translated': sum, 'total': sum})
            print('{}%'.format(to_pct(r.translated, r.total)))

    # Progress overall
    tp = TP.agg({'translated': sum, 'total': sum})
    print('Overall progress:   {}%'.format(to_pct(tp.translated, tp.total)))

    # Progress by file
    shown = 50
    print(F'Progress by file (near finished {shown} files):')
    if len(FILES) == 1:
        print(TP)
    else:
        print(TP.where(TP.pct != 100)\
            .sort_values('pct', ascending=False)\
            .dropna()\
            .head(shown))


if __name__ == "__main__":
    # Single file(s)/subsys to debug, will be ignored if it's empty
    FILES = path_to_files(sys.argv[1:]) if len(sys.argv) >= 2 else []

    if not FILES:
        print(usage)

        # Don't run this when processes specified files
        compare_file_existency()

    compare_file_length(files=FILES)

    # DataFrame 显示所有数据
    # pd.set_option('display.max_rows', 100)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', None)
    # pd.set_option('display.max_colwidth', None)
    translate_progress(files=FILES)

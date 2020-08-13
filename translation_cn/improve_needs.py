#!/usr/bin/python3

import glob
import os


doc_cn = '/git/DRUNKARD/ceph-Chinese-doc'
doc_en = '/git/ceph/doc'

LEN_DIFF_THRESHOLD = 20  # 译文和原文行数差别大于此值才显示
DIFF_ALIGN = 51     # 等号对齐列数
IGNORE_FILES = [
    # plain file
    'grep_words.sh',
    'README.md',    # empty file in ceph/doc as placeholder
    'README.rst',
    'vi_two_files.sh',

    # directory
    'translation_cn',
]


def compare_file_existency():
    cnfl, enfl = get_file_list(doc_cn), get_file_list(doc_en)
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
    print("译文和原文文件差异：")
    print('    译文版独有文件：{}\n    原文版独有文件：{}\n\n'.format(cn_uniq or '无', en_uniq or '无'))


def compare_file_length():
    cnfl, enfl = get_file_list(doc_cn), get_file_list(doc_en)
    fl = [cf for cf in cnfl
          if cf in enfl and
          (cf.endswith('.rst') or cf.endswith('.conf'))]
    print('"译文"和"原文"共有文件行数差别（行数差大于 {} 的）：'.format(LEN_DIFF_THRESHOLD))
    for f in fl:
        cn, en = file_row_counts(doc_cn, f), file_row_counts(doc_en, f)
        d = abs(cn - en)
        if d > LEN_DIFF_THRESHOLD:
            ss = '{} - {}'.format(cn, en)
            # 文件名缩进4， 行数相减右对齐，然后 = ，然后结果左对齐。
            print('    {} {:>{diff_align}} === {:}'
                  .format(f.ljust(DIFF_ALIGN), ss, d, diff_align=(DIFF_ALIGN / 3.1)))


def file_row_counts(*file_names):
    return len(open(os.path.join(*file_names)).readlines())


def get_file_list(directory):
    """
    返回一目录下的所有普通文件列表，递归，排序好。
    """
    if not os.path.isdir(directory):
        print('Not directory, please fix in code: {}'.format(directory))
        os.exit(2)
    p = str(directory) + '/**'
    fl = [os.path.relpath(f, start=directory)
         for f in glob.glob(p, recursive=True) if os.path.isfile(f)]
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


if __name__ == "__main__":
    compare_file_existency()
    compare_file_length()

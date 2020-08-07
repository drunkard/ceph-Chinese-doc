#!/usr/bin/python3

IGNORE_FILES = [
    # plain file
    'grep_words.sh',
    'README.rst',
    'vi_two_files.sh',

    # directory
    'translation_cn',
]


def compare_file_existency():
	desc = "译文和原文文件数上的差异"


def compare_file_length():
	desc = "译文和原文行数差别"


if __name__ == "__main__":
    compare_file_existency()
    compare_file_length()

#!/bin/bash

f1=${0%/*}/env.sh
f2=${0%/*}/translation_cn/env.sh
if [ -e $f1 ]; then
	. $f1
elif [ -e $f2 ]; then
	. $f2
else
	echo "找不到环境配置文件： env.sh"
	exit 1
fi

print_help() {
	echo "从中文、英文文档里过滤字符串"
	exit 0
}

if [[ $@ ]]; then
	words="$@"
else
	print_help
fi

echo "中文文档里:"
if cd $ZH_REPO; then
	grep --color=always -Ri -n "$words" *
else
	echo "未能进入文档库： $ZH_REPO"
fi

echo -e "\n英文文档里:"
if cd $EN_DOC; then
	grep --color=always -Ri -n "$words" *
	grep --color=always -Ri -n "$words" $EN_YAML
else
	echo "未能进入文档库： $ZH_REPO"
fi

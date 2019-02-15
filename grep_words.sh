#!/bin/bash

. ${0%/*}/update-env.sh

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
	grep --color=always -Ri "$words" *
else
	echo "未能进入文档库： $ZH_REPO"
fi

echo -e "\n英文文档里:"
if cd $EN_DOC; then
	grep --color=always -Ri "$words" *
else
	echo "未能进入文档库： $ZH_REPO"
fi

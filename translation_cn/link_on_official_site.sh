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

version="squid"

if [[ $@ ]]; then
	for file in $@; do
		# only accept rst file
		grep -q .rst$ <<< "$file" || {
			echo "不是 rst 文本文件，跳过: $file"
			continue
		}

		file=`remove_prefix_path "$file"`
		f="${file%.rst}"
		echo -e "本地英文: http://localhost:8080/$f/"
		echo -e "本地中文: http://localhost:9080/$f/"
		echo
		echo -e "官网:\t https://docs.ceph.com/en/$version/$f/"
	done
else
	cat <<-EOF
	打印出本地文档在官方网站的对应地址。

	用法: $0 <doc file>
	EOF
fi

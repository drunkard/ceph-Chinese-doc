#!/bin/bash

CN_PATH=$(dirname `realpath $0`)
EN_PATH="/git/ceph/doc-en"

open_files() {
	cn_doc="$CN_PATH/$1"
	en_doc="$EN_PATH/$1"

	[ -e $cn_doc ] || {
		echo "中文版文档不存在: $1"
		return 1
	}
	[ -e $en_doc ] || {
		echo "英文版文档不存在: $1"
		return 1
	}

	echo 'vim +"set colorcolumn=64" -O' $cn_doc $en_doc
	vim +"set colorcolumn=64" -O $cn_doc $en_doc
}

if [ $# -ge 1 ]; then
	for f in $@; do
		open_files "$f"
	done
else
	cat <<-EOF
	指定一个文件名即可同时打开文档的中文版和英文，指定多个文件则依次打开
	EOF
fi

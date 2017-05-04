#!/bin/bash

CEPH_GIT="/git/ceph"
CN_PATH=$(dirname `realpath $0`)
if [ -L $CEPH_GIT/doc ]; then
	EN_PATH="$CEPH_GIT/doc-en"
elif [ ! -L $CEPH_GIT/doc -a -d $CEPH_GIT/doc ]; then
	EN_PATH="$CEPH_GIT/doc"
else
	echo "Unknown ceph/doc directory type, please check by hand"
	exit 2
fi

open_files() {
	cn_doc="$CN_PATH/$1"
	en_doc="$EN_PATH/$1"

	if [ ! -e $cn_doc ]; then
		if [ -e $en_doc ]; then
			echo "中文版不存在，复制一个过来 ..."
			mkdir -p `dirname $cn_doc`
			cp -v $en_doc $cn_doc
		else
			echo "中文版、英文版文档都不存在: $1"
			return 1
		fi
	fi
	[ -e $en_doc ] || {
		echo "英文版文档不存在: $1"
		return 1
	}

	# Convert to relative path
	cn_doc=`realpath --relative-to=$CN_PATH $cn_doc`
	en_doc=`realpath --relative-to=$CN_PATH $en_doc`

	cat <<-EOF
	vim -O +"set colorcolumn=64" $cn_doc $en_doc	# 垂直分割
	vim -o +"set colorcolumn=64" $cn_doc $en_doc	# 水平分割
	EOF
	vim -O +"set colorcolumn=64" $cn_doc $en_doc
}

remove_prefix() {
	local str="$@"
	# $str could be:
	#	a/doc/dev/osd_internals/log_based_pg.rst
	#	b/radosgw/swift/auth.rst
	grep -qe ^[ab]/ <<< "$str" && \
		str=`sed -e 's:^[ab]/::' <<< "$str"`

	grep -qe ^doc/ <<< "$str" && \
		str=`sed -e 's:^doc/::' <<< "$str"`
	echo -n "$str"
}

if [ $# -ge 1 ]; then
	for f in $@; do
		f=`remove_prefix "$f"`
		open_files "$f"
	done
else
	cat <<-EOF
	指定一个文件名即可同时打开文档的中文版和英文，指定多个文件则依次打开
	EOF
fi

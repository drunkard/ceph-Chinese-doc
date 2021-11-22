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

open_files() {
	cd $ZH_DOC

	case $1 in
		*.yaml.in)
			# *.yaml.in files
			f=${1##*/}
			cn_doc="$ZH_YAML/$f"
			en_doc="$EN_YAML/$f"
			;;
		*)
			cn_doc="$ZH_DOC/$1"
			en_doc="$EN_DOC/$1"
	esac

	# When build doc/, hints has no suffix .rst, so add them automatically
	if [ ! -e $cn_doc -a -f $cn_doc.rst ] && [ ! -e $en_doc -a -f $en_doc.rst ]; then
		cn_doc=$cn_doc.rst
		en_doc=$en_doc.rst
	fi

	if [ ! -f $cn_doc ]; then
		# Check if they are exist
		if [ -f $en_doc ]; then
			echo "中文版不存在，复制一个过来 ..."
			mkdir -p `dirname $cn_doc`
			cp -v $en_doc $cn_doc
			sleep 1s;	# 让译者看一眼
		else
			echo "中文版、英文版文档都不存在: $1"
			return 1
		fi
	fi
	[ -f $en_doc ] || {
		echo "英文版文档不存在: $1"
		return 1
	}

	# compare them, hint if they are the same
	if [ `diff -u $cn_doc $en_doc | wc -l` -eq 0 ]; then
		echo -e "二者完全相同: $cn_doc == $en_doc\n"
	fi

	# Convert to relative path
	cn_doc=`realpath --relative-to=$ZH_DOC $cn_doc`
	# en_doc=`realpath --relative-to=$ZH_DOC $en_doc`

	cat <<-EOF
	vim -O +"set colorcolumn=64" $cn_doc $en_doc	# 垂直分割（默认）
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
	grep -qe ^doc-en/ <<< "$str" && \
		str=`sed -e 's:^doc-en/::' <<< "$str"`
	grep -qe ^/git/ceph/doc-zh/ <<< "$str" && \
		str=`sed -e 's:^/git/ceph/doc-zh/::' <<< "$str"`
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

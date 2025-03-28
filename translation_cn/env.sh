# 定义更新此文档的配置环境，以及更新进度

# 此文件用法：
# . ${0%/*}/env.sh

# 更稳妥的用法：
# f1=${0%/*}/env.sh
# f2=${0%/*}/translation_cn/env.sh
# if [ -e $f1 ]; then
# 	. $f1
# elif [ -e $f2 ]; then
# 	. $f2
# else
# 	echo "找不到环境配置文件： env.sh"
# 	exit 1
# fi


CEPH_REPO="/git/ceph"
CEPH_REPO_OUTDATE_DAYS=2	# 超过此天数没有更新时，可能被强制更新
ZH_REPO="/git/ceph-Chinese-doc"
ZH_READABLE_REPO="/git/ceph-readable-doc"

BUILT_OUTPUT="$CEPH_REPO/build-doc/output-zh/"

# directory or symlinks in $CEPH_REPO
EN="doc-en"
ZH="doc-zh"

EN_DOC="$CEPH_REPO/$EN"
ZH_DOC="$ZH_REPO"
if [ -L $CEPH_REPO/doc ]; then
	EN_DOC="$CEPH_REPO/$EN"
elif [ ! -L $CEPH_REPO/doc -a -d $CEPH_REPO/doc ]; then
	EN_DOC="$CEPH_REPO/doc"
else
	echo "Unknown ceph/doc directory type, please check by hand"
	exit 2
fi

EN_YAML="$CEPH_REPO/src/common/options"
ZH_YAML="$ZH_REPO/zh_options"

# 当前的库同步到了哪里
# Where we synced with ceph mainline. Note by date is more reliable than
# commit ID, because there's too many criss-cross branches which is hard
# for us to sync by branch/commit ID.
# sync by $STEP days once, 0 to disable
SYNC_TO="2023-02-22"

# 一次更新多少天的
STEP=10
SYNC_UNTIL=`date -d "$SYNC_TO +$STEP days" +%Y-%m-%d`

PROGRESS_FILE="translation_cn/env.sh"

# vim options
# 64 if align chars strictly; 80 for split by sentence;
VI_COLUMN=64,80


# 删除文件的前缀路径，便于后续操作
remove_prefix_path() {
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
	grep -qe ^/data/git/ceph/doc/ <<< "$str" && \
		str=`sed -e 's:^/data/git/ceph/doc/::' <<< "$str"`
	echo -n "$str"
}

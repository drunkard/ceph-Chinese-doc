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
ZH_REPO="/git/DRUNKARD/ceph-Chinese-doc"
ZH_READABLE_REPO="/git/DRUNKARD/ceph-readable-doc"

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

# 当前的库同步到了哪里
# Where we synced with ceph mainline. Note by date is more reliable than
# commit ID, because there's too many criss-cross branches which is hard
# for us to sync by branch/commit ID.
SYNC_TO="2020-02-11"
PROGRESS_FILE="translation_cn/env.sh"

# sync by STEP days once, 0 to disable
STEP=5
SYNC_UNTIL=`date -d "$SYNC_TO +$STEP days" +%Y-%m-%d`

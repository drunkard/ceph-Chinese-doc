# 定义更新此文档的配置环境，以及更新进度

# 此文件用法：
# . ${0%/*}/update-env.sh

CEPH_GIT="/git/ceph"

EN="doc-en"
EN_DOC="$CEPH_GIT/$EN"

ZH_REPO="/git/DRUNKARD/ceph-Chinese-doc"
ZH="doc-zh"
ZH_DOC="$ZH_REPO"
ZH_realpath=`realpath $ZH_DOC`

OUR_TOP_DIR=`realpath ${0%/*}`

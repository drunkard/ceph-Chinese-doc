# 定义更新此文档的配置环境，以及更新进度

CEPH_GIT="/git/ceph"

EN="doc-en"
EN_DOC="$CEPH_GIT/$EN"

ZH="doc-zh"
ZH_DOC="$CEPH_GIT/$ZH"
ZH_realpath=`realpath $ZH_DOC`

OUR_TOP_DIR=`realpath ${0%/*}`
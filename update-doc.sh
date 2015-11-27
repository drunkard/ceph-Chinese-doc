#!/bin/bash
# Where we synced with ceph mainline:
CUR=d8a728ec1507eabaa2ce6071574a5f4d9f5091cb

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

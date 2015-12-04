#!/bin/bash
# Where we synced with ceph mainline:
CUR=387d7800359154950431d0984c756f43f21dd9b4

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

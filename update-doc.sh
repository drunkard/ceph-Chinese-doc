#!/bin/bash
# Where we synced with ceph mainline:
CUR=504a48a3d39a68c1ceac10128c047436d0f6e03b

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

#!/bin/bash
# Where we synced with ceph mainline:
CUR=74180ad8b3461cb7091044f82adf5aab94a1573b

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview --reverse --date-order ${CUR}.. -- doc/ &
fi

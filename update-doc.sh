#!/bin/bash
# Where we synced with ceph mainline. Note by date is more reliable than
# commit ID, because there's too many criss-cross branches which is hard
# for us to sync by branch/commit ID.
SYNC_START=2015-12-23

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline --since=${SYNC_START} doc/ | wc -l` commits to sync"
	gitview --reverse --date-order --since=${SYNC_START} -- doc/ &
fi

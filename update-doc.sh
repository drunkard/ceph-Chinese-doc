#!/bin/bash
# Where we synced with ceph mainline. Note by date is more reliable than
# commit ID, because there's too many criss-cross branches which is hard
# for us to sync by branch/commit ID.
SYNC_START="2016-06-19"

if ! /usr/bin/which tig &>/dev/null; then
	echo "Need command line tool: tig"
	exit 127
fi

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline --since=${SYNC_START} doc/ | wc -l` commits to sync"
	tig --date-order --reverse --since=${SYNC_START} -- doc/
fi

#!/bin/bash
# Where we synced with ceph mainline:
CUR=d5cee59b024f9acc594d727c1a776efc051f3f09

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview --reverse --date-order ${CUR}.. -- doc/ &
fi

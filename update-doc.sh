#!/bin/bash
# Where we synced with ceph mainline:
CUR=07c334a2ca5ac7da7d7797888d045a35ee0cabf7

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview --reverse --date-order ${CUR}.. -- doc/ &
fi

#!/bin/bash
# Where we synced with ceph mainline:
CUR=12efe7f2c9744c0a2bc22b6d844f10d913d7e2c9

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

#!/bin/bash
# Where we synced with ceph mainline:
CUR=738d64c7e4023e7bb73f3630cea776abf87e5caa

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

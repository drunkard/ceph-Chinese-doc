#!/bin/bash
# Where we synced with ceph mainline:
CUR=8eaa2f263d1055a6e482b33c6d4f48b97d7169a3

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

#!/bin/bash
# Where we synced with ceph mainline:
CUR=406b1d0347dcc27f698c7ec361a1e5d6a66277e8

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

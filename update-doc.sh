#!/bin/bash
# Where we synced with ceph mainline:
CUR=c1b28591a2ba55abd644186938d440fc90743f15

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

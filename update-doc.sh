#!/bin/bash
# Where we synced with ceph mainline:
CUR=1baeb1c743046cc654e21f13915499436ae163cb

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

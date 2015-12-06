#!/bin/bash
# Where we synced with ceph mainline:
CUR=0507cff4eb89ffad950129ea89da027ffb46e066

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

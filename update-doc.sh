#!/bin/bash
# Where we synced with ceph mainline:
CUR=8178e7e0065da00c7d8065a77e13330057a369a5

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

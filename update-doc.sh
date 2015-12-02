#!/bin/bash
# Where we synced with ceph mainline:
CUR=77cdb500af97e0ee75b79faef844f5eaae8733fd

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

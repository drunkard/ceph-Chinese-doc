#!/bin/bash
# Where we synced with ceph mainline:
CUR=792e24bd3085413b675355d1f102d0a98188bd4d

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

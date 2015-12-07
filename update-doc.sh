#!/bin/bash
# Where we synced with ceph mainline:
CUR=1786fa8aa937d167d903a766af88655850940569

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

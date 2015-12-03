#!/bin/bash
# Where we synced with ceph mainline:
CUR=de00f6d0df159d51bd9dcec6a111e47b04a97c96

MYPATH="${0%/*}"
CEPH_REPO=/git/ceph
if cd $CEPH_REPO; then
	echo "There's `git log --oneline ${CUR}.. doc/ | wc -l` commits to sync"
	gitview ${CUR}.. -- doc/ &
fi

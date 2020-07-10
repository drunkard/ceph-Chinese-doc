#!/bin/bash

. ${0%/*}/env.sh

if ! /usr/bin/which tig &>/dev/null; then
	echo "Need command line tool: tig"
	exit 127
fi

if [[ $STEP ]] && [ x$STEP == x0 ]; then
	tig_opts=""
else
	tig_opts="--until=${SYNC_UNTIL}"
fi

update_ceph_repo() {
	# If ceph repo has outdated more than $CEPH_REPO_OUTDATE_DAYS, do 'git pull' first.
	differ=$(( `date -d 'now' +%s` - `git -C $CEPH_REPO log -1 --date=short --format=%at` ))
	if [ $differ -ge $(( 86400 * $CEPH_REPO_OUTDATE_DAYS )) ]; then
		echo "Ceph git repo outdated more than $CEPH_REPO_OUTDATE_DAYS days, updating ..."
		git -C $CEPH_REPO pull
		git -C $CEPH_REPO submodule update
		git -C $CEPH_REPO gc --quiet
		echo	# new line for following command tig
	fi
}

if cd $CEPH_REPO; then
	update_ceph_repo

	# view "git log" using "tig"
	# echo "There's `git log --oneline --since=${SYNC_TO} doc/ | wc -l` commits to sync"
	echo "command: tig --date-order --reverse --since=${SYNC_TO} $tig_opts -- doc/"
	tig --date-order --reverse --since=${SYNC_TO} $tig_opts -- doc/
else
	echo "Failed to enter git repo for ceph: $CEPH_REPO"
fi
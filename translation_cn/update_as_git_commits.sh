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

auto_sync() {
	# exec translation_cn/auto_sync.sh
	local s="translation_cn/auto_sync.sh"
	if cd $ZH_REPO; then
		echo -e "\nRunning $s ..."
		sh $s
		echo
	else
		echo "$FUNCNAME: failed to exec $s"
		exit 1
	fi
}

ceph_pull_rebase() {
	run_cmd git -C $CEPH_REPO pull --rebase
	run_cmd git -C $CEPH_REPO submodule update
	run_cmd git -C $CEPH_REPO gc --quiet
}

run_cmd() {
	cmd="$@"
	echo -e "\nRunning command: $cmd"
	$cmd
}

update_ceph_repo() {
	# If ceph repo has outdated more than $CEPH_REPO_OUTDATE_DAYS, do 'git pull' first.
	differ=$(( `date -d 'now' +%s` - `git -C $CEPH_REPO log -20 --date=short --format=%at | sort -nr | head -1` ))
	if [ $differ -ge $(( 86400 * $CEPH_REPO_OUTDATE_DAYS )) ]; then
		echo "Ceph git repo outdated more than $CEPH_REPO_OUTDATE_DAYS days, updating ..."
		if [[ `git -C $CEPH_REPO status -s` ]]; then
			run_cmd git -C $CEPH_REPO stash push -- doc/ src/common/options/
			ceph_pull_rebase
			run_cmd git -C $CEPH_REPO stash pop --quiet
		else
			ceph_pull_rebase
		fi
		echo	# new line for following command tig
	fi
}

if cd $CEPH_REPO; then
	update_ceph_repo
	auto_sync

	# view "git log" using "tig"
	# echo "There's `git log --oneline --since=${SYNC_TO} doc/ | wc -l` commits to sync"
	cd $CEPH_REPO || exit 1
	run_cmd tig --date-order --reverse --since=${SYNC_TO} $tig_opts -- doc/ src/common/options/
else
	echo "Failed to enter git repo for ceph: $CEPH_REPO"
fi

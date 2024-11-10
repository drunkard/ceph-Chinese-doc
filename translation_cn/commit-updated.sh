#!/bin/bash
# 用于自动提交已完成的翻译

. ${0%/*}/env.sh

readable_commit_title="ceph doc: updated to $SYNC_TO"


commit_file() {
	echo -e "$FUNCNAME: commit started with $1"
	msg="finished $1"
	GIT="git -C $ZH_REPO"
	cd $ZH_REPO || {
		echo "$FUNCNAME: cd $ZH_REPO failed"
		return 1
	}
	$GIT add $1
	$GIT commit --signoff -m "$msg" $1
	if [ $? -eq 0 ]; then
		echo -e "$FUNCNAME: commit ok in git repo: $ZH_REPO\n"
	else
		echo -e "$FUNCNAME: commit failed in git repo: $ZH_REPO\n"
		return 1
	fi
	$GIT gc --quiet
}

commit_zh_code() {
	echo -e "$FUNCNAME: commit started"
	cd $ZH_REPO || {
		echo "$FUNCNAME: cd $ZH_REPO failed"
		return 1
	}
	synced_with_upstream || return 2

	git -C $ZH_REPO add .
	git -C $ZH_REPO commit -a --signoff -m "doc: sync with mainline, updated to: $SYNC_TO"
	if [ $? -eq 0 ]; then
		echo -e "$FUNCNAME: commit ok in git repo: $ZH_REPO\n"
	else
		echo -e "$FUNCNAME: commit failed in git repo: $ZH_REPO\n"
		return 1
	fi
	git -C $ZH_REPO gc --quiet
}

commit_zh_readable() {
	echo -e "$FUNCNAME: commit started"
	# start commit
	GIT="git -C $ZH_READABLE_REPO"
	cd $ZH_REPO || {
		echo "$FUNCNAME: cd $ZH_REPO failed"
		return 1
	}
	if [ $# -eq 1 ] && [ -f $1 ]; then
		msg="finished $1"
	else
		synced_with_upstream || return 2
		msg="ceph doc: updated to $SYNC_TO"
	fi

	sync_zh_readable || return 2
	$GIT add html/ man/ && \
	$GIT commit --signoff -m "$msg" html/ man/
	if [ $? -eq 0 ]; then
		echo -e "$FUNCNAME: commit ok in repo: $ZH_READABLE_REPO\n"
	else
		echo -e "$FUNCNAME: commit failed in repo: $ZH_READABLE_REPO\n"
		return 1
	fi
	$GIT gc --quiet
}

# TODO
# commit_zh_github_io() {
# drunkard.github.io
# 22:43:05 /git/DRUNKARD/ceph-readable-doc/html $ rsync -avrR --exclude=.git --exclude=_config.yml --del . /git/DRUNKARD/drunkard.github.io/ 

push_remotes() {
	local repos repo
	local remotes remote
	if [ $# -ge 1 ]; then
		repos=$@
	else
		echo "$FUNCNAME: wrong argument, need at least one git repo"
		return 127
	fi
	for repo in $repos; do
		remotes=`git -C $repo remote`
		for remote in $remotes; do
			echo -e "\nPushing $repo to remote: $remote ..."
			git -C $repo push $remote
		done
	done
}

sync_zh_readable() {
	# sync newly built html/man
	if [ -d $BUILT_OUTPUT ] && cd $BUILT_OUTPUT; then
		local cmd="rsync -arR --del html/ man/ $ZH_READABLE_REPO/"
		echo -n "$FUNCNAME running sync command: $cmd ... "
		$cmd
		if [ $? -eq 0 ]; then
			echo -e "done\n"
		else
			echo -e "failed"
			return 2
		fi
	else
		echo "$FUNCNAME: failed to enter built doc directory: $BUILT_OUTPUT"
		return 2
	fi
}

synced_with_upstream() {
	# check if updated cursor
	if [ `git -C $ZH_REPO diff $PROGRESS_FILE |grep -c SYNC_TO=` -ne 2 -a \
		`git -C $ZH_REPO diff --cached $PROGRESS_FILE |grep -c SYNC_TO=` -ne 2 ]; then
		echo "$FUNCNAME: $PROGRESS_FILE not changed, please update SYNC_TO="
		return 2
	fi
}

cat <<-EOF
Commit changed translation automatically, commit by date, or commit only ONE file.

Commit by "commit date" in ceph git repo:
    $0

Commit only one file (translated doc):
    $0 <changed file name to commit>

EOF

err=0
if [ $# -eq 1 -a -f $1 ]; then
	commit_file $1 || let err++
	commit_zh_readable $1 || let err++
else
	commit_zh_code || let err++
	commit_zh_readable || let err++
fi
if [ $err -eq 0 ]; then
	push_remotes $ZH_REPO $ZH_READABLE_REPO
else
	echo -e "Previous steps got errors, won't push"
fi

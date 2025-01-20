#!/bin/bash
# 用于自动提交已完成的翻译

. ${0%/*}/env.sh

readable_commit_title="ceph doc: updated to $SYNC_TO"


commit_file() {
	echo -e "$FUNCNAME: commit started with file $1"
	msg="finished $1"
	GIT="git -C $ZH_REPO"
	cd $ZH_REPO || {
		echo "$FUNCNAME: cd $ZH_REPO failed"
		return 1
	}

	# check if this file modified
	[[ `$GIT status -s "$1"` ]] || {
		echo "$FUNCNAME: the file not modified, exit now"
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

	# exclude tools change under translation_cn/
	trans_tools_dir="translation_cn"
	[[ `git status -s $trans_tools_dir/ | grep -v -e $trans_tools_dir/env.sh -e $trans_tools_dir/translation-convention.rst` ]] && {
		echo "$FUNCNAME: There is other changes under $trans_tools_dir/ , please commit them manually first !"
		return 2
	}

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
	echo -e "$FUNCNAME: commit started at $ZH_READABLE_REPO"
	# start commit
	GIT="git -C $ZH_READABLE_REPO"
	cd $ZH_READABLE_REPO || {
		echo "$FUNCNAME: cd $ZH_REPO failed"
		return 1
	}

	if [ $# -eq 1 ] && [ -f $1 ]; then
		msg="finished $1"
	else
		msg="ceph doc: updated to $SYNC_TO"
	fi

	sync_zh_readable || return 2

	# check if this repo modified, must after sync
	[[ `$GIT status -s` ]] || {
		echo "$FUNCNAME: repo not modified, exit now"
		return 1
	}

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
# 22:43:05 /git/ceph-readable-doc/html $ rsync -avrR --exclude=.git --exclude=_config.yml --del . /git/drunkard.github.io/

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

# help info, show every runs
cat <<-EOF
Commit changed translation automatically:
  commit by date of ceph git repo, eg: $0
  or commit only ONE file (translated doc), eg: $0 <changed file path to commit>

EOF

# If doc is building, exit, or we could sync a incomplete ZH_READABLE_REPO
if [[ `pgrep -f sphinx-build` ]]; then
	echo "building of doc is running, wait for completion, exit now."
	exit 2
fi

err=0
if [ $# -eq 1 -a -f $1 ]; then
	( commit_file $1 && commit_zh_readable $1 ) || let err++
else
	( commit_zh_code && commit_zh_readable ) || let err++
fi
if [ $err -eq 0 ]; then
	push_remotes $ZH_REPO $ZH_READABLE_REPO
else
	echo -e "Previous steps got errors, won't push"
fi

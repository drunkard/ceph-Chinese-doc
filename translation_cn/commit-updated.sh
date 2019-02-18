#!/bin/bash
# 用于自动提交已完成的翻译

. ${0%/*}/env.sh

readable_commit_title="ceph doc: updated to $SYNC_TO"


commit_zh_code() {
	cd $ZH_REPO || {
		echo "$FUNCNAME: cd $ZH_REPO failed"
		return 1
	}
	# check if updated cursor
	if [ `git -C $ZH_REPO diff $PROGRESS_FILE |grep -c SYNC_TO=` -ne 2 ]; then
		echo "$FUNCNAME: $PROGRESS_FILE not changed, please update SYNC_TO="
		return 2
	fi

	git commit -a --signoff -m "doc: sync with mainline, updated to: $SYNC_TO"
	if [ $? -eq 0 ]; then
		echo -e "$FUNCNAME: commit ok in git repo: $ZH_REPO\n"
	else
		echo -e "$FUNCNAME: commit failed in git repo: $ZH_REPO\n"
		return 1
	fi
	git -C $ZH_REPO gc --quiet
}

commit_zh_readable() {
	if [ -d $BUILT_OUTPUT ] && cd $BUILT_OUTPUT; then
		# ./ includes current sub-directories: html/ man/
		if rsync -avrR --del ./ $ZH_READABLE_REPO/; then
			echo -e "synced with most recent build\n"
		else
			echo -e "$FUNCNAME: sync failed"
			return 2
		fi
	else
		echo "$FUNCNAME: failed to enter built doc directory: $BUILT_OUTPUT"
		return 2
	fi

	git -C $ZH_READABLE_REPO add html/ man/ && \
	git -C $ZH_READABLE_REPO commit --signoff -m "ceph doc: updated to $SYNC_TO" html/ man/
	if [ $? -eq 0 ]; then
		echo -e "$FUNCNAME: commit ok in repo: $ZH_READABLE_REPO\n"
	else
		echo -e "$FUNCNAME: commit failed in repo: $ZH_READABLE_REPO\n"
		return 1
	fi
	git -C $ZH_READABLE_REPO gc --quiet
}

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

if commit_zh_code && commit_zh_readable; then
	push_remotes $ZH_REPO $ZH_READABLE_REPO
fi

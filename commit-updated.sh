#!/bin/bash
BASE_DIR="/git"
MAINLINE=${BASE_DIR}/ceph
ZH_CODE=${BASE_DIR}/DRUNKARD/ceph-Chinese-doc
ZH_READABLE=${BASE_DIR}/DRUNKARD/ceph-readable-doc

MAINLINE_HEAD_ID=`awk -F'"' '{if($1=="SYNC_START=") print $2}' $ZH_CODE/update-doc.sh`
ZH_CODE_HEAD_ID=`git -C $ZH_CODE log -1 --pretty=%H`

CODE_MSG="doc: sync with mainline, updated to: $MAINLINE_HEAD_ID"

READABLE_MSG="ceph doc: updates

sync with $ZH_CODE_HEAD_ID in github.com/drunkard/ceph-Chinese-doc or
$MAINLINE_HEAD_ID in official ceph.git"


commit_zh_code() {
	cd $ZH_CODE || {
		echo "$FUNCNAME: cd $ZH_CODE failed"
		return 1
	}
	# check if updated cursor
	if [ `git -C $ZH_CODE diff update-doc.sh |grep -c SYNC_START=` -ne 2 ]; then
		echo "$FUNCNAME: update-doc.sh not changed, please update SYNC_START="
		return 2
	fi
	git commit -a --signoff -m "$CODE_MSG"
	if [ $? -eq 0 ]; then
		echo -e "$FUNCNAME: commit ok in git repo: $ZH_CODE\n"
	else
		echo -e "$FUNCNAME: commit failed in git repo: $ZH_CODE\n"
		return 1
	fi
}

commit_zh_readable() {
	if [ -d $MAINLINE/build-doc/output ] && cd $MAINLINE/build-doc/output; then
		# ./ includes current sub-directories: html/ man/
		if rsync -avrR ./ $ZH_READABLE/; then
			echo -e "synced with most recent build\n"
		else
			echo -e "$FUNCNAME: sync failed"
			return 2
		fi
	fi
	git -C $ZH_READABLE add html/ man/ && \
	git -C $ZH_READABLE commit --signoff -m "$READABLE_MSG" html/ man/
	if [ $? -eq 0 ]; then
		echo -e "$FUNCNAME: commit ok in repo: $ZH_READABLE\n"
	else
		echo -e "$FUNCNAME: commit failed in repo: $ZH_READABLE\n"
		return 1
	fi
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
	push_remotes $ZH_CODE $ZH_READABLE
fi

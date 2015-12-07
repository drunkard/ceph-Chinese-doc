#!/bin/bash
MAINLINE=/git/ceph
ZH_CODE=/repo/ceph-Chinese-doc
ZH_READABLE=/repo/ceph-readable-doc

MAINLINE_HEAD_ID=`awk -F'=' '{if($1=="CUR") print $2}' $ZH_CODE/update-doc.sh`
ZH_CODE_HEAD_ID=`git -C $ZH_CODE log -1 --pretty=%H`

CODE_MSG="doc: sync with mainline
                       
Updated to: $MAINLINE_HEAD_ID"

READABLE_MSG="ceph doc: updates

sync with $ZH_CODE_HEAD_ID in github.com/drunkard/ceph-Chinese-doc or
$MAINLINE_HEAD_ID in official ceph.git"


commit_zh_code() {
	cd $ZH_CODE || {
		echo "$FUNCNAME: cd $ZH_CODE failed"
		return 1
	}
	git commit -a --signoff -m "$CODE_MSG"
	if [ $? -ne 0 ]; then
		echo "$FUNCNAME: commit failed"
		return 1
	fi
}

commit_zh_readable() {
	if [ -d $MAINLINE/build-doc ] && cd $MAINLINE/build-doc; then
		if rsync -avrR output/ $ZH_READABLE/; then
			echo -e "synced with most recent build\n"
		else
			echo -e "$FUNCNAME: sync failed"
			return 2
		fi
	fi
	git -C $ZH_READABLE add output/ && \
	git -C $ZH_READABLE commit --signoff -m "$READABLE_MSG" output/
	if [ $? -ne 0 ]; then
		echo "$FUNCNAME: commit failed"
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

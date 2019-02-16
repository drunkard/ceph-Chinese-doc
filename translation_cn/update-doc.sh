#!/bin/bash

. ${0%/*}/env.sh

if ! /usr/bin/which tig &>/dev/null; then
	echo "Need command line tool: tig"
	exit 127
fi

if cd $CEPH_REPO; then
	# echo "There's `git log --oneline --since=${SYNC_TO} doc/ | wc -l` commits to sync"
	tig --date-order --reverse --since=${SYNC_TO} -- doc/
fi

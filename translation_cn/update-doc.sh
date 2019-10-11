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
if cd $CEPH_REPO; then
	# echo "There's `git log --oneline --since=${SYNC_TO} doc/ | wc -l` commits to sync"
	echo "command: tig --date-order --reverse --since=${SYNC_TO} $tig_opts -- doc/"
	tig --date-order --reverse --since=${SYNC_TO} $tig_opts -- doc/
fi

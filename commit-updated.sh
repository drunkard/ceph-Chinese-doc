#!/bin/bash
work_dir=`dirname $0`
msg="doc: sync with mainline
                       
Updated to: `cat UPDATETO`"

cd $work_dir && \
	git commit -a --signoff -m "$msg"

[ $? -eq 0 ] || {
	echo "commit failed"
}

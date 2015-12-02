#!/bin/bash
work_dir=`dirname $0`
origin_id=`awk -F'=' '{if($1=="CUR") print $2}' $work_dir/update-doc.sh`
msg="doc: sync with mainline
                       
Updated to: $origin_id"

cd $work_dir && \
	git commit -a --signoff -m "$msg"

[ $? -eq 0 ] || {
	echo "commit failed"
}

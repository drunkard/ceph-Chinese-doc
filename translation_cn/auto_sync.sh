#!/bin/bash

. ${0%/*}/env.sh

updates="
CMakeLists.txt
conf.py
favicon.ico
logo.png
man/CMakeLists.txt
man/8/CMakeLists.txt

changelog/
images/
scripts/
_ext/
_static/
_templates/
_themes/
"

# 自动同步 changelog
if cd $EN_DOC/; then
	rsync -avrR --del --exclude=__pycache__ $updates $ZH_REPO/
	retv=$?
	if [ $retv -ne 0 ]; then
		echo "$0: sync failed with error code: $retv"
	fi
else
	echo "$0: failed to enter directory $EN_DOC, sync failed"
fi


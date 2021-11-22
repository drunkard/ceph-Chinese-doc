#!/bin/bash

. ${0%/*}/env.sh

updates="
favicon.ico
logo.png

cephfs/cephfs-architecture.svg
cephfs/cephfs-top.png
cephfs/mds-state-diagram.dot
cephfs/subtree-partitioning.svg

dev/cephadm/design/mockups/OSD_Creation_device_mode.svg
dev/cephadm/design/mockups/OSD_Creation_host_mode.svg
dev/osd_internals/osdmap_versions.txt
dev/osd_internals/osd_throttles.txt
dev/peering_graph.generated.dot
dev/PlanningImplementation.txt

jaegertracing/osd_jaeger.png
jaegertracing/rgw_jaeger.png

rados/command/list-inconsistent-obj.json
rados/command/list-inconsistent-snap.json
rados/configuration/demo-ceph.conf
rados/configuration/pool-pg.conf

releases/argonaut.rst
releases/bobtail.rst
releases/cuttlefish.rst
releases/dumpling.rst
releases/emperor.rst
releases/firefly.rst
releases/giant.rst
releases/hammer.rst
releases/infernalis.rst
releases/jewel.rst
releases/kraken.rst
releases/luminous.rst
releases/mimic.rst
releases/nautilus.rst
releases/octopus.rst
releases/pacific.rst

releases/releases.yml

CMakeLists.txt
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

# compares if conf.py from upstream changed, hint if changed.
compare_conf_py() {
	should_be=`diff -u $EN_DOC/conf.py $ZH_DOC/conf.py | grep ^[+-] | wc -l`
	if [ $should_be -ne 4 ]; then
		echo -e "\n上游配置文件变了，请更新 conf.py"
		diff -u $EN_DOC/conf.py $ZH_DOC/conf.py
	fi
}

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

compare_conf_py

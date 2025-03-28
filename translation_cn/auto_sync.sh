#!/bin/bash

. ${0%/*}/env.sh

updates="
favicon.ico
logo.png

cephfs/cephfs-architecture.svg
cephfs/cephfs-top.png
cephfs/mds-state-diagram.dot
cephfs/quiesce-set-states.svg
cephfs/subtree-partitioning.svg

dev/cephadm/design/mockups/OSD_Creation_device_mode.svg
dev/cephadm/design/mockups/OSD_Creation_host_mode.svg
dev/crimson/*.png
dev/osd_internals/osdmap_versions.txt
dev/peering_graph.generated.dot
dev/peering_graph.generated.svg
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
releases/quincy.rst
releases/reef.rst
releases/squid.rst

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

yaml_updates="
CMakeLists.txt
"

# compares if conf.py from upstream changed, hint if changed.
compare_conf_py() {
	should_be=`diff -u $EN_DOC/conf.py $ZH_DOC/conf.py | grep ^[+-] | wc -l`
	if [ $should_be -ne 4 ]; then
		echo -e "\n上游配置文件变了，请更新 conf.py"
		diff --color=auto -u $EN_DOC/conf.py $ZH_DOC/conf.py
	fi
}

sync_doc_files() {
	echo "$FUNCNAME: syncing docs ..."
	cd $EN_DOC && \
	rsync -avrR --del --exclude=__pycache__ $updates $ZH_REPO/
	retv=$?
	if [ $retv -ne 0 ]; then
		echo "$0: sync failed with error code: $retv"
	fi
}


sync_yaml_files() {
	echo -e "\n$FUNCNAME: syncing yaml files ($EN_YAML -> $ZH_YAML) ..."
	cd $EN_YAML && \
	rsync -avrR --del --exclude=__pycache__ *.py $yaml_updates $ZH_YAML/
	retv=$?
	if [ $retv -ne 0 ]; then
		echo "$0: sync failed with error code: $retv"
	fi
}

if [ -d $EN_DOC ]; then
	sync_doc_files
	sync_yaml_files

	compare_conf_py
else
	echo "$0: failed to enter directory $EN_DOC, sync failed"
fi

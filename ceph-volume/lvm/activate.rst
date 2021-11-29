.. _ceph-volume-lvm-activate:

``activate``
============

Once :ref:`ceph-volume-lvm-prepare` is completed, and all the various steps
that entails are done, the volume is ready to get "activated".

This activation process enables a systemd unit that persists the OSD ID and its
UUID (also called ``fsid`` in Ceph CLI tools), so that at boot time it can
understand what OSD is enabled and needs to be mounted.

.. note:: The execution of this call is fully idempotent, and there is no
          side-effects when running multiple times

For OSDs deployed by cephadm, please refer to :ref:cephadm-osd-activate: 
instead.

新 OSD
------
.. New OSDs

To activate newly prepared OSDs both the :term:`OSD id` and :term:`OSD uuid`
need to be supplied. For example::

    ceph-volume lvm activate --bluestore 0 0263644D-0BF1-4D6D-BC34-28BD98AE3BC8

.. note:: 这个 UUID 存储于 OSD 路径下的 ``fsid`` 文件内，它\
   是在调用 :ref:`ceph-volume-lvm-prepare` 时生成的。

激活所有 OSD
------------
.. Activating all OSDs

.. note:: For OSDs deployed by cephadm, please refer to :ref:cephadm-osd-activate: 
          instead.

It is possible to activate all existing OSDs at once by using the ``--all``
flag. For example::

    ceph-volume lvm activate --all

This call will inspect all the OSDs created by ceph-volume that are inactive
and will activate them one by one. If any of the OSDs are already running, it
will report them in the command output and skip them, making it safe to rerun
(idempotent).

必备 uuid
^^^^^^^^^
.. requiring uuids

The :term:`OSD uuid` is being required as an extra step to ensure that the
right OSD is being activated. It is entirely possible that a previous OSD with
the same id exists and would end up activating the incorrect one.


dmcrypt
^^^^^^^
If the OSD was prepared with dmcrypt by ceph-volume, there is no need to
specify ``--dmcrypt`` on the command line again (that flag is not available for
the ``activate`` subcommand). An encrypted OSD will be automatically detected.


发现
----
.. Discovery

With OSDs previously created by ``ceph-volume``, a *discovery* process is
performed using :term:`LVM tags` to enable the systemd units.

The systemd unit will capture the :term:`OSD id` and :term:`OSD uuid` and
persist it. Internally, the activation will enable it like::

    systemctl enable ceph-volume@lvm-$id-$uuid

例如： ::

    systemctl enable ceph-volume@lvm-0-8715BEB4-15C5-49DE-BA6F-401086EC7B41

Would start the discovery process for the OSD with an id of ``0`` and a UUID of
``8715BEB4-15C5-49DE-BA6F-401086EC7B41``.

.. note:: for more details on the systemd workflow see :ref:`ceph-volume-lvm-systemd`

The systemd unit will look for the matching OSD device, and by looking at its
:term:`LVM tags` will proceed to:

# mount the device in the corresponding location (by convention this is
  ``/var/lib/ceph/osd/<cluster name>-<osd id>/``)

# ensure that all required devices are ready for that OSD. In the case of
a journal (when ``--filestore`` is selected) the device will be queried (with
``blkid`` for partitions, and lvm for logical volumes) to ensure that the
correct device is being linked. The symbolic link will *always* be re-done to
ensure that the correct device is linked.

# 启动 ``ceph-osd@0`` systemd unit

.. note:: The system infers the objectstore type (filestore or bluestore) by
          inspecting the LVM tags applied to the OSD devices

对于已有 OSD
------------
.. Existing OSDs

对于之前已经用 ``ceph-disk`` 部署的各 OSD ，需要\
:ref:`用 simple 子命令 <ceph-volume-simple>`\ 扫描并激活。如果\
用的是其它的工具链，把它们移植到新机制唯一的方法是再准备一次\
（会丢数据）。如何操作见 :ref:`ceph-volume-lvm-existing-osds` 。

总结
----
.. Summary

To recap the ``activate`` process for :term:`bluestore`:

#. require both :term:`OSD id` and :term:`OSD uuid`
#. enable the system unit with matching id and uuid
#. Create the ``tmpfs`` mount at the OSD directory in
   ``/var/lib/ceph/osd/$cluster-$id/``
#. Recreate all the files needed with ``ceph-bluestore-tool prime-osd-dir`` by
   pointing it to the OSD ``block`` device.
#. the systemd unit will ensure all devices are ready and linked
#. the matching ``ceph-osd`` systemd unit will get started

And for :term:`filestore`:

#. require both :term:`OSD id` and :term:`OSD uuid`
#. enable the system unit with matching id and uuid
#. the systemd unit will ensure all devices are ready and mounted (if needed)
#. the matching ``ceph-osd`` systemd unit will get started

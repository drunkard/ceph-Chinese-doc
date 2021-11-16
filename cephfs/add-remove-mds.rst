.. Deploying Metadata Servers

==================
 部署元数据服务器
==================

Each CephFS file system requires at least one MDS. The cluster operator will
generally use their automated deployment tool to launch required MDS servers as
needed.  Rook and ansible (via the ceph-ansible playbooks) are recommended
tools for doing this. For clarity, we also show the systemd commands here which
may be run by the deployment technology if executed on bare-metal.

关于元数据服务器的配置，见 `MDS 配置参考`_\ 。


.. Provisioning Hardware for an MDS

为 MDS 准备硬件
===============

The present version of the MDS is single-threaded and CPU-bound for most
activities, including responding to client requests. An MDS under the most
aggressive client loads uses about 2 to 3 CPU cores. This is due to the other
miscellaneous upkeep threads working in tandem.

Even so, it is recommended that an MDS server be well provisioned with an
advanced CPU with sufficient cores. Development is on-going to make better use
of available CPU cores in the MDS; it is expected in future versions of Ceph
that the MDS server will improve performance by taking advantage of more cores.

The other dimension to MDS performance is the available RAM for caching. The
MDS necessarily manages a distributed and cooperative metadata cache among all
clients and other active MDSs. Therefore it is essential to provide the MDS
with sufficient RAM to enable faster metadata access and mutation. The default
MDS cache size (see also :doc:`/cephfs/cache-configuration`) is 4GB. It is
recommended to provision at least 8GB of RAM for the MDS to support this cache
size.

Generally, an MDS serving a large cluster of clients (1000 or more) will use at
least 64GB of cache. An MDS with a larger cache is not well explored in the
largest known community clusters; there may be diminishing returns where
management of such a large cache negatively impacts performance in surprising
ways. It would be best to do analysis with expected workloads to determine if
provisioning more RAM is worthwhile.

In a bare-metal cluster, the best practice is to over-provision hardware for
the MDS server. Even if a single MDS daemon is unable to fully utilize the
hardware, it may be desirable later on to start more active MDS daemons on the
same node to fully utilize the available cores and memory. Additionally, it may
become clear with workloads on the cluster that performance improves with
multiple active MDS on the same node rather than over-provisioning a single
MDS.

Finally, be aware that CephFS is a highly-available file system by supporting
standby MDS (see also :ref:`mds-standby`) for rapid failover. To get a real
benefit from deploying standbys, it is usually necessary to distribute MDS
daemons across at least two nodes in the cluster. Otherwise, a hardware failure
on a single node may result in the file system becoming unavailable.

Co-locating the MDS with other Ceph daemons (hyperconverged) is an effective
and recommended way to accomplish this so long as all daemons are configured to
use available hardware within certain limits.  For the MDS, this generally
means limiting its cache size.


.. Adding an MDS

增加一个 MDS
============

#. Create an mds data point ``/var/lib/ceph/mds/ceph-${id}``. The daemon only uses this directory to store its keyring.

#. Create the authentication key, if you use CephX: ::

	$ sudo ceph auth get-or-create mds.${id} mon 'profile mds' mgr 'profile mds' mds 'allow *' osd 'allow *' > /var/lib/ceph/mds/ceph-${id}/keyring

#. Start the service: ::

	$ sudo systemctl start ceph-mds@${id}

#. The status of the cluster should show: ::

	mds: ${id}:1 {0=${id}=up:active} 2 up:standby

#. Optionally, configure the file system the MDS should join (:ref:`mds-join-fs`): ::

    $ ceph config set mds.${id} mds_join_fs ${fs}


.. Removing an MDS

删除一个 MDS
============

If you have a metadata server in your cluster that you'd like to remove, you may use
the following method.

#. (Optionally:) Create a new replacement Metadata Server. If there are no
   replacement MDS to take over once the MDS is removed, the file system will
   become unavailable to clients.  If that is not desirable, consider adding a
   metadata server before tearing down the metadata server you would like to
   take offline.

#. Stop the MDS to be removed. ::

	$ sudo systemctl stop ceph-mds@${id}

   The MDS will automatically notify the Ceph monitors that it is going down.
   This enables the monitors to perform instantaneous failover to an available
   standby, if one exists. It is unnecessary to use administrative commands to
   effect this failover, e.g. through the use of ``ceph mds fail mds.${id}``.

#. Remove the ``/var/lib/ceph/mds/ceph-${id}`` directory on the MDS. ::

	$ sudo rm -rf /var/lib/ceph/mds/ceph-${id}


.. _MDS 配置参考: ../mds-config-ref

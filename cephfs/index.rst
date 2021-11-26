.. _ceph-file-system:

===============
 Ceph 文件系统
===============

Ceph 文件系统（ CephFS ）是个与 POSIX 标准兼容的文件系统，\
它建立在 Ceph 的分布式对象存储 RADOS 之上。
CephFS endeavors to provide
a state-of-the-art, multi-use, highly available, and performant file store for
a variety of applications, including traditional use-cases like shared home
directories, HPC scratch space, and distributed workflow shared storage.

CephFS achieves these goals through the use of some novel architectural
choices.  Notably, file metadata is stored in a separate RADOS pool from file
data and served via a resizable cluster of *Metadata Servers*, or **MDS**,
which may scale to support higher throughput metadata workloads.  Clients of
the file system have direct access to RADOS for reading and writing file data
blocks. For this reason, workloads may linearly scale with the size of the
underlying RADOS object store; that is, there is no gateway or broker mediating
data I/O for clients.

Access to data is coordinated through the cluster of MDS which serve as
authorities for the state of the distributed metadata cache cooperatively
maintained by clients and MDS. Mutations to metadata are aggregated by each MDS
into a series of efficient writes to a journal on RADOS; no metadata state is
stored locally by the MDS. This model allows for coherent and rapid
collaboration between clients within the context of a POSIX file system.

.. image:: cephfs-architecture.svg

CephFS is the subject of numerous academic papers for its novel designs and
contributions to file system research. It is the oldest storage interface in
Ceph and was once the primary use-case for RADOS.  Now it is joined by two
other storage interfaces to form a modern unified storage system: RBD (Ceph
Block Devices) and RGW (Ceph Object Storage Gateway).


CephFS 入门
^^^^^^^^^^^
.. Getting Started with CephFS

For most deployments of Ceph, setting up a CephFS file system is as simple as:

.. code:: bash

    ceph fs volume create <fs name>

The Ceph `Orchestrator`_  will automatically create and configure MDS for
your file system if the back-end deployment technology supports it (see
`Orchestrator deployment table`_). Otherwise, please `deploy MDS manually
as needed`_.

Finally, to mount CephFS on your client nodes, see `Mount CephFS:
Prerequisites`_ page. Additionally, a command-line shell utility is available
for interactive access or scripting via the `cephfs-shell`_.

.. _Orchestrator: ../mgr/orchestrator
.. _deploy MDS manually as needed: add-remove-mds
.. _Orchestrator deployment table: ../mgr/orchestrator/#current-implementation-status
.. _Mount CephFS\: Prerequisites: mount-prerequisites
.. _cephfs-shell: cephfs-shell


.. raw:: html

   <!---

管理
^^^^
.. Administration

.. raw:: html

   --->

.. toctree:: 
   :maxdepth: 1
   :hidden:

    创建 CephFS 文件系统 <createfs>
    管理命令 <administration>
    Creating Multiple File Systems <multifs>
    配备、增加、删除 MDS <add-remove-mds>
    MDS 故障切换和灾备配置 <standby>
    MDS Cache Configuration <cache-configuration>
    MDS 配置选项 <mds-config-ref>
    ceph-mds 手册页 <../../man/8/ceph-mds>
    通过 NFS 导出 <nfs>
    应用最佳实践 <app-best-practices>
    FS 卷和子卷 <fs-volumes>
    CephFS 配额管理 <quota>
    健康消息 <health-messages>
    升级旧文件系统 <upgrading>
    CephFS Top Utility <cephfs-top>
    Scheduled Snapshots <snap-schedule>
    CephFS Snapshot Mirroring <cephfs-mirroring>

.. raw:: html

   <!---

挂载 CephFS
^^^^^^^^^^^
.. Mounting CephFS

.. raw:: html

   --->

.. toctree:: 
   :maxdepth: 1
   :hidden:

    客户端配置选项 <client-config-ref>
    客户端认证 <client-auth>
    挂载 CephFS: 前提条件 <mount-prerequisites>
    用内核驱动挂载 CephFS 文件系统 <mount-using-kernel-driver>
    用 FUSE 挂载 CephFS <mount-using-fuse>
    在 Windows 上挂载 CephFS <ceph-dokan>
    CephFS Shell 的用法 <../../man/8/cephfs-shell>
    内核驱动支持的功能 <kernel-features>
    ceph-fuse 手册页 <../../man/8/ceph-fuse>
    mount.ceph 手册页 <../../man/8/mount.ceph>
    mount.fuse.ceph 手册页 <../../man/8/mount.fuse.ceph>

.. raw:: html

   <!---

CephFS 内幕
^^^^^^^^^^^
.. CephFS Concepts

.. raw:: html

   --->

.. toctree:: 
   :maxdepth: 1
   :hidden:

    MDS 的各种状态 <mds-states>
    POSIX 兼容性 <posix>
    MDS Journaling <mds-journaling>
    文件布局 <file-layouts>
    分布式元数据缓存 <mdcache>
    CephFS 内的动态元数据管理 <dynamic-metadata-management>
    CephFS IO 路径 <cephfs-io-path>
    LazyIO <lazyio>
    目录分片的配置 <dirfrags>
    多活 MDS 的配置 <multimds>


.. raw:: html

   <!---

故障排除和灾难恢复
^^^^^^^^^^^^^^^^^^
.. Troubleshooting and Disaster Recovery

.. raw:: html

   --->

.. toctree:: 
   :hidden:

    驱逐客户端 <eviction>
    洗刷 <scrub>
    文件系统占满的处理 <full>
    元数据修复 <disaster-recovery-experts>
    故障排除 <troubleshooting>
    灾难恢复 <disaster-recovery>
    cephfs-journal-tool <cephfs-journal-tool>
    Recovering file system after monitor store loss <recover-fs-after-mon-store-loss>


.. raw:: html

   <!---

开发者指南
==========
.. Developer Guides

.. raw:: html

   --->

.. toctree:: 
   :maxdepth: 1
   :hidden:

    Journaler 配置 <journaler>
    客户端的能力 <capabilities>
    Java 和 Python 捆绑库 <api/index>
    Mantle <mantle>


.. raw:: html

   <!---

更多细节
^^^^^^^^
.. Additional Details

.. raw:: html

   --->

.. toctree::
   :maxdepth: 1
   :hidden:

    实验性功能 <experimental-features>

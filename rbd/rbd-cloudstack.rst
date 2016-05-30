=====================
 块设备与 CloudStack
=====================

CloudStack 4.0 及以上版本可以通过 ``libvirt`` 使用 Ceph 块设备， ``libvirt`` 会配\
置 QEMU 与 ``librbd`` 交互。 Ceph 会把块设备映像条带化为对象并分布到整个集群，这意\
味着大个的 Ceph 块设备性能会优于单体服务器！

要让 CloudStack 4.0 及更高版使用 Ceph 块设备，你得先安装 QEMU 、 ``libvirt`` \
和 CloudStack 。我们建议在另外一台物理服务器上安装 CloudStack ，此软件最低需要 \
4GB 内存和一个双核 CPU ，但是资源越多越好。下图描述了 CloudStack/Ceph 技术栈。


.. ditaa::  +---------------------------------------------------+
            |                   CloudStack                      |
            +---------------------------------------------------+
            |                     libvirt                       |
            +------------------------+--------------------------+
                                     |
                                     | configures
                                     v
            +---------------------------------------------------+
            |                       QEMU                        |
            +---------------------------------------------------+
            |                      librbd                       |
            +---------------------------------------------------+
            |                     librados                      |
            +------------------------+-+------------------------+
            |          OSDs          | |        Monitors        |
            +------------------------+ +------------------------+

.. important:: 要让 CloudStack 使用 Ceph 块设备，你必须有 Ceph 存储集群的访问权限。

CloudStack 集成了 Ceph 的块设备作为它的后端主要存储（ Primary Storage ），下列指令\
详述了 CloudStack 主存储的安装。

.. note:: 我们建议您安装 Ubuntu 14.04 或更高版本，这样就不用手动编译 libvirt 了。

安装、配置 QEMU 用于 CloudStack 时不需要任何特殊处理。确保你的 Ceph 存储集群在运行。\
安装并配置好 QEMU ；然后安装 ``libvirt`` v 0.9.13 或更高版本（也许得从源码手动编译）\
并确保它与 Ceph 结合后可正常运行。

.. note:: Ubuntu 14.04 和 CentOS 7.2 上的 ``libvirt`` 默认支持 RBD 存储池。


.. index:: pools; CloudStack

创建存储池
==========

默认情况下， Ceph 块设备使用 ``rbd`` 存储池，建议为 CloudStack NFS 主存储新建一个\
存储池。确保 Ceph 集群在运行，然后创建存储池： ::

   ceph osd pool create cloudstack

具体可参考\ `创建存储池`_\ 为存储池指定归置组数量，参考\ `归置组`_\ 确定应该为存储池分配\
多少归置组。


创建 Ceph 用户
==============

为了使用 Ceph 集群，我们需要一个有正确授权的用户，来访问刚才创建的 ``cloudstack`` 存\
储池。虽然我们可以使用 ``client.admin`` ，但还是推荐创建一个只对 ``cloudstack`` 存储池\
有访问权限的用户。 ::

	ceph auth get-or-create client.cloudstack mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=cloudstack'

在后面添加主存储的步骤里，会使用到该条命令的返回信息。

更多信息见 `用户管理`_ 。


添加主存储
==========

添加 Ceph 块设备作为主存储的方法可参考 `添加主存储 (4.2.0)`_ ，步骤包括：

#. 登录 CloudStack 界面。
#. 点击左侧导航条的 **Infrastructure** 。
#. 选择要用于主存储的域。
#. 点击 **Compute** 标签。
#. 选择图表中 `Primary Storage` 节点上的 **View All** 。
#. 点击 **Add Primary Storage** 。
#. 依次按提示执行：

   - **Protocol** 那里选择 ``RBD`` ；
   - 添加集群信息（支持 cephx ）。注：不要加用户名的 ``client.`` 部分。
   - 把 ``rbd`` 加为标签。


创建硬盘方案
============

要新建硬盘方案，参考\ `新建硬盘方案 (4.2.0)`_ 。创建一个硬盘方案以与 ``rbd`` 标签\
相配。这样 ``StoragePoolAllocator`` 查找合适的存储池时就会选择 ``rbd`` 存储池；如果\
硬盘方案没有与 ``rbd`` 标签相匹配， ``StoragePoolAllocator`` 就会选用你创建的存储池\
（比如 ``clouldstack`` ）。


局限性
======

- ClouldStack 只能绑定一个 monitor（但你可以在多个 monitors 上创建一个轮询域名服务）。


.. _创建存储池: ../../rados/operations/pools#createpool
.. _归置组: ../../rados/operations/placement-groups
.. _安装和配置 QEMU: ../qemu-rbd
.. _安装和配置 libvirt: ../libvirt
.. _KVM Hypervisor Host Installation: http://cloudstack.apache.org/docs/en-US/Apache_CloudStack/4.2.0/html/Installation_Guide/hypervisor-kvm-install-flow.html
.. _添加主存储 (4.2.0): http://cloudstack.apache.org/docs/en-US/Apache_CloudStack/4.2.0/html/Admin_Guide/primary-storage-add.html
.. _新建硬盘方案 (4.2.0): http://cloudstack.apache.org/docs/en-US/Apache_CloudStack/4.2.0/html/Admin_Guide/compute-disk-service-offerings.html#creating-disk-offerings
.. _用户管理: ../../rados/operations/user-management

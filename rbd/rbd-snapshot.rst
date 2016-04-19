======
 快照
======

.. index:: Ceph Block Device; snapshots

快照是映像在某个特定时间点的一份只读副本。 Ceph 块设备的一个高级特性就是你可\
以为映像创建快照来保留其历史。 Ceph 还支持分层快照，让你快速、简便地克隆映像（如 \
VM 映像）。 Ceph 的快照功能支持 ``rbd`` 命令和多种高级接口，包括 `QEMU`_ 、 \
`libvirt`_ 、 `OpenStack`_ 和 `CloudStack`_ 。

.. important:: 要使用 RBD 快照功能，你必须有一个在运行的 Ceph 集群。

.. note:: 如果在做快照时映像仍在进行 `I/O` 操作，快照可能就获取不到该映像准确的\
   或最新的数据，并且该快照可能不得不被克隆到一个新的可挂载的映像中。所以，我\
   们建议在做快照前先停止 `I/O` 操作。如果映像内包含文件系统，在做快照前请确保\
   文件系统处于一致的状态。要停止 `I/O` 操作可以使用 `fsfreeze` 命令。详情可参\
   考 `fsfreeze(8)` 手册页。对于虚拟机，`qemu-guest-agent` 被用来在做快照时自动\
   冻结文件系统。

.. ditaa:: +------------+         +-------------+
           | {s}        |         | {s} c999    |
           |   Active   |<-------*|   Snapshot  |
           |   Image    |         |   of Image  |
           | (stop i/o) |         | (read only) |
           +------------+         +-------------+


Cephx 注意事项
==============

启用了 `cephx`_ 时（默认的），你必须指定用户名或 ID 、及其对应的密钥文件，详情见\ \
`用户管理`_\ 。你也可以用 ``CEPH_ARGS`` 环境变量来避免重复输入下列参数。 ::

	rbd --id {user-ID} --keyring=/path/to/secret [commands]
	rbd --name {username} --keyring=/path/to/secret [commands]

例如： ::

	rbd --id admin --keyring=/etc/ceph/ceph.keyring [commands]
	rbd --name client.admin --keyring=/etc/ceph/ceph.keyring [commands]

.. tip:: 把用户名和密钥写入 ``CEPH_ARGS`` 环境变量，这样就无需每次手动输入。


快照基础
========

下列过程演示了如何用 ``rbd`` 命令创建、罗列、和删除快照。


创建快照
--------

用 ``rbd`` 命令创建快照，要指定 ``snap create`` 选项、存储池\
名和映像名。 ::

	rbd snap create {pool-name}/{image-name}@{snap-name}

例如： ::

	rbd snap create rbd/foo@snapname


罗列快照
--------

列出某个映像的快照，需要指定存储池名和映像名。 ::

	rbd snap ls {pool-name}/{image-name}

例如： ::

	rbd snap ls rbd/foo


回滚快照
--------

用 ``rbd`` 命令回滚到某一快照，指定 ``snap rollback`` 选项、存储\
池名、映像名和快照名。 ::

	rbd snap rollback {pool-name}/{image-name}@{snap-name}

例如： ::

	rbd snap rollback rbd/foo@snapname

.. note:: 把映像回滚到某一快照的意思是，用快照中的数据覆盖映像的当前\
   版本，映像越大，此过程花费的时间就越长。从快照\ **克隆要快于回滚**\
   \ 到某快照，这也是回到先前状态的首选方法。


删除快照
--------

要用 ``rbd`` 删除一快照，指定 ``snap rm`` 选项、存储池名、映像名和\
快照名。 ::

	rbd snap rm {pool-name}/{image-name}@{snap-name}

例如： ::

	rbd snap rm rbd/foo@snapname

.. note:: Ceph OSDs 异步地删除数据，所以删除快照后不会立即释放\
   磁盘空间。


清除快照
--------

要用 ``rbd`` 删除某个映像的所有快照，指定 ``snap purge`` 选项、存储池名\
和映像名。 ::

	rbd snap purge {pool-name}/{image-name}

例如： ::

	rbd snap purge rbd/foo


.. index:: Ceph Block Device; snapshot layering

分层
====

Ceph 支持为某一设备快照创建很多个写时复制（ COW ）克隆。分层快照使得 \
Ceph 块设备客户端可以很快地创建映像。例如，你可以创建一个包含有 Linux \
VM 的块设备映像；然后做快照、保护快照，再创建任意多个写时复制克\
隆。快照是只读的，所以简化了克隆快照的语义 —— 使得克隆很迅速。


.. ditaa:: +-------------+              +-------------+
           | {s} c999    |              | {s}         |
           |  Snapshot   | Child refers |  COW Clone  |
           |  of Image   |<------------*| of Snapshot |
           |             |  to Parent   |             |
           | (read only) |              | (writable)  |
           +-------------+              +-------------+

               Parent                        Child

.. note:: 这里的术语“父”和“子”指的是一个 Ceph 块设备快照（父），和从此快照克隆出来\
   的对应映像（子）。这些术语对下列的命令行用法来说很重要。

各个克隆出来的映像（子）都存储着对父映像的引用，这使得克隆出来的映像可以打开父映像并\
读取它。

一个快照的 COW 克隆和其它任何 Ceph 块设备映像的行为完全一样。克隆出的映像没有特别的\
限制，你可以读出、写入、克隆、调整克隆映像的大小。然而快照的写时复制克隆引用了快照，\
所以你克隆快照前\ **必须**\ 保护它。下图描述了此过程。

.. note:: Ceph 仅支持克隆 format 2 的映像（即用 \
   ``rbd create --image-format 2`` 创建的）。内核客户端从 3.10 \
   版开始支持克隆的映像。


分层入门
--------

Ceph 块设备的分层是个简单的过程。你必须有个映像、必须为它创建快照、并且必须保护快照，执\
行过这些步骤后，你才能克隆快照。

.. ditaa:: +----------------------------+        +-----------------------------+
           |                            |        |                             |
           | Create Block Device Image  |------->|      Create a Snapshot      |
           |                            |        |                             |
           +----------------------------+        +-----------------------------+
                                                                |
                         +--------------------------------------+
                         |
                         v
           +----------------------------+        +-----------------------------+
           |                            |        |                             |
           |   Protect the Snapshot     |------->|     Clone the Snapshot      |
           |                            |        |                             |
           +----------------------------+        +-----------------------------+


克隆出的映像包含对父快照的引用，也包含存储池 ID 、映像 ID 和快照 ID 。包含存储池 \
ID 意味着你可以把一个存储池内的快照克隆到其他存储池。

#. **映像模板：** 块设备分层的一个常见用法是创建一个主映像及其快照，并作为模板以供\
   克隆。例如，用户可以创建某一 Linux 发行版（如 Ubuntu 12.04 ）的映像、并对其做快照。\
   此用户可能会周期性地更新映像、并创建新的快照（如在 ``rbd snap create`` 之后执\
   行 ``sudo apt-get update`` 、 ``sudo apt-get upgrade`` 、 \
   ``sudo apt-get dist-upgrade`` ）。当映像成熟时，用户可以克隆任意快照。

#. **扩展模板：** 更高级的用法包括扩展映像模板，来提供比基础映像更多的信息。例\
   如，用户可以克隆一个映像（如 VM 模板）、并安装其它软件（如数据库、内容管理系\
   统、分析系统等等），然后为此扩展映像做快照，做好的快照可以像基础映像一样进行更新。

#. **模板存储池：** 块设备分层的一种用法是创建一个存储池，存放作为模板的主映像\
   和那些模板的快照。然后把只读权限分给用户，这样他们就可以克隆快照了，而无需分配此\
   存储池的写和执行权限。

#. **映像迁移/恢复：** 块设备分层的一种用法是把某一存储池内的数据迁移或恢复到另一存储池。


保护快照
--------

克隆映像要访问父快照。如果用户不小心删除了父快照，所有克隆映像都会\
损坏。为防止数据丢失，在克隆前\ **必须**\ 先保护快照。 ::

	rbd snap protect {pool-name}/{image-name}@{snapshot-name}

例如： ::

	rbd snap protect rbd/my-image@my-snapshot

.. note:: 你删除不了受保护的快照。


克隆快照
--------

要克隆快照，你得指定父存储池、父映像名和快照，还有子存储池和子映像名。\
克隆前必须先保护快照。 ::

	rbd clone {pool-name}/{parent-image}@{snap-name} {pool-name}/{child-image-name}

例如： ::

	rbd clone rbd/my-image@my-snapshot rbd/new-image

.. note:: 你可以把某个存储池中映像的快照克隆到另一存储池。例如，你可\
   以把某一存储池中的只读映像及其快照作为模板维护，把可写克隆置于另一\
   存储池。


取消快照保护
------------

删除快照前，必须先取消保护。另外，你\ *不可以*\ 删除被克隆映像引用的快\
照，所以在你删除快照前，必须先拍平（ flatten ）此快照的各个克隆。 ::

	rbd snap unprotect {pool-name}/{image-name}@{snapshot-name}

例如： ::

	rbd snap unprotect rbd/my-image@my-snapshot


罗列快照的子孙
--------------

用下列命令罗列某个快照的子孙： ::

	rbd children {pool-name}/{image-name}@{snapshot-name}

例如： ::

	rbd children rbd/my-image@my-snapshot


拍平克隆映像
------------

克隆出来的映像仍保留了对父快照的引用。要从子克隆删除这些到父快照的引用，\
你可以把快照的信息复制给子克隆，也就是“拍平”它。拍平克隆映像的时间随\
快照尺寸增大而增加。要删除快照，必须先拍平子映像。 ::

	rbd flatten {pool-name}/{image-name}

例如： ::

	rbd flatten rbd/my-image

.. note:: 因为拍平的映像包含了快照的所有信息，所以拍平的映像占用的存储空间会比分层\
   克隆要大。


.. _cephx: ../../rados/configuration/auth-config-ref/
.. _用户管理: ../../operations/user-management
.. _QEMU: ../qemu-rbd/
.. _OpenStack: ../rbd-openstack/
.. _CloudStack: ../rbd-cloudstack/
.. _libvirt: ../libvirt/

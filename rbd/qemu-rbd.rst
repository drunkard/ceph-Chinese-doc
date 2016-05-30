
================
 QEMU 与块设备
================

.. index:: Ceph Block Device; QEMU KVM

Ceph 块设备最常见的用法之一是作为虚拟机的块设备映像。例如，用户可创建一个安装、配置\
好了操作系统和相关软件的“黄金标准”映像，然后对此映像做快照，最后再克隆此快照\
（通常很多次）。详情参见\ `快照`_\ 。能制作快照的写时复制克隆意味着 Ceph 可以快速\
地为虚拟机提供块设备映像，因为客户端每次启动一个新虚拟机时不必下载整个映像。


.. ditaa::  +---------------------------------------------------+
            |                       QEMU                        |
            +---------------------------------------------------+
            |                      librbd                       |
            +---------------------------------------------------+
            |                     librados                      |
            +------------------------+-+------------------------+
            |          OSDs          | |        Monitors        |
            +------------------------+ +------------------------+


Ceph 块设备可以和 QEMU 虚拟机集成到一起，关于 QEMU 可参考 `QEMU 开源处理器仿真器`_\ ，\
其文档可参考 `QEMU 手册`_\ 。关于如何安装见\ `安装`_\ 。

.. important:: 要让 QEMU 使用 Ceph 块设备，你必须有个运行着的 Ceph 集群。


用法
====

QEMU 命令行要求你指定 存储池名和映像名，还可以指定快照名。

QEMU 会假设 Ceph 配置文件位于默认位置（如 ``/etc/ceph/$cluster.conf`` ），\
并且你是以默认的 ``client.admin`` 用户执行命令，除非你另外指定了其它 Ceph \
配置文件路径或用户。指定用户时， QEMU 只需要 ``ID`` 部分，无需完整地\
指定 ``TYPE:ID`` ，详情见\ `用户管理——用户`_\ 。不要在用户 ``ID`` 前面加客户\
端类型（即 ``client.`` ），否则会认证失败。还应该把 ``admin`` 用户、或者你\
用 ``:id={user}`` 选项所指定用户的密钥文件保存到默认路径（即 ``/etc/ceph`` ）\
或本地目录内，并修正密钥环文件的所有权和权限。命令格式如下： ::

	qemu-img {command} [options] rbd:{pool-name}/{image-name}[@snapshot-name][:option1=value1][:option2=value2...]

例如，应该这样指定 ``id`` 和 ``conf`` 选项： ::

	qemu-img {command} [options] rbd:glance-pool/maipo:id=glance:conf=/etc/ceph/ceph.conf

.. tip:: 配置中的值如果包含这些字符： ``:`` 、 ``@`` 、 ``=`` ，可在此符号\
   前加反斜线 ``\`` 转义。


用 QEMU 创建映像
================

你可以用 QEMU 创建块设备映像。必须指定 ``rbd`` 、存储池名、要创建的映像名\
以及映像尺寸。 ::

	qemu-img create -f raw rbd:{pool-name}/{image-name} {size}

例如： ::

	qemu-img create -f raw rbd:data/foo 10G

.. important::  ``raw`` 数据格式是使用 RBD 时的唯一可用 ``format`` 选项。\
   从技术上讲，你可以使用 QEMU 支持的其他格式（例如 ``qcow2`` 或 ``vmdk``），\
   但是这样做可能会带来额外开销，而且在开启缓存（见下）模式下进行虚拟机的\
   热迁移时会导致卷的不安全性。


用 QEMU 更改映像尺寸
====================

你可以通过 QEMU 调整块设备大小。必须指定 ``rbd`` 、存储池名、要调整的映像名，还有映\
像尺寸。 ::

	qemu-img resize rbd:{pool-name}/{image-name} {size}

例如： ::

	qemu-img resize rbd:data/foo 10G


用 QEMU 检索映像信息
====================

你可以用 QEMU 检索块设备映像信息。必须指定 ``rbd`` 、存储池名和映像名。 ::

	qemu-img info rbd:{pool-name}/{image-name}

例如： ::

	qemu-img info rbd:data/foo


通过 RBD 运行 QEMU
==================

QEMU 能把一主机上的块设备传递给客户机，但从 QEMU 0.15 起，不需要在主机上把映像映射为\
块设备了。 QEMU 现在能通过 ``librbd`` 直接把映像作为虚拟块设备访问。这样性能更好，因\
为它避免了额外的上下文切换，而且能利用开启 `RBD 缓存`_\ 带来的好处。

你可以用 ``qemu-img`` 把已有的虚拟机映像转换为 Ceph 块设备映像。比如你有一个 \
qcow2 映像，可以这样转换： ::

	qemu-img convert -f qcow2 -O raw debian_squeeze.qcow2 rbd:data/squeeze

要从那个映像启动虚拟机，执行： ::

	qemu -m 1024 -drive format=raw,file=rbd:data/squeeze

启用 `RBD 缓存`_\ 可显著提升性能。从 QEMU 1.2 起， QEMU 的缓存选项可控制 ``librbd`` 缓存： ::

	qemu -m 1024 -drive format=rbd,file=rbd:data/squeeze,cache=writeback

如果你的 QEMU 版本较老，你可以用 ‘file’ 参数更改 ``librbd`` 缓存配置（就像其它 Ceph 配置\
选项一样）： ::

	qemu -m 1024 -drive format=raw,file=rbd:data/squeeze:rbd_cache=true,cache=writeback

.. important:: 如果你设置了 rbd_cache=true ，那就必须设置 cache=writeback， 否则有\
   可能丢失数据。不设置 cache=writeback ， QEMU 就不会向 librbd 发送回写请求。如果 \
   QEMU 退出时未清理干净， rbd 之上的文件系统就有可能崩溃。

.. _启用 RBD 缓存: ../rbd-config-ref/#rbd-cache-config-settings


.. index:: Ceph Block Device; discard trim and libvirt

启用 Discard/TRIM 功能
======================

从 Ceph 0.46 和 QEMU 1.1 起， Ceph 块设备支持 discard 操作。这意味着客户机可以\
发送 TRIM 请求来让 Ceph 块设备回收未使用的空间。此功能可在客户机上挂载 ``ext4`` 或 \
``XFS`` 时加上 ``discard`` 选项。

客户机要想使用此功能，必须对块设备显式启用。为此，你必须在相关驱动器上指定 \
``discard_granularity`` ： ::

	qemu -m 1024 -drive format=raw,file=rbd:data/squeeze,id=drive1,if=none \
		-device driver=ide-hd,drive=drive1,discard_granularity=512

注意此处使用 IDE 驱动器， virtio 驱动不支持 discard 。

如果用的是 libvirt ，需要用 ``virsh edit`` 编辑配置文件，加上 ``xmlns:qemu`` 值。然\
后加一个 ``qemu:commandline`` 块作为那个域的子域。下例展示了如何用 ``qemu id=`` \
为两个设备设置不同的 ``discard_granularity`` 值。

.. code-block:: guess

	<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
		<qemu:commandline>
			<qemu:arg value='-set'/>
			<qemu:arg value='block.scsi0-0-0.discard_granularity=4096'/>
			<qemu:arg value='-set'/>
			<qemu:arg value='block.scsi0-0-1.discard_granularity=65536'/>
		</qemu:commandline>
	</domain>


.. index:: Ceph Block Device; cache options

QEMU 缓存选项
=============

QEMU 的缓存选项对应下列的 Ceph `RBD 缓存`_\ 选项。

回写： ::

	rbd_cache = true

透写： ::

	rbd_cache = true
	rbd_cache_max_dirty = 0

无： ::

	rbd_cache = false

QEMU 的缓存选项会覆盖 Ceph 的默认选项（就是那些 Ceph 配置文件里没有的选项）。如果\
你在 Ceph 配置文件内设置了 `RBD 缓存`_\ 选项，那么它们会覆盖 QEMU 缓存选项。如果你\
在 QEMU 命令行中设置了缓存选项，它们则会覆盖 Ceph 配置文件里的选项。


.. _QEMU 开源处理器仿真器: http://wiki.qemu.org/Main_Page
.. _QEMU 手册: http://wiki.qemu.org/Manual
.. _RBD 缓存: ../rbd-config-ref/
.. _快照: ../rbd-snapshot/
.. _安装: ../../install
.. _用户管理 — 用户: ../../rados/operations/user-management#user

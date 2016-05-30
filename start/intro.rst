==========
 Ceph 简介
==========

不管你是想为\ :term:`云平台`\ 提供\ :term:`Ceph 对象存储`\ 和/或 \
:term:`Ceph 块设备`\ ，还是想部署一个 :term:`Ceph 文件系统`\ 或者\
把 Ceph 作为他用，所有 :term:`Ceph 存储集群`\ 的部署都始于部署一个个 \
:term:`Ceph 节点`\ 、网络和 Ceph 存储集群。 Ceph 存储集群至\
少需要一个 Ceph Monitor 和两个 OSD 守护进程。而运行 Ceph 文件系统客户端时，则必须要有\
元数据服务器（ Metadata Server ）。

.. ditaa::  +---------------+ +---------------+ +---------------+
            |      OSDs     | |    Monitor    | |      MDS      |
            +---------------+ +---------------+ +---------------+

- **Ceph OSDs**: :term:`Ceph OSD 守护进程`\ （ Ceph OSD ）的功能是\
  存储数据，处理数据的复制、恢复、回填、再均衡，并通过检查其他OSD 守护进程\ 
  的心跳来向 Ceph Monitors 提供一些监控信息。当 Ceph 存储集群设定为有2个副本时，至少需要2个 OSD \
  守护进程，集群才能达到 ``active+clean`` 状态（ Ceph 默认有3个副本，但你\ 
  可以调整副本数）。

- **Monitors**: :term:`Ceph Monitor`\ 维护着展示集群状态的各种图表，包括监\
  视器图、 OSD 图、归置组（ PG ）图、和 CRUSH 图。 Ceph 保存着发生在Monitors \
  、 OSD 和 PG上的每一次状态变更的历史信息（称为 epoch ）。

- **MDSs**: :term:`Ceph 元数据服务器`\ （ MDS ）为 \
  :term:`Ceph 文件系统`\ 存储元数据（也就是说，Ceph 块设备和 Ceph \
  对象存储不使用MDS ）。元数据服务器使得 POSIX 文件系统的用户们，可以在\
  不对 Ceph 存储集群造成负担的前提下，执行诸如 ``ls``\ 、\ ``find`` 等基本命令。

Ceph 把客户端数据保存为存储池内的对象。通过使用 CRUSH 算法， Ceph 可以\
计算出哪个归置组（PG）应该持有指定的对象(Object)，然后进一步计算出哪个 OSD 守护进\
程持有该归置组。 CRUSH 算法使得 Ceph 存储集群能够动态地伸\
缩、再均衡和修复。


.. raw:: html

	<style type="text/css">div.body h3{margin:5px 0px 0px 0px;}</style>
	<table cellpadding="10"><colgroup><col width="50%"><col width="50%"></colgroup><tbody valign="top"><tr><td><h3>建议</h3>

开始把 Ceph 用于生产环境前，您应该回顾一下我们的硬件和操作系统推荐。

.. toctree::
   :maxdepth: 2

   硬件推荐 <hardware-recommendations>
   操作系统推荐 <os-recommendations>


.. raw:: html

	</td><td><h3>参与</h3>

   欢迎您加入社区，贡献文档、代码，或发现软件缺陷。

.. toctree::
   :maxdepth: 2

   get-involved
   documenting-ceph

.. raw:: html

	</td></tr></tbody></table>

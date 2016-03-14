==========
 Ceph 简介
==========

不管你是想为\ :term:`云平台`\ 提供\ :term:`Ceph 对象存储`\ 和/或 \
:term:`Ceph 块设备`\ ，还是想部署一个 :term:`Ceph 文件系统`\ 或者\
把 Ceph 作为他用，所有 :term:`Ceph 存储集群`\ 的部署都始于各 \
:term:`Ceph 节点`\ 、网络和 Ceph 存储集群。 Ceph 存储集群至\
少需要一个 Monitor 和两个 OSD 守护进程，只有运行 Ceph 文件系统客户端时才需要\
元数据服务器（ Metadata Server ）。

.. ditaa::  +---------------+ +---------------+ +---------------+
            |      OSDs     | |    Monitor    | |      MDS      |
            +---------------+ +---------------+ +---------------+

- **Ceph OSDs**: :term:`Ceph OSD 守护进程`\ （ Ceph OSD ）的功能是\
  存储数据，处理数据复制、恢复、回填、重均衡，并通过检查其他 OSD 守护进程\ 
  的心跳来向 Monitors 提供一些监控信息。当 Ceph 存储集群设定为2副本时，至少需要两个 OSD \
  守护进程才能达到 ``active+clean`` 状态（ Ceph 默认为3副本，此值\ 
  可调）。

- **Monitors**: :term:`Ceph Monitor`\ 维护着集群的各种状态图，包括监\
  视器图、 OSD 图、归置组（ PG ）图、和 CRUSH 图。 Ceph 维护着 Monitors \
  、 OSD 和 PG 各自的状态变更历史（称为 epoch ）。

- **MDSs**: :term:`Ceph 元数据服务器`\ （ MDS ）为 \
  :term:`Ceph 文件系统`\ 存储元数据（也就是说 Ceph 块设备和 Ceph \
  对象存储不需要MDS ）。元数据服务器使得 POSIX 文件系统用户可以调用\
  像 ``ls``\ 、\ ``find`` 等一些基本命令，而不会对 Ceph 存储集群造成负担。

Ceph 把客户端数据保存为存储池内的对象。根据 CRUSH 算法， Ceph 可\
计算出哪个归置组应该持有指定对象，然后进一步计算出哪个 OSD 守护进\
程持有该归置组。 CRUSH 算法使得 Ceph 存储集群具备动态伸\
缩、重均衡和动态修复的功能。


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

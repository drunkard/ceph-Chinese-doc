.. _hardware-recommendations:

==========
 硬件推荐
==========

Ceph 为普通硬件设计，这可使构建、维护 PB 级数据集群的费用相对\
低廉。规划集群硬件时，需要均衡几方面的因素，包括区域失效和潜在\
的性能问题。硬件规划要包含把使用 Ceph 集群的 Ceph 守护进程和\
其他进程恰当分布。通常，我们推荐在一台机器上只运行一种类型的\
守护进程。我们推荐把使用数据集群的进程（如 OpenStack 、 \
CloudStack 等）安装在别的机器上。


.. tip:: 另请参考 `Ceph 博客文章`_\ 。


CPU
===

Ceph 元数据服务器对 CPU 敏感，它会动态地重分布它们的负载，所以\
你的元数据服务器应该有足够的处理能力（如 4 核或更强悍的 CPU
）。 Ceph 的 OSD 运行着 :term:`RADOS` 服务、用 :term:`CRUSH`
计算数据存放位置、复制数据、维护它自己的集群运行图副本，因此
OSD 需要一定的处理能力（如双核 CPU ）。监视器只简单地维护着\
集群运行图的副本，因此对 CPU 不敏感；但必须考虑机器以后是否\
还会运行 Ceph 监视器以外的 CPU 密集型任务。例如，如果服务器\
以后要运行用于计算的虚拟机（如 OpenStack Nova ），你就要确保给
Ceph 进程保留了足够的处理能力，所以我们推荐在其他机器上运行
CPU 密集型任务。


.. RAM

RAM 内存
========

一般来说，内存越多越好。
Monitor / manager nodes for a modest cluster
might do fine with 64GB; for a larger cluster with hundreds of OSDs 128GB
is a reasonable target.  There is a memory target for BlueStore OSDs that
defaults to 4GB.  Factor in a prudent margin for the operating system and
administrative tasks (like monitoring and metrics) as well as increased
consumption during recovery:  provisioning ~8GB per BlueStore OSD
is advised.


.. Monitors and managers (ceph-mon and ceph-mgr)

监视器和管理器（ ceph-mon 和 ceph-mgr ）
----------------------------------------

Monitor and manager daemon memory usage generally scales with the size of the
cluster.  Note that at boot-time and during topology changes and recovery these
daemons will need more RAM than they do during steady-state operation, so plan
for peak usage.  For very small clusters, 32 GB suffices.  For
clusters of up to, say, 300 OSDs go with 64GB.  For clusters built with (or
which will grow to) even more OSDS you should provision
128GB.  You may also want to consider tuning settings like ``mon_osd_cache_size``
or ``rocksdb_cache_size`` after careful research.


.. Metadata servers (ceph-mds)

元数据服务器（ ceph-mds ）
--------------------------

The metadata daemon memory utilization depends on how much memory its cache is
configured to consume.  We recommend 1 GB as a minimum for most systems.  See
``mds_cache_memory``.


OSDs (ceph-osd)
---------------

.. Memory

内存
====

Bluestore uses its own memory to cache data rather than relying on the
operating system page cache.  In bluestore you can adjust the amount of memory
the OSD attempts to consume with the ``osd_memory_target`` configuration
option.

- Setting the osd_memory_target below 2GB is typically not recommended (it may
  fail to keep the memory that low and may also cause extremely slow performance.

- Setting the memory target between 2GB and 4GB typically works but may result
  in degraded performance as metadata may be read from disk during IO unless the
  active data set is relatively small.

- 4GB is the current default osd_memory_target size and was set that way to try
  and balance memory requirements and OSD performance for typical use cases.

- Setting the osd_memory_target higher than 4GB may improve performance when
  there are many (small) objects or large (256GB/OSD or more) data sets being
  processed.

.. important:: The OSD memory autotuning is "best effort".  While the OSD may
   unmap memory to allow the kernel to reclaim it, there is no guarantee that
   the kernel will actually reclaim freed memory within any specific time
   frame.  This is especially true in older versions of Ceph where transparent
   huge pages can prevent the kernel from reclaiming memory freed from
   fragmented huge pages. Modern versions of Ceph disable transparent huge
   pages at the application level to avoid this, though that still does not
   guarantee that the kernel will immediately reclaim unmapped memory.  The OSD
   may still at times exceed it's memory target.  We recommend budgeting around
   20% extra memory on your system to prevent OSDs from going OOM during
   temporary spikes or due to any delay in reclaiming freed pages by the
   kernel.  That value may be more or less than needed depending on the exact
   configuration of the system.

When using the legacy FileStore backend, the page cache is used for caching
data, so no tuning is normally needed, and the OSD memory consumption is
generally related to the number of PGs per daemon in the system.


.. Data Storage

数据存储
========

要谨慎地规划数据存储配置，因为其间涉及明显的成本和性能折衷。\
来自操作系统的并行操作和到单个硬盘的多个守护进程并发读、写请\
求操作会极大地降低性能。

.. important:: 因为 Ceph 发送 ACK 前必须把所有数据写入日志（\
   至少对 xfs 来说是），因此均衡日志和 OSD 性能相当重要。


.. Hard Disk Drives

硬盘驱动器
----------

OSD 应该有足够的空间用于存储对象数据。考虑到大硬盘的每 GB 成\
本，我们建议用容量大于 1TB 的硬盘。建议用 GB 数除以硬盘价格来\
计算每 GB 成本，因为较大的硬盘通常会对每 GB 成本有较大影响，\
例如，单价为 $75 的 1TB 硬盘其每 GB 价格为 $0.07 （
$75/1024=0.0732 ），又如单价为 $150 的 3TB 硬盘其每 GB 价格为
$0.05 （ $150/3072=0.0488 ），这样使用 1TB 硬盘会增加 40% 的\
每 GB 价格，它将表现为较低的经济性。另外，单个驱动器容量越大，\
其对应的 OSD 所需内存就越大，特别是在重均衡、回填、恢复期间。\
根据经验， 1TB 的存储空间大约需要 1GB 内存。

.. tip:: 不顾分区而在单个硬盘上运行多个OSD，这样\ **不明智**\ ！

.. tip:: 不顾分区而在运行了OSD的硬盘上同时运行监视器或元数据\
   服务器也\ **不明智**\ ！

存储驱动器受限于寻道时间、访问时间、读写时间、还有总吞吐量，\
这些物理局限性影响着整体系统性能，尤其在系统恢复期间。因此我\
们推荐独立的驱动器用于安装操作系统和软件，另外每个 OSD 守护\
进程占用一个驱动器。大多数 “slow OSD”问题的起因都是在相同的\
硬盘上运行了操作系统、多个 OSD 、和/或多个日志文件。对小型集群\
来说，鉴于解决性能问题的成本差不多会超过另外增加磁盘驱动器，\
你应该在规划设计时就避免增加 OSD 存储驱动器的负担来优化集群。

Ceph 允许你在每块硬盘驱动器上运行多个 OSD ，但这会导致资源竞\
争并降低总体吞吐量； Ceph 也允许把日志和对象数据存储在相同驱\
动器上，但这会增加记录写日志并回应客户端的延时，因为 Ceph 必\
须先写入日志才会回应确认了写动作。

Ceph 最佳实践指示，你应该分别在单独的硬盘运行操作系统、 OSD
数据和 OSD 日志。


.. Solid State Drives

固态硬盘
--------

一种提升性能的方法是使用固态硬盘（ SSD ）来降低随机访问时间和\
读延时，同时增加吞吐量。 SSD 和硬盘相比每 GB 成本通常要高
10 倍以上，但访问时间至少比硬盘快 100 倍。

SSD 没有可移动机械部件，所以不存在和硬盘一样的局限性。但 SSD
也有局限性，评估 SSD 时，顺序读写性能很重要，在为多个 OSD
存储日志时，有着 400MB/s 顺序读写吞吐量的 SSD 其性能远高于
120MB/s 的。

.. important:: 我们建议发掘 SSD 的用法来提升性能。然而在\
   大量投入 SSD 前，我们\ **强烈建议**\ 核实 SSD 的性能指标，\
   并在测试环境下衡量性能。

正因为 SSD 没有移动机械部件，所以它很适合 Ceph 里不需要太多\
存储空间的地方。相对廉价的 SSD 很诱人，慎用！可接受的
IOPS 指标对选择用于 Ceph 的 SSD 还不够，用于日志和 SSD 时还有\
几个重要考量：

- **写密集语义：** 记日志涉及写密集语义，所以你要确保选用的 SSD
  写入性能和硬盘相当或好于硬盘。廉价 SSD 可能在加速访问的同时\
  引入写延时，有时候高性能硬盘的写入速度可以和便宜 SSD 相媲美。

- **顺序写入：** 在一个 SSD 上为多个 OSD 存储多个日志时也\
  必须考虑 SSD 的顺序写入极限，因为它们要同时处理多个 OSD 日志\
  的写入请求。

- **分区对齐：** 采用了 SSD 的一个常见问题是人们喜欢分区，\
  却常常忽略了分区对齐，这会导致 SSD 的数据传输速率慢很多，\
  所以请确保分区对齐了。

SSD 用于对象存储太昂贵了，但是把 OSD 的日志存到 SSD 、把\
对象数据存储到独立的硬盘可以明显提升性能。 ``osd journal``
选项的默认值是 ``/var/lib/ceph/osd/$cluster-$id/journal`` ，\
你可以把它挂载到一个 SSD 或 SSD 分区，这样它就不再是和对象数据\
一样存储在同一个硬盘上的文件了。

提升 CephFS 文件系统性能的一种方法是从 CephFS 文件内容里分离出\
元数据。 Ceph 提供了默认的 ``metadata`` 存储池来存储
CephFS 元数据，所以你不需要给 CephFS 元数据创建存储池，但是\
可以给它创建一个仅指向某主机 SSD 的 CRUSH 运行图。详情见
:ref:`CRUSH 设备类<crush-map-device-class>`\ 。


.. Controllers

控制器
------

硬盘控制器对写吞吐量也有显著影响，要谨慎地选择，以免产生\
性能瓶颈。

.. tip:: `Ceph 博客文章`_ 常常是优秀的 Ceph 性能问题信息源，见
   `Ceph Write Throughput 1`_ 和 `Ceph Write Throughput 2`_ 。




.. Additional Considerations

其他注意事项
------------

你可以在同一主机上运行多个 OSD ，但要确保 OSD 硬盘总吞吐量\
不超过为客户端提供读写服务所需的网络带宽；还要考虑集群在每台\
主机上所存储的数据占总体的百分比，如果一台主机所占百分比太大\
而它挂了，就可能导致诸如超过 ``full ratio`` 的问题，此问题会使
Ceph 中止运作以防数据丢失。

如果每台主机运行多个 OSD ，也得保证内核是最新的。参阅\
`操作系统推荐`_\ 里关于 ``glibc`` 和 ``syncfs(2)`` 的部分，\
确保硬件性能可达期望值。




.. Networks

网络
====

建议每台机器最少两个千兆网卡，现在大多数机械硬盘都能达到大概 100MB/s 的吞吐\
量，网卡应该能处理所有 OSD 硬盘总吞吐量，所以推荐最少两个千兆网卡，分别用于\
公网（前端）和集群网络（后端）。集群网络（最好别连接到国际互联网）用于处理由\
数据复制产生的额外负载，而且可防止拒绝服务攻击，拒绝服务攻击会干扰数据归置\
组，使之在 OSD 数据复制时不能回到 ``active + clean`` 状态。请考虑部署万兆网\
卡。通过 1Gbps 网络复制 1TB 数据耗时 3 小时，而 3TB （典型配置）需要 9 小时，\
相比之下，如果使用 10Gbps 复制时间可分别缩减到 20 分钟和 1 小时。在一个 PB \
级集群中， OSD 磁盘失败是常态，而非异常；在性价比合理的的前提下，系统管理员\
想让 PG 尽快从 ``degraded`` （降级）状态恢复到 ``active + clean`` 状态。另\
外，一些部署工具（如 Dell 的 Crowbar ）部署了 5 个不同的网络，但使用了 VLAN \
以提高网络和硬件可管理性。 VLAN 使用 802.1q 协议，还需要采用支持 VLAN 功能的\
网卡和交换机，增加的硬件成本可用节省的运营（网络安装、维护）成本抵消。使用 \
VLAN 来处理集群和计算栈（如 OpenStack 、 CloudStack 等等）之间的 VM 流量时，\
采用 10G 网卡仍然值得。每个网络的机架路由器到核心路由器应该有更大的带宽，如 \
40Gbps 到 100Gbps 。

服务器应配置底板管理控制器（ Baseboard Management Controller, BMC ），管理和\
部署工具也应该大规模使用 BMC ，所以请考虑带外网络管理的成本/效益平衡，此程序\
管理着 SSH 访问、 VM 映像上传、操作系统安装、端口管理、等等，会徒增网络负载。\
运营 3 个网络有点过分，但是每条流量路径都指示了部署一个大型数据集群前要仔细考\
虑的潜能力、吞吐量、性能瓶颈。


.. Failure Domains

故障域
======

故障域指任何导致不能访问一个或多个 OSD 的故障，可以是主机上停止的进程、硬盘故\
障、操作系统崩溃、有问题的网卡、损坏的电源、断网、断电等等。规划硬件需求时，\
要在多个需求间寻求平衡点，像付出很多努力减少故障域带来的成本削减、隔离每个潜\
在故障域增加的成本。


.. Minimum Hardware Recommendations

最低硬件推荐
============

Ceph 可以运行在廉价的普通硬件上，小型生产集群和开发集群可以在\
一般的硬件上。

+--------------+----------------+-----------------------------------------+
|  进程        | 规范           | 最低建议                                |
+==============+================+=========================================+
| ``ceph-osd`` | Processor      | - 1 core minimum                        |
|              |                | - 1 core per 200-500 MB/s               |
|              |                | - 1 core per 1000-3000 IOPS             |
|              |                |                                         |
|              |                | * Results are before replication.       |
|              |                | * Results may vary with different       |
|              |                |   CPU models and Ceph features.         |
|              |                |   (erasure coding, compression, etc)    |
|              |                | * ARM processors specifically may       |
|              |                |   require additional cores.             |
|              |                | * Actual performance depends on many    |
|              |                |   factors including drives, net, and    |
|              |                |   client throughput and latency.        |
|              |                |   Benchmarking is highly recommended.   |
|              +----------------+-----------------------------------------+
|              | RAM            | - 4GB+ per daemon (more is better)      |
|              |                | - 2-4GB often functions (may be slow)   |
|              |                | - Less than 2GB not recommended         |
|              +----------------+-----------------------------------------+
|              | Volume Storage |  1x storage drive per daemon            |
|              +----------------+-----------------------------------------+
|              | DB/WAL         |  1x SSD partition per daemon (optional) |
|              +----------------+-----------------------------------------+
|              | Network        |  1x 1GbE+ NICs (10GbE+ recommended)     |
+--------------+----------------+-----------------------------------------+
| ``ceph-mon`` | Processor      | - 2 cores minimum                       |
|              +----------------+-----------------------------------------+
|              | RAM            |  2-4GB+ per daemon                      |
|              +----------------+-----------------------------------------+
|              | Disk Space     |  60 GB per daemon                       |
|              +----------------+-----------------------------------------+
|              | Network        |  1x 1GbE+ NICs                          |
+--------------+----------------+-----------------------------------------+
| ``ceph-mds`` | Processor      | - 2 cores minimum                       |
|              +----------------+-----------------------------------------+
|              | RAM            |  2GB+ per daemon                        |
|              +----------------+-----------------------------------------+
|              | Disk Space     |  1 MB per daemon                        |
|              +----------------+-----------------------------------------+
|              | Network        |  1x 1GbE+ NICs                          |
+--------------+----------------+-----------------------------------------+

.. tip:: 如果在只有一块硬盘的机器上运行 OSD ，要把数据和操作系\
   统分别放到不同分区；一般来说，我们推荐操作系统和数据分别使\
   用不同的硬盘。





.. _Ceph 博客文章: https://ceph.com/community/blog/
.. _Ceph Write Throughput 1: http://ceph.com/community/ceph-performance-part-1-disk-controller-write-throughput/
.. _Ceph Write Throughput 2: http://ceph.com/community/ceph-performance-part-2-write-throughput-without-ssd-journals/
.. _给存储池指定 OSD: ../../rados/operations/crush-map#placing-different-pools-on-different-osds
.. _操作系统推荐: ../os-recommendations

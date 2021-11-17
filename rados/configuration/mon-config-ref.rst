.. Monitor Config Reference

================
 监视器配置参考
================

理解如何配置 :term:`Ceph 监视器`\ 是构建可靠的
:term:`Ceph 存储集群`\ 的重要方面，\
**任何 Ceph 集群都需要至少一个监视器**\ 。一个监视器通常相当\
一致，但是你可以增加、删除、或替换集群中的监视器，详情见\
`增加/删除监视器`_\ 。



.. index:: Ceph Monitor; Paxos
.. Background

背景
====

Ceph 监视器们维护着\ :term:`集群运行图`\ 的“主副本”，就是说，
:term:`Ceph 客户端`\ 只要连到一个 Ceph 监视器并获取一份当前的\
集群运行图就能确定所有监视器、 OSD 和元数据服务器的位置。
Ceph 客户端读写 OSD 或元数据服务器前，必须先连到一个监视器，\
用当前的集群运行图副本和 CRUSH 算法，客户端能计算出任何对象的\
位置，拥有计算对象位置的技能——故此客户端可以直接与 OSD 通讯，
这对 Ceph 的高伸缩性、高性能来说非常重要。更多信息见\
`伸缩性和高可用性`_\ 。

监视器的主要角色是维护集群运行图的主副本，它也提供认证和\
日志记录服务。 Ceph 监视器们把监视器服务的所有更改写入一个\
单独的 Paxos 例程，然后 Paxos 以键/值方式存储所有变更以实现\
高度一致性。同步期间， Ceph 监视器能查询集群运行图的近期版本，\
它们通过操作键/值存储快照和迭代器（用 leveldb ）来进行\
存储级同步。


.. ditaa::

 /-------------\               /-------------\
 |   Monitor   | Write Changes |    Paxos    |
 |   cCCC      +-------------->+   cCCC      |
 |             |               |             |
 +-------------+               \------+------/
 |    Auth     |                      |
 +-------------+                      | Write Changes
 |    Log      |                      |
 +-------------+                      v
 | Monitor Map |               /------+------\
 +-------------+               | Key / Value |
 |   OSD Map   |               |    Store    |
 +-------------+               |  cCCC       |
 |   PG Map    |               \------+------/
 +-------------+                      ^
 |   MDS Map   |                      | Read Changes
 +-------------+                      |
 |    cCCC     |*---------------------+
 \-------------/


.. deprecated:: 0.58 版

在 0.58 及更早版本中， Ceph 监视器每个服务用一个 Paxos 例程，\
并把运行图存储为文件。



.. index:: Ceph Monitor; cluster map
.. Cluster Maps

集群运行图
----------

集群运行图是多个图的组合，包括监视器图、 OSD 图、归置组图和\
元数据服务器图。集群运行图追踪几个重要事件：哪些进程在集群里\
（ ``in`` ）；哪些进程在集群里（ ``in`` ）是 ``up`` 且在运行、\
或 ``down`` ；归置组状态是 ``active`` 或 ``inactive`` 、 \
``clean`` 或其他状态；和其他反映当前集群状态的信息，像总存储\
容量、和使用量。

当集群状态有明显变更时，如一 OSD 挂了、一归置组降级了等等，\
集群运行图会被更新以反映集群当前状态。另外，监视器也维护着集群\
的主要状态历史。监视器图、 OSD 图、归置组图和元数据服务器图\
各自维护着它们的运行图版本。我们把各图的版本称为一个 epoch 。

运营集群时，跟踪这些状态是系统管理任务的重要部分。详情见\
`监控集群`_\ 和\ `监控 OSD 和归置组`_\ 。



.. index:: high availability; quorum
.. Monitor Quorum

监视器法定人数
--------------

本文配置部分提供了一个简陋的 `Ceph 配置文件`_\ ，它提供了一个\
监视器用于测试。只用一个监视器集群可以良好地运行，然而\
**单监视器是一个单故障点**\ ，生产集群要实现高可用性的话得配\
置多个监视器，这样单个监视器的失效才\ **不会**\ 影响整个集群。

集群用多个监视器实现高可用性时，多个监视器用 `Paxos`_ 算法对\
主集群运行图达成一致，这里的一致要求大多数监视器都在运行且够\
成法定人数（如 1 个、 3 之 2 在运行、 5 之 3 、 6 之 4 等等）。


``mon force quorum join``

:描述: 强制监视器加入法定人数，即使它曾被踢出运行图。
:类型: Boolean
:默认值: ``False``



.. index:: Ceph Monitor; consistency
.. Consistency

一致性
------

你把监视器加进 Ceph 配置文件时，得注意一些架构问题， Ceph
发现集群内的其他监视器时对其有着\ **严格的一致性要求**\ 。\
尽管如此， Ceph 客户端和其他 Ceph 守护进程用配置文件发现\
监视器，监视器却用监视器图（ monmap ）相互发现而非配置文件。

一个监视器发现集群内的其他监视器时总是参考 monmap 的本地副本，\
用 monmap 而非 Ceph 配置文件避免了可能损坏集群的错误（如
``ceph.conf`` 中指定地址或端口的拼写错误）。正因为监视器把
monmap 用于发现、并共享于客户端和其他 Ceph 守护进程间，
**monmap可严格地保证监视器的一致性是可靠的**\ 。

严格的一致性也适用于 monmap 的更新，因为关于监视器的任何更新、\
关于 monmap 的变更都是通过称为 `Paxos`_ 的分布式一致性算法\
传递的。监视器们必须就 monmap 的每次更新达成一致，以确保\
法定人数里的每个监视器 monmap 版本相同，如增加、删除一个\
监视器。 monmap 的更新是增量的，所以监视器们都有最新的\
一致版本，以及一系列之前版本。历史版本的存在允许一个落后的\
监视器跟上集群当前状态。

如果监视器通过配置文件而非 monmap 相互发现，这会引进其他风险，\
因为 Ceph 配置文件不是自动更新并分发的，监视器有可能不小心\
用了较老的配置文件，以致于不认识某监视器、放弃法定人数、或者\
产生一种 `Paxos`_ 不能确定当前系统状态的情形。



.. index:: Ceph Monitor; bootstrapping monitors
.. Bootstrapping Monitors

初始化监视器
------------

在大多数配置和部署案例中，部署 Ceph 的工具可以帮你生成一个\
监视器图来初始化监视器（如 ``cephadm`` 等），一个监视器需要
4 个选项：

- **文件系统标识符：** ``fsid`` 是对象存储的唯一标识符。因为\
  你可以在一套硬件上运行多个集群，所以在初始化监视器时必须指定\
  对象存储的唯一标识符。部署工具通常可替你完成（如
  ``cephadm`` 会调用类似 ``uuidgen`` 的程序），但是你\
  也可以手动指定 ``fsid`` 。

- **监视器标识符：** 监视器标识符是分配给集群内各监视器的\
  唯一 ID ，它是一个字母数字组合，为方便起见，标识符通常以\
  字母顺序结尾（如 ``a`` 、 ``b`` 等等），可以设置于
  Ceph 配置文件（如 ``[mon.a]`` 、 ``[mon.b]`` 等等）、\
  部署工具、或 ``ceph`` 命令行工具。

- **密钥：** 监视器必须有密钥。像 ``cephadm`` 这样的\
  部署工具通常会自动生成，也可以手动完成。见\ `监视器密钥环`_\ 。

关于初始化的具体信息见\ `初始化监视器`_\ 。



.. index:: Ceph Monitor; configuring monitors
.. Configuring Monitors

监视器的配置
============

要把配置应用到整个集群，把它们放到 ``[global]`` 下；要用于\
所有监视器，置于 ``[mon]`` 下；要用于某监视器，指定监视器例程，\
如 ``[mon.a]`` ）。按惯例，监视器例程用字母命名。

.. code-block:: ini

	[global]

	[mon]

	[mon.a]

	[mon.b]

	[mon.c]



.. Minimum Configuration

最小配置
--------

Ceph 监视器的最简配置必须包括一主机名及其监视器地址，这些配置\
可置于 ``[mon]`` 下或某个监视器下。

.. code-block:: ini

	[mon]
		mon host = hostname1,hostname2,hostname3
		mon addr = 10.0.0.10:6789,10.0.0.11:6789,10.0.0.12:6789


.. code-block:: ini

	[mon.a]
		host = hostname1
		mon addr = 10.0.0.10:6789

详情见\ `网络配置参考`_\ 。

.. note:: 这里的监视器最简配置假设部署工具会自动给你生成
   ``fsid`` 和 ``mon.`` 密钥。

一旦部署完 Ceph 集群，监视器 IP 地址就\ **不应该**\ 更改了。\
然而，如果你决意要改，必须严格按照\ `更改监视器 IP 地址`_\
来改。

也可以让客户端通过 DNS 的 SRV 记录发现监视器，详情见\
`通过 DNS 查询监视器`_\ 。



.. Cluster ID

集群 ID
-------

每个 Ceph 存储集群都有一个唯一标识符（ ``fsid`` ）。如果\
指定了，它应该出现在配置文件的 ``[global]`` 段下。部署工具\
通常会生成 ``fsid`` 并存于监视器图，所以不一定会写入配置文件，\
``fsid`` 使得在一套硬件上运行多个集群成为可能。


``fsid``

:描述: 集群 ID ，一集群一个。
:类型: UUID
:是否必需: Yes.
:默认值: 无。若未指定，部署工具会生成。

.. note:: 如果你用部署工具就不能设置。



.. index:: Ceph Monitor; initial members
.. Initial Members

初始成员
--------

我们建议在生产环境下最少部署 3 个监视器，以确保高可用性。运行\
多个监视器时，你可以指定为形成法定人数成员所需的初始监视器，\
这能减小集群上线时间。

.. code-block:: ini

	[mon]
		mon initial members = a,b,c


``mon initial members``

:描述: 集群启动时初始监视器的 ID ，若指定， Ceph 需要奇数个\
       监视器来确定最初法定人数（如 3 ）。
:类型: String
:默认值: None

.. note:: 集群内的\ *大多数*\ 监视器必须能互通以建立法定人数，\
   你可以用此选项减小初始监视器数量来形成。



.. index:: Ceph Monitor; data path
.. Data

数据
----

Ceph 监视器有存储数据的默认路径。为优化性能，在生产集群上，\
我们建议在独立主机上运行 Ceph 监视器，不要与运行 Ceph OSD
守护进程的主机混用。因为 leveldb 靠 ``mmap()`` 写数据， Ceph
监视器会频繁地把数据从内存刷回磁盘，如果其数据与 OSD
守护进程共用存储器，就会与 Ceph OSD 守护进程的载荷冲突。

在 Ceph 0.58 及更早版本中，监视器数据以文件保存，这样人们可以\
用 ``ls`` 和 ``cat`` 这些普通工具检查监视器数据，然而它不能\
提供健壮的一致性。

在 Ceph 0.59 及后续版本中，监视器以键/值对存储数据。监视器需要
`ACID`_ 事务，数据存储的使用可防止监视器用损坏的版本进行恢复，\
除此之外，它允许在一个原子批量操作中进行多个修改操作。

一般来说我们不建议更改默认数据位置，如果要改，我们建议所有\
监视器统一配置，加到配置文件的 ``[mon]`` 下。


``mon data``

:描述: 监视器的数据位置。
:类型: String
:默认值: ``/var/lib/ceph/mon/$cluster-$id``


``mon data size warn``

:描述: 监视器的数据量大于 15GB 时发一条 ``HEALTH_WARN``
       集群日志。
:类型: Integer
:默认值: ``15*1024*1024*1024*``


``mon data avail warn``

:描述: 监视器的数据存储磁盘可用空间小于或等于此百分比时发一条
       ``HEALTH_WARN`` 集群日志。
:类型: Integer
:默认值: ``30``


``mon data avail crit``

:描述: 监视器的数据存储磁盘可用空间小于或等于此百分比时发一条
       ``HEALTH_ERR`` 集群日志。
:类型: Integer
:默认值: ``5``


``mon warn on cache pools without hit sets``

:描述: 如果某个缓存存储池没配置 ``hit_set_type`` ，发出一条
       ``HEALTH_WARN`` 集群日志。详情见
       :ref:`hit_set_type <hit_set_type>` 。
:类型: Boolean
:默认值: ``True``


``mon warn on crush straw calc version zero``

:描述: 如果 CRUSH 的 ``straw_calc_version`` 值为 0 ，发出一条
       ``HEALTH_WARN`` 集群日志。详情见
       :ref:`CRUSH 图的可调选项 <crush-map-tunables>`\ 。
:类型: Boolean
:默认值: ``True``


``mon warn on legacy crush tunables``

:描述: 如果 CRUSH 可调选项太旧（比 ``mon_min_crush_required_version``
       旧），发出一条 ``HEALTH_WARN`` 集群日志。
:类型: Boolean
:默认值: ``True``


``mon crush min required version``

:描述: 此集群要求的最低可调配置版本号，详情见
       :ref:`CRUSH 图的可调选项 <crush-map-tunables>`\ 。
:类型: String
:默认值: ``hammer``


``mon warn on osd down out interval zero``

:描述: 如果 ``mon osd down out interval`` 是 0 ，发出一条
       ``HEALTH_WARN`` 集群日志。 Leader 上的这个选项设置为 0 \
       时，结果类似 ``noout`` 标记。集群没有设置 ``noout``
       标记，而表现出的行为却一样时很难查出为什么，所以我们\
       对此情况发出警告。
:类型: Boolean
:默认值: ``True``


``mon warn on slow ping ratio``

:描述: Issue a ``HEALTH_WARN`` in cluster log if any heartbeat
              between OSDs exceeds ``mon warn on slow ping ratio``
              of ``osd heartbeat grace``.  The default is 5%.
:类型: Float
:默认值: ``0.05``


``mon warn on slow ping time``

:描述: Override ``mon warn on slow ping ratio`` with a specific value.
              Issue a ``HEALTH_WARN`` in cluster log if any heartbeat
              between OSDs exceeds ``mon warn on slow ping time``
              milliseconds.  The default is 0 (disabled).
:类型: Integer
:默认值: ``0``


``mon warn on pool no redundancy``

:描述: Issue a ``HEALTH_WARN`` in cluster log if any pool is
              configured with no replicas.
:类型: Boolean
:默认值: ``True``


``mon cache target full warn ratio``

:描述: 存储池使用率达到 ``cache_target_full`` 和 ``target_max_object``
       的多大比例时发出警告。
:类型: Float
:默认值: ``0.66``


``mon health to clog``

:描述: 是否周期性地向集群日志发送健康摘要。
:类型: Boolean
:默认值: ``True``


``mon health to clog tick interval``

:描述: 监视器向集群日志发送健康摘要的频率，单位为秒。非正数\
       表示禁用此功能。如果当前健康摘要为空或者与上次的相同，\
       监视器就不会发给集群日志了。
:类型: Float
:默认值: ``60.0``


``mon health to clog interval``

:描述: 监视器向集群日志发送健康摘要的频率，单位为秒。非正数\
       表示禁用此功能。不管摘要有没有变化，监视器都会把摘要\
       发给集群日志。
:类型: Integer
:默认值: ``3600``


.. index:: Ceph Storage Cluster; capacity planning, Ceph Monitor; capacity planning

.. _storage-capacity:

存储容量
--------
.. Storage Capacity

Ceph 存储集群利用率接近最大容量时（即 ``mon osd full ratio`` ），\
作为防止数据丢失的安全措施，它会阻止你读写 OSD 。因此，让\
生产集群用满可不是好事，因为牺牲了高可用性。 full ratio
默认值是 ``.95`` 或容量的 95% 。对小型测试集群来说这是非常激进\
的设置。

.. tip:: 监控集群时，要警惕和 ``nearfull`` 相关的警告。这\
   意味着一些 OSD 的失败会导致临时服务中断，应该增加一些 OSD
   来扩展存储容量。

在测试集群时，一个常见场景是：系统管理员从集群删除一个 OSD 、\
接着观察重均衡；然后继续删除其他 OSD ，直到集群达到占满率并\
锁死。我们建议，即使在测试集群里也要规划一点空闲容量用于保证\
高可用性。理想情况下，要做好这样的预案：一系列 OSD 失败后，\
短时间内不更换它们仍能恢复到 ``active + clean`` 状态。你也可以\
在 ``active + degraded`` 状态运行集群，但对正常使用来说并不好。

下图描述了一个简化的 Ceph 集群，它包含 33 个节点、每主机一个
OSD 、每 OSD 3TB 容量，所以这个小白鼠集群有 99TB 的实际容量，\
其 ``mon osd full ratio`` 为 ``.95`` 。如果它只剩余 5TB 容量，\
集群就不允许客户端再读写数据，所以它的运行容量是 95TB ，而非
99TB 。

.. ditaa::

 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
 | Rack 1 |  | Rack 2 |  | Rack 3 |  | Rack 4 |  | Rack 5 |  | Rack 6 |
 | cCCC   |  | cF00   |  | cCCC   |  | cCCC   |  | cCCC   |  | cCCC   |
 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
 | OSD 1  |  | OSD 7  |  | OSD 13 |  | OSD 19 |  | OSD 25 |  | OSD 31 |
 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
 | OSD 2  |  | OSD 8  |  | OSD 14 |  | OSD 20 |  | OSD 26 |  | OSD 32 |
 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
 | OSD 3  |  | OSD 9  |  | OSD 15 |  | OSD 21 |  | OSD 27 |  | OSD 33 |
 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
 | OSD 4  |  | OSD 10 |  | OSD 16 |  | OSD 22 |  | OSD 28 |  | Spare  |
 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
 | OSD 5  |  | OSD 11 |  | OSD 17 |  | OSD 23 |  | OSD 29 |  | Spare  |
 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+
 | OSD 6  |  | OSD 12 |  | OSD 18 |  | OSD 24 |  | OSD 30 |  | Spare  |
 +--------+  +--------+  +--------+  +--------+  +--------+  +--------+

在这样的集群里，坏一或两个 OSD 很平常；一种罕见但可能发生的\
情形是一个机架的路由器或电源挂了，这会导致多个 OSD 同时离线\
（如 OSD 7-12 ），在这种情况下，你仍要力争保持集群可运行并达到
``active + clean`` 状态，即使这意味着你得在短期内额外增加一些
OSD 及主机。如果集群利用率太高，在解决故障域期间也许不会\
丢数据，但很可能牺牲数据可用性，因为利用率超过了 full ratio 。\
故此，我们建议至少要粗略地规划下容量。

找出你集群的两个数字：

#. OSD 数量。
#. 集群总容量。

用集群里 OSD 总数除以集群总容量，就能得到 OSD 平均容量；如果\
按预计的 OSD 数乘以这个值所得的结果计算（偏小），实际应用时将\
出错；最后再用集群容量乘以占满率能得到最大运行容量，然后扣除\
预估的 OSD 失败率；用较高的失败率（如整机架的 OSD ）重复前述\
过程看是否接近占满率。

下列配置仅在创建集群时有效，之后就存储在 OSDMap 里。

.. code-block:: ini

	[global]

		mon osd full ratio = .80
		mon osd backfillfull ratio = .75
		mon osd nearfull ratio = .70


``mon osd full ratio``

:描述: OSD 硬盘使用率达到多少就认为它 ``full`` 。
:类型: Float
:默认值: ``.95``


``mon osd backfillfull ratio``

:描述: OSD 磁盘空间利用率达到多少就认为它太满了，不能再接受\
       回填。
:类型: Float
:默认值: ``.90``


``mon osd nearfull ratio``

:描述: OSD 硬盘使用率达到多少就认为它 ``nearfull`` 。
:类型: Float
:默认值: ``.85``


.. tip:: 如果一些 OSD 快满了，但其他的仍有足够空间，你可能配错
   CRUSH 权重了。

.. tip:: 这些配置仅在创建集群时有效。之后要改它们就在 OSDMap
   里了，可以用 ``ceph osd set-nearfull-ratio`` 和
   ``ceph osd set-full-ratio``



.. index:: heartbeat
.. Heartbeat

心跳
----

Ceph 监视器要求各 OSD 向它报告、并接收 OSD 们的邻居状态报告，\
以此来掌握集群。 Ceph 提供了监视器与 OSD 交互的合理默认值，\
然而你可以按需修改，详情见\ `监视器与 OSD 的交互`_\ 。



.. index:: Ceph Monitor; leader, Ceph Monitor; provider, Ceph Monitor; requester, Ceph Monitor; synchronization
.. Monitor Store Synchronization

监视器存储同步
--------------

当你用多个监视器支撑一个生产集群时，各监视器都要检查邻居是否有\
集群运行图的最新版本（如，邻居监视器的图有一或多个 epoch 版本\
高于当前监视器的最高版 epoch ），过一段时间，集群里的某个\
监视器可能落后于其它监视器太多而不得不离开法定人数，然后同步到\
集群当前状态，并重回法定人数。为了同步，监视器可能承担三种中的\
一种角色：

#. **Leader**: `Leader` 是实现最新 Paxos 版本的第一个监视器。

#. **Provider**: `Provider` 有最新集群运行图的监视器，但不是\
   第一个实现最新版。

#. **Requester:** `Requester` 落后于 leader ，重回法定人数前，\
   必须同步以获取关于集群的最新信息。

有了这些角色区分， leader就 可以给 provider 委派同步任务，\
这会避免同步请求压垮 leader 、影响性能。在下面的图示中，
requester 已经知道它落后于其它监视器，然后向 leader 请求同步，
leader 让它去和 provider 同步。


.. ditaa::

           +-----------+          +---------+          +----------+
           | Requester |          | Leader  |          | Provider |
           +-----------+          +---------+          +----------+
                  |                    |                     |
                  |                    |                     |
                  | Ask to Synchronize |                     |
                  |------------------->|                     |
                  |                    |                     |
                  |<-------------------|                     |
                  | Tell Requester to  |                     |
                  | Sync with Provider |                     |
                  |                    |                     |
                  |               Synchronize                |
                  |--------------------+-------------------->|
                  |                    |                     |
                  |<-------------------+---------------------|
                  |        Send Chunk to Requester           |
                  |         (repeat as necessary)            |
                  |    Requester Acks Chuck to Provider      |
                  |--------------------+-------------------->|
                  |                    |
                  |   Sync Complete    |
                  |    Notification    |
                  |------------------->|
                  |                    |
                  |<-------------------|
                  |        Ack         |
                  |                    |


新监视器加入集群时有必要进行同步。在运行中，监视器会不定时收到\
集群运行图的更新，这就意味着 leader 和 provider 角色可能在\
监视器间变幻。如果这事发生在同步期间（如 provider 落后于
leader ）， provider 能终结和 requester 间的同步。

一旦同步完成， Ceph 需要修复整个集群，使归置组回到
``active + clean`` 状态。


``mon sync timeout``

:描述: 监视器与上家同步的时候，等待下一个更新消息的时长（单位\
       为秒），超时此时间就放弃然后从头再来。
:类型: Double
:默认值: ``60.0``


``mon sync max payload size``

:描述: 同步载荷的最大尺寸（单位为字节）。
:类型: 32-bit Integer
:默认值: ``1045676``


``paxos max join drift``

:描述: 允许的最大 Paxos 迭代量，超过此值必须先同步监视器数据。\
       当某个监视器发现别的互联点比它领先太多的时候，它得先同\
       步数据才能继续工作。
:类型: Integer
:默认值: ``10``


``paxos stash full interval``

:描述: 多久（按提交数量计算）存储一份完整的 PaxosService 状态。\
       当前这个选项会影响 ``mds`` 、 ``mon`` 、 ``auth`` 和
       ``mgr`` 的 PaxosService 。
:类型: Integer
:默认值: ``25``


``paxos propose interval``

:描述: 提议更新之前收集本时间段的更新。
:类型: Double
:默认值: ``1.0``


``paxos min``

:描述: 保留着的 paxos 状态的最小数量。
:类型: Integer
:默认值: ``500``


``paxos min wait``

:描述: 经过一段不活跃时间后，收集更新的最小等待时间。
:类型: Double
:默认值: ``0.05``


``paxos trim min``

:描述: 有多少多余的提议才能清理。
:类型: Integer
:默认值: ``250``


``paxos trim max``

:描述: 一次最多清理多少多余的提议。
:类型: Integer
:默认值: ``500``


``paxos service trim min``

:描述: 至少积攒多少个版本再触发清理机制（ 0 禁用此选项）。
:类型: Integer
:默认值: ``250``


``paxos service trim max``

:描述: 一次提议最多可以清理多少个版本（ 0 禁用此选项）。
:类型: Integer
:默认值: ``500``


``mon mds force trim to``

:描述: 强制让监视器把 mdsmap 裁截到这一点（ 0 禁用此选项）。非\
       常危险，慎用！
:类型: Integer
:默认值: ``0``


``mon osd force trim to``

:描述: 强制让监视器把 osdmap 裁截到这一点，即使指定的时间结上\
       仍有不干净的 PG 也在所不惜。 0 禁用此选项。非常危险，\
       慎用！
:类型: Integer
:默认值: ``0``


``mon osd cache size``

:描述: osdmap 缓存的尺寸，与底层存储的缓存无关。
:类型: Integer
:默认值: ``500``


``mon election timeout``

:描述: 等待大家确认选举提案的最大时长。单位为秒。
:类型: Float
:默认值: ``5.00``


``mon lease``

:描述: 监视器版本租期（秒）。
:类型: Float
:默认值: ``5.00``


``mon lease renew interval factor``

:描述: ``mon lease`` \* ``mon lease renew interval factor``
       时长就是 Leader （头领）刷新其他监视器租期的间隔。此\
       系数应该小于 ``1.0`` 。
:类型: Float
:默认值: ``0.6``


``mon lease ack timeout factor``

:描述: Leader 会等着各 Provider 确认租期延续，时间不超过
       ``mon lease`` \* ``mon lease ack timeout factor`` 。
:类型: Float
:默认值: ``2.0``


``mon accept timeout factor``

:描述: Leader 会等着 Requester(s) 接收 Paxos 更新，时间不超过
       ``mon lease`` \* ``mon accept timeout factor`` 。出于\
       类似目的，在 Paxos 恢复阶段也会用到此配置。
:类型: Float
:默认值: ``2.0``


``mon min osdmap epochs``

:描述: 一直保存的 OSD 图元素最小数量。
:类型: 32-bit Integer
:默认值: ``500``


``mon max log epochs``

:描述: 监视器应该保留的最大日志数量。
:类型: 32-bit Integer
:默认值: ``500``



.. index:: Ceph Monitor; clock

时钟
----

Ceph 的守护进程会相互传递关键消息，这些消息必须在达到超时阀值\
前处理掉。如果 Ceph 监视器时钟不同步，就可能出现多种异常情况。\
例如：

- 守护进程忽略了收到的消息（如时间戳过时了）
- 消息未及时收到时，超时触发得太快或太晚。

详情见\ `监视器存储同步`_\ 。


.. tip:: 你\ **应该**\ 在所有监视器主机上安装 NTP 以确保监视器\
   集群的时钟同步。

时钟漂移即使尚未造成损坏也能被 NTP 感知， Ceph 的时钟漂移或时\
钟偏差警告即使在 NTP 同步水平合理时也会被触发。提高时钟漂移值\
有时候尚可容忍，然而很多因素（像载荷、网络延时、覆盖默认超时值\
和\ `监视器存储同步`_\ 选项）都能在不降低 Paxos 保证级别的情况\
下影响可接受的时钟漂移水平。

Ceph 提供了下列这些可调选项，让你自己琢磨可接受的值。


``mon tick interval``

:描述: 监视器的心跳间隔，单位为秒。
:类型: 32-bit Integer
:默认值: ``5``


``mon clock drift allowed``

:描述: 监视器间允许的时钟漂移量
:类型: Float
:默认值: ``.050``


``mon clock drift warn backoff``

:描述: 时钟偏移警告的退避指数。
:类型: Float
:默认值: ``5``


``mon timecheck interval``

:描述: 和 Leader 的时间偏移检查（时钟漂移检查）。单位为秒。
:类型: Float
:默认值: ``300.0``


``mon timecheck skew interval``

:描述: 时间检查间隔（时钟漂移检查），单位为秒。出现时间偏差时，
       Leader 间隔多久检查一次。
:类型: Float
:默认值: ``30.0``



.. Client

客户端
------


``mon client hunt interval``

:描述: 客户端每 ``N`` 秒尝试一个新监视器，直到它建立连接。
:类型: Double
:默认值: ``3.0``


``mon client ping interval``

:描述: 客户端每 ``N`` 秒 ping 一次监视器。
:类型: Double
:默认值: ``10.0``


``mon client max log entries per message``

:描述: 某监视器为每客户端生成的最大日志条数。
:类型: Integer
:默认值: ``1000``


``mon client bytes``

:描述: 内存中允许存留的客户端消息数量（字节数）。
:类型: 64-bit Integer Unsigned
:默认值: ``100ul << 20``



.. Pool settings

存储池选项
==========

从 v0.94 版起，存储池可通过标记来表明这个存储池允许或禁止更改。

如果配置过了，监视器也可以阻止存储池的删除。


``mon allow pool delete``

:描述: 监视器是否允许删除存储池。此选项可覆盖存储池标记值。
:类型: Boolean
:默认值: ``false``


``osd pool default ec fast read``

:描述: Whether to turn on fast read on the pool or not. It will be used as
              the default setting of newly created erasure coded pools if ``fast_read``
              is not specified at create time.

:类型: Boolean
:默认值: ``false``


``osd pool default flag hashpspool``

:描述: 设置新存储池的 hashpspool 标记。
:类型: Boolean
:默认值: ``true``


``osd pool default flag nodelete``

:描述: 设置新存储池的 nodelete 标记。此标记可防止存储池以任何\
       方式被删除。
:类型: Boolean
:默认值: ``false``


``osd pool default flag nopgchange``

:描述: 设置新存储池的 nopgchange 标记。不允许更改此存储池的 PG
       数量。
:类型: Boolean
:默认值: ``false``


``osd pool default flag nosizechange``

:描述: 设置新存储池的 nosizechange 标记。不允许更改此存储池的\
       副本数。
:类型: Boolean
:默认值: ``false``

关于存储池标记详情请看\ `存储池标记值`_\ 。



.. Miscellaneous

杂项
====


``mon max osd``

:描述: 集群允许的最大 OSD 数量。
:类型: 32-bit Integer
:默认值: ``10000``


``mon globalid prealloc``

:描述: 为集群预分配的全局 ID 数量。
:类型: 32-bit Integer
:默认值: ``10000``


``mon subscribe interval``

:描述: 同步的刷新间隔（秒），同步机制允许获取集群运行图和日志\
       信息。
:类型: Double
:默认值: ``86400.00``


``mon stat smooth intervals``

:描述: Ceph 将平滑最后 ``N`` 个归置组图的统计信息。
:类型: Integer
:默认值: ``2``


``mon probe timeout``

:描述: 监视器自举无效，搜寻节点前等待的时间。
:类型: Double
:默认值: ``2.00``


``mon daemon bytes``

:描述: 给元数据服务器和 OSD 的消息使用的内存空间（字节）。
:类型: 64-bit Integer Unsigned
:默认值: ``400ul << 20``


``mon max log entries per event``

:描述: 每个事件允许的最大日志条数。
:类型: Integer
:默认值: ``4096``


``mon osd prime pg temp``

:描述: 当一个先前处于 out 状态的 OSD 回到集群时，捡回（prime ）\
       还是不捡回包含先前各 OSD 的 PGMap 。设置为 ``true`` 时，\
       客户端们会继续使用先前的 OSD 们，直到新增了 OSD ，因为\
       原来的 PG 照旧互联。

       .. note::
          译者注：原文的 priming 翻译为“捡回”。因为此字意为：\
          底漆、启动、起爆剂、点火装置等，我的理解是，旧版的
          PGMap 已经一层层盖着压箱底了，新的本应从当前运行的\
          集群里汇总，可这里启用了旧的，相当于扒了一层底漆、\
          或者点燃了装填好的弹药，故译为捡回。

:类型: Boolean
:默认: ``true``


``mon osd prime pg temp max time``

:描述: 当某一先前状态为 out 的 OSD 回到集群、监视器在捡回 PGMap
       时尝试的最大时间，单位为秒。
:类型: Float
:默认: ``0.50``


``mon osd prime pg temp max time estimate``

:描述: 在每个 PG 上所花费时间的最大估值，超过此值我们就并行地\
       捡回所有 PG 。
:类型: Float
:默认值: ``0.25``


``mon mds skip sanity``

:描述: 跳过 FSMap 的安全性检查确认（遇到软件缺陷时还想继续）。\
       如果 FSMap 健全性检查失败，监视器会终止，但我们可以让它\
       继续，启用此选项即可。
:类型: Boolean
:默认值: ``False``


``mon max mdsmap epochs``

:描述: 一次提议最多可清理多少 mdsmap 时间结。
:类型: Integer
:默认值: ``500``


``mon config key max entry size``

:描述: config-key 条目的最大尺寸，单位为字节。
:类型: Integer
:默认值: ``65536``


``mon scrub interval``

:描述: 监视器洗刷（对比存储的与根据存储的键计算出的两个校验和）\
       其存储的频率，单位为秒。
:类型: Integer
:默认值: ``3600*24``


``mon scrub max keys``

:描述: 每次最多洗刷多少个键。
:类型: Integer
:默认值: ``100``


``mon compact on start``

:描述: ``ceph-mon`` 启动时压缩监视器存储所用的数据库。如果日常\
       压缩失效，手动压缩有助于缩小监视器的数据库、并提升其性\
       能。
:类型: Boolean
:默认值: ``False``


``mon compact on bootstrap``

:描述: 自举引导期间压缩监视器所用的数据库。监视器完成自举引导\
       后开始互相探测，以建立法定人数；如果加入法定人数超时，\
       它会从头开始自举引导。
:类型: Boolean
:默认值: ``False``


``mon compact on trim``

:描述: 清理旧的状态存档时也压缩这个前缀（包括 paxos ）。
:类型: Boolean
:默认值: ``True``


``mon cpu threads``

:描述: 监视器执行 CPU 密集型工作时使用的线程数。
:类型: Boolean
:默认值: ``True``


``mon osd mapping pgs per chunk``

:描述: 我们按块计算归置组到 OSD 的映射关系。这个选项指定了每个\
       块的归置组数量。
:类型: Integer
:默认值: ``4096``


``mon session timeout``

:描述: 会话闲置时间超过此限制，监视器就会终结这个不活跃的会话。
:类型: Integer
:默认值: ``300``


``mon osd cache size min``

:描述: The minimum amount of bytes to be kept mapped in memory for osd
               monitor caches.

:类型: 64-bit Integer
:默认值: ``134217728``


``mon memory target``

:描述: The amount of bytes pertaining to osd monitor caches and kv cache
              to be kept mapped in memory with cache auto-tuning enabled.

:类型: 64-bit Integer
:默认值: ``2147483648``


``mon memory autotune``

:描述: Autotune the cache memory being used for osd monitors and kv
              database.

:类型: Boolean
:默认值: ``True``



.. _Paxos: https://en.wikipedia.org/wiki/Paxos_(computer_science)
.. _监视器密钥环: ../../../dev/mon-bootstrap#secret-keys
.. _Ceph 配置文件: ../ceph-conf/#monitors
.. _网络配置参考: ../network-config-ref
.. _通过 DNS 查询监视器: ../mon-lookup-dns
.. _ACID: https://en.wikipedia.org/wiki/ACID
.. _增加/删除监视器: ../../operations/add-or-rm-mons
.. _监控集群: ../../operations/monitoring
.. _监控 OSD 和归置组: ../../operations/monitoring-osd-pg
.. _初始化监视器: ../../../dev/mon-bootstrap
.. _更改监视器 IP 地址: ../../operations/add-or-rm-mons#changing-a-monitor-s-ip-address
.. _监视器与 OSD 的交互: ../mon-osd-interaction
.. _伸缩性和高可用性: ../../../architecture#scalability-and-high-availability
.. _存储池标记值: ../../operations/pools/#set-pool-values

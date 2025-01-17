============
 归置组排障
============

归置组总不整洁
==============
.. Placement Groups Never Get Clean

归置组（ PG ）们应该保持在 ``active`` 状态、 ``active+remapped`` 状态或者
``active+degraded`` 状态，一直不能进入 ``active+clean`` 状态可能预示着
Ceph 集群的配置有问题。

在这种情况下，应该仔细检查下\ `存储池、归置组和 CRUSH 配置参考`_
里的配置选项，做一些调整。

一般来说，你的集群应该有一个以上 OSD 、并且存储池的对象副本数大于 2 。

.. _one-node-cluster:

单节点集群
----------
.. One Node Cluster

Ceph 不再提供单节点的运营文档，
因为你不可能在单个节点上设计、部署一套分布式计算系统。
另外，在运行 Ceph 守护进程的节点上同时用内核客户端挂载会导致死机，
这是 Linux 内核自身的问题（除非你在 VM 里跑客户端）。
抛开这里提到的诸多限制，用单节点配置体验 Ceph 是可以的。

如果你正尝试在单个节点上创建一个集群，在创建监视器和 OSD 前，
必须把配置文件里的 ``osd crush chooseleaf type`` 的默认值从
``1`` （表示 ``host`` 或 ``node`` ）改成 ``0`` （表示 ``osd`` ）。
就是告诉 Ceph ， OSD 可以和同一主机上的其它 OSD 互联。
如果你想要建一套单节点集群，
而 ``osd crush chooseleaf type`` 却大于 ``0`` ，
根据你的配置， Ceph 就会让一个 OSD 上的 PG 与\
另一节点、机箱、机架、行、甚至是数据中心里面的 PG 互联。

.. tip:: **不要** 在运行 Ceph 存储集群的同一主机上\
   用内核客户端直接挂载，因为会有内核冲突。
   但是，你可以在同一节点上的虚拟机里面用内核客户端挂载。

如果你在用单个磁盘创建 OSD ，
你必须先创建好数据目录。


OSD 数量小于副本数
------------------
.. Fewer OSDs than Replicas

如果你已经把两个 OSD 带到了 ``up`` 且 ``in`` 状态，
却还没见到处于 ``active + clean`` 状态的归置组，
可能是因为你的 ``osd pool default size`` 大于 ``2`` 。

有几种办法解决这个问题。如果你想让\
一个双副本集群进入 ``active + degraded`` 状态，
你可以把 ``osd pool default min size`` 设置为 ``2`` ，
这样就能在 ``active + degraded`` 状态下写入对象了。
你还可以把 ``osd pool default size`` 设置成 ``2`` ，
这样你就有两份副本了（原始的和一个副本），
这种情况下，集群还能达到 ``active + clean`` 状态。

.. note:: 你可以在运行时做出更改。如果在配置文件里更改，
   就需要重启集群。


存储池副本数为 1
----------------
.. Pool Size = 1

如果把 ``osd pool default size`` 设置成 ``1`` ，你就只有一份对象副本。
OSD 靠其它 OSD 们告诉它，它应该持有哪些对象。
如果第一个 OSD 有某个对象的一个副本、并且没有第二个副本，
那么就没有第二个 OSD 能告诉第一个 OSD 它应该有那个副本。
对于映射到第一个 OSD 的每个归置组（见 ``ceph pg dump`` ），
你可以强制第一个 OSD 通知它需要的归置组，用命令：

.. prompt:: bash

   	ceph osd force-create-pg <pgid>


CRUSH 图错误
------------
.. CRUSH Map Errors

归置组仍然不整洁的另一个原因可能是 CRUSH 图中的错误。


卡住的归置组
============
.. Stuck Placement Groups

有失败时归置组会进入“degraded”（降级）或“peering”（连接建立中）状态，
这事时有发生，通常这些状态意味着正常的失败恢复正在进行。
然而，如果一个归置组长时间处于某个这些状态就意味着有更大的问题，
因此监视器在归置组卡 （stuck） 在非最优状态时会警告。
我们具体检查：

* ``inactive`` （不活跃）——归置组长时间无活跃
  （即它不能提供读写服务了）；
  
* ``unclean`` （不干净）——归置组长时间不干净
  （例如它未能从前面的失败完全恢复）；

* ``stale`` （不新鲜）——归置组状态没有被 ``ceph-osd`` 更新，
  表明存储这个归置组的所有节点可能都挂了。

你可以摆出卡住的归置组，用下列命令之一：

.. prompt:: bash

	ceph pg dump_stuck stale
	ceph pg dump_stuck inactive
	ceph pg dump_stuck unclean

卡在 ``stale`` 状态的归置组通过修复 ``ceph-osd`` 进程通常可以修复；
卡在 ``inactive`` 状态的归置组通常是互联问题
（参见 :ref:`failures-osd-peering` ）；
卡在 ``unclean`` 状态的归置组通常是由于某些原因\
阻止了恢复的完成，像未找到的对象
（参见 :ref:`failures-osd-unfound` ）。


.. _failures-osd-peering:

归置组挂了——互联失败
========================
.. Placement Group Down - Peering Failure

在某些情况下， ``ceph-osd`` 的 `互联` 进程会遇到问题，
使 PG 不能活跃、可用。
例如 ``ceph health`` 也许显示：

.. prompt:: bash

	ceph health detail

::

	HEALTH_ERR 7 pgs degraded; 12 pgs down; 12 pgs peering; 1 pgs recovering; 6 pgs stuck unclean; 114/3300 degraded (3.455%); 1/3 in osds are down
	...
	pg 0.5 is down+peering
	pg 1.4 is down+peering
	...
	osd.1 is down since epoch 69, last address 192.168.106.220:6801/8651

查询下集群，看看到底 PG 为什么被标记为 ``down`` ，按下面的格式运行命令：

.. prompt:: bash

	ceph pg 0.5 query

.. code-block:: javascript

 { "state": "down+peering",
   ...
   "recovery_state": [
        { "name": "Started\/Primary\/Peering\/GetInfo",
          "enter_time": "2012-03-06 14:40:16.169679",
          "requested_info_from": []},
        { "name": "Started\/Primary\/Peering",
          "enter_time": "2012-03-06 14:40:16.169659",
          "probing_osds": [
                0,
                1],
          "blocked": "peering is blocked due to down osds",
          "down_osds_we_would_probe": [
                1],
          "peering_blocked_by": [
                { "osd": 1,
                  "current_lost_at": 0,
                  "comment": "starting or marking this osd lost may let us proceed"}]},
        { "name": "Started",
          "enter_time": "2012-03-06 14:40:16.169513"}
    ]
 }

``recovery_state`` 段告诉我们因 ``ceph-osd`` 守护进程挂了\
而导致互联被阻塞，本例是 ``osd.1`` 挂了，
启动这个 ``ceph-osd`` 应该就可以恢复。

另外，如果 ``osd.1`` 是灾难性的失败（如硬盘损坏），
我们可以告诉集群它丢失（ ``lost`` ）了，
让集群尽力完成副本拷贝。

.. important:: 此信息告知集群说一个 OSD 丢失了，非常危险，
   因为集群不能保证其它数据副本是一致且最新！

要报告一个 OSD 丢失（ ``lost`` ）了，并且让 Ceph 无论如何继续恢复，
按下面的格式执行：

.. prompt:: bash

	ceph osd lost 1

恢复将继续。



.. _failures-osd-unfound:

未找到的对象
============
.. Unfound Objects

某几种失败相组合可能导致 Ceph 抱怨有找不到（ ``unfound`` ）的\
对象：

.. prompt:: bash

	ceph health detail

::

	HEALTH_WARN 1 pgs degraded; 78/3778 unfound (2.065%)
	pg 2.4 is active+degraded, 78 unfound

这意味着存储集群知道一些对象
（或者现有对象的较新副本）存在，\
却没有找到它们的副本。下例展示了这种情况是如何发生的，
一个 PG 的数据存储在 ceph-osd 1 和 2 上：

* 1 挂了；
* 2 独自处理一些写动作；
* 1 起来了；
* 1 和 2 重新互联， 1 上面丢失的对象加入队列准备恢复；
* 新对象还未拷贝完， 2 挂了。

这时， 1 知道这些对象存在，但是活着的 ``ceph-osd`` 都没有副本，\
这种情况下，读写这些对象的 IO 就会被阻塞，
集群只能指望节点早点恢复。
这时我们假设用户希望先得到一个 IO 错误。

.. note:: 上面描述的情境是可能导致数据丢失的其中一个原因，就是
   在给多副本存储池配置 ``size=2`` ，
   或者给纠删码存储池配置 ``m=1`` 。

确认哪些对象找不到了，命令格式如下：

.. prompt:: bash

	ceph pg 2.4 list_unfound [starting offset, in json]

.. code-block:: javascript

  {
    "num_missing": 1,
    "num_unfound": 1,
    "objects": [
        {
            "oid": {
                "oid": "object",
                "key": "",
                "snapid": -2,
                "hash": 2249616407,
                "max": 0,
                "pool": 2,
                "namespace": ""
            },
            "need": "43'251",
            "have": "0'0",
            "flags": "none",
            "clean_regions": "clean_offsets: [], clean_omap: 0, new_object: 1",
            "locations": [
                "0(3)",
                "4(2)"
            ]
        }
    ],
    "state": "NotRecovering",
    "available_might_have_unfound": true,
    "might_have_unfound": [
        {
            "osd": "2(4)",
            "status": "osd is down"
        }
    ],
    "more": false
  }

如果在一次查询里列出的对象太多，
``more`` 这个字段将为 ``true`` ，因此你可以查询更多。
（命令行工具可能隐藏了，但这里没有）

然后找出哪些 OSD 上探测到了、
或可能包含数据。

在这份罗列结果的末尾（ ``more: false`` 之前），
``available_might_have_unfound`` 是 true 的时候会有 ``might_have_unfound`` 。
这个和 ``ceph pg #.# query`` 的输出是等价的，
只是这个结果让我们省去了直接查询（ ``query`` ）的必要。
``might_have_unfound`` 信息的提供方式和下文 ``query`` 的相同，
仅有的差异是有 ``already probed`` 状态的 OSD 会被忽略。

``query`` 的用法：

.. prompt:: bash

	ceph pg 2.4 query

.. code-block:: javascript

   "recovery_state": [
        { "name": "Started\/Primary\/Active",
          "enter_time": "2012-03-06 15:15:46.713212",
          "might_have_unfound": [
                { "osd": 1,
                  "status": "osd is down"}]},

本案例中，集群知道 ``osd.1`` 可能有数据，但它挂了（ ``down`` ）。\
所有可能的状态有：

* 已经探测到了
* 在查询
* OSD 挂了
* 尚未查询

有时候集群要花一些时间来查询可能的位置。

还有一种可能性，对象存在于其它位置却未被列出，
例如，集群里的一个 ``ceph-osd`` 停止且被剔出，
然后完全恢复了；后来的失败、恢复后仍有未找到的对象，
它也不会觉得早已死亡的 ``ceph-osd`` 上仍可能包含这些对象。
（这种情况几乎不太可能发生）。

如果所有位置都查询过了仍有对象丢失，
那就得放弃丢失的对象了。
这仍可能是罕见的失败组合导致的，
集群在写入完成前，未能得知写入是否已执行。
以下命令把未找到的（ unfound ）对象\
标记为丢失（ lost ）。

.. prompt:: bash

	ceph pg 2.5 mark_unfound_lost revert|delete

上述最后一个参数 （ ``revert|delete`` ）告诉集群应该
如何处理丢失的对象。

``delete`` 选项将导致完全删除它们。

``revert`` 选项（纠删码存储池不可用）会回滚到前一个版本或者
（如果它是新对象的话）删除它。要慎用，
它可能迷惑那些期望对象存在的应用程序。


无根归置组
==========
.. Homeless Placement Groups

拥有归置组拷贝的 OSD 都可以失败，
在这种情况下，那一部分的对象存储不可用，
监视器就不会收到那些归置组的状态更新了。
为检测这种情况，监视器把任何主 OSD 失败的归置组\
标记为 ``stale`` （不新鲜），例如：

.. prompt:: bash

	ceph health

::

	HEALTH_WARN 24 pgs stale; 3/300 in osds are down

你能找出哪些归置组 ``stale`` 、和最后存储这些归置组的 OSD ，
命令如下：

.. prompt:: bash

	ceph health detail

::

	HEALTH_WARN 24 pgs stale; 3/300 in osds are down
	...
	pg 2.5 is stuck stale+active+remapped, last acting [2,0]
	...
	osd.10 is down since epoch 23, last address 192.168.106.220:6800/11080
	osd.11 is down since epoch 13, last address 192.168.106.220:6803/11539
	osd.12 is down since epoch 24, last address 192.168.106.220:6806/11861

如果想使归置组 2.5 重新在线，例如，
上面的输出告诉我们它最后由 ``osd.0`` 和 ``osd.2`` 处理，
重启这些 ``ceph-osd`` 将恢复那个归置组（还有其它的很多 PG ）。


只有几个 OSD 接收数据
=====================
.. Only a Few OSDs Receive Data

如果你的集群有很多节点，但只有其中几个接收数据，检查下
存储池的归置组数量，按照 :ref:`归置组<rados_ops_pgs_get_pg_num>`
文档里的方法。因为在把归置组映射到多个 OSD 的操作中，
是按照集群内 OSD 的数量来确定集群归置组数量的，
这样归置组（在此操作中，是余下的部分）数量较小时就不能分布于整个集群。
在这样的情况下，创建存储池时的归置组数量应该是 OSD 数量的若干倍，
详情见\ `归置组`_\ 。参考
:ref:`存储池、归置组和 CRUSH 配置参考 <rados_config_pool_pg_crush_ref>`
里的指导，去更改分配给各个存储池的默认归置组数量。


不能写入数据
============
.. Can't Write Data

如果你的集群已启动，但一些 OSD 没起来，导致不能写入数据，
确认下运行的 OSD 数量满足归置组要求的最低 OSD 数。
如果不能满足， Ceph 就不会允许你写入数据，
因为 Ceph 不能保证复制能如愿进行。
详情参见\ `存储池、归置组和 CRUSH 配置参考`_\ 里的
``osd pool default min size`` 。


归置组不一致
============
.. PGs Inconsistent

如果 ``ceph health detail`` 返回的状态是
``active + clean + inconsistent`` ，
这表明可能在洗刷时遇到了错误。
用下面的命令找出不一致的归置组：

.. prompt:: bash

    $ ceph health detail

::

    HEALTH_ERR 1 pgs inconsistent; 2 scrub errors
    pg 0.6 is active+clean+inconsistent, acting [0,1,2]
    2 scrub errors

另外，如果你喜欢程序化的输出可以用这个命令：

.. prompt:: bash

    $ rados list-inconsistent-pg rbd

::

    ["0.6"]

一致的状态只有一种，然而在最坏的情况下，
我们可能会遇到多个对象产生了各种各样的不一致。
假设在 PG ``0.6`` 里的一个名为 ``foo`` 的对象被截断了，
``rados list-inconsistent-pg rbd`` 命令的输出可能是这样的：

.. prompt:: bash

    $ rados list-inconsistent-obj 0.6 --format=json-pretty

.. code-block:: javascript

    {
        "epoch": 14,
        "inconsistents": [
            {
                "object": {
                    "name": "foo",
                    "nspace": "",
                    "locator": "",
                    "snap": "head",
                    "version": 1
                },
                "errors": [
                    "data_digest_mismatch",
                    "size_mismatch"
                ],
                "union_shard_errors": [
                    "data_digest_mismatch_info",
                    "size_mismatch_info"
                ],
                "selected_object_info": "0:602f83fe:::foo:head(16'1 client.4110.0:1 dirty|data_digest|omap_digest s 968 uv 1 dd e978e67f od ffffffff alloc_hint [0 0 0])",
                "shards": [
                    {
                        "osd": 0,
                        "errors": [],
                        "size": 968,
                        "omap_digest": "0xffffffff",
                        "data_digest": "0xe978e67f"
                    },
                    {
                        "osd": 1,
                        "errors": [],
                        "size": 968,
                        "omap_digest": "0xffffffff",
                        "data_digest": "0xe978e67f"
                    },
                    {
                        "osd": 2,
                        "errors": [
                            "data_digest_mismatch_info",
                            "size_mismatch_info"
                        ],
                        "size": 0,
                        "omap_digest": "0xffffffff",
                        "data_digest": "0xffffffff"
                    }
                
            }
        ]
    }

此时，我们可以从输出里看到：

* 唯一不一致的对象名为 ``foo`` ，并且这就是\
  它不一致的 head 。
* 不一致分为两类：

  #. ``errors``: 这些错误表明不一致性出现在分片之间，但是没说明\
     哪个（或哪些）分片有问题。如果 ``shards`` 数组中有 ``errors`` \
     字段，且不为空，它会指出问题所在。

     * ``data_digest_mismatch``: OSD.2 内读取到的副本的数字摘要\
       与 OSD.0 和 OSD.1 的不一样。
     * ``size_mismatch``: OSD.2 内读取到的副本的尺寸是 0 ，而
       OSD.0 和 OSD.1 说是 968 。

  #. ``union_shard_errors``: ``shards`` 数组中、所有与分片相关\
     的错误 ``errors`` 的联合体。 ``errors`` 是个错误原因集合，
     汇集了存在这类问题的分片，包括 ``read_error`` 等相似的错误。
     以 ``oi`` 结尾的 ``errors`` 表明它是与 ``selected_object_info`` 的对照结果。
     从 ``shards`` 数组里可以查到哪个分片有什么样的错误。

     * ``data_digest_mismatch_info``: 存储在 object-info （对象信息）
       里的数字签名不是 ``0xffffffff`` 
       （这个是根据 OSD.2 上的分片计算出来的）。
     * ``size_mismatch_info``: ``object-info`` 内存储的尺寸与 ``OSD.2``
       上读出的对象尺寸不同。后者是 ``0`` 。

.. warning:: 如果 ``read_error`` 出现在一个分片的 ``errors`` 属性里，
   不一致很可能是物理存储器错误导致的。遇到这样的情况，
   就要检查下那个 OSD 所用的存储驱动器。

   在维修驱动器前，先检查下 ``dmesg`` 和 ``smartctl`` 的输出。

你可以用下列命令修复不一致的归置组：

.. prompt:: bash

	ceph pg repair {placement-group-ID}

例如：

.. prompt:: bash #

   ceph pg repair 1.4

.. warning:: 此命令会用\ `权威的`\ 副本覆盖\ `有问题的`\ 。
   根据既定规则，多数情况下 Ceph 都能从若干副本中选择正确的，
   但也不是所有情况下都行得通，也会有例外。比如，
   存储的数字签名可能正好丢了，
   Ceph 选择权威副本时就会忽略计算出的数字签名，
   总之，用此命令时小心为好。

.. note:: PG ID 的格式是 ``N.xxxxx`` ，其中 ``N`` 是这个 PG
   所在存储池的号码。 ``ceph osd listpools`` 命令和
   ``ceph osd dump | grep pool`` 命令可以查看存储池号码列表。

如果你时不时遇到时钟偏移引起的 ``active + clean + inconsistent`` 状态，
最好在监视器主机上配置 peer 角色的
`NTP <https://en.wikipedia.org/wiki/Network_Time_Protocol>`_ 服务。
配置细节可参考\ `网络时间协议 <http://www.ntp.org>`_\ 和 Ceph
:ref:`时钟选项 <mon-config-ref-clock>`\ 。


有关修复 PG 的更多信息
----------------------
.. More Information on PG Repair

Ceph 会存储和更新集群内存储着的对象的校验和。
在洗刷一个 PG 时， lead OSD 会尝试从其副本中选择一个权威副本。
各种可能的情况里只有一种是一致的。
执行深度洗刷后， Ceph 会计算从磁盘读出的每个对象的校验和，
并将其与之前记录的校验和进行比对。
如果当前校验和与之前记录的校验和不匹配，
那么这个不匹配将被视为不一致。对于多副本存储池来说，
对象的任何副本与权威副本的校验和不匹配都意味着存在不一致。
发现这些不一致会导致 PG 的状态被设置为不一致（ ``inconsistent`` ）。

``pg repair`` 命令试图修复各种类型的不一致。
当 ``pg repair`` 发现不一致的 PG 时，
它会尝试用权威副本的签名覆盖不一致副本的签名。
当 ``pg repair`` 在多副本存储池中发现不一致副本时，
它会将不一致副本标记为丢失。对于多副本存储池，
恢复不在 ``pg repair`` 的范围内。

对于纠删码存储池和 BlueStore 存储池，如果
``osd_scrub_auto_repair`` （默认为 ``false`` ）设置为 ``true`` ，
而且发现的错误个数不超过 ``osd_scrub_auto_repair_num_errors``
（默认为 ``5`` ）， Ceph 就会自动执行修复。

``pg repair`` 命令不能解决所有问题。
当发现 PG 存在不一致时，Ceph 也不会自动修复 PG。

RADOS 对象或 omap 的校验和并非总是可用。
校验和是以增量方式计算的。如果一个对象副本不是顺序更新的，
更新时的写入操作会改变对象并使其校验和失效。
在重新计算校验和时，不会读取整个对象。
即使无法获得校验和， ``pg repair`` 命令也能进行修复，
比如在使用 Filestore 时。使用多副本 Filestore 存储池
的用户可能更喜欢手动修复而不是 ``ceph pg repair`` 。

这部分材料与 Filestore 有关，而与 BlueStore 无关，因为 BlueStore
有它自己的内部校验和。记录的校验和与计算出的校验和相匹配
并不能证明哪一份副本确实是权威的。
如果没有可用的校验和， ``pg repair`` 会倾向于主 PG 内的数据，
但它可能不是未损坏的副本。由于存在这种不确定性，
所以发现不一致时有必要人工介入。
人工介入有时还得使用 ``ceph-objectstore-tool`` 工具。


PG 修复实战
-----------
.. PG Repair Walkthrough

https://ceph.io/geen-categorie/ceph-manually-repair-object/ - 这个网页
上有一个 PG 修复的实战记录。如果你从来没修复过，
现在想试试，建议先读一下。


纠删编码的归置组不是 active+clean
=================================
.. Erasure Coded PGs are not active+clean

CRUSH 找不到足够多的 OSD 映射到某个 PG 时，它会显示为
``2147483647`` ，意思是 ``ITEM_NONE`` 或 ``no OSD found`` ，例如： ::

	[2,1,6,0,5,8,2147483647,7,4]

OSD 不够多
----------
.. Not enough OSDs

如果 Ceph 集群仅有 8 个 OSD ，但是纠删码存储池需要 9 个，
集群就会显示 "Not enough OSDs" 。这时候，
你还可以另外创建一个需要较少 OSD 的纠删码存储池，
命令格式如下constraints：

.. prompt:: bash

	ceph osd erasure-code-profile set myprofile k=5 m=3
	ceph osd pool create erasurepool erasure myprofile

或者新增一个 OSD ，这个 PG 会自动用上的。

CRUSH 条件不能满足
------------------
.. CRUSH constraints cannot be satisfied

即使集群拥有足够多的 OSD ， CRUSH 规则的强制条件仍有可能无法满足。
假如有 10 个 OSD 分布于两个主机上，
而 CRUSH 规则要求相同归置组不得使用位于同一主机的两个 OSD ，
这样映射就会失败，因为只能找到两个 OSD 。
你可以从规则里查看（ dump ）必要条件：

.. prompt:: bash

   ceph osd crush rule ls

::

    [
        "replicated_rule",
        "erasurepool"]
    $ ceph osd crush rule dump erasurepool
    { "rule_id": 1,
      "rule_name": "erasurepool",
      "type": 3,
      "steps": [
            { "op": "take",
              "item": -1,
              "item_name": "default"},
            { "op": "chooseleaf_indep",
              "num": 0,
              "type": "host"},
            { "op": "emit"}]}

可以这样解决此问题，创建新存储池，其内的 PG 允许多个 OSD
位于同一主机，命令如下：

.. prompt:: bash

	ceph osd erasure-code-profile set myprofile crush-failure-domain=osd
	ceph osd pool create erasurepool erasure myprofile


CRUSH 过早中止
--------------
.. CRUSH gives up too soon

假设集群拥有的 OSD 足以映射到 PG
（比如有 9 个 OSD 和一个纠删码存储池的集群，
每个 PG 需要 9 个 OSD ）， CRUSH 仍然\
有可能在找到映射前就中止了。可以这样解决：

* 降低纠删存储池内 PG 的要求，让它使用较少的 OSD
  （需创建另一个存储池，
  因为纠删码配置不支持动态修改）。

* 向集群添加更多 OSD （无需修改纠删存储池，
  它会自动回到清洁状态）。

* 通过手工打造的 CRUSH 规则，让它多试几次以找到合适的映射。
  把 ``set_choose_tries`` 设置得\
  高于默认值即可。

从集群中提取出 crushmap 之后，应该先用 ``crushtool`` 校验一下\
是否有问题，这样你的试验就无需触及 Ceph 集群，只要在一个\
本地文件上测试即可：

.. prompt:: bash

    $ ceph osd crush rule dump erasurepool

::

    { "rule_id": 1,
      "rule_name": "erasurepool",
      "type": 3,
      "steps": [
            { "op": "take",
              "item": -1,
              "item_name": "default"},
            { "op": "chooseleaf_indep",
              "num": 0,
              "type": "host"},
            { "op": "emit"}]}
    $ ceph osd getcrushmap > crush.map
    got crush map from osdmap epoch 13
    $ crushtool -i crush.map --test --show-bad-mappings \
       --rule 1 \
       --num-rep 9 \
       --min-x 1 --max-x $((1024 * 1024))
    bad mapping rule 8 x 43 num_rep 9 result [3,2,7,1,2147483647,8,5,6,0]
    bad mapping rule 8 x 79 num_rep 9 result [6,0,2,1,4,7,2147483647,5,8]
    bad mapping rule 8 x 173 num_rep 9 result [0,4,6,8,2,1,3,7,2147483647]

其中 ``--num-rep`` 是纠删码 CRUSH 规则所需的 OSD 数量，
``--rule`` 是 ``ceph osd crush rule dump`` 命令结果中
``rule_id`` 字段的值。此测试会尝试映射一百万个值
（即 ``[--min-x,--max-x]`` 所指定的范围），
且必须至少显示一个坏映射；如果它没有任何输出，
说明所有映射都成功了，你可以就此打住：
问题的根源不在这里。

修改 set_choose_tries 的值
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. Changing the value of set_choose_tries

#. 反编译 crush 图后，你可以手动编辑其 CRUSH 规则：

   .. prompt:: bash

	  crushtool --decompile crush.map > crush.txt

#. 并把下面这行加进规则： ::

	  step set_choose_tries 100

   然后 ``crush.txt`` 文件内的这部分大致如此： ::

      rule erasurepool {
              id 1
              type erasure
              step set_chooseleaf_tries 5
              step set_choose_tries 100
              step take default
              step chooseleaf indep 0 type host
              step emit
      }

#. 然后编译、并再次测试：

   .. prompt:: bash

	  crushtool --compile crush.txt -o better-crush.map

#. 所有映射都成功时，
   用 ``crushtool`` 的 ``--show-choose-tries`` 选项\
   能看到所有成功映射的尝试次数直方图，
   如下面的例子：

   .. prompt:: bash

      crushtool -i better-crush.map --test --show-bad-mappings \
       --show-choose-tries \
       --rule 1 \
       --num-rep 9 \
       --min-x 1 --max-x $((1024 * 1024))
    ...
    11:        42
    12:        44
    13:        54
    14:        45
    15:        35
    16:        34
    17:        30
    18:        25
    19:        19
    20:        22
    21:        20
    22:        17
    23:        13
    24:        16
    25:        13
    26:        11
    27:        11
    28:        13
    29:        11
    30:        10
    31:         6
    32:         5
    33:        10
    34:         3
    35:         7
    36:         5
    37:         2
    38:         5
    39:         5
    40:         2
    41:         5
    42:         4
    43:         1
    44:         2
    45:         2
    46:         3
    47:         1
    48:         0
    ...
    102:         0
    103:         1
    104:         0
    ...

   有 42 个归置组需 11 次重试、 44 个归置组需 12 次重试，\
   以此类推。这样，重试的最高次数就是防止坏映射的最低值，也就是
   ``set_choose_tries`` 的取值（即上面输出中的 103 ，因为任意\
   归置组成功映射的重试次数都没有超过 103 ）。

.. _检查: ../../operations/placement-groups#get-the-number-of-placement-groups
.. _归置组: ../../operations/placement-groups
.. _存储池、归置组和 CRUSH 配置参考: ../../configuration/pool-pg-config-ref

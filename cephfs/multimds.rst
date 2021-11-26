.. _cephfs-multimds:

多活 MDS 守护进程的配置
-----------------------
.. Configuring multiple active MDS daemons

*也叫： multi-mds 、 active-active MDS*

每个 CephFS 文件系统默认情况下都只配置一个活跃 MDS 守护进程。\
在大型系统中，为了扩展元数据性能你可以配置多个活跃的 MDS 守护\
进程，它们会共同承担元数据负载。

什么情况下我需要多个活跃的 MDS 守护进程？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. When should I use multiple active MDS daemons?

当元数据默认的单个 MDS 成为瓶颈时，你应该配置多个活跃的 MDS 守\
护进程。

增加守护进程不一定都能提升性能，要看负载类型。典型地，单个客户\
端上的单个应用程序就不会受益于 MDS 守护进程的增加，除非这个应\
用程序是在并行地操作元数据。

通常，有很多客户端（操作着很多不同的目录时更好）时，大量活跃的
MDS 守护进程有利于性能提升。

MDS 活跃集群的扩容
~~~~~~~~~~~~~~~~~~
.. Increasing the MDS active cluster size

每一个 CephFS 文件系统都有自己的 *max_mds* 配置，它控制着会创\
建多少 rank 。有空闲守护进程可接管新 rank 时，文件系统 rank 的\
实际数量才会增加，比如只有一个 MDS 守护进程运行着、 max_mds 被\
设置成了 2 ，此时不会创建第二个 rank 。

把 ``max_mds`` 设置为想要的 rank 数量。在下面的例子里，
``ceph status`` 输出的 fsmap 行是此命令可能输出的结果。 ::

    # fsmap e5: 1/1/1 up {0=a=up:active}, 2 up:standby

    ceph fs set <fs_name> max_mds 2

    # fsmap e8: 2/2/2 up {0=a=up:active,1=c=up:creating}, 1 up:standby
    # fsmap e9: 2/2/2 up {0=a=up:active,1=c=up:active}, 1 up:standby

新创建的 rank (1) 会从 creating 状态过渡到 active 状态。

灾备守护进程
~~~~~~~~~~~~
.. Standby daemons

即使拥有多活 MDS 守护进程，一个高可用系统\ *仍然需要灾备守护进\
程*\ 来顶替失效的活跃守护进程。

因此，高可用系统的 ``max_mds`` 实际最大值比系统中 MDS 服务器的\
总数小一。

为了在多个服务器失效时仍能保持可用，需增加系统中的灾备守护进\
程，以弥补你能承受的服务器失效数量。

减少 rank 数量
~~~~~~~~~~~~~~
.. Decreasing the number of ranks

减少 rank 数量和减少 ``max_mds`` 一样简单：

::

    # fsmap e9: 2/2/2 up {0=a=up:active,1=c=up:active}, 1 up:standby
    ceph fs set <fs_name> max_mds 1
    # fsmap e10: 2/2/1 up {0=a=up:active,1=c=up:stopping}, 1 up:standby
    # fsmap e10: 2/2/1 up {0=a=up:active,1=c=up:stopping}, 1 up:standby
    ...
    # fsmap e10: 1/1/1 up {0=a=up:active}, 2 up:standby

集群将会自动逐步地停掉多余的 rank ，直到符合 ``max_mds`` 。

See :doc:`/cephfs/administration` for more details which forms ``<role>`` can
take.

注意：被停掉的 rank 会先进入 stopping 状态，并持续一段时间，\
在此期间它要把它分享的那部分元数据转手给仍然活跃着的
MDS 守护进程，这个过程可能要持续数秒到数分钟。如果这个 MDS
卡在了 stopping 状态，那可能是触发了软件缺陷。

如果一个 MDS 守护进程正处于 ``up:stopping`` 状态时崩溃了、或是\
被杀死了，就会有一个灾备顶替它，而且集群的监视器们也会阻止停止\
此守护进程的尝试。

守护进程完成 stopping 状态后，它会自己重生并成为灾备。


.. _cephfs-pinning:

手动将目录树插入特定的 rank
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. Manually pinning directory trees to a particular rank

在多活元数据服务器配置中，均衡器负责在集群内均匀地散布元数据\
负荷。此设计对大多数用户来说都够用了，但是，有时人们想要跳过\
动态均衡器，手动把某些元数据映射到特定的 rank ；这样一来，\
管理员或用户就可以均匀地散布应用负荷、或者限制用户的\
元数据请求，以防他影响整个集群。

为实现此目的，引入了一个机制，名为 ``export pin`` （导出销），\
是目录的一个扩展属性，名为 ``ceph.dir.pin`` 。用户可以用\
标准命令配置此属性：

::

    setfattr -n ceph.dir.pin -v 2 path/to/dir

这个扩展属性的值是给这个目录树分配的 rank ，默认值 ``-1`` 表示\
此目录没有销进（某个 rank ）。

一个目录的导出销是从最近的、配置了导出销的父目录继承的；同理，\
在一个目录上配置导出销会影响它的所有子目录。然而，设置子目录的\
导出销可以覆盖从父目录继承来的销子，例如：

::

    mkdir -p a/b
    # "a" and "a/b" both start without an export pin set
    setfattr -n ceph.dir.pin -v 1 a/
    # a and b are now pinned to rank 1
    setfattr -n ceph.dir.pin -v 0 a/b
    # a/b is now pinned to rank 0 and a/ and the rest of its children are still pinned to rank 1


.. _cephfs-ephemeral-pinning:

Setting subtree partitioning policies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible to setup **automatic** static partitioning of subtrees via
a set of **policies**. In CephFS, this automatic static partitioning is
referred to as **ephemeral pinning**. Any directory (inode) which is
ephemerally pinned will be automatically assigned to a particular rank
according to a consistent hash of its inode number. The set of all
ephemerally pinned directories should be uniformly distributed across all
ranks.

Ephemerally pinned directories are so named because the pin may not persist
once the directory inode is dropped from cache. However, an MDS failover does
not affect the ephemeral nature of the pinned directory. The MDS records what
subtrees are ephemerally pinned in its journal so MDS failovers do not drop
this information.

A directory is either ephemerally pinned or not. Which rank it is pinned to is
derived from its inode number and a consistent hash. This means that
ephemerally pinned directories are somewhat evenly spread across the MDS
cluster. The **consistent hash** also minimizes redistribution when the MDS
cluster grows or shrinks. So, growing an MDS cluster may automatically increase
your metadata throughput with no other administrative intervention.

Presently, there are two types of ephemeral pinning:

**Distributed Ephemeral Pins**: This policy causes a directory to fragment
(even well below the normal fragmentation thresholds) and distribute its
fragments as ephemerally pinned subtrees. This has the effect of distributing
immediate children across a range of MDS ranks.  The canonical example use-case
would be the ``/home`` directory: we want every user's home directory to be
spread across the entire MDS cluster. This can be set via:

::

    setfattr -n ceph.dir.pin.distributed -v 1 /cephfs/home


**Random Ephemeral Pins**: This policy indicates any descendent sub-directory
may be ephemerally pinned. This is set through the extended attribute
``ceph.dir.pin.random`` with the value set to the percentage of directories
that should be pinned. For example:

::

    setfattr -n ceph.dir.pin.random -v 0.5 /cephfs/tmp

Would cause any directory loaded into cache or created under ``/tmp`` to be
ephemerally pinned 50 percent of the time.

It is recomended to only set this to small values, like ``.001`` or ``0.1%``.
Having too many subtrees may degrade performance. For this reason, the config
``mds_export_ephemeral_random_max`` enforces a cap on the maximum of this
percentage (default: ``.01``). The MDS returns ``EINVAL`` when attempting to
set a value beyond this config.

Both random and distributed ephemeral pin policies are off by default in
Octopus. The features may be enabled via the
``mds_export_ephemeral_random`` and ``mds_export_ephemeral_distributed``
configuration options.

Ephemeral pins may override parent export pins and vice versa. What determines
which policy is followed is the rule of the closest parent: if a closer parent
directory has a conflicting policy, use that one instead. For example:

::

    mkdir -p foo/bar1/baz foo/bar2
    setfattr -n ceph.dir.pin -v 0 foo
    setfattr -n ceph.dir.pin.distributed -v 1 foo/bar1

The ``foo/bar1/baz`` directory will be ephemerally pinned because the
``foo/bar1`` policy overrides the export pin on ``foo``. The ``foo/bar2``
directory will obey the pin on ``foo`` normally.

For the reverse situation:

::

    mkdir -p home/{patrick,john}
    setfattr -n ceph.dir.pin.distributed -v 1 home
    setfattr -n ceph.dir.pin -v 2 home/patrick

The ``home/patrick`` directory and its children will be pinned to rank 2
because its export pin overrides the policy on ``home``.

.. _mds-standby:

术语
----

一个 Ceph 集群内可以没有、或者有多个 CephFS *文件系统*\ 。
CephFS 文件系统有一个人类可读的名字（用 ``fs new`` 设置）、和\
一个整数 ID ，这个 ID 称为文件系统集群 ID 或 *FSCID* 。

每个 CephFS 都有几个 *rank* ，默认是一个，从 0 起。一个 rank
可看作是一个元数据分片。文件系统 rank 数量的控制在
:doc:`/cephfs/multimds` 里详述。

CephFS 的每个 ceph-mds 进程（一个\ *守护进程*\ ）刚启动时都没\
有 rank ，它由监视器集群分配。一个守护进程一次只能占据一个
rank ，只有在 ceph-mds 守护进程停止的时候才会释放 rank 。

如果某个 rank 没有依附一个守护进程，那这个 rank 就\
*失效了（ failed ）*\ 。分配给守护进程的 rank 才被当作\
*正常的（ up ）*\ 。

首次配置守护进程时，管理员需分配静态的\ *名字*\ ，一般配置都\
会用守护进程所在的主机名作为其守护进程名字。

A ceph-mds daemons can be assigned to a particular file system by
setting the `mds_join_fs` configuration option to the file system
name.

守护进程每次启动时，还会被分配一个 *GID* ，对于这个守护进程的\
特定进程的生命周期来说它是唯一的。 GID 是整数。

.. todo:: 译者注： rank 翻译为“席位”、“座席”？它们共同处理元数\
   据，且动态分配，类似客服中心的座席。


.. Referring to MDS daemons

MDS 守护进程的引用
------------------

针对 MDS 守护进程的大多数管理命令都接受一个灵活的参数格式，它\
可以包含 rank 、 GID 或名字。

使用 rank 时，它前面可以加文件系统的名字或 ID ，也可以不加。如\
果某个守护进程是灾备的（即当前还没给它分配 rank ），那就只能通\
过 GID 或名字引用。

例如，假设我们有一个 MDS 守护进程，名为 myhost ，其 GID 为
5446 ，分配的 rank 是 0 ，它位于名为 myfs 的文件系统内，文件系\
统的 FSCID 是 3 ，那么，下面的几种形式都适用于 fail 命令： ::

    ceph mds fail 5446     # GID
    ceph mds fail myhost   # Daemon name
    ceph mds fail 0        # Unqualified rank
    ceph mds fail 3:0      # FSCID and rank
    ceph mds fail myfs:0   # Filesystem name and rank


.. Managing failover

故障切换的管理
--------------

如果一个 MDS 守护进程不再与监视器通讯，监视器把它标记为 *laggy*
（滞后）状态前会等待 ``mds_beacon_grace`` 秒（默认是 15 秒）。\
如果有可用灾备，监视器会立即替换处于 laggy 状态的守护进程。

为安全起见，每个文件系统都要指定一些灾备守护进程，灾备数量包括\
处于热备状态、等着接替失效 rank 的（记着，热备守护进程\
不会被重分配去接管另一个 rank 、或者另一个 CephFS 文件系统内的\
失效守护进程）。不在重放状态的灾备守护进程会被任意文件系统当作\
自己的灾备。每个文件系统都可以单独配置期望的灾备守护进程数量，\
用这个： ::

    ceph fs set <fs name> standby_count_wanted <count>

``count`` 设置为 0 表示禁用健康检查。


.. Configuring standby-replay
.. _mds-standby-replay:

热备的配置
----------

Each CephFS file system may be configured to add standby-replay daemons.  These
standby daemons follow the active MDS's metadata journal to reduce failover
time in the event the active MDS becomes unavailable. Each active MDS may have
only one standby-replay daemon following it.

Configuring standby-replay on a file system is done using:

::

    ceph fs set <fs name> allow_standby_replay <bool>

Once set, the monitors will assign available standby daemons to follow the
active MDSs in that file system.

Once an MDS has entered the standby-replay state, it will only be used as a
standby for the rank that it is following. If another rank fails, this
standby-replay daemon will not be used as a replacement, even if no other
standbys are available. For this reason, it is advised that if standby-replay
is used then every active MDS should have a standby-replay daemon.


.. Configuring MDS file system affinity
.. _mds-join-fs:

配置 MDS 与文件系统的亲和性
---------------------------

You may want to have an MDS used for a particular file system. Or, perhaps you
have larger MDSs on better hardware that should be preferred over a last-resort
standby on lesser or over-provisioned hardware. To express this preference,
CephFS provides a configuration option for MDS called ``mds_join_fs`` which
enforces this `affinity`.

As part of any failover, the Ceph monitors will prefer standby daemons with
``mds_join_fs`` equal to the file system name with the failed rank.  If no
standby exists with ``mds_join_fs`` equal to the file system name, it will
choose a `vanilla` standby (no setting for ``mds_join_fs``) for the replacement
or any other available standby as a last resort. Note, this does not change the
behavior that ``standby-replay`` daemons are always selected before looking at
other standbys.

Even further, the monitors will regularly examine the CephFS file systems when
stable to check if a standby with stronger affinity is available to replace an
MDS with lower affinity. This process is also done for standby-replay daemons:
if a regular standby has stronger affinity than the standby-replay MDS, it will
replace the standby-replay MDS.

For example, given this stable and healthy file system:

::

    $ ceph fs dump
    dumped fsmap epoch 399
    ...
    Filesystem 'cephfs' (27)
    ...
    e399
    max_mds 1
    in      0
    up      {0=20384}
    failed
    damaged
    stopped
    ...
    [mds.a{0:20384} state up:active seq 239 addr [v2:127.0.0.1:6854/966242805,v1:127.0.0.1:6855/966242805]]

    Standby daemons:

    [mds.b{-1:10420} state up:standby seq 2 addr [v2:127.0.0.1:6856/2745199145,v1:127.0.0.1:6857/2745199145]]


You may set ``mds_join_fs`` on the standby to enforce your preference: ::

    $ ceph config set mds.b mds_join_fs cephfs

after automatic failover: ::

    $ ceph fs dump
    dumped fsmap epoch 405
    e405
    ...
    Filesystem 'cephfs' (27)
    ...
    max_mds 1
    in      0
    up      {0=10420}
    failed
    damaged
    stopped
    ...
    [mds.b{0:10420} state up:active seq 274 join_fscid=27 addr [v2:127.0.0.1:6856/2745199145,v1:127.0.0.1:6857/2745199145]]

    Standby daemons:

    [mds.a{-1:10720} state up:standby seq 2 addr [v2:127.0.0.1:6854/1340357658,v1:127.0.0.1:6855/1340357658]]

Note in the above example that ``mds.b`` now has ``join_fscid=27``. In this
output, the file system name from ``mds_join_fs`` is changed to the file system
identifier (27). If the file system is recreated with the same name, the
standby will follow the new file system as expected.

Finally, if the file system is degraded or undersized, no failover will occur
to enforce ``mds_join_fs``.

==========
 故障排除
==========

慢或卡住的操作
==============
.. Slow/stuck operations

如果遇到了明显的卡顿操作，首先要定位问题源头：是客户端、
MDS 、抑或是连接二者的网络。从存在卡顿操作的地方下手（参考下面\
的 :ref:`slow_requests` ），进而缩小范围。

我们可以这样获取线索，把 MDS 缓存转储出来看看发生了什么： ::

  ceph daemon mds.<name> dump cache /tmp/dump.txt

.. note:: `dump.txt` 这个文件在运行着 MDS 的机器上，而且，
   对于 systemd 控制着的 MDS 服务，它是在 MDS 容器内的一个 tmpfs 上。
   可以用 `nsenter(1)` 来定位 `dump.txt` ，或者指定另外一个系统级的路径。

如果 MDS 设置了较高的日志级别，那里差不多肯定有我们需要的诊断信息，
解决问题有望了。


RADOS 健康状况
==============
.. RADOS Health

如果 CephFS 的元数据或者数据存储池的某一部分不可用、且 CephFS 不响应，
很有可能是 RADOS 本身有问题，应该先解决这样的问题
（ :doc:`../../rados/troubleshooting/index` ）。


MDS 问题
========
.. The MDS

如果某个操作卡在了 MDS 内部，类似 "slow requests are blocked" 的消息\
最终会出现在 ``ceph health`` 里；也可能指出是客户端的问题，
如 "failing to respond" 或其它形式的异常行为。
如果 MDS 认定某些客户端的行为异常，你应该弄明白起因。常见起因有：

通常是这些起因：

#. 系统过载（如果你还有空闲内存，增大 ``mds cache memory limit`` 配置试试，
   默认才 1GiB ；活跃文件比较多，超过 MDS 缓存容量是此问题的首要起因！）

#. 客户端比较老（行为乖张）；

#. 底层的 RADOS 问题。

除此之外，你也许遇到了新的软件缺陷，应该报告给开发者！


.. _slow_requests:

慢请求（ MDS 端）
-----------------

通过管理套接字，你可以罗列当前正在运行的操作： ::

        ceph daemon mds.<name> dump_ops_in_flight

在 MDS 主机上执行。找出卡住的命令、并调查卡住的原因。
通常最后一个“事件”（ event ）尝试过收集锁、或者把这个操作发往 MDS 日志。
如果它是在等待 OSD ，修正即可；如果操作都卡在了某个索引节点上，
原因可能是一个客户端一直占着能力，别人就没法拿到，
也可能是这个客户端想刷回脏数据，还可能是你遇到了 CephFS 分布式文件锁的\
代码（文件能力子系统、 capabilities 、 caps ）缺陷。

如果起因是能力代码的缺陷，重启 MDS 也许能解决此问题。

如果 MDS 上没发现慢请求，而且也没报告客户端行为异常，
那问题就可能在客户端上、或者它的请求还没到 MDS 上。


.. _ceph_fuse_debugging:

ceph-fuse 的调试
================
.. ceph-fuse debugging

ceph-fuse 也支持 dump_ops_in_flight 命令，可以查看是否卡住、卡在哪里了。

调试输出
--------

要想看到 ceph-fuse 的更多调试信息，试试在前台运行，让日志输出到\
控制台（ ``-d`` ）、打开客户端调试（ ``--debug-client=20`` ）、\
打印发送过的所有消息（ ``--debug-ms=1`` ）。

如果你怀疑是监视器的问题，也可以打开监视器调试开关（ ``--debug-monc=20`` ）。


.. _kernel_mount_debugging:

内核挂载的调试
==============
.. Kernel mount debugging

如果内核客户端有问题，最重要的是找出问题起因是在内核客户端上、
还是在 MDS 上，通常都比较容易发现。如果内核客户端直接垮了，
``dmesg`` 里会有输出信息，要收集好它们、还有任何不对劲的内核状态。

慢请求
------

遗憾的是内核客户端不支持管理套接字，可是如果你的内核启用了
（如果限制过） debugfs ，那么它就有相似的接口了。
``sys/kernel/debug/ceph/`` 路径下有一个文件夹（其名字形如
``28f7427e-5558-4ffd-ae1a-51ec3042759a.client25386880`` ），
而且其内包含很多文件，用 ``cat`` 命令查看它们的内容时会看到有趣的输出。
这些文件描述如下，最有助于调试慢请求问题的文件可能是 ``mdsc`` 和 ``osdc`` 。

* bdi: 关于 Ceph 系统的 BDI 信息（脏块、已写入的等等）
* caps: 文件的 caps 数据结构计数，包括内存中的和用过的
* client_options: 倒出挂载 CephFS 时所用的选项
* dentry_lru: 倒出当前内存中的 CephFS dentry
* mdsc: 倒出当前发给 MDS 的请求
* mdsmap: 倒出当前的 MDSMap 时间结和所有 MDS
* mds_sessions: 倒出当前与 MDS 建立的会话
* monc: 倒出当前从监视器获取的各种映射图，以及其它“订阅”信息
* monmap: 倒出当前的监视器图和所有监视器
* osdc: 倒出当前发往 OSD 的操作（即文件数据的 IO ）
* osdmap: 倒出当前的 OSDMap 时间结、存储池、所有 OSD

如果数据存储池处于 NEARFULL 状态，那么内核 cephfs 客户端\
将会切换到同步写，此时会非常慢。

断线后又重新挂载的文件系统
==========================
.. Disconnected+Remounted FS

因为 CephFS 有个“一致性缓存”，如果你的网络连接中断时间较长，
客户端就会被系统强制断开，此时，内核客户端仍然傻站着（ in a bind ）：
它不能安全地写回脏数据，另外很多应用程序在 close() 时不能正确处理 IO 错误。
这个时候，内核客户端会重新挂载这个文件系统，
但是先前的文件系统 IO 也许能完成、也许不能，
这些情况下，你也许得重启客户端系统。

如果 dmesg 或者 kern.log 里出现了类似消息，说明你遇到的就是这种情况： ::

    Jul 20 08:14:38 teuthology kernel: [3677601.123718] ceph: mds0 closed our session
    Jul 20 08:14:38 teuthology kernel: [3677601.128019] ceph: mds0 reconnect start
    Jul 20 08:14:39 teuthology kernel: [3677602.093378] ceph: mds0 reconnect denied
    Jul 20 08:14:39 teuthology kernel: [3677602.098525] ceph:  dropping dirty+flushing Fw state for ffff8802dc150518 1099935956631
    Jul 20 08:14:39 teuthology kernel: [3677602.107145] ceph:  dropping dirty+flushing Fw state for ffff8801008e8518 1099935946707
    Jul 20 08:14:39 teuthology kernel: [3677602.196747] libceph: mds0 172.21.5.114:6812 socket closed (con state OPEN)
    Jul 20 08:14:40 teuthology kernel: [3677603.126214] libceph: mds0 172.21.5.114:6812 connection reset
    Jul 20 08:14:40 teuthology kernel: [3677603.132176] libceph: reset on mds0

这是正在改善的领域，内核将很快能够可靠地向正在进行的 IO 发送错误代码，
即便你的应用程序不能良好地应对这些情况。长远来看，
在不违背 POSIX 语义的情况下，我们希望可以重连和回收数据
（通常是其它客户端尚未访问、或修改的数据）。


挂载问题
========

Mount 5 Error
-------------

mount 5 错误通常是 MDS 服务器滞后或崩溃导致的。
要确保至少有一个 MDS 是启动且运行的，集群也要处于 ``active+healthy`` 状态。

Mount 12 Error
--------------

mount 12 错误显示 ``cannot allocate memory`` ，
常见于 :term:`Ceph 客户端`\ 和 :term:`Ceph 存储集群`\ 版本不匹配。
用以下命令检查版本： ::

	ceph -v

如果 Ceph 客户端版本落后于集群，试着升级它： ::

	sudo apt-get update && sudo apt-get install ceph-common 

你也许得卸载、清理和删除 ``ceph-common`` ，然后再重新安装，以确保安装的是最新版。


动态调试
========
.. Dynamic Debugging

你可以对 CephFS 模块开启动态调试。

请看： https://github.com/ceph/ceph/blob/master/src/script/kcon_all.sh


报告问题
========
.. Reporting Issues

如果你确信发现了问题，报告时请附带尽可能多的信息，特别是重要信息：

* 客户端和服务器所安装的 Ceph 版本；
* 你在用内核、还是用户空间客户端；
* 如果你在用内核客户端，是什么版本？
* 有多少个客户端在用？什么样的负载？
* 如果某个系统“卡住”了，它影响所有客户端呢还是只影响一个？
* 关于 Ceph 的健康状况消息；
* 崩溃时写入日志的回调栈。

如果你觉得自己发现了一个缺陷，请在\ `缺陷追踪器`_\ 提交。\
一般问题的话可以发邮件到 `ceph-users 邮件列表`_\ 询问。

.. _缺陷追踪器: http://tracker.ceph.com
.. _ceph-users 邮件列表:  http://lists.ceph.com/listinfo.cgi/ceph-users-ceph.com/

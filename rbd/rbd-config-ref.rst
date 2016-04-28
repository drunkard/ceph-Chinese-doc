=============
 librbd 选项
=============

详情见\ `块设备`_\ 。

缓存选项
========

.. sidebar:: 内核缓存

	Ceph 块设备的内核驱动可利用 Linux 页缓存来提升性能。

Ceph 块设备的用户空间实现（即 ``librbd`` ）不能利用 Linux 页缓存，所以它自己实现了\
内存缓存，名为“ RBD 缓存”。 RBD 缓存行为就像硬盘缓存一样端正。当 OS 发送了 barrier \
或 flush 请求时，所有脏数据都会写入 OSDs 。这意味着只要 VM 会正确地发送 flush 命令（即\
内核版本大于 2.6.32 ），使用回写缓存和常见物理硬盘一样安全。此缓存用最近最少使用\
（ Least Recently Used, LRU ）算法，而且在回写模式下它能合并相邻请求以提高吞吐量。

.. versionadded:: 0.46

Ceph 支持为 RBD 提供回写缓存。要启用此功能，在 ``ceph.conf`` 配置文件的 ``[client]`` \
段下添加 ``rbd cache = true`` 。 ``librbd`` 默认不会进行任何缓存。写和读都直接到\
达存储集群，而且只有当数据的所有副本都写入磁盘后写操作才会返回。启用缓存后，写操作\
会立即返回，除非未刷写的字节数大于 ``rbd cache max dirty`` 。这种情况下，写动作会触发\
回写机制并一直阻塞，直到足够多的字节数被刷写。

.. versionadded:: 0.47

Ceph 支持为 RBD 提供透写缓存。你可以设置缓存的大小，以及从回写缓存切换到透写缓存的\
目标和临界值。要启用透写模式，把 ``rbd cache max dirty`` 置为 0。这意味着只有当数据\
的所有副本都写入磁盘后写操作才会返回，但可能会直接从缓存中读取数据。缓存信息保存\
在客户端的内存中，每个 RBD 映像有其自己的缓存。对客户端来说缓存位于本地，所以如果\
有其他用户访问某个映像，不会存在缓存一致性的问题。打开缓存时，在 RBD 之上不能运行 \
GFS 或 OCFS 。

RBD 选项应该位于 ``ceph.conf`` 配置文件的 ``[client]`` 段下，可用选项有：


``rbd cache``

:描述: 允许为 RADOS 块设备（ RBD ）提供缓存。
:类型: Boolean
:是否必需: No
:默认值: ``true``


``rbd cache size``

:描述: RBD 缓存大小，单位是字节。
:类型: 64-bit Integer
:是否必需: No
:默认值: ``32 MiB``


``rbd cache max dirty``

:描述: 使缓存触发回写的 ``dirty`` 临界值，单位是字节。若为 ``0`` ，直接使用透写缓存。
:类型: 64-bit Integer
:是否必需: No
:约束条件: 必须小于 ``rbd cache size`` 。
:默认值: ``24 MiB``


``rbd cache target dirty``

:描述: 缓存开始向数据存储写回数据前的 ``dirty target`` 。不会阻塞到缓存的写动作。
:类型: 64-bit Integer
:是否必需: No
:约束条件: 必须小于 ``rbd cache max dirty``.
:默认值: ``16 MiB``


``rbd cache max dirty age``

:描述: 写回开始前，脏数据在缓存中的暂存时间。
:类型: Float
:是否必需: No
:默认值: ``1.0``

.. versionadded:: 0.60

``rbd cache writethrough until flush``

:描述: 开始进入透写模式，并且在收到首个 flush 请求后切换到回写模式。启用该项保\
       守但安全，以防 rbd 之上的虚拟机内核太老而不能发送 flush ，例如 Linux 2.6.32 \
       之前的 virtio 驱动。
       
:类型: Boolean
:是否必需: No
:默认值: ``true``

.. _块设备: ../../rbd/rbd/


预读选项
========

.. versionadded:: 0.86

RBD 支持预读或预取功能，以此优化小块的顺序读。此功能通常应该由访客操作系统\
（在虚拟机的情况下）处理，但是引导加载程序可能不会发出高效的读请求。\
如果停用缓存功能，预读也会自动被禁用。


``rbd readahead trigger requests``

:描述: 触发预读的顺序读请求数量。
:类型: Integer
:是否必需: No
:默认值: ``10``


``rbd readahead max bytes``

:描述: 预读请求的最大尺寸。如果是零，禁用预读。
:类型: 64-bit Integer
:是否必需: No
:默认值: ``512 KiB``


``rbd readahead disable after bytes``

:描述: 从 RBD 映像读取这么多字节后，预读功能将被禁用，直到关闭。这样访客操作\
       系统一旦启动后就可以接管预读了。设为 0 时仍开启预读。
       
:类型: 64-bit Integer
:是否必需: No
:默认值: ``50 MiB``

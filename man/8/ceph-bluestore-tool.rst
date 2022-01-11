:orphan:

===========================================
 ceph-bluestore-tool -- bluestore 管理工具
===========================================

.. program:: ceph-bluestore-tool

提纲
====

| **ceph-bluestore-tool** *command*
  [ --dev *device* ... ]
  [ -i *osd_id* ]
  [ --path *osd path* ]
  [ --out-dir *dir* ]
  [ --log-file | -l *filename* ]
  [ --deep ]
| **ceph-bluestore-tool** fsck|repair --path *osd path* [ --deep ]
| **ceph-bluestore-tool** qfsck       --path *osd path*
| **ceph-bluestore-tool** allocmap    --path *osd path*
| **ceph-bluestore-tool** restore_cfb --path *osd path*
| **ceph-bluestore-tool** show-label --dev *device* ...
| **ceph-bluestore-tool** prime-osd-dir --dev *device* --path *osd path*
| **ceph-bluestore-tool** bluefs-export --path *osd path* --out-dir *dir*
| **ceph-bluestore-tool** bluefs-bdev-new-wal --path *osd path* --dev-target *new-device*
| **ceph-bluestore-tool** bluefs-bdev-new-db --path *osd path* --dev-target *new-device*
| **ceph-bluestore-tool** bluefs-bdev-migrate --path *osd path* --dev-target *new-device* --devs-source *device1* [--devs-source *device2*]
| **ceph-bluestore-tool** free-dump|free-score --path *osd path* [ --allocator block/bluefs-wal/bluefs-db/bluefs-slow ]
| **ceph-bluestore-tool** reshard --path *osd path* --sharding *new sharding* [ --sharding-ctrl *control string* ]
| **ceph-bluestore-tool** show-sharding --path *osd path*


描述
====

**ceph-bluestore-tool** 工具可在 BlueStore 例程上执行\
底层管理操作。


命令
====

:command:`help`

   显示帮助

:command:`fsck` [ --deep ]

   对 BlueStore 元数据进行一致性检查。如果加了 *--deep* ，\
   还会读取所有对象数据并核对校验和。

:command:`repair`

   运行一致性检查，\ *并且*\ 修复所有可修复的错误。

:command:`qfsck`

   对 BlueStore 元数据进行一致性检查，比对分配器数据
   （有 RocksDB CFB 就用它、没有用分配信息文件）与 ONode 状态。

:command:`allocmap`

   进行与 qfsck 相同的检查，然后保存一个新的分配信息文件
   （此命令默认被禁用了，需要特意编译）。

:command:`restore_cfb`

   回退新 NCB 代码做出的更改（通过重启 Ceph 或运行 allocmap 命令）、
   并恢复 RocksDB B Column-Family (allocator-map) 。

:command:`bluefs-export`

   把 BlueFS 内容（即 RocksDB 文件）导出到一个输出目录。

:command:`bluefs-bdev-sizes` --path *osd path*

   打印出设备尺寸，即 BlueFS 所认为的尺寸。

:command:`bluefs-bdev-expand` --path *osd path*

   让 BlueFS 检查它的块设备尺寸，并且，如果发现它们扩大了，
   把那些额外空间也用起来。请注意，在空闲空间足够的前提下，
   只有 BlueFS 新建的文件才会被分配到首选块设备；
   而已经存在的、溢出到慢速设备上的文件会在 RocksDB 压缩时逐渐删除。
   换句话说，如果有数据溢出到了慢速设备上，
   它会随着时间的推移被挪到高速设备上。

:command:`bluefs-bdev-new-wal` --path *osd path* --dev-target *new-device*

   给 BlueFS 增加 WAL 设备，如果已有 WAL 设备此命令就会失败。

:command:`bluefs-bdev-new-db` --path *osd path* --dev-target *new-device*

   给 BlueFS 增加 DB 设备，如果已有 DB 设备此命令就会失败。
   
:command:`bluefs-bdev-migrate` --dev-target *new-device* --devs-source *device1* [--devs-source *device2*]

   把一个或多个源设备上的 BlueFS 数据移动到目标设备，
   成功后源设备（除了主要的那个）将被删除。
   目标设备可以是已加入集群的、或新设备。稍后，
   它将被加进 OSD ，以替换某一个源设备。
   遵循下面的替换规则（按优先级，匹配到即停止）：

      - 如果源列表中有 DB 卷——目标设备替换它；
      - 如果源列表中有 WAL 卷——目标设备替换它；
      - 如果源列表中只有慢速卷——操作不允许，
        要显式地用 new-db 、 new-wal 命令分配。

:command:`show-label` --dev *device* [...]

   出示设备标签。

:command:`free-dump` --path *osd path* [ --allocator block/bluefs-wal/bluefs-db/bluefs-slow ]

   展示分配器中的所有空闲区域。

:command:`free-score` --path *osd path* [ --allocator block/bluefs-wal/bluefs-db/bluefs-slow ]

   会收到一个 0-1 之间的数字，用于表示分配器中碎片的质量。
   0 表示所有空闲空间都在一个块中的情形； 1 表示最糟糕的碎片散布情形。

:command:`reshard` --path *osd path* --sharding *new sharding* [ --resharding-ctrl *control string* ]

   更改 BlueStore 内 RocksDB 的分片配置。
   分片建立在 RocksDB 列族基础之上。
   此选项方便你测试 *new sharding* 的性能，而无需重新部署 OSD 。
   重分片一般都耗时绵长，需要遍历整个 RocksDB 键名空间、
   并把其中某些挪到别的列族。
   ``--resharding-ctrl`` 选项便于你对重分片过程进行性能控制。
   中断重分片会妨碍 OSD 的正常运行；中断重分片不会损坏数据；\
   而且随时可以继续之前的重分片，或者选用其它分片方案，
   包括回退到最初的那个。

:command:`show-sharding` --path *osd path*

   罗列出当前正被应用到 BlueStore 的 RocksDB 的分片。


选项
====
.. Options

.. option:: --dev *device*

   把设备 *device* 加进涉及到的设备列表中。

.. option:: -i *osd_id*

   以 OSD *osd_id* 的身份进行操作。
   连接到监视器以实现 OSD 的特定选项。
   如果监视器不可用，加上 --no-mon-config 选项\
   直接从 ceph.conf 读取。

.. option:: --devs-source *device*

   把设备 *device* 加进迁移操作涉及到的源设备列表中。

.. option:: --dev-target *device*

   指定用于迁移操作或新增设备的目标设备 *device* ，以便新增
   DB/WAL 。

.. option:: --path *osd path*

   指定一个 osd 路径。大多数情况下，设备列表都是从 *osd path*
   里的符号链接推断出来的。通常比显式地用 --dev 指定几个设备要简单些。

.. option:: --out-dir *dir*

   bluefs-export 的输出目录。

.. option:: -l, --log-file *log file*

   记录日志的文件

.. option:: --log-level *num*

   调试日志级别。默认是 30 （极其详细）， 20 是非常详细，
   10 是详细， 而 1 是不怎么详细。

.. option:: --deep

   深度洗刷、修复（读取并校验对象数据，而不只是元数据）

.. option:: --allocator *name*

   适用于 *free-dump* 和 *free-score* 操作。选择分配器。

.. option:: --resharding-ctrl *control string*

   提供了对重分片过程的控制手段，指示多久刷一次 RocksDB 递归器，\
   以及提交给 RocksDB 的批次应该是多大。
   选项格式为：
   <iterator_refresh_bytes>/<iterator_refresh_keys>/<batch_commit_bytes>/<batch_commit_keys> 。
   默认值： 10000000/10000/1000000/1000


ceph.conf 附加选项
==================
.. Additional ceph.conf options

OSD 接受的任何配置选项都可以传给 **ceph-bluestore-tool** 。
当不能访问监视器、 ceph.conf ， ``-i`` 选项也不能用时，
用此方法提供必要的配置选项很有用。


设备标签
========
.. Device labels


每个 BlueStore 块设备都有一个单独的块标签，位于设备起始处。
你可以用此命令查看标签内容： ::

  ceph-bluestore-tool show-label --dev *device*

主设备会有很多元数据，包括\
以前在 OSD 数据目录下存储的小文件内的信息。
辅助设备（ db 和 wal ）只含有必需的最少字段
（ OSD UUID 、尺寸、设备类型、创建时间）。


OSD 目录启动
============
.. OSD directory priming

你可以给一个 OSD 数据目录生成些数据，
借此才能用 *prime-osd-dir* 启动 BlueStore OSD ： ::

  ceph-bluestore-tool prime-osd-dir --dev *main device* --path /var/lib/ceph/osd/ceph-*id*


拯救 BlueFS 日志
================
.. BlueFS log rescue

有些版本的 BlueStore ，它的 BlueFS 日志会增长得非常巨大 ——
以至于 OSD 都没法启动了。
如果启动用了很长时间却在 _replay 函数里失败了，那就是遇到了这种状态。

这情况可以这样修复： ::

    ceph-bluestore-tool fsck --path *osd path* --bluefs_replay_recovery=true

建议您首先检查一下拯救过程是否会成功： ::

    ceph-bluestore-tool fsck --path *osd path* \
        --bluefs_replay_recovery=true --bluefs_replay_recovery_disable_compact=true

如果上面的 fsck 成功了，就可以施行修复过程。


使用范围
========

**ceph-bluestore-tool** 是 Ceph 的一部分，这是个伸缩力强、\
开源、分布式的存储系统，更多信息参见 https://docs.ceph.com 。


参考
====

:doc:`ceph-osd <ceph-osd>`\(8)

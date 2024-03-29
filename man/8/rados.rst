:orphan:

=============================
 rados -- rados 对象存储工具
=============================

.. program:: rados

提纲
====

| **rados** [ *options* ] [ *command* ]


描述
====

**rados** 工具可操纵 Ceph 对象存储集群（ RADOS ），是 Ceph
分布式存储系统的一部分。


全局选项
========

.. option:: --object-locator object_locator

   设置操作的 object_locator （对象定位器？）。

.. option:: -p pool, --pool pool

   操作指定的存储池。大多数命令都得指定此参数。

.. option:: --target-pool pool

   按名字指定目标存储池。

.. option:: --pgid

   作为 ``--pool`` 的外加参数， ``--pgid`` 是让用户指定 PG id
   的，然后命令就径直导向此 PG 。加上这个选项，用户就可以把\
   某些命令（如 ``ls`` ）的范围限定于指定 PG 。

.. option:: -N namespace, --namespace namespace

   指定要给对象用的 rados 命名空间。

.. option:: --all

   ls 时加此选项来罗列所有命名空间里的对象。
   放入 CEPH_ARGS 环境变量可以成为默认值。

.. option:: --default

   ls 时加此选项来罗列默认命名空间里的对象。
   --all 在环境变量里时，优先级高于 --all 。

.. option:: -s snap, --snap snap

   从指定的存储池快照读出。适用于所有与存储池相关的读操作。

.. option:: --create

   创建指定的存储池或目录。

.. option:: -i infile

   指定输入文件，其内容将作为此命令的载荷发送给监视器集群。
   仅适用于部分监视器命令。

.. option:: -m monaddress[:port]

   连接指定监视器（而非通过 ceph.conf 查找）。

.. option:: -b block_size

   设置块尺寸，适用于 put/get/append 操作、及写入压力测试。

.. option:: --striper

   使用 rados 的条带化 API 而非默认的，支持的操作有 stat 、
   get 、 put 、 append 、 truncate 、 rm 、 ls 以及所有与
   xattr 相关的操作。

.. option:: -O object_size, --object-size object_size

   在做写入压力测试的时候，设置 put/get 操作的对象尺寸。

.. option:: --max-objects

   设置写压力测试的最大对象数。

.. option:: --lock-cookie locker-cookie

   申请咨询锁（ lock get 命令）时将设置锁 cookie 。
   如果此 cookie 不是空的，那么释放锁时必须\
   给 lock break 命令加上这个选项，为的是找到正确的锁。

.. option:: --target-locator

   与 cp 命令一起用，可指定新对象的定位符。

.. option:: --target-nspace

   与 cp 命令一起用，可指定新对象的命名空间。


压力测试选项
============
.. Bench options

.. option:: -t N, --concurrent-ios=N

   设置并发 I/O 操作的数量。

.. option:: --show-time

   输出时用日期、时间作前缀。

.. option:: --no-verify

   不要校验读对象的内容。

.. option:: --write-object

   向对象们写入内容。

.. option:: --write-omap

   向 omap 写入内容。

.. option:: --write-xattr

   向扩展属性写入内容。


Load gen 选项
=============
.. Load gen options

.. option:: --num-objects

   对象总量。

.. option:: --min-object-size

   最小对象尺寸。

.. option:: --max-object-size

   最大对象尺寸。

.. option:: --min-op-len

   操作的最小 IO 尺寸。

.. option:: --max-op-len

   操作的最大 IO 尺寸。

.. option:: --max-ops

   最大操作量。

.. option:: --max-backlog

   最大积压尺寸。

.. option:: --read-percent

   读操作的百分比。

.. option:: --target-throughput

   目标吞吐量（按字节）。

.. option:: --run-length

   总时长（按秒）。

.. option:: --offset-align

   对齐随机操作偏移量的边界。


缓存存储池选项
==============
.. Cache pools options

.. option:: --with-clones

   刷回或赶回对象时包括克隆品。


OMAP 选项
=========

.. option:: --omap-key-file file

   从一个文件读取 omap 键名。


通用选项
========
.. Generic options

.. option:: -c FILE, --conf FILE

   从指定配置文件读取配置。

.. option:: --id ID

   设置自己名字的 ID 部分。

.. option:: -n TYPE.ID, --name TYPE.ID

   设置 cephx 用户名。

.. option:: --cluster NAME

   设置集群名（默认： ceph ）

.. option:: --setuser USER

   给指定用户或 UID 设置 uid （并给用户的 gid 设置 gid）

.. option:: --setgroup GROUP

   给指定用户组或 GID 设置 gid 。

.. option:: --version

   显示版本并退出。


全局命令
========

:command:`lspools`
  罗列对象存储池

:command:`df`
  显示利用率统计信息，显示整个系统以及各存储池的磁盘空间（字节数）、对象数量。

:command:`list-inconsistent-pg` *pool*
  罗列指定存储池内不一致的归置组。

:command:`list-inconsistent-obj` *pgid*
  罗列指定 PG 内不一致的对象。

:command:`list-inconsistent-snapset` *pgid*
  罗列指定 PG 内不一致的 snapset 。


特定于存储池的命令
==================

:command:`get` *name* *outfile*
  从集群读出名为 name 的对象、并把它写入 outfile 。

:command:`put` *name* *infile* [--offset offset]
  把 infile 的内容写入集群内名为 name 的对象、从偏移量 *offset* （默认为 0 ）处写起。
  **警告：**\ put 命令创建的是单个 RADOS 对象，尺寸和你的输入文件完全一样。
  你如果不能保证对象的尺寸合理且一致，最好改用 RGW/S3 、 CephFS 或 RBD ，
  否则实际运行情况和你期望的会有出入。

:command:`append` *name* *infile*
  把 infile 的内容追加给集群内名为 name 的对象。

:command:`rm` [--force-full] *name* ...
  删除名为 name 的对象。集群被标记为 full 时需加上 ``--force-full`` 选项。

:command:`listwatchers` *name*
  罗列此对象名的关注者。

:command:`ls` *outfile*
  罗列指定存储池内的对象，并把名单写入 outfile 文件。

:command:`lssnap`
  罗列指定存储池的快照。

:command:`clonedata` *srcname* *dstname* --object-locator *key*
  从 *srcname* 到 *dstname* 克隆对象字节数据，两个对象都必须以定位符关键词 *key*
  （通常是 *srcname* 或 *dstname* ）存储。不会复制或克隆对象属性和 omap 键。

:command:`mksnap` *foo*
  创建存储池快照，名为 *foo* 。

:command:`rmsnap` *foo*
  删除名为 *foo* 的存储池快照。

:command:`bench` *seconds* *mode* [ -b *objsize* ] [ -t *threads* ]
  压力测试 *seconds* 秒。 *mode* 可以是 *write* 、 *seq* 或 \
  *rand* 。 *seq* 和 *rand* 分别是顺序读、随机读压力测试，要想\
  做读压力测试，先得加 *--no-cleanup* 选项做一次写压力测试。\
  默认对象尺寸是 4 MB ，默认的模拟线程数（并行写操作）为 16 。\
  *--run-name <label>* 选项适用于多个客户端并行测试以评估最大\
  载荷。 *<label>* 表示任意对象名，默认为 \
  "benchmark_last_metadata" ，且作为“读”和“写”操作的底层对象名。
  注： -b *objsize* 仅适用于 *write* 模式。
  注： *write* 和 *seq* 必须运行在相同的主机上，否则 *write* \
  所创建对象的名字不能被 *seq* 所接受。

:command:`cleanup` [ --run-name *run_name* ] [ --prefix *prefix* ]
  清理先前的基准测试操作。
  注意：默认的 run-name 是 ``benchmark_last_metadata``

:command:`listxattr` *name*
  罗列一个对象的所有扩展属性。

:command:`getxattr` *name* *attr*
  获取某一对象的扩展属性 *attr* 的值。

:command:`setxattr` *name* *attr* *value*
  设置某一对象的扩展属性，把扩展属性 *attr* 的值设置为 *value* 。

:command:`rmxattr` *name* *attr*
  删除某一对象的扩展属性 *attr* 。

:command:`stat` *name*
  获取指定对象的 stat 信息（即 mtime 、 size ）。

:command:`stat2` *name*
  获取指定对象的 stat 信息（与 stat 类似，但是时间精度更高）。

:command:`listomapkeys` *name*
  罗列 name 对象的对象映射图内存储的所有键。

:command:`listomapvals` *name*
  罗列 name 对象的对象映射图内存储的所有键值对。值会被转储为\
  十六进制。

:command:`getomapval` [ --omap-key-file *file* ] *name* *key* [ *out-file* ]
  把 name 对象的对象映射图内 key 的值转储为十六进制。
  如果没有提供可选参数 *out-file* ，
  这个值就会写到标准输出。

:command:`setomapval` [ --omap-key-file *file* ] *name* *key* [ *value* ]
  设置 name 对象的对象映射图内 key 的值。
  如果没加可选的 *value* 参数，
  就从标准输入读取。

:command:`rmomapkey` [ --omap-key-file *file* ] *name* *key*
  从 name 对象的对象映射图内删除 key 。

:command:`getomapheader` *name*
  把 name 对象的对象映射图头部转储为十六进制。

:command:`setomapheader` *name* *value*
  设置 name 对象的对象映射图头部的值。

:command:`export` *filename*
  把存储池内容序列化为一个文件或标准输出。

:command:`import` [--dry-run] [--no-overwrite] < filename | - >
  把一个文件或标准输入的内容载入存储池。


实例
====

查看集群使用情况： ::

       rados df

获取存储池 foo 内的对象列表，并显示在标准输出： ::

       rados -p foo ls -

获取 PG 0.6 内的一些对象： ::

       rados --pgid 0.6 ls

写入一个对象： ::

       rados -p foo put myobject blah.txt

创建一个快照： ::

       rados -p foo mksnap mysnap

删除对象： ::

       rados -p foo rm myobject

读取对象先前的快照版内容： ::

       rados -p foo -s mysnap get myobject blah.txt.old

罗列 PG 0.6 内不一致的对象： ::

       rados list-inconsistent-obj 0.6 --format=json-pretty


使用范围
========

**rados** 是 Ceph 的一部分，这是个伸缩力强、开源、分布式的存储系统，\
更多信息参见 https://docs.ceph.com 。


参考
====

:doc:`ceph <ceph>`\(8)

:orphan:

.. _osdmaptool:

=======================================
 osdmaptool -- ceph osd 运行图操作工具
=======================================

.. program:: osdmaptool

提纲
====

| **osdmaptool** *mapfilename* [--print] [--createsimple *numosd*
  [--pgbits *bitsperosd* ] ] [--clobber]
| **osdmaptool** *mapfilename* [--import-crush *crushmap*]
| **osdmaptool** *mapfilename* [--export-crush *crushmap*]
| **osdmaptool** *mapfilename* [--upmap *file*] [--upmap-max *max-optimizations*]
  [--upmap-deviation *max-deviation*] [--upmap-pool *poolname*]
  [--save] [--upmap-active]
| **osdmaptool** *mapfilename* [--upmap-cleanup] [--upmap *file*]


描述
====

**osdmaptool** 工具可用于创建、查看、修改 Ceph 分布式存储系统\
的 OSD 集群运行图。很显然，它可用于提取内嵌的 CRUSH 图，或者\
导入新 CRUSH 图。它也能模拟 upmap 均衡器模式，这样你就能\
切身感受到，要均衡 PG 还需要什么。


选项
====

.. option:: --print

   修改完成后，打印此运行图的一份纯文本转储。

.. option:: --dump <format>

   <format> 为 plain 时以纯文本方式显示运行图，
   若不支持指定格式就默认为 json 。
   这是 print 选项的替代品。

.. option:: --clobber

   修改时允许 osdmaptool 覆盖 mapfilename 。

.. option:: --import-crush mapfile

   从 mapfile 载入 CRUSH 图并把它嵌入 OSD 图。

.. option:: --export-crush mapfile

   从 OSD 图提取出 CRUSH 图并写入 mapfile 。

.. option:: --createsimple numosd [--pg-bits bitsperosd] [--pgp-bits bits]

   创建有 numosd 个设备的相对通用的 OSD 图。
   若指定了 --pg-bits 选项，每个 OSD 的归置组数量将是 bitsperosd 个位偏移。
   也就是 pg_num 属性将被设置为 numosd 数值再右移 bitsperosd 位。
   若指定了 --pgp-bits 选项，
   pgp_num 属性将被设置为 numosd 数值再右移 bits 位。

   <译者注>: pgp_num map attribute: 意为 osd map 之中的 pgp_num 属性

.. option:: --create-from-conf

   按默认配置创建一份 OSD 图。

.. option:: --test-map-pgs [--pool poolid] [--range-first <first> --range-last <last>]

   打印出归置组到 OSD 的映射关系。
   如果指定了范围，那它就依次递归
   osdmaptool 参数所指目录内 first 到 last 之间的。
   例如： **osdmaptool --test-map-pgs --range-first 0 --range-last 2 osdmap_dir**.
   它会递归 osdmap_dir 内名为 0 、 1 、 2 的文件。

.. option:: --test-map-pgs-dump [--pool poolid] [--range-first <first> --range-last <last>]

   打印出所有归置组及其与 OSD 映射关系的汇总。如果指定了范围，\
   那它就依次递归 osdmaptool 参数所指目录内 first 到 last 之间\
   的。
   例如： **osdmaptool --test-map-pgs-dump --range-first 0 --range-last 2 osdmap_dir**.
   它会递归 osdmap_dir 内名为 0 、 1 、 2 的文件。

.. option:: --test-map-pgs-dump-all [--pool poolid] [--range-first <first> --range-last <last>]

   会打印出所有归置组及其到所有 OSD 映射关系\
   的汇总。
   如果指定了范围， osdmaptool 会根据参数指定的目录\
   从头到尾挨个迭代。
   例如： **osdmaptool --test-map-pgs-dump-all --range-first 0 --range-last 2 osdmap_dir** ，
   此命令会迭代 osdmap_dir 里名为 0,1,2 的文件们。

.. option:: --test-random

   把归置组随机地映射到各个 OSD 。

.. option:: --test-map-pg <pgid>

   把某个特定的归置组（用 pgid 指定的）映射到多个 OSD 。

.. option:: --test-map-object <objectname> [--pool <poolid>]

   把某个特定的归置组（由对象名 objectname 确定）映射到一组 OSD 。

.. option:: --test-crush [--range-first <first> --range-last <last>]

   把各归置组映射到正常工作的 OSD 们。
   如果指定了范围，根据 osdmaptool 参数里指定的、
   从目录里的第一个到最后一个挨个迭代。
   例如： **osdmaptool --test-crush --range-first 0 --range-last 2 osdmap_dir**.
   此命令会迭代 osdmap_dir 里名为 0,1,2 的文件。

.. option:: --mark-up-in

   把 OSD 们标记为 up 且 in （但不持久化）。

.. option:: --mark-out

   把 OSD 们标记为 out （但不持久化）。

.. option:: --mark-up <osdid>

   把 OSD 们标记为 up （但不持久化）。

.. option:: --mark-in <osdid>

   把 OSD 们标记为 in （但不持久化）。

.. option:: --tree

   按分级树显示此运行图。

.. option:: --clear-temp

   清空 pg_temp 和 primary_temp 变量。

.. option:: --clean-temps

   清空 pg_temps 。

.. option:: --health

   转储出健康检查信息。

.. option:: --with-default-pool

   创建运行图时包含默认的存储池。

.. option:: --upmap-cleanup <file>

   清理 pg_upmap[_items] 条目，把命令写入 <file> [默认: - 表示写入 stdout]

.. option:: --upmap <file>

   计算 pg upmap 条目，以均衡 pg 布局，把命令写入 <file> [默认: - 表示写入 stdout]

.. option:: --upmap-max <max-optimizations>

   设置要计算的最大 upmap 条目数 [默认: 10]

.. option:: --upmap-deviation <max-deviation>

   与目标的最大偏差 [默认: 5]

.. option:: --upmap-pool <poolname>

   把 upmap 均衡限制在指定存储池之内，此选项可以重用多次以指定多个存储池。

.. option:: --upmap-active

   像一个活跃的均衡器一样运行，不停地应用变更直到均衡完成。

.. option:: --adjust-crush-weight <osdid:weight>[,<osdid:weight>,<...>]

   更改 <osdid> 的 CRUSH 权重。

.. option:: --save

   写入更改过（ upmap 或调整了 crush ）的 osdmap


实例
====

要创建个有 16 个设备的简易图： ::

        osdmaptool --createsimple 16 osdmap --clobber

查看结果： ::

        osdmaptool --print osdmap

要查看存储池 1 的归置组映射情况： ::

        osdmaptool --test-map-pgs-dump rbd --pool 1

        pool 1 pg_num 8
        1.0     [0,2,1] 0
        1.1     [2,0,1] 2
        1.2     [0,1,2] 0
        1.3     [2,0,1] 2
        1.4     [0,2,1] 0
        1.5     [0,2,1] 0
        1.6     [0,1,2] 0
        1.7     [1,0,2] 1
        #osd    count   first   primary c wt    wt
        osd.0   8       5       5       1       1
        osd.1   8       1       1       1       1
        osd.2   8       2       2       1       1
         in 3
         avg 8 stddev 0 (0x) (expected 2.3094 0.288675x))
         min osd.0 8
         max osd.0 8
        size 0  0
        size 1  0
        size 2  0
        size 3  8

在上面的输出结果中，
 #. 存储池 1 有 8 个归置组，及后面的两张表：
 #. 一张表是归置组。每行表示一个归置组，列分别是：

    * 归置组 id ，
    * acting set ，和
    * 主 OSD 。
 #. 一张表是所有的 OSD 。每行表示一个 OSD ，列分别是：

    * 映射到此 OSD 的归置组数量，
    * 此 OSD 是它所属 acting set 的第一个，这样的归置组数量，
    * 此 OSD 是归置组的主 OSD ，这样的归置组数量，
    * 此 OSD 的 CRUSH 权重，还有
    * 此 OSD 的权重。
 #. 再看是托管着归置组的 OSD 数量，是 3 个。接下来是

    * avarge, stddev （标准偏差）, stddev/average, expected stddev, expected stddev / average
    * min 和 max
 #. 映射到 n 个 OSD 的归置组数量。在本例中，全部的 8 个归置组\
    都映射到了 3 个不同的 OSD 。

在一个均衡得不太好的集群中，我们也许会看到类似如下的归置组分布\
统计，其标准偏差是 1.41421 : ::

        #osd    count   first   primary c wt    wt
        osd.0   8       5       5       1       1
        osd.1   8       1       1       1       1
        osd.2   8       2       2       1       1

        #osd    count   first    primary c wt    wt
        osd.0   33      9        9       0.0145874     1
        osd.1   34      14       14      0.0145874     1
        osd.2   31      7        7       0.0145874     1
        osd.3   31      13       13      0.0145874     1
        osd.4   30      14       14      0.0145874     1
        osd.5   33      7        7       0.0145874     1
         in 6
         avg 32 stddev 1.41421 (0.0441942x) (expected 5.16398 0.161374x))
         min osd.4 30
         max osd.1 34
        size 00
        size 10
        size 20
        size 364

模拟 upmap 模式下的动态均衡器： ::

    osdmaptool --upmap upmaps.out --upmap-active --upmap-deviation 6 --upmap-max 11 osdmap

    osdmaptool: osdmap file 'osdmap'
    writing upmap command output to: upmaps.out
    checking for upmap cleanups
    upmap, max-count 11, max deviation 6
    pools movies photos metadata data
    prepared 11/11 changes
    Time elapsed 0.00310404 secs
    pools movies photos metadata data
    prepared 11/11 changes
    Time elapsed 0.00283402 secs
    pools data metadata movies photos
    prepared 11/11 changes
    Time elapsed 0.003122 secs
    pools photos metadata data movies
    prepared 11/11 changes
    Time elapsed 0.00324372 secs
    pools movies metadata data photos
    prepared 1/11 changes
    Time elapsed 0.00222609 secs
    pools data movies photos metadata
    prepared 0/11 changes
    Time elapsed 0.00209916 secs
    Unable to find further optimization, or distribution is already perfect
    osd.0 pgs 41
    osd.1 pgs 42
    osd.2 pgs 42
    osd.3 pgs 41
    osd.4 pgs 46
    osd.5 pgs 39
    osd.6 pgs 39
    osd.7 pgs 43
    osd.8 pgs 41
    osd.9 pgs 46
    osd.10 pgs 46
    osd.11 pgs 46
    osd.12 pgs 46
    osd.13 pgs 41
    osd.14 pgs 40
    osd.15 pgs 40
    osd.16 pgs 39
    osd.17 pgs 46
    osd.18 pgs 46
    osd.19 pgs 39
    osd.20 pgs 42
    Total time elapsed 0.0167765 secs, 5 rounds



使用范围
========

**osdmaptool** 是 Ceph 的一部分，这是个伸缩力强、开源、
分布式的存储系统，更多信息参见 https://docs.ceph.com 。


参考
====

:doc:`ceph <ceph>`\(8),
:doc:`crushtool <crushtool>`\(8),

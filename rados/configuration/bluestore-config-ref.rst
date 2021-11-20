====================
 BlueStore 配置参考
====================
.. BlueStore Config Reference

设备
====
.. Devices

BlueStore 可管理一个、两个、或（某些情况下）三个存储设备。

In the simplest case, BlueStore consumes a single (primary) storage device.
The storage device is normally used as a whole, occupying the full device that
is managed directly by BlueStore. This *primary device* is normally identified
by a ``block`` symlink in the data directory.

The data directory is a ``tmpfs`` mount which gets populated (at boot time, or
when ``ceph-volume`` activates it) with all the common OSD files that hold
information about the OSD, like: its identifier, which cluster it belongs to,
and its private keyring.

It is also possible to deploy BlueStore across one or two additional devices:

* A *write-ahead log (WAL) device* (identified as ``block.wal`` in the data directory) can be
  used for BlueStore's internal journal or write-ahead log. It is only useful
  to use a WAL device if the device is faster than the primary device (e.g.,
  when it is on an SSD and the primary device is an HDD).
* A *DB device* (identified as ``block.db`` in the data directory) can be used
  for storing BlueStore's internal metadata.  BlueStore (or rather, the
  embedded RocksDB) will put as much metadata as it can on the DB device to
  improve performance.  If the DB device fills up, metadata will spill back
  onto the primary device (where it would have been otherwise).  Again, it is
  only helpful to provision a DB device if it is faster than the primary
  device.

If there is only a small amount of fast storage available (e.g., less
than a gigabyte), we recommend using it as a WAL device.  If there is
more, provisioning a DB device makes more sense.  The BlueStore
journal will always be placed on the fastest device available, so
using a DB device will provide the same benefit that the WAL device
would while *also* allowing additional metadata to be stored there (if
it will fit).  This means that if a DB device is specified but an explicit
WAL device is not, the WAL will be implicitly colocated with the DB on the faster
device.

A single-device (colocated) BlueStore OSD can be provisioned with::

  ceph-volume lvm prepare --bluestore --data <device>

To specify a WAL device and/or DB device, ::

  ceph-volume lvm prepare --bluestore --data <device> --block.wal <wal-device> --block.db <db-device>

.. note:: --data 可以是以 *vg/lv* 方式表达的逻辑卷。其他设备\
   可以是现有的逻辑卷或 GPT 分区。

存储配置策略
------------
.. Provisioning strategies

虽然有多种途径部署后端为 BlueStore 的 OSD （不像 Filestore
只有一种），但是这里的两种常见用法有助于澄清部署策略。

.. _bluestore-single-type-device-config:

**block (data) only**
^^^^^^^^^^^^^^^^^^^^^
If all devices are the same type, for example all rotational drives, and
there are no fast devices to use for metadata, it makes sense to specifiy the
block device only and to not separate ``block.db`` or ``block.wal``. The
:ref:`ceph-volume-lvm` command for a single ``/dev/sda`` device looks like::

    ceph-volume lvm create --bluestore --data /dev/sda

If logical volumes have already been created for each device, (a single LV
using 100% of the device), then the :ref:`ceph-volume-lvm` call for an LV named
``ceph-vg/block-lv`` would look like::

    ceph-volume lvm create --bluestore --data ceph-vg/block-lv

.. _bluestore-mixed-device-config:

**block and block.db**
^^^^^^^^^^^^^^^^^^^^^^
If you have a mix of fast and slow devices (SSD / NVMe and rotational),
it is recommended to place ``block.db`` on the faster device while ``block``
(data) lives on the slower (spinning drive).

You must create these volume groups and logical volumes manually as 
the ``ceph-volume`` tool is currently not able to do so automatically.

For the below example, let us assume four rotational (``sda``, ``sdb``, ``sdc``, and ``sdd``)
and one (fast) solid state drive (``sdx``). First create the volume groups::

    $ vgcreate ceph-block-0 /dev/sda
    $ vgcreate ceph-block-1 /dev/sdb
    $ vgcreate ceph-block-2 /dev/sdc
    $ vgcreate ceph-block-3 /dev/sdd

Now create the logical volumes for ``block``::

    $ lvcreate -l 100%FREE -n block-0 ceph-block-0
    $ lvcreate -l 100%FREE -n block-1 ceph-block-1
    $ lvcreate -l 100%FREE -n block-2 ceph-block-2
    $ lvcreate -l 100%FREE -n block-3 ceph-block-3

We are creating 4 OSDs for the four slow spinning devices, so assuming a 200GB
SSD in ``/dev/sdx`` we will create 4 logical volumes, each of 50GB::

    $ vgcreate ceph-db-0 /dev/sdx
    $ lvcreate -L 50GB -n db-0 ceph-db-0
    $ lvcreate -L 50GB -n db-1 ceph-db-0
    $ lvcreate -L 50GB -n db-2 ceph-db-0
    $ lvcreate -L 50GB -n db-3 ceph-db-0

Finally, create the 4 OSDs with ``ceph-volume``::

    $ ceph-volume lvm create --bluestore --data ceph-block-0/block-0 --block.db ceph-db-0/db-0
    $ ceph-volume lvm create --bluestore --data ceph-block-1/block-1 --block.db ceph-db-0/db-1
    $ ceph-volume lvm create --bluestore --data ceph-block-2/block-2 --block.db ceph-db-0/db-2
    $ ceph-volume lvm create --bluestore --data ceph-block-3/block-3 --block.db ceph-db-0/db-3

These operations should end up creating four OSDs, with ``block`` on the slower
rotational drives with a 50 GB logical volume (DB) for each on the solid state
drive.

调整尺寸
========
.. Sizing

When using a :ref:`mixed spinning and solid drive setup
<bluestore-mixed-device-config>` it is important to make a large enough
``block.db`` logical volume for BlueStore. Generally, ``block.db`` should have
*as large as possible* logical volumes.

The general recommendation is to have ``block.db`` size in between 1% to 4%
of ``block`` size. For RGW workloads, it is recommended that the ``block.db``
size isn't smaller than 4% of ``block``, because RGW heavily uses it to store
metadata (omap keys). For example, if the ``block`` size is 1TB, then ``block.db`` shouldn't
be less than 40GB. For RBD workloads, 1% to 2% of ``block`` size is usually enough.

In older releases, internal level sizes mean that the DB can fully utilize only
specific partition / LV sizes that correspond to sums of L0, L0+L1, L1+L2,
etc. sizes, which with default settings means roughly 3 GB, 30 GB, 300 GB, and
so forth.  Most deployments will not substantially benefit from sizing to
accomodate L3 and higher, though DB compaction can be facilitated by doubling
these figures to 6GB, 60GB, and 600GB.

Improvements in releases beginning with Nautilus 14.2.12 and Octopus 15.2.6
enable better utilization of arbitrary DB device sizes, and the Pacific
release brings experimental dynamic level support.  Users of older releases may
thus wish to plan ahead by provisioning larger DB devices today so that their
benefits may be realized with future upgrades.

When *not* using a mix of fast and slow devices, it isn't required to create
separate logical volumes for ``block.db`` (or ``block.wal``). BlueStore will
automatically colocate these within the space of ``block``.


自动调整缓存尺寸
================
.. Automatic Cache Sizing

BlueStore can be configured to automatically resize its caches when TCMalloc
is configured as the memory allocator and the ``bluestore_cache_autotune``
setting is enabled.  This option is currently enabled by default.  BlueStore
will attempt to keep OSD heap memory usage under a designated target size via
the ``osd_memory_target`` configuration option.  This is a best effort
algorithm and caches will not shrink smaller than the amount specified by
``osd_memory_cache_min``.  Cache ratios will be chosen based on a hierarchy
of priorities.  If priority information is not available, the
``bluestore_cache_meta_ratio`` and ``bluestore_cache_kv_ratio`` options are
used as fallbacks.

.. confval:: bluestore_cache_autotune
.. confval:: osd_memory_target
.. confval:: bluestore_cache_autotune_interval
.. confval:: osd_memory_base
.. confval:: osd_memory_expected_fragmentation
.. confval:: osd_memory_cache_min
.. confval:: osd_memory_cache_resize_interval


手动调整缓存尺寸
================
.. Manual Cache Sizing

The amount of memory consumed by each OSD for BlueStore caches is
determined by the ``bluestore_cache_size`` configuration option.  If
that config option is not set (i.e., remains at 0), there is a
different default value that is used depending on whether an HDD or
SSD is used for the primary device (set by the
``bluestore_cache_size_ssd`` and ``bluestore_cache_size_hdd`` config
options).

BlueStore and the rest of the Ceph OSD daemon do the best they can
to work within this memory budget.  Note that on top of the configured
cache size, there is also memory consumed by the OSD itself, and
some additional utilization due to memory fragmentation and other
allocator overhead.

The configured cache memory budget can be used in a few different ways:

* Key/Value metadata (i.e., RocksDB's internal cache)
* BlueStore metadata
* BlueStore data (i.e., recently read or written object data)

Cache memory usage is governed by the following options:
``bluestore_cache_meta_ratio`` and ``bluestore_cache_kv_ratio``.
The fraction of the cache devoted to data
is governed by the effective bluestore cache size (depending on
``bluestore_cache_size[_ssd|_hdd]`` settings and the device class of the primary
device) as well as the meta and kv ratios.
The data fraction can be calculated by
``<effective_cache_size> * (1 - bluestore_cache_meta_ratio - bluestore_cache_kv_ratio)``

.. confval:: bluestore_cache_size
.. confval:: bluestore_cache_size_hdd
.. confval:: bluestore_cache_size_ssd
.. confval:: bluestore_cache_meta_ratio
.. confval:: bluestore_cache_kv_ratio


校验和
======
.. Checksums

BlueStore checksums all metadata and data written to disk.  Metadata
checksumming is handled by RocksDB and uses `crc32c`. Data
checksumming is done by BlueStore and can make use of `crc32c`,
`xxhash32`, or `xxhash64`.  The default is `crc32c` and should be
suitable for most purposes.

Full data checksumming does increase the amount of metadata that
BlueStore must store and manage.  When possible, e.g., when clients
hint that data is written and read sequentially, BlueStore will
checksum larger blocks, but in many cases it must store a checksum
value (usually 4 bytes) for every 4 kilobyte block of data.

It is possible to use a smaller checksum value by truncating the
checksum to two or one byte, reducing the metadata overhead.  The
trade-off is that the probability that a random error will not be
detected is higher with a smaller checksum, going from about one in
four billion with a 32-bit (4 byte) checksum to one in 65,536 for a
16-bit (2 byte) checksum or one in 256 for an 8-bit (1 byte) checksum.
The smaller checksum values can be used by selecting `crc32c_16` or
`crc32c_8` as the checksum algorithm.

The *checksum algorithm* can be set either via a per-pool
``csum_type`` property or the global config option.  For example, ::

  ceph osd pool set <pool-name> csum_type <algorithm>

.. confval:: bluestore_csum_type


内联压缩
========
.. Inline Compression

BlueStore 支持内联压缩，可用 `snappy` 、 `zlib` 或 `lz4`
压缩算法。请注意， `lz4` 压缩插件不在官方发布内。

Whether data in BlueStore is compressed is determined by a combination
of the *compression mode* and any hints associated with a write
operation.  The modes are:

* **none**: 永不压缩数据；
* **passive**: Do not compress data unless the write operation has a
  *compressible* hint set.
* **aggressive**: Compress data unless the write operation has an
  *incompressible* hint set.
* **force**: 压缩一切数据。

For more information about the *compressible* and *incompressible* IO
hints, see :c:func:`rados_set_alloc_hint`.

Note that regardless of the mode, if the size of the data chunk is not
reduced sufficiently it will not be used and the original
(uncompressed) data will be stored.  For example, if the ``bluestore
compression required ratio`` is set to ``.7`` then the compressed data
must be 70% of the size of the original (or smaller).

The *compression mode*, *compression algorithm*, *compression required
ratio*, *min blob size*, and *max blob size* can be set either via a
per-pool property or a global config option.  Pool properties can be
set with::

  ceph osd pool set <pool-name> compression_algorithm <algorithm>
  ceph osd pool set <pool-name> compression_mode <mode>
  ceph osd pool set <pool-name> compression_required_ratio <ratio>
  ceph osd pool set <pool-name> compression_min_blob_size <size>
  ceph osd pool set <pool-name> compression_max_blob_size <size>

.. confval:: bluestore_compression_algorithm
.. confval:: bluestore_compression_mode
.. confval:: bluestore_compression_required_ratio
.. confval:: bluestore_compression_min_blob_size
.. confval:: bluestore_compression_min_blob_size_hdd
.. confval:: bluestore_compression_min_blob_size_ssd
.. confval:: bluestore_compression_max_blob_size
.. confval:: bluestore_compression_max_blob_size_hdd
.. confval:: bluestore_compression_max_blob_size_ssd

``bluestore compression required ratio``

:描述: 为了存得下压缩后的版本，压缩后的数据块尺寸与原始尺寸的\
       比率必须小于此数值。

:类型: Floating point
:是否必需: No
:默认值: .875

``bluestore compression max blob size ssd``

:描述: 用非旋转（固态）媒体时
       ``bluestore compression max blob size`` 的默认值。

:类型: Unsigned Integer
:是否必需: No
:默认值: 64K

.. _bluestore-rocksdb-sharding:

RocksDB Sharding
================

Internally BlueStore uses multiple types of key-value data,
stored in RocksDB.  Each data type in BlueStore is assigned a
unique prefix. Until Pacific all key-value data was stored in
single RocksDB column family: 'default'.  Since Pacific,
BlueStore can divide this data into multiple RocksDB column
families. When keys have similar access frequency, modification
frequency and lifetime, BlueStore benefits from better caching
and more precise compaction. This improves performance, and also
requires less disk space during compaction, since each column
family is smaller and can compact independent of others.

OSDs deployed in Pacific or later use RocksDB sharding by default.
If Ceph is upgraded to Pacific from a previous version, sharding is off.

To enable sharding and apply the Pacific defaults, stop an OSD and run

    .. prompt:: bash #

      ceph-bluestore-tool \
        --path <data path> \
        --sharding="m(3) p(3,0-12) O(3,0-13)=block_cache={type=binned_lru} L P" \
        reshard

.. confval:: bluestore_rocksdb_cf
.. confval:: bluestore_rocksdb_cfs

Throttling
==========

.. confval:: bluestore_throttle_bytes
.. confval:: bluestore_throttle_deferred_bytes
.. confval:: bluestore_throttle_cost_per_io
.. confval:: bluestore_throttle_cost_per_io_hdd
.. confval:: bluestore_throttle_cost_per_io_ssd


SPDK 用法
=========
.. SPDK Usage

如果你想让 NVMe SSD 使用 SPDK 驱动，你得先配置好系统。详情见
`SPDK 文档`_\ 。

.. _SPDK 文档: http://www.spdk.io/doc/getting_started.html#getting_started_examples

SPDK 有个脚本可以自动配置设备，以 root 身份执行： ::

  $ sudo src/spdk/scripts/setup.sh

之后你需要在这里给 ``bluestore_block_path`` 指定 NVMe 设备的\
设备档位，它以 spdk: 为前缀。

例如，你可以这样找出一个 Intel PCIe SSD 的设备档位： ::

  $ lspci -mm -n -D -d 8086:0953

设备档位的格式肯定是 ``DDDD:BB:DD.FF`` 或 ``DDDD.BB.DD.FF`` 。

然后这样设置： ::

  bluestore block path = spdk:0000:01:00.0

其中， ``0000:01:00.0`` 就是在前面 ``lspci`` 命令的输出里找到\
的。

If you want to run multiple SPDK instances per node, you must specify the
amount of dpdk memory size in MB each instance will use, to make sure each
instance uses its own dpdk memory

In most cases, we only need one device to serve as data, db, db wal purposes.
We need to make sure configurations below to make sure all IOs issued under
SPDK.::

  bluestore_block_db_path = ""
  bluestore_block_db_size = 0
  bluestore_block_wal_path = ""
  bluestore_block_wal_size = 0

Otherwise, the current implementation will setup symbol file to kernel
filesystem location and uses kernel driver to issue DB/WAL IO.

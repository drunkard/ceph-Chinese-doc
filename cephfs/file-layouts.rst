.. _file-layouts:

文件布局
========

文件布局可控制如何把文件内容映射到各 Ceph RADOS 对象，你可以\
用\ *虚拟扩展属性*\ 或 xattrs 来读、写某一文件的布局。

客户端在写文件的布局时必须用 ``p`` 标志。见
:ref:`布局和配额使用条件（ p 标记） <cephfs-layout-and-quota-restriction>` 。

布局 xattrs 的名字取决于此文件是常规文件还是目录，常规文件的\
布局 xattrs 叫作 ``ceph.file.layout`` 、目录的布局 xattrs 叫作
``ceph.dir.layout`` 。因此后续实例中若用的是
``ceph.file.layout`` ，处理目录时就要替换为 ``dir`` 。

.. tip::
   你的 Linux 发行版也许默认没提供操作 xattrs 的命令，所需\
   软件包通常是 ``attr`` 。


布局字段
--------
.. Layout fields

pool
    字符串，可指定 ID 或名字，
    其字符必须出自 ``[a-zA-Z0-9\_-.]`` 集合。
    它是文件的数据对象所在的 RADOS 存储池。

pool_id
    这是数字组成的字符串。这是存储池的 ID ，
    是在创建这个 RADOS 存储池时 Ceph 分配的。

pool_name
    这是个字符串。这是 RADOS 存储池的名字，
    是用户在创建此存储池时指定的。

pool_namespace
    字符串，其字符必须出自 ``[a-zA-Z0-9\_-.]`` 集合。
    这个参数决定对象应该写入数据存储池的哪个 RADOS 命名空间。
    默认为空（即默认命名空间）。

stripe_unit
    字节数、整数。一个文件的数据块按照此尺寸（字节）分布。
    一文件所有条带单元的尺寸一样，最后一个条带单元通常不完整——
    即它包含直到文件末尾 EOF 的数据、还有用于满足固定条带单元尺寸的填充数据。

stripe_count
    整数。组成 RAID 0 “条带”数据的连续条带单元数量。

object_size
    整数个字节。文件数据按此尺寸分块为 RADOS 对象。

.. tip::
   RADOS 会确保对象的尺寸是个可配置的限量：如果你自行增大 CephFS 对象尺寸，
   超过了那个限量，那么写入可能不会成功。
   对应的 OSD 选项是 ``osd_max_object_size`` ，默认值是 128MB 。
   RADOS 对象过于大可能会影响集群的平稳运行，所以不建议对象尺寸限量超过默认值。


用 ``getfattr`` 读取布局
------------------------
.. Reading layouts with ``getfattr``

读出的布局信息表示为单个字符串：

.. code-block:: bash

    $ touch file
    $ getfattr -n ceph.file.layout file
    # file: file
    ceph.file.layout="stripe_unit=4194304 stripe_count=1 object_size=4194304 pool=cephfs_data"

读取单个布局字段：

.. code-block:: bash

    $ getfattr -n ceph.file.layout.pool_name file
    # file: file
    ceph.file.layout.pool_name="cephfs_data"
    $ getfattr -n ceph.file.layout.pool_id file
    # file: file
    ceph.file.layout.pool_id="5"
    $ getfattr -n ceph.file.layout.pool file
    # file: file
    ceph.file.layout.pool="cephfs_data"
    $ getfattr -n ceph.file.layout.stripe_unit file
    # file: file
    ceph.file.layout.stripe_unit="4194304"
    $ getfattr -n ceph.file.layout.stripe_count file
    # file: file
    ceph.file.layout.stripe_count="1"
    $ getfattr -n ceph.file.layout.object_size file
    # file: file
    ceph.file.layout.object_size="4194304"    

.. note::

    读取布局时，存储池通常是以名字标识的。
    然而在极少数情况下，如存储池刚创建时，可能会输出 ID 。

目录只有经过定制才会有显式的布局，如果从没更改过，那么读取其布局时就会失败：\
这表明它会继承父目录的显式布局设置。

.. code-block:: bash

    $ mkdir dir
    $ getfattr -n ceph.dir.layout dir
    dir: ceph.dir.layout: No such attribute
    $ setfattr -n ceph.dir.layout.stripe_count -v 2 dir
    $ getfattr -n ceph.dir.layout dir
    # file: dir
    ceph.dir.layout="stripe_unit=4194304 stripe_count=2 object_size=4194304 pool=cephfs_data"

获取 json 格式的布局。如果没有为特定 inode 设置特定布局，
系统会向后遍历目录路径，找到距离最近的、
有布局的上级目录，并以 json 格式返回。
文件布局也可以用 ``ceph.file.layout.json`` vxattr 以 json 格式检索。

在 json 输出中会增加一个名为 ``inheritance`` 的虚拟字段，
用于展示布局的状态。 ``inheritance`` 字段可以有以下值：

``@default`` 表示系统默认布局
``@set`` 表示已为该特定 inode 设置了指定的布局
``@inherited`` 表示从上级目录继承了返回的布局

.. code-block:: bash

   $ getfattr -n ceph.dir.layout.json --only-values /mnt/mycephs/accounts
   {"stripe_unit": 4194304, "stripe_count": 1, "object_size": 4194304, "pool_name": "cephfs.a.data", "pool_id": 3, "pool_namespace": "", "inheritance": "@default"}


用 ``setfattr`` 设置布局
------------------------
.. Writing layouts with ``setfattr``

布局字段可用 ``setfattr`` 修改：

.. code-block:: bash

    $ ceph osd lspools
    0 rbd
    1 cephfs_data
    2 cephfs_metadata

    $ setfattr -n ceph.file.layout.stripe_unit -v 1048576 file2
    $ setfattr -n ceph.file.layout.stripe_count -v 8 file2
    $ setfattr -n ceph.file.layout.object_size -v 10485760 file2
    $ setfattr -n ceph.file.layout.pool -v 1 file2  # Setting pool by ID
    $ setfattr -n ceph.file.layout.pool -v cephfs_data file2  # Setting pool by name
    $ setfattr -n ceph.file.layout.pool_id -v 1 file2  # Setting pool by ID
    $ setfattr -n ceph.file.layout.pool_name -v cephfs_data file2  # Setting pool by name

.. note::
   用 ``setfattr`` 命令修改文件的布局字段时，此文件必须是空的，否则会报错。

.. code-block:: bash

    # 创建空文件
    $ touch file1
    # 可如愿修改布局字段
    $ setfattr -n ceph.file.layout.stripe_count -v 3 file1

    # 向文件写入些东西
    $ echo "hello world" > file1
    $ setfattr -n ceph.file.layout.stripe_count -v 4 file1
    setfattr: file1: Directory not empty

文件和目录布局也可以用 json 格式设置。
设置布局时 ``inheritance`` 字段将被忽略。
此外，如果同时指定了 ``pool_name`` 和 ``pool_id`` 字段，
则优先使用 ``pool_name`` ，因为它更清晰明了，不容易出现歧义。

.. code-block:: bash

   $ setfattr -n ceph.file.layout.json -v '{"stripe_unit": 4194304, "stripe_count": 1, "object_size": 4194304, "pool_name": "cephfs.a.data", "pool_id": 3, "pool_namespace": "", "inheritance": "@default"}' file1


清除布局
--------
.. Clearing layouts

如果你想删除某一目录的布局，
以便继承上级的布局，可以这样：

.. code-block:: bash

    setfattr -x ceph.dir.layout mydir

类似地，如果你已经设置了 ``pool_namespace`` 属性，
又想让布局改回默认命名空间：

.. code-block:: bash

    # 创建个目录，并给它设置命名空间
    mkdir mydir
    setfattr -n ceph.dir.layout.pool_namespace -v foons mydir
    getfattr -n ceph.dir.layout mydir
    ceph.dir.layout="stripe_unit=4194304 stripe_count=1 object_size=4194304 pool=cephfs_data_a pool_namespace=foons"

    # 清除目录布局的命名空间
    setfattr -x ceph.dir.layout.pool_namespace mydir
    getfattr -n ceph.dir.layout mydir
    ceph.dir.layout="stripe_unit=4194304 stripe_count=1 object_size=4194304 pool=cephfs_data_a"


布局的继承
----------
.. Inheritance of layouts

文件会在创建时继承其父目录的布局，
然而之后对父目录布局的更改不会影响其子孙。

.. code-block:: bash

    $ getfattr -n ceph.dir.layout dir
    # file: dir
    ceph.dir.layout="stripe_unit=4194304 stripe_count=2 object_size=4194304 pool=cephfs_data"

    # 证实 file1 继承了其父的布局
    $ touch dir/file1
    $ getfattr -n ceph.file.layout dir/file1
    # file: dir/file1
    ceph.file.layout="stripe_unit=4194304 stripe_count=2 object_size=4194304 pool=cephfs_data"

    # 现在更改目录布局，然后再创建第二个文件
    $ setfattr -n ceph.dir.layout.stripe_count -v 4 dir
    $ touch dir/file2

    # 证实 file1 的布局未变
    $ getfattr -n ceph.file.layout dir/file1
    # file: dir/file1
    ceph.file.layout="stripe_unit=4194304 stripe_count=2 object_size=4194304 pool=cephfs_data"

    # 但 file2 继承了父目录的新布局
    $ getfattr -n ceph.file.layout dir/file2
    # file: dir/file2
    ceph.file.layout="stripe_unit=4194304 stripe_count=4 object_size=4194304 pool=cephfs_data"

如果中层目录没有设置布局，
那么内层目录中创建的文件也会继承此目录的布局：

.. code-block:: bash

    $ getfattr -n ceph.dir.layout dir
    # file: dir
    ceph.dir.layout="stripe_unit=4194304 stripe_count=4 object_size=4194304 pool=cephfs_data"
    $ mkdir dir/childdir
    $ getfattr -n ceph.dir.layout dir/childdir
    dir/childdir: ceph.dir.layout: No such attribute
    $ touch dir/childdir/grandchild
    $ getfattr -n ceph.file.layout dir/childdir/grandchild
    # file: dir/childdir/grandchild
    ceph.file.layout="stripe_unit=4194304 stripe_count=4 object_size=4194304 pool=cephfs_data"


.. _adding-data-pool-to-file-system:

把数据存储池加入文件系统
------------------------
.. Adding a data pool to the File System 

要通过 CephFS 使用一个存储池，你必须把它加入元数据服务器。

.. code-block:: bash

    $ ceph fs add_data_pool cephfs cephfs_data_ssd
    $ ceph fs ls  # Pool should now show up
    .... data pools: [cephfs_data cephfs_data_ssd ]

确保你的 cephx 密钥允许客户端访问这个新存储池。

然后就能在 CephFS 内更新一个目录的布局了，以使用刚加上的存储池：

.. code-block:: bash

    $ mkdir /mnt/cephfs/myssddir
    $ setfattr -n ceph.dir.layout.pool -v cephfs_data_ssd /mnt/cephfs/myssddir

此后，在那个目录内新创建的文件都会继承它的布局、
并把它们的数据放入你新加的存储池。

你也许注意到了，主数据存储池（传递给 ``fs new`` 的那个）内的\
对象计数仍在继续增加，即使创建的文件位于你后加的存储池内。\
这很正常：文件的数据存储于由布局指定的存储池内，
但是所有文件的元数据还都存储在主数据存储池内，数量很小。

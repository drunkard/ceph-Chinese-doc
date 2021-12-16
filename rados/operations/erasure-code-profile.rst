.. _erasure-code-profiles:

============
 纠删码配置
============

纠删码由\ **配置**\ 定义，在创建纠删码存储池及其相关的 CRUSH \
规则时用到。

名为 **default** 的纠删码配置（ Ceph 集群初始化时创建的）
会把数据等分为 2 块、还有两个相同尺寸的奇偶校验块。
它在集群内占用的空间和 2 副本存储池一样，
却能容许 4 个数据块丢 2 块。
这样的配置就是 **k=2** 且 **m=4** ，
意思是信息分布在四个 OSD （ k+m=4 ）且容许其中两个丢失。

为了在不增加原始存储空间需求的前提下提升冗余性，
你可以新建配置。例如，一个 **k=10** 且
**m=4** 的配置可容忍 4 个 OSD 失效，
它会把一对象分布到 14 个（ k+m=14 ） OSD 上。
此对象先被分割为 **10** 块（若对象为 10MB ，那每块就是 1MB ）、
并计算出 **4** 个用于恢复的编码块
（各编码块尺寸等于数据块，即 1MB ）；
这样，原始空间仅多占用 10% 就可容许 4 个 OSD 同时失效、
且不丢失数据。

.. _可用插件列表:

.. toctree::
	:maxdepth: 1

	erasure-code-jerasure
	erasure-code-isa
	erasure-code-lrc
	erasure-code-shec
	erasure-code-clay


osd erasure-code-profile set
============================

要新建纠删码配置： ::

	ceph osd erasure-code-profile set {name} \
             [{directory=directory}] \
             [{plugin=plugin}] \
             [{stripe_unit=stripe_unit}] \
             [{key=value} ...] \
             [--force]

其中：


``{directory=directory}``

:描述: 设置纠删码插件的路径，需是\ **目录**\ 。
:类型: String
:是否必需: No.
:默认值: /usr/lib/ceph/erasure-code


``{plugin=plugin}``

:描述: 指定纠删码\ **插件**\ 来计算编码块、及恢复丢失块。
       详见 `可用插件列表`_\ 。
:类型: String
:是否必需: No.
:默认值: jerasure


``{stripe_unit=stripe_unit}``

:描述: 每一个条带中、一个数据块的数据量。例如，
       在一个配置中，数据块为 2 且 stripe_unit=4K ，
       数据进来时会把 0-4K 放入块 0 ，
       4K-8K 放入块 1 ；然后 8K-12K 又是块 0 。
       为实现最佳性能，这里应该设置成 4K 的倍数。
       默认值是在存储池创建时从监视器配置选项
       ``osd_pool_erasure_code_stripe_unit`` 获取的。
       一个使用着这个配置的存储池，
       其 stripe_width 值（条带宽度）就是\
       数据块的数量乘以这里的 stripe_unit 值。

:类型: String
:是否必需: No.


``{key=value}``

:描述: 纠删码插件所定义的键/值对含义。
:类型: String
:是否必需: No.


``--force``

:描述: 覆盖同名配置，
       还能设置没有按 4K 对齐的 stripe_unit 。
:类型: String
:是否必需: No.


osd erasure-code-profile rm
============================

要删除纠删码配置： ::

	ceph osd erasure-code-profile rm {name}

若此配置还被某个存储池使用着，则删除会失败。


osd erasure-code-profile get
============================

要查看一纠删码配置： ::

	ceph osd erasure-code-profile get {name}


osd erasure-code-profile ls
===========================

列出所有纠删码配置： ::

	ceph osd erasure-code-profile ls

===============
 Ceph 对象网关
===============

:term:`Ceph 对象网关`\ 是一个构建在 ``librados`` 之上的对象存储接口，它为应用程\
序访问Ceph 存储集群提供了一个 RESTful 风格的网关 。 :term:`Ceph 对象存储`\ 支持 2 种接口：

#. **兼容S3:** 提供了对象存储接口，兼容 亚马逊S3 RESTful 接口的一个大子集。

#. **兼容Swift:** 提供了对象存储接口，兼容 Openstack Swift 接口的一个大子集。
   
Ceph 对象存储使用 Ceph 对象网关守护进程（ ``radosgw`` ），它是个与 Ceph 存储集群\
交互的 FastCGI 模块。因为它提供了与 OpenStack Swift 和 Amazon S3 兼容的接口， \
RADOS 要有它自己的用户管理。 Ceph 对象网关可与 Ceph FS 客户端或 Ceph 块设备客户端\
共用一个存储集群。 S3 和 Swift 接口共用一个通用命名空间，所以你可以用一个接口写如\
数据、然后用另一个接口取出数据。

.. ditaa::  +------------------------+ +------------------------+
            |   S3 compatible API    | |  Swift compatible API  |
            +------------------------+-+------------------------+
            |                      radosgw                      |
            +---------------------------------------------------+
            |                      librados                     |
            +------------------------+-+------------------------+
            |          OSDs          | |        Monitors        |
            +------------------------+ +------------------------+   

.. note:: Ceph 对象存储\ **不**\ 使用 Ceph 元数据服务器。


.. toctree::
	:maxdepth: 1

	手动安装 <../../install/install-ceph-gateway>
	简单配置 <config>
	异地同步配置 <federated-config>
	配置参考 <config-ref>
	管理指南 <admin>
	清除临时数据 <purge-temp>
	S3 API <s3>
	Swift API <swift>
	管理操作 API <adminops>
	与 OpenStack Keystone 集成 <keystone>
	故障排除
	radosgw 手册页 <../../man/8/radosgw>
	radosgw-admin 手册页 <../../man/8/radosgw-admin>

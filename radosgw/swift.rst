.. _radosgw swift:

=========================
 Ceph 对象网关 Swift API
=========================

Ceph 支持 REST 风格的 API ，它与 `Swift API`_ 的基本访问模型兼容。


API
---

.. toctree::
	:maxdepth: 1

	认证 <swift/auth>
	服务操作 <swift/serviceops>
	容器操作 <swift/containerops>
	对象操作 <swift/objectops>
	临时 URL 操作 <swift/tempurl>
	指导手册 <swift/tutorial>
	Java <swift/java>
	Python <swift/python>
	Ruby <swift/ruby>


功能支持
--------
.. Features Support

下面的表格描述了对当前 Swift 功能的支持情况：

+---------------------------------+-----------------+----------------------------------------+
| 功能                            | 状态            | 备注                                   |
+=================================+=================+========================================+
| **Authentication**              | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Get Account Metadata**        | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Swift ACLs**                  | 支持            | 支持部分 Swift ACL                     |
+---------------------------------+-----------------+----------------------------------------+
| **List Containers**             | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Delete Container**            | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Create Container**            | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Get Container Metadata**      | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Update Container Metadata**   | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Delete Container Metadata**   | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **List Objects**                | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Static Website**              | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Create Object**               | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Create Large Object**         | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Delete Object**               | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Get Object**                  | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Copy Object**                 | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Get Object Metadata**         | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Update Object Metadata**      | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Expiring Objects**            | 支持            |                                        |
+---------------------------------+-----------------+----------------------------------------+
| **Temporary URLs**              | 部分支持        | No support for container-level keys    |
+---------------------------------+-----------------+----------------------------------------+
| **Object Versioning**           | 部分支持        | 不支持 ``X-History-Location``          |
+---------------------------------+-----------------+----------------------------------------+
| **CORS**                        | 不支持          |                                        |
+---------------------------------+-----------------+----------------------------------------+


.. _Swift API: https://developer.openstack.org/api-ref/object-store/index.html

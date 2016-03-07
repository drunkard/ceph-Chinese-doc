==============
 安装（快速）
==============

.. raw:: html

	<style type="text/css">div.body h3{margin:5px 0px 0px 0px;}</style>
	<table cellpadding="10"><colgroup><col width="33%"><col width="33%"><col width="33%"></colgroup><tbody valign="top"><tr><td><h3>步骤一：预检</h3>

在部署 Ceph 存储集群之前，需要对 :term:`Ceph 客户端`\ 和 :term:`Ceph 节点`\ 进行一些基本的配置，你也可以加入 Ceph 社区以寻求帮助。

.. toctree::

   预检 <quick-start-preflight>

.. raw:: html

	</td><td><h3>步骤二：存储集群</h3>

完成预检之后，你就可以开始部署 Ceph 存储集群了。

.. toctree::

	存储集群快速入门 <quick-ceph-deploy>


.. raw:: html

	</td><td><h3>步骤三： Ceph 客户端</h3>

大多数 Ceph 用户不会直接往 Ceph 存储集群里存储对象，他们通常会用 Ceph 块设备、 \
Ceph 文件系统、或 Ceph 对象存储这三大功能中的一个或多个。

.. toctree::

   块设备快速入门 <quick-rbd>
   文件系统快速入门 <quick-cephfs>
   对象存储快速入门 <quick-rgw>

.. raw:: html

	</td></tr></tbody></table>

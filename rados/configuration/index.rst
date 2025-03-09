======
 配置
======

各个 Ceph 进程、守护进程或工具都是在启动时从几个来源获取其配置，\
包括 (1) 本地配置、 (2) 监视器、 (3) 命令行、和 (4) 环境变量。

配置选项可以设置为全局的，如此一来它们就可应用于 (1) 所有守护进程、\
(2) 某种类型的所有守护进程或服务、\
或 (3) 仅适用于某个守护进程、进程或客户端。


.. raw:: html

	<table cellpadding="10"><colgroup><col width="50%"><col width="50%"></colgroup><tbody valign="top"><tr><td><h3>配置对象存储</h3>

下列是通用对象存储的配置：

.. toctree::
   :maxdepth: 1

   存储设备 <storage-devices>
   ceph-conf


.. raw:: html 

	</td><td><h3>参考</h3>

参考下列文档优化集群性能：

.. toctree::
   :maxdepth: 1

   通用选项 <common>
   网络选项 <network-config-ref>
   信使协议 v2 <msgr2>
   认证选项 <auth-config-ref>
   监视器选项 <mon-config-ref>
   mon-lookup-dns
   心跳选项（监视器与 OSD 的的交互） <mon-osd-interaction>
   OSD 选项 <osd-config-ref>
   DmClock 配置 <mclock-config-ref>
   BlueStore 配置 <bluestore-config-ref>
   FileStore 配置 <filestore-config-ref>
   日志选项 <journal-ref>
   存储池、归置组和 CRUSH 选项 <pool-pg-config-ref.rst>
   常规选项 <general-config-ref>

   
.. raw:: html

	</td></tr></tbody></table>

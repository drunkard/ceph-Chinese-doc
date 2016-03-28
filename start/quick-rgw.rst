======================
 Ceph 对象存储快速入门
======================

从 firefly（v0.80）起，Ceph 存储集群显著地简化了 Ceph 对象网关的安装和配置。\
网关守护进程内嵌了 Civetweb，无需额外安装 web 服务器或配置 FastCGI。此外，可以直接 \
使用 ``ceph-deploy`` 来安装网关软件包、生成密钥、配置数据目录以及创建一个网关实例。

.. tip:: Civetweb 默认使用 ``7480`` 端口。要么直接打开 ``7480`` 端口，要么在你的 \
   Ceph 配置文件中设置首选端口（例如 ``80`` 端口）。
   
要使用 Ceph 对象网关，请执行下列步骤：

安装 Ceph 对象网关
==================

#. 在 ``client-node`` 上执行预安装步骤。如果你打算使用 Civetweb 的默认端口 ``7480`` ，\
   必须通过 ``firewall-cmd`` 或 ``iptables`` 来打开它。详情见\ `预检`_\ 。

#. 从管理节点的工作目录，在 ``client-node`` 上安装 Ceph 对象网关软件包。例如： ::

	ceph-deploy install --rgw <client-node> [<client-node> ...]
	
新建 Ceph 对象网关实例
======================

从管理节点的工作目录，在 ``client-node`` 上新建一个 Ceph 对象网关实例。例如： ::

	ceph-deploy rgw create

一旦网关开始运行，你就可以通过 ``7480`` 端口来访问它（比如 ``http://client-node:7480`` ）。

配置 Ceph 对象网关实例
======================

#. 通过修改 Ceph 配置文件可以更改默认端口（比如改成 ``80`` ）。增加名为 \
   ``[client.rgw.<client-node>]`` 的小节，把 ``<client-node>`` 替换成你自\
   己 Ceph 客户端节点的短名称（即 ``hostname -s`` 的输出）。例如，你的节点\
   名就是 ``client-node`` ，在 ``[global]`` 节后增加一个类似于下面的小节： ::

    [client.rgw.client-node]
    rgw_frontends = "civetweb port=80"

   .. note:: 确保在 ``rgw_frontends`` 键值对的 ``port=<port-number>`` 中没\
      有空格。

   .. important:: 如果你打算使用 80 端口，确保 Apache 服务器没有在使用该端口，\
      否则会和 Civetweb 冲突。出现这种情况时我们建议移除 Apache 服务。
	   
#. 为了使新端口的设置生效，需要重启 Ceph 对象网关。在 RHEL 7 和 Fedora 上 ，\
   执行： ::
   
    sudo systemctl restart ceph-radosgw.service
	
   在 RHEL 6 和 Ubuntu 上，执行： ::

    sudo service radosgw restart id=rgw.<short-hostname>
	
#. 最后，检查节点的防火墙，确保你所选用的端口（例如 ``80`` 端口）处于开放状态。\
   如果没有，把该端口加入放行规则并重载防火墙的配置。例如： ::
   
    sudo firewall-cmd --list-all sudo firewall-cmd --zone=public --add-port
    80/tcp --permanent
    sudo firewall-cmd --reload
	
   关于使用 ``firewall-cmd`` 或 ``iptables`` 配置防火墙的详细信息，请参阅\
   \ `预检`_\。
   
   你应该可以生成一个未授权的请求，并收到应答。例如，一个如下不带参数的请求： ::
   
    http://<client-node>:80
	
   应该收到这样的应答： ::
   
    <?xml version="1.0" encoding="UTF-8"?>
    <ListAllMyBucketsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
      <Owner>
        <ID>anonymous</ID>
        <DisplayName></DisplayName>
      </Owner>
      <Buckets>
      </Buckets>
    </ListAllMyBucketsResult>

   更多管理和 API 细节请参阅 `Ceph 对象网关的配置`_ 指南\ 。
   
.. _Ceph 对象网关的配置: ../../radosgw/config
.. _预检: ../quick-start-preflight

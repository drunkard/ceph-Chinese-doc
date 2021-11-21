================
 Cephx 配置参考
================

``cephx`` 协议已默认开启。\
加密认证要耗费一定计算资源，但通常很低。\
如果您的客户端和服务器网络环境相当安全，\
而且认证的负面效应更大，你可以关闭它，\ **通常不推荐您这么做**\ 。

.. note:: 如果禁用了认证，就会有篡改客户端/服务器消息\
   这样的中间人攻击风险，这会导致灾难性后果。

关于创建用户请参考\ `用户管理`_\ ；\
关于 Cephx 的体系结构请参考\ `体系结构——高可用性认证`_\ 。


部署场景
========
.. Deployment Scenarios

There are two main scenarios for deploying a Ceph cluster, which impact
how you initially configure Cephx. Most first time Ceph users use
``cephadm`` to create a cluster (easiest). For clusters using
other deployment tools (e.g., Chef, Juju, Puppet, etc.), you will need
to use the manual procedures or configure your deployment tool to
bootstrap your monitor(s).


手动部署
--------
.. Manual Deployment

When you deploy a cluster manually, you have to bootstrap the monitor manually
and create the ``client.admin`` user and keyring. To bootstrap monitors, follow
the steps in `监视器的自举引导`_. The steps for monitor bootstrapping are
the logical steps you must perform when using third party deployment tools like
Chef, Puppet,  Juju, etc.


启用和禁用 Cephx
================
.. Enabling/Disabling Cephx

Enabling Cephx requires that you have deployed keys for your monitors,
OSDs and metadata servers. If you are simply toggling Cephx on / off, 
you do not have to repeat the bootstrapping procedures.


启用 Cephx
----------
.. Enabling Cephx

启用 ``cephx`` 后， Ceph 将在默认搜索路径（包括
``/etc/ceph/ceph.$name.keyring`` ）里查找密钥环。你可以在
`Ceph 配置`_\ 文件的 ``[global]`` 段里添加 ``keyring`` 选项来\
修改，但不推荐。

在禁用了 ``cephx`` 的集群上执行下面的步骤来启用它，如果你（\
或者部署工具）已经生成了密钥，你可以跳过相关步骤。

#. 创建 ``client.admin`` 密钥，并为客户端保存此密钥的副本：

   .. prompt:: bash $

     ceph auth get-or-create client.admin mon 'allow *' mds 'allow *' mgr 'allow *' osd 'allow *' -o /etc/ceph/ceph.client.admin.keyring

   **警告：** 此命令会覆盖任何存在的
   ``/etc/ceph/client.admin.keyring`` 文件，如果部署工具已经\
   完成此步骤，千万别再执行此命令。多加小心！

#. 创建监视器集群所需的密钥环、并给它们生成密钥。

   .. prompt:: bash $

     ceph-authtool --create-keyring /tmp/ceph.mon.keyring --gen-key -n mon. --cap mon 'allow *'

#. 把监视器密钥环复制到 ``ceph.mon.keyring`` 文件，再把此文件\
   复制到各监视器的 ``mon data`` 目录下。比如要把它复制给名为
   ``ceph`` 集群的 ``mon.a`` ，用此命令：

   .. prompt:: bash $

     cp /tmp/ceph.mon.keyring /var/lib/ceph/mon/ceph-a/keyring

#. 为每个 MGR 生成一个密钥， ``{$id}`` 是 MGR 的名字：

   .. prompt:: bash $

      ceph auth get-or-create mgr.{$id} mon 'allow profile mgr' mds 'allow *' osd 'allow *' -o /var/lib/ceph/mgr/ceph-{$id}/keyring

#. 为每个 OSD 生成密钥， ``{$id}`` 是 OSD 编号：

   .. prompt:: bash $

      ceph auth get-or-create osd.{$id} mon 'allow rwx' osd 'allow *' -o /var/lib/ceph/osd/ceph-{$id}/keyring

#. 为每个 MDS 生成密钥， ``{$id}`` 是 MDS 的标识字母：

   .. prompt:: bash $

      ceph auth get-or-create mds.{$id} mon 'allow rwx' osd 'allow *' mds 'allow *' mgr 'allow profile mds' -o /var/lib/ceph/mds/ceph-{$id}/keyring

#. 把以下配置加入 `Ceph 配置`_\ 文件的 ``[global]`` 段下以启用
   ``cephx`` 认证：

   .. code-block:: ini

      auth_cluster_required = cephx
      auth_service_required = cephx
      auth_client_required = cephx

#. 启动或重启 Ceph 集群，详情见\ `操纵集群`_\ 。

要手动自启监视器，请参考\ `手动部署`_\ 。


.. Disabling Cephx

禁用 Cephx
----------

下述步骤描述了如何禁用 Cephx 。如果你的集群环境相对安全，你可以减免认证耗费的计算资\
源，然而\ **我们不推荐**\ 。但是临时禁用认证会使安装、和/或排障更简单。

#. 把下列配置加入 `Ceph 配置`_\ 文件的 ``[global]`` 段下即可禁用 ``cephx`` 认证：

   .. code-block:: ini

      auth_cluster_required = none
      auth_service_required = none
      auth_client_required = none

#. 启动或重启 Ceph 集群，具体参考\ `操纵集群`_\ 。


配置选项
========
.. Configuration Settings

启用事项
--------
.. Enablement

``auth cluster required``

:描述: 如果启用了， Ceph 存储集群守护进程（如 ``ceph-mon`` 、
       ``ceph-osd`` 、 ``ceph-mds`` 和 ``ceph-mgr`` ）间必须\
       相互认证。可用选项有 ``cephx`` 或 ``none`` 。
:类型: String
:是否必需: No
:默认值: ``cephx``.


``auth service required``

:描述: 如果启用，客户端要访问 Ceph 服务的话，集群守护进程会要求它和集群认\
       证。可用选项为 ``cephx`` 或 ``none`` 。
:类型: String
:是否必需: No
:默认值: ``cephx``.


``auth client required``

:描述: 如果启用，客户端会要求 Ceph 集群和它认证。可用选项为 ``cephx`` 或 \
       ``none`` 。
:类型: String
:是否必需: No
:默认值: ``cephx``.


.. index:: keys; keyring

密钥
----
.. Keys

如果你的集群启用了认证， ``ceph`` 管理命令和客户端得有密钥\
才能访问集群。

给 ``ceph`` 管理命令和客户端提供密钥的最常用方法就是把密钥环\
放到 ``/etc/ceph`` 目录下。在 Octopus 和后续版本用
``cephadm`` ，其文件名通常是 ``ceph.client.admin.keyring``
（或 ``$cluster.client.admin.keyring`` ）。如果你的密钥环位于
``/etc/ceph`` 目录下，就不需要在 Ceph 配置文件里指定
``keyring`` 选项了。

我们建议把集群的密钥环复制到你执行管理命令的节点，它包含
``client.admin`` 密钥。

手动复制可执行此命令： ::

	sudo scp {user}@{ceph-cluster-host}:/etc/ceph/ceph.client.admin.keyring /etc/ceph/ceph.client.admin.keyring

.. tip:: 确保给客户端上的 ``ceph.keyring`` 设置合理的权限位（如
   ``chmod 644`` ）。

你可以用 ``key`` 选项把密钥写在配置文件里（别这样），或者用
``keyfile`` 选项指定个路径。


``keyring``

:描述: 密钥环文件的路径。
:类型: String
:是否必需: No
:默认值: ``/etc/ceph/$cluster.$name.keyring,/etc/ceph/$cluster.keyring,/etc/ceph/keyring,/etc/ceph/keyring.bin``


``keyfile``

:描述: 到密钥文件的路径，如一个只包含密钥的文件。
:类型: String
:是否必需: No
:默认值: None


``key``

:描述: 密钥（密钥文本），最好别这样做。
:类型: String
:是否必需: No
:默认值: None


.. index:: signatures

签名
----
.. Signatures

Ceph 施行的签名检查可以为消息提供一些有限的保护，以防消息被\
在线篡改（比如被“中间人”攻击篡改）。

像 Ceph 认证的其他部分一样，客户端和集群间的消息签名也能做到\
细粒度控制；而且能启用或禁用 Ceph 守护进程间的签名。

注意，即便启用了签名，数据也没在线加密。


``cephx require signatures``

:描述: 若设置为 ``true`` ， Ceph 会要求对所有消息流量签名，\
       包括 Ceph 客户端与 Ceph 存储集群间的、和构成 Ceph
       存储集群的各守护进程之间。

       Ceph Argonaut 和版本号小于 3.19 的 Linux 内核不支持\
       签名，如果在用这样的客户端，可以关闭此选项，以允许它们\
       连接。
:类型: Boolean
:是否必需: No
:默认值: ``false``


``cephx cluster require signatures``

:描述: 若设置为 ``true`` ， Ceph 要求集群内所有守护进程签名\
       相互之间的消息。
:类型: Boolean
:是否必需: No
:默认值: ``false``


``cephx service require signatures``

:描述: 若设置为 ``true`` ， Ceph 要求签名所有客户端和集群间的消息。
:类型: Boolean
:是否必需: No
:默认值: ``false``


``cephx sign messages``

:描述: 如果 Ceph 版本支持对消息签名， Ceph 会签名所有消息以使\
       欺骗更困难。
:类型: Boolean
:默认值: ``true``


生存期
------
.. Time to Live

``auth service ticket ttl``

:描述: Ceph 存储集群发给客户端一个用于认证的票据时分配给这个\
       票据的生存期。
:类型: Double
:默认值: ``60*60``


.. _监视器的自举引导: ../../../install/manual-deployment#monitor-bootstrapping
.. _操纵集群: ../../operations/operating
.. _手动部署: ../../../install/manual-deployment
.. _Ceph 配置: ../ceph-conf
.. _体系结构——高可用性认证: ../../../architecture#high-availability-authentication
.. _用户管理: ../../operations/user-management

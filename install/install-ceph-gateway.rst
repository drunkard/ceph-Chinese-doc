====================
 安装 Ceph 对象网关
====================

自从  `firefly` (v0.80) 版本开始，Ceph 对象网关运行在 Civetweb 上（已\
经集成进守护进程 ``ceph-radosgw`` ），而不再是 Apache 和 FastCGI 之上。\
使用 Civetweb简化了Ceph对象网关的安装和配置。

.. Note:: 要提供 Ceph 网关服务，你得有一个正常运行的 Ceph 集群，且网关\
   主机能访问存储集群的公共网络。

.. Note:: 在\ 0.80\ 版本中，Ceph 对象网关不再支持SSL。你可以设置一个支\
   持 SSL 的反向代理服务器来将 HTTPS 请求转为 HTTP 请求发给 CivetWeb。

执行安装前的准备工作
----------------------

首先进行\  `环境检查`_\ 并在你的 Ceph 对象网关节点上执行安装前的准备工\
作。特别的，你需要禁用部署 Ceph 集群所用用户的 ``requiretty`` ，同时设\
置 SELinux 为 ``Permissive`` 以及 Ceph 部署用户使用 ``sudo`` 时无需密\
码。对于 Ceph 对象网关，在生产环境下你需要开起 Civetweb 所使用的端口。

.. Note:: Civetweb\ 默认运行在 ``7480``  端口上。

安装 Ceph 对象网关
-----------------------

在你的管理节点的工作目录下，给 Ceph 对象网关节点安装Ceph对象所需的软件\
包。例如::

 ceph-deploy install --rgw <gateway-node1> [<gateway-node2> ...]

``ceph-common`` 包是它的一个依赖性，所以 ``ceph-deploy`` 也将安装这个\
包。 ``ceph`` 的命令行工具就会为管理员准备好。为了让你的 Ceph 对象网关\
节点成为管理节点，可以在管理节点的工作目录下执行以下命令::

 ceph-deploy admin <node-name>

新建网关实例
-----------------------

在你的管理节点的工作目录下，使用命令在 Ceph 对象网关节点上新建一个 Ceph\
对象网关实例。举例如下::

 ceph-deploy rgw create <gateway-node1>

在网关服务成功运行后，你可以使用未经授权的请求来访问端口 ``7480`` ，就\
像这样::

 http://client-node:7480

如果网关实例工作正常，你接收到的返回信息大概如下所示::

 <?xml version="1.0" encoding="UTF-8"?>
 <ListAllMyBucketsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
        <Owner>
        <ID>anonymous</ID>
        <DisplayName></DisplayName>
    </Owner>
    <Buckets>
    </Buckets>
 </ListAllMyBucketsResult>

在任何时候如果你遇到麻烦，而你也想重新来一次，执行下面的命令来清除配置::

 ceph-deploy purge <gateway-node1> [<gateway-node2>]
 ceph-deploy purgedata <gateway-node1> [<gateway-node2>]

如果你执行了 ``purge``, 你必须重新安装 Ceph.

修改默认端口
----------------------

Civetweb 默认运行在端口 ``7480`` 之上.。如果想修改这个默认端口 (比如使\
用端口 ``80``)，修改你的管理节点的工作目录下的 Ceph 配置文件。 添加一\
节，以 ``[client.rgw.<gateway-node>]`` 作为名字， 使用你的 Ceph 对象网\
关节点的短主机名替换其中的 ``<gateway-node>`` (如, ``hostname -s``).

.. Note:: 在 0.94 版本中，Ceph 对象网关不再支持 SSL。你可以设置一个支\
   持 SSL 的反向代理服务器来将 HTTPS 请求转为HTTP请求发给 CivetWeb。

比如, 如果你的主机名是 ``gateway-node1``， 在 ``[global]`` 节后添加的\
节名如下::

 [client.rgw.gateway-node1]
 rgw_frontends = "civetweb port=80"

.. Note:: 请确保在 ``rgw_frontends`` 的键值对中 ``port=<port-number>`` \
          内部没有红格。 节名 ``[client.rgw.gateway-node1]`` 表示接下来\
          的 Ceph 配置文件配置了一个 Ceph 存储集群的客户端，这个客户端\
          的类型是Ceph 对象网关存储  (比如, ``rgw``)， 同时实例名是 ``gateway-node1``.

将该配置文件推送到你的 Ceph 对象网关节点(也包括其他 Ceph 节点)::

 ceph-deploy --overwrite-conf config push <gateway-node> [<other-nodes>]

为了使新配置的端口生效，需要重启 Ceph 对象网关::

 sudo systemctl restart ceph-radosgw.service

最后，需要确保你选择的端口在节点的防火墙配置中是开放的 (比如, 端口 ``80``)。
如果它不是开放的，将它设为开放并重启防火墙。 如果你是用的是 ``firewald``，\
执行下面的命令::

  sudo firewall-cmd --list-all
  sudo firewall-cmd --zone=public --add-port 80/tcp --permanent
  sudo firewall-cmd --reload

如果你使用 ``iptables``， 执行::

  sudo iptables --list
  sudo iptables -I INPUT 1 -i <iface> -p tcp -s <ip-address>/<netmask> --dport 80 -j ACCEPT

替换其中的 ``<iface>`` and ``<ip-address>/<netmask>`` 为你的 Ceph 对象\
网关节点的实际值。

一旦你完成了 ``iptables`` 的配置， 请确保你已经将本次更改持久化，这样\
它在你的 Ceph 对象网关节点重启也依然生效。持久化请执行::

  sudo apt-get install iptables-persistent

会有一个终端界面弹出。选择 ``yes`` 来保存当前 ``IPv4`` 的 iptables 规\
则到文件 ``/etc/iptables/rules.v4`` 中，当前的 ``IPv6`` iptables 规则\
到文件 ``/etc/iptables/rules.v6`` 中。

在前面一步设置的 ``IPv4`` iptables规则t将会被写入文件``/etc/iptables/rules.v4`` \
，这样就实现了持久化，重启也依然生效。

如果你在安装``iptables-persistent`` 后有新增了新的 ``IPv4`` iptables \
规则，你需要使用 ``root`` 执行下面的命令::

 iptables-save > /etc/iptables/rules.v4

从 Apache 迁移到 Civetweb
---------------------------------

如果你在0.80或以上版本的 Ceph 存储上使用 Apache 和 FastCGI 来构建 Ceph \
对象网关，实际上你已经运行了 Civetweb --它随着 ``ceph-radosgw`` 进程启\
动而启动，默认情况下运行在 7480 端口，因此它不会跟基于 Apache 和 FastCGI \
安装的以及其他常用的web服务所使用的端口冲突。迁移到使用 Civetweb 首先\
需要删除您的 Apache。然后，您必须从 Ceph 配置文件中删除 Apache 和 FastCGI \
的设置并重置 ``rgw_frontends`` 到 Civetweb。

回顾使用 ``ceph-deploy`` 来安装 Ceph 对象网关的描述，注意到它的配置文\
件只有一个名为 ``rgw_frontends`` 的设置(这是假设你选择改变默认端口)。\ 
``ceph-deploy`` 会生成对象网关的数据目录和 keyring，并将keyring放在 \
``/var/lib/ceph/radosgw/{rgw-intance}`` 目录下。从这个目录上看这个守护\
进程是在默认位置，然而你也可以在 Ceph 配置文件中指定不同的位置。因为你\
已经有密钥和数据目录，因此如果你使用的是默认路径之外的其他目录，你就需\
要在 Ceph 配置文件中维护这些路径。

一个典型的基于 Apache 部署的 Ceph 对象网关配置文件类似下面的样例:

在 Red Hat Enterprise Linux 系统上::

 [client.radosgw.gateway-node1]
 host = {hostname}
 keyring = /etc/ceph/ceph.client.radosgw.keyring
 rgw socket path = ""
 log file = /var/log/radosgw/client.radosgw.gateway-node1.log
 rgw frontends = fastcgi socket\_port=9000 socket\_host=0.0.0.0
 rgw print continue = false

在 Ubuntu 系统上::

 [client.radosgw.gateway-node]
 host = {hostname}
 keyring = /etc/ceph/ceph.client.radosgw.keyring
 rgw socket path = /var/run/ceph/ceph.radosgw.gateway.fastcgi.sock
 log file = /var/log/radosgw/client.radosgw.gateway-node1.log

为了能够使用 Civetweb，需要做一点修改，简单地删除 Apache 特有的设置如 \
``rgw_socket_path`` 和 ``rgw_print_continue`` 。然后，改变 ``rgw_frontends`` \
的设置来指向 Civetweb 而不是 Apache FastCGI 作为前端，并指定您想要使用\
的端口号。例如::

 [client.radosgw.gateway-node1]
 host = {hostname}
 keyring = /etc/ceph/ceph.client.radosgw.keyring
 log file = /var/log/radosgw/client.radosgw.gateway-node1.log
 rgw_frontends = civetweb port=80

最后，重启 Ceph 对象网关。在 Red Hat Enterprise Linux 请执行::

 sudo systemctl restart ceph-radosgw.service

在 Ubuntu 上执行::

 sudo service radosgw restart id=rgw.<short-hostname>

如果你使用的端口还没有在防护墙端放开，你还需要在你的防火墙开放该端口。

配置 Bucket Sharding
-------------------------

Ceph 对象网关在 ``index_pool`` 中存储 bucket 的索引数据，默认情况下是\
资源池 ``.rgw.buckets.index`` 。有时用户喜欢把很多对象(几十万到上百万\
的对象)存放到同一个 bucket 中。如果你不使用网关的管理接口来为每个 bucket \
的最大对象数设置配额，那么当一旦用户存放大量的对象到一个 bucket 中时，\
bucket 索引的性能会呈现明显的下降。

在0.94版本的 Ceph 中，您可以给 bucket 索引进行分片，这样在你允许 bucket \
中有大量对象时，能够有助于防止出现性能瓶颈。设置项的 “rgw_override_bucket_index_max_shards“ \
允许您设置一个 bucket 的最大分片数。它的默认值为 ``0`` ，这意味着 bucket \
索引分片功能在默认情况下情况下是关闭的。

开启 bucket 的索引分片功能，只需给 ``rgw_override_bucket_index_max_shards`` \
设置一个大于 ``0`` 的值。

简单的配置，只需要在 Ceph 配置文件中加入 ``rgw_override_bucket_index_max_shards`` \
。将其添加在 ``[global]`` 部分来设置一个系统层面生效的值。你也可以在 \
Ceph 配置文件中将它设置为某一个实例生效。

一旦你在 Ceph 配置文件中修改了你的bucket分片设置，你需要重启网关。\
在 Red Hat Enterprise Linux 请执行::

 sudo systemctl restart ceph-radosgw.service

在 Ubuntu 上请执行::

 sudo service radosgw restart id=rgw.<short-hostname>

对于异地场景的配置而言，为了灾备每一个 zone 都有一个不同的 ``index_pool`` \
设置。为了保持这个参数在一个 region 的所有 zone 中保持一致，你可以在 \
region 的网关配置中指定 ``rgw_override_bucket_index_max_shards`` 。举\
例如下::

  radosgw-admin region get > region.json

打开 ``region.json`` 的文件，为每一个 zone 编辑 ``bucket_index_max_shards`` \
的设置。保存 ``region.json`` 文件并重置 region。举例如下::

   radosgw-admin region set < region.json

一旦你更新了你的 region，你需要更新 region map。举例如下::

   radosgw-admin regionmap update --name client.rgw.ceph-client

其中的 ``client.rgw.ceph-client`` 是网关用户的名字。

.. note:: 通过 CRUSH 规则集将索引资源池 (如果可以为每一个zone设置) 映射到基于 SSD\
          的 OSD 上也能够提升 bucket 索引的性能。

给 DNS 添加泛域名解析
-------------------

为了通过 S3 风格的子域名来使用 Ceph(如：bucket-name.domain-name.com)，\
你应该给你的 ``ceph-radosgw`` 守护进程所在服务器在 DNS 服务器上给它的 DNS \
记录添加泛域名解析。

这个 DNS 地址也必须在 Ceph 配置文件中通过 ``rgw dns name = {hostname}`` \
设置项来指定。

对于 ``dnsmasq`` 而言，通过在主机名前添加点号 (.) 来实现添加 DNS 地址设置::

 address=/.{hostname-or-fqdn}/{host-ip-address}

举例如下::

 address=/.gateway-node1/192.168.122.75


对于 ``bind`` 而言，给 DNS 记录添加一个泛域名解析。举例如下::

 $TTL    604800
 @       IN      SOA     gateway-node1. root.gateway-node1. (
                               2         ; Serial
                          604800         ; Refresh
                           86400         ; Retry
                         2419200         ; Expire
                          604800 )       ; Negative Cache TTL
 ;
 @       IN      NS      gateway-node1.
 @       IN      A       192.168.122.113
 *       IN      CNAME   @

重启你的 DNS 服务，然后使用子域名 ping 你的服务器来确保你的 ``ceph-radosgw`` \
进程能够出来子域名请求::

 ping mybucket.{hostname}

举例如下::

 ping mybucket.gateway-node1

开启 Debugging (如果需要)
-------------------------

一旦你完成了安装过程，如果在你的配置下遇到了问题，你可以在 Ceph 配合文\
件的 ``[global]`` 小节下面添加调试选项，然后重启网关服务，进而帮助解决\
配置过程出现的问题。例如::

 [global]
 #append the following in the global section.
 debug ms = 1
 debug rgw = 20

使用网关
-----------------

为了使用 REST 接口，首先需要为S3接口创建一个初始 Ceph 对象网关用户。然\
后，为 Swift 接口创建一个子用户。然后你需要验证创建的用户是否能够访问\
网关。

为 S3 访问创建 RADOSGW 用户
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

一个``radosgw`` 用户需要被新建并被分配权限。命令 ``man radosgw-admin`` \
会提供该命令的额外信息。

为了新建用户，在 ``gateway host`` 上执行下面的命令::

 sudo radosgw-admin user create --uid="testuser" --display-name="First User"

命令的输出跟下面的类似::

 {
	 "user_id": "testuser",
	 "display_name": "First User",
	 "email": "",
	 "suspended": 0,
	 "max_buckets": 1000,
	 "auid": 0,
	 "subusers": [],
	 "keys": [{
		 "user": "testuser",
		 "access_key": "I0PJDPCIYZ665MW88W9R",
		 "secret_key": "dxaXZ8U90SXydYzyS5ivamEP20hkLSUViiaR+ZDA"
	 }],
	 "swift_keys": [],
	 "caps": [],
	 "op_mask": "read, write, delete",
	 "default_placement": "",
	 "placement_tags": [],
	 "bucket_quota": {
		 "enabled": false,
		 "max_size_kb": -1,
		 "max_objects": -1
	 },
	 "user_quota": {
		 "enabled": false,
		 "max_size_kb": -1,
		 "max_objects": -1
	 },
	 "temp_url_keys": []
 }

.. note:: 其中 ``keys->access_key`` 和``keys->secret_key`` 的值在访问\
   的时候需要用来做验证

.. important:: 请检查输出的 key。有个时候 ``radosgw-admin`` 会在生成的\
               JSON 中的 ``access_key`` 和和 ``secret_key`` 部分包含有\
               转义字符 ``\`` ，并且一些客户端不知道如何处理 JSON 中的\
               这个字符。补救措施包括移除 JSON 中的 ``\`` 字符，将该字\
               符串封装到引号中，重新生成这个 key 并确保不再包含 ``\`` ，\
               或者手动指定``access_key`` 和和 ``secret_key`` 。如果 \
               ``radosgw-admin`` 生成的 JSON 中的同一个key中包含转义字\
               符 ``\`` 同时包含有正斜杠 ``/`` 形如 ``\/`` ，请只移除 \
               JSON 转义字符 ``\`` ，不要删除正斜杠 ``/`` ，因为在 key \
               中它是一个有效字符。

新建一个 Swift 用户
^^^^^^^^^^^^^^^^^^^

如果你想要使用这种方式访问集群，你需要新建一个 Swift 子用户。创建 Swift \
用户包括两个步骤。第一步是创建用户。第二步是创建 secret key。

在``gateway host`` 上执行喜爱按的步骤:

新建 Swift 用户::

 sudo radosgw-admin subuser create --uid=testuser --subuser=testuser:swift --access=full

输出类似下面这样::

 {
	 "user_id": "testuser",
	 "display_name": "First User",
	 "email": "",
	 "suspended": 0,
	 "max_buckets": 1000,
	 "auid": 0,
	 "subusers": [{
		 "id": "testuser:swift",
		 "permissions": "full-control"
	 }],
	 "keys": [{
		 "user": "testuser:swift",
		 "access_key": "3Y1LNW4Q6X0Y53A52DET",
		 "secret_key": ""
	 }, {
		 "user": "testuser",
		 "access_key": "I0PJDPCIYZ665MW88W9R",
		 "secret_key": "dxaXZ8U90SXydYzyS5ivamEP20hkLSUViiaR+ZDA"
	 }],
	 "swift_keys": [],
	 "caps": [],
	 "op_mask": "read, write, delete",
	 "default_placement": "",
	 "placement_tags": [],
	 "bucket_quota": {
		 "enabled": false,
		 "max_size_kb": -1,
		 "max_objects": -1
	 },
	 "user_quota": {
		 "enabled": false,
		 "max_size_kb": -1,
		 "max_objects": -1
	 },
	 "temp_url_keys": []
  }

新建 secret key::

 sudo radosgw-admin key create --subuser=testuser:swift --key-type=swift --gen-secret

输出类似下面这样::

 {
	 "user_id": "testuser",
	 "display_name": "First User",
	 "email": "",
	 "suspended": 0,
	 "max_buckets": 1000,
	 "auid": 0,
	 "subusers": [{
		 "id": "testuser:swift",
		 "permissions": "full-control"
	 }],
	 "keys": [{
		 "user": "testuser:swift",
		 "access_key": "3Y1LNW4Q6X0Y53A52DET",
		 "secret_key": ""
	 }, {
		 "user": "testuser",
		 "access_key": "I0PJDPCIYZ665MW88W9R",
		 "secret_key": "dxaXZ8U90SXydYzyS5ivamEP20hkLSUViiaR+ZDA"
	 }],
	 "swift_keys": [{
		 "user": "testuser:swift",
		 "secret_key": "244+fz2gSqoHwR3lYtSbIyomyPHf3i7rgSJrF\/IA"
	 }],
	 "caps": [],
	 "op_mask": "read, write, delete",
	 "default_placement": "",
	 "placement_tags": [],
	 "bucket_quota": {
		 "enabled": false,
		 "max_size_kb": -1,
		 "max_objects": -1
	 },
	 "user_quota": {
		 "enabled": false,
		 "max_size_kb": -1,
		 "max_objects": -1
	 },
	 "temp_url_keys": []
 }

访问验证
^^^^^^^^^^^^^^^^^^^

测试 S3 访问
""""""""""""""

为了验证 S3 访问，你需要编写并运行一个 Python 测试脚本。S3 访问测试脚\
本将连接 ``radosgw``, 新建一个新的 bucket 并列出所有的 buckets。 ``aws_access_key_id`` \
和 ``aws_secret_access_key`` 的值来自于命令``radosgw_admin`` 的返回值 \
``access_key`` 和 ``secret_key`` 。

执行下面的步骤:

#. 你需要安装 ``python-boto`` 包::

    sudo yum install python-boto

#. 新建 Python 脚本文件::

    vi s3test.py

#. 将下面的内容添加到文件中::

    import boto
    import boto.s3.connection

    access_key = 'I0PJDPCIYZ665MW88W9R'
    secret_key = 'dxaXZ8U90SXydYzyS5ivamEP20hkLSUViiaR+ZDA'
    conn = boto.connect_s3(
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            host = '{hostname}', port = {port},
            is_secure=False, calling_format = boto.s3.connection.OrdinaryCallingFormat(),
            )

    bucket = conn.create_bucket('my-new-bucket')
        for bucket in conn.get_all_buckets():
                print "{name}".format(
                        name = bucket.name,
                        created = bucket.creation_date,
     )

   将 ``{hostname}`` 替换为你配置了网关服务的节点的主机名。比如 \
   ``gateway host``. 将 {port} 替换为 Civetweb 所使用的端口。

#. 运行脚本::

    python s3test.py

   输出类似下面的内容::

    my-new-bucket 2015-02-16T17:09:10.000Z

测试 swift 访问
"""""""""""""""""

Swift 访问的验证则可以使用``swift`` 的命令行客户端。可以通过命令 \
``man swift`` 获取更多命令行选项的更多信息。

执行下面的命令安装 ``swift`` 客户端，在 Red Hat Enterprise Linux上执行::

 sudo yum install python-setuptools
 sudo easy_install pip
 sudo pip install --upgrade setuptools
 sudo pip install --upgrade python-swiftclient

在基于 Debian 的发行版上执行::

 sudo apt-get install python-setuptools
 sudo easy_install pip
 sudo pip install --upgrade setuptools
 sudo pip install --upgrade python-swiftclient

执行下面的命令验证 swift 访问::

 swift -A http://{IP ADDRESS}:{port}/auth/1.0 -U testuser:swift -K '{swift_secret_key}' list

使用网关服务器的外网 IP 地址替换其中的 ``{IP ADDRESS}`` ，使用新建 \
``swift`` 用户时执行的命令 ``radosgw-admin key create`` 的输出替换其中\
的 ``{swift_secret_key}`` 。使用你的 Civetweb 所使用的端口替换其中 \
{port} ，比如默认是 ``7480`` 。如果你不替换这个端口，它的默认值是 ``80``.
举例如下::

 swift -A http://10.19.143.116:7480/auth/1.0 -U testuser:swift -K '244+fz2gSqoHwR3lYtSbIyomyPHf3i7rgSJrF/IA' list

输出类似下面这样::

 my-new-bucket

.. _环境检查:  ../../start/quick-start-preflight

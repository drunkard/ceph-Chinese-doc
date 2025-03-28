.. _mon-dns-lookup:

=====================
 通过 DNS 查询监视器
=====================
.. Looking up Monitors through DNS

从 11.0.0 (Kraken) 版起， RADOS 支持通过 DNS 查询监视器。

这样的话，守护进程和客户端们的 ``ceph.conf``
配置文件里就不需要 *mon host* 配置了。

更新了 DNS ，客户端们和守护进程们就能注意到监视器拓扑的变化。
说得更精确、更专业一些，
客户端们通过 ``DNS SRV TCP`` 记录来查询监视器。

默认情况下，客户端和守护进程会查询名为 *ceph-mon* 的 TCP 服务，
它是通过 *mon_dns_srv_name* 选项配置的。

.. confval:: mon_dns_srv_name

.. note:: Instead of using a DNS search domain, it is possible to manually
   designate the search domain by passing the search domain's name followed by
   an underscore to ``mon_dns_srv_name``. The syntax for this is
   ``<service-name>_<upper-level-domain>``. For example, passing
   ``ceph-mon_example.com`` will direct Ceph to look for the ``SRV`` record at
   ``_ceph-mon._tcp.example.com``.


实例
----

假设 DNS 域名是 *example.com* ，域文件内可加上如下配置。

首先，创建监视器的相关记录，可以是 IPv4 (A) 或 IPv6 (AAAA) 的。

::

    mon1.example.com. AAAA 2001:db8::100
    mon2.example.com. AAAA 2001:db8::200
    mon3.example.com. AAAA 2001:db8::300

::

    mon1.example.com. A 192.168.0.1
    mon2.example.com. A 192.168.0.2
    mon3.example.com. A 192.168.0.3

这些记录配置好后，我们用 *ceph-mon* 名字创建 SRV TCP 记录，
分别指向三个监视器。

::

    _ceph-mon._tcp.example.com. 60 IN SRV 10 20 6789 mon1.example.com.
    _ceph-mon._tcp.example.com. 60 IN SRV 10 30 6789 mon2.example.com.
    _ceph-mon._tcp.example.com. 60 IN SRV 20 50 6789 mon3.example.com.

此时，所有监视器都运行在 *6789* 端口上，它们的优先级分别是
10 、 10 、 20 ，权重分别是 20 、 30 、 50 。

监视器客户端根据 SRV 记录选择监视器，如果集群内多个监视器的 SRV 记录的优先级相同，
客户端和守护进程们将会按照 SRV 权重字段的数值、把负载均衡地分布到各监视器。

在上面的例子中，结果会是大约 40% 的客户端和守护进程连接到 mon1 、 60% 的连接到 mon2 。
然而，如果它俩都连不上， mon3 就作为备机上场。

参阅 `Messenger v2 <msgr2>`_ 。

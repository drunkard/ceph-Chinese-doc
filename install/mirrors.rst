===========
 Ceph 镜像
===========
.. Ceph Mirrors

为提升用户体验，世界各地有多个 Ceph 镜像。

这些镜像是愿意支持 Ceph 的多家公司慷慨解囊资助的。


位置
----
.. Locations

这些镜像位于如下地点：

- **EU: 荷兰**: http://eu.ceph.com/
- **AU: 澳大利亚**: http://au.ceph.com/
- **SE: 瑞典**: http://se.ceph.com/
- **DE: 德国**: http://de.ceph.com/
- **FR: 法国**: http://fr.ceph.com/
- **UK: 英国**: http://uk.ceph.com
- **US-Mid-West: 芝加哥**: http://mirrors.gigenet.com/ceph/
- **US-West: 美国西海岸**: http://us-west.ceph.com/
- **CN: 中国**: http://mirrors.ustc.edu.cn/ceph/

你可以把所有的 download.ceph.com URL 替换成任意镜像，例如：

- http://download.ceph.com/tarballs/
- http://download.ceph.com/debian-hammer/
- http://download.ceph.com/rpm-hammer/

可以改成：

- http://eu.ceph.com/tarballs/
- http://eu.ceph.com/debian-hammer/
- http://eu.ceph.com/rpm-hammer/


建镜像点
========

你自己可以用 Bash 脚本和 rsync 建 Ceph 镜像，很简单。
`Github`_ 上也有个易用的脚本。

镜像 Ceph 时，请遵守如下守则：

- 选择离你近的镜像
- 同步间隔不要小于 3 小时
- 别在一小时的 0 分开始同步，在 0 到 59 之间随机选一个


申请官方镜像
============

如果你想为其他 Ceph 用户提供一个公共镜像，你可以选择成为官方\
镜像。

为确保所有镜像都符合相同的标准，所有镜像站点都需符合一定的要\
求。具体信息在 `Github`_ 上有。

如果你想申请成为官方镜像，请联系 ceph-users 邮件列表。


.. _Github: https://github.com/ceph/ceph/tree/master/mirroring

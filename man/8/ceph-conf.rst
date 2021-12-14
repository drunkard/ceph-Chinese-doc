:orphan:

================================
 ceph-conf -- ceph 配置文件工具
================================

.. program:: ceph-conf

提纲
====

| **ceph-conf** -c *conffile* --list-all-sections
| **ceph-conf** -c *conffile* -L
| **ceph-conf** -c *conffile* -l *prefix*
| **ceph-conf** *key* -s *section1* ...
| **ceph-conf** [-s *section* ] [-r] --lookup *key*
| **ceph-conf** [-s *section* ] *key*


描述
====

**ceph-conf** 是用来从 Ceph 配置文件获取信息的工具。
像大多数 Ceph 程序一样，
你可以用 ``-c`` 选项指定 Ceph 配置文件。

注意，不像其它 ceph 工具， **ceph-conf** *只能*\
读取配置文件（或返回内置的默认值），
它\ *不会*\ 从监视器集群获取配置值。
正因为如此，我们建议只在严格基于配置文件的旧环境下用 **ceph-conf** 。
新部署的和工具们都依赖于向监视器查询配置
（如 ``ceph config get <daemon> <option>`` ）或\
用守护进程自身来获取有效的配置选项
（如 ``ceph-osd -i 123 --show-config-value osd_data`` ）。
后一种途径更好，可以从内置默认值
（有时候与别的守护进程相差巨大）、
配置文件、和监视器的配置数据库中汇总出\
此守护进程启动时到底会用哪个值。


功能
====

**ceph-conf** 可执行以下功能之一：

.. option:: -L, --list-all-sections

   列举配置文件中所有的段落名字。

.. option:: -l, --list-sections *prefix*

   列举包含指定前缀的所有段落。例如， ``--list-sections mon``
   会罗列出所有以 ``mon`` 打头的段落。

.. option:: --lookup *key*

   搜寻并打印指定的配置信息。注：
   ``--lookup`` 是默认动作。
   如果没在命令行上指定其它动作，那就默认为查找。

.. option:: -h, --help

   打印用法摘要。


选项
====

.. option:: -c *conffile*

   指定 Ceph 配置文件。

.. option:: --filter-key *key*

   过滤段落列表，只留下与 *key* 匹配的段落。

.. option:: --filter-key-value *key* ``=`` *value*

   过滤段落列表，只留下与 *key*/*value* 对匹配的段落。

.. option:: --name *type.id*

   指定要搜寻段落的 Ceph 名字（默认为 client.admin ）。
   例如指定 ``--name osd.0`` 的话，
   将搜寻 [osd.0] 、 [osd] 、 [global] 。

.. option:: --pid *pid*

   展开选项时覆盖 ``$pid`` 。例如，
   如果一个选项配置成了 ``/var/log/$name.$pid.log`` ，
   它的值里的 ``$pid`` 部分将会被 **ceph-conf** 的 PID 替换掉，
   而不是用 ``--name`` 选项指定的进程的 PID 。

.. option:: -r, --resolve-search

   从生成的、逗号分隔的搜索列表中找出第一个存在、
   并可以打开的文件。

.. option:: --section, -s

   额外指定要搜寻的段落，
   这些段落优先于正常搜索范围。
   同样，它会返回先匹配到的条目。


实例
====

要查明 osd 0 的 ``osd data`` 选项会用什么值： ::

        ceph-conf -c foo.conf --name osd.0 --lookup "osd data"

要查明 mds a 的 ``log file`` 选项会用什么值： ::

        ceph-conf -c foo.conf --name mds.a "log file"

要罗列以 "osd" 打头的所有段落： ::

        ceph-conf -c foo.conf -l osd

要罗列所有段落： ::

        ceph-conf -c foo.conf -L

要打印 "client.0" 所使用的 "keyring" 的路径： ::

	ceph-conf --name client.0 -r -l keyring


相关文件
========

``/etc/ceph/$cluster.conf``, ``~/.ceph/$cluster.conf``, ``$cluster.conf``

没指定的话就用这些 Ceph 配置文件。


使用范围
========

**ceph-conf** 是 Ceph 的一部分，这是个伸缩力强、开源、分布式\
的存储系统，更多信息参见 https://docs.ceph.com 。



参考
====

:doc:`ceph <ceph>`\(8),

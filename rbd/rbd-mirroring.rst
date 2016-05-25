=========
 RBD 镜像
=========

.. index:: Ceph Block Device; mirroring

可以在两个 Ceph 集群中异步备份 RBD images。该能力利用了 RBD image 的日志特性，\
以确保集群间的副本崩溃一致性。镜像功能需要在同伴集群（ peer clusters ）中的每一\
个对应的 pool 上进行配置，可设定自动备份某个存储池内的所有 images 或仅备份 \
images 的一个特定子集。用 ``rbd`` 命令来配置镜像功能。 ``rbd-mirror`` 守护进程\
负责从远端集群拉取 image 的更新，并写入本地集群的对应 image 中。

.. note:: RBD 镜像功能需要 Ceph Jewel 或更新的发行版本。

.. important:: 要使用 RBD 镜像功能，你必须有 2 个 Ceph 集群， 每个集群都要运行 \
   ``rbd-mirror`` 守护进程。

存储池配置
==========

下面的程序说明了如何执行一些基本的管理工作，来用 ``rbd`` 命令配置镜像功能。\
镜像功能是在 Ceph 集群内的存储池级别上配置的。

配置存储池的步骤需要在 2 个同伴集群内都执行一遍。为清楚起见，下面的步骤假定\
这两个集群分别叫做“本地（local）”和“远端（remote）”，而且单主机对这 2 个集群\
都拥有访问权。

如何连接不同的 Ceph 集群，详情可参考 \ `rbd`_\  手册页。 

.. note:: 在下面的例子中，集群名称和 Ceph 配置文件的名称相同（比如 /etc/ceph\
   /remote.conf）。可参考 \ `ceph-conf`_\  文档来配置多集群环境。

启用镜像功能
------------

使用 ``rbd`` 启用某个存储池的镜像功能，需要指定 ``mirror pool enable`` \
命令，存储池名和镜像模式： ::

        rbd mirror pool enable {pool-name} {mode}

镜像模式可以是 ``pool`` 或 ``image``：

* **pool**：当设定为 ``pool`` 模式，存储池中所有开启了日志特性的 images 都会被备份。
* **image**：当设定为 ``image`` 模式，需要对每个 image \ `显式启用`_\ 镜像功能。

例如： ::

        rbd --cluster local mirror pool enable image-pool pool
        rbd --cluster remote mirror pool enable image-pool pool

禁用镜像功能
------------

使用 ``rbd`` 禁用某个存储池的镜像功能，需要指定 ``mirror pool disable`` 命令\
和存储池名： ::

        rbd mirror pool disable {pool-name}

当采用这种方式禁用某个存储池的镜像功能时，存储池内的任一个 image 的镜像功能也\
会被禁用，即使曾显式启用过。

例如： ::

        rbd --cluster local mirror pool disable image-pool
        rbd --cluster remote mirror pool disable image-pool

添加同伴集群
------------

为了使 ``rbd-mirror`` 守护进程发现它的同伴集群，需要向存储池注册。使用 ``rbd`` \
添加同伴 Ceph 集群，需要指定 ``mirror pool peer add`` 命令、存储池名和集群说明： ::

        rbd mirror pool peer add {pool-name} {client-name}@{cluster-name}

例如： ::

        rbd --cluster local mirror pool peer add image-pool client.remote@remote
        rbd --cluster remote mirror pool peer add image-pool client.local@local

移除同伴集群
------------

使用 ``rbd`` 移除同伴 Ceph 集群，指定 ``mirror pool peer remove`` 命令、存储池名\
和同伴的 UUID（可通过 ``rbd mirror pool info`` 命令获取）： ::

        rbd mirror pool peer remove {pool-name} {peer-uuid}

例如： ::

        rbd --cluster local mirror pool peer remove image-pool 55672766-c02b-4729-8567-f13a66893445
        rbd --cluster remote mirror pool peer remove image-pool 60c0e299-b38f-4234-91f6-eed0a367be08

Image 配置
==========

不同于存储池配置，image 配置只需针对单个 Ceph 集群操作。

镜像 RBD image 被指定为主镜像或者副镜像。这是 image 而非存储池的特性。被指定为副\
镜像的 image 不能被修改。

当一个 image 首次启用镜像功能时（存储池的镜像模式设为 **pool** 且启用了该 image \
的日志特性，或者通过 ``rbd`` 命令\ `显式启用`_\ ），它会自动晋升为主镜像。

启用 Image 的日志支持
---------------------

RBD 镜像功能使用了 RBD 日志特性，来保证 image 副本间的崩溃一致性。在备份 image 到\
另一个同伴集群前，必须启用日志特性。该特性可在使用 ``rbd`` 命令创建 image 时通过\
指定 ``--image-feature exclusive-lock,journaling`` 选项来启用。

或者，可以动态启用已有 image 的日志特性。使用 ``rbd`` 开启日志特性，需要指定 \
``feature enable`` 命令，存储池名，image 名和特性名： ::

        rbd feature enable {pool-name}/{image-name} {feature-name}

例如： ::

        rbd --cluster local feature enable image-pool/image-1 journaling

.. note:: 日志特性依赖于独占锁（exclusive-lock）特性。如果没有启用独占锁，则必须\
   在启用日志特性之前先启用独占锁。

.. tip:: 你可以通过在 Ceph 配置文件中增加 ``rbd default features = 125`` ，使得所\
   有新建 image 默认启用日志特性。

启用 Image 镜像功能
-------------------

如果把某个存储池的镜像功能配置为 ``image`` 模式，还需要对存储池中的每一个 image ，\
明确启用镜像功能。通过 ``rbd`` 启用某个特定 image 的镜像功能，要指定 \
``mirror image enable`` 命令、存储池名和 image 名： ::

        rbd mirror image enable {pool-name}/{image-name}

例如： ::

        rbd --cluster local mirror image enable image-pool/image-1

禁用 Image 镜像功能
-------------------

通过 ``rbd`` 禁用某个特定 image 的镜像功能，要指定 ``mirror image disable`` 命令、\
存储池名和 image 名： ::

        rbd mirror image disable {pool-name}/{image-name}

例如： ::

        rbd --cluster local mirror image disable image-pool/image-1

Image 的升级与降级
------------------

在需要把主名称转移到同伴 Ceph 集群这样一个故障切换场景中，应该停止所有对主 image \
的访问（比如关闭 VM 的电源或移除 VM 的相关驱动），当前的主 image 降级为副，\
原副 image 升级为主，然后在备份集群上恢复对该 image 访问。

.. note:: RBD 仅提供了一些必要的工具来帮助 image 有序的故障切换。还需要一种外部机制来\
   协调整个故障切换流程（比如在降级之前关闭 image）。

通过 ``rbd`` 降级主 image，需要指定 ``mirror image demote`` 命令、存储池名和 image \
名： ::

        rbd mirror image demote {pool-name}/{image-name}

例如： ::

        rbd --cluster local mirror image demote image-pool/image-1

通过 ``rbd`` 升级副 image，需要指定 ``mirror image promote`` 命令、存储池名和 image \
名： ::

        rbd mirror image promote {pool-name}/{image-name}

例如： ::

        rbd --cluster remote mirror image promote image-pool/image-1

.. tip:: 由于主 / 副状态是对于每个 image 而言的，故可以让两个集群拆分 IO 负载来进行\
   故障切换 / 故障自动恢复。

.. note:: 可以使用 ``--force`` 选项来强制升级。当降级要求不能被正确传播到同伴 Ceph \
   集群的时候（比如 Ceph 集群故障，通信中断），就需要强制升级。这会导致两个集群间的\
   脑裂，而且在调用\ `强制重新同步命令`_\ 之前，image 将不会自动同步。

强制 Image 重新同步
-------------------

如果 ``rbd-daemon`` 探测到了脑裂事件，它在此情况得到纠正之前，是不会尝试去备份受到影\
响的 image。为了恢复对 image 的镜像备份，首先判定\ `降级 image`_\  已经过时，然后向主 \
image 请求重新同步。 通过 ``rbd`` 重新同步 image，需要指定 ``mirror image resync`` 命\
令、存储池名和 image 名： ::

        rbd mirror image resync {pool-name}/{image-name}

例如： ::

        rbd mirror image resync image-pool/image-1

.. note:: 此条 ``rbd`` 命令仅标记了某 image 需要重新同步。本地集群的 ``rbd-mirror`` \
   守护进程会异步实施真正的重新同步过程。

rbd-mirror 守护进程
===================

有两个 ``rbd-mirror`` 守护进程负责监控远端同伴集群的 image 日志，并针对本地集群进行\
日志重放。RBD image 日志特性会按发生的顺序记录下对该 image 的所有修改。这保证了远端 \
image 的崩溃一致性镜像在本地是可用的。

通过安装可选发行包 ``rbd-mirror`` 来获取 ``rbd-mirror`` 守护进程。

.. important:: 每一个 ``rbd-mirror`` 守护进程需要同时连接本地和远程集群。
.. warning:: 每个 Ceph 集群只能运行一个 ``rbd-mirror`` 守护进程。将来的 Ceph 发行版\
   将会支持对 ``rbd-mirror`` 守护进程进行水平扩展。

.. _rbd: ../../man/8/rbd
.. _ceph-conf: ../../rados/configuration/ceph-conf/#running-multiple-clusters
.. _显式启用: #启用-image-镜像功能
.. _强制重新同步命令: #强制-image-重新同步
.. _降级 image: #image-的升级与降级

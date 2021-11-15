==============
 MDS 配置参考
==============

``mds cache memory limit``

:描述: MDS 对其缓存内存的硬限制。
:类型:  64-bit Integer Unsigned
:默认值: ``4G``


``mds cache reservation``

:描述: MDS 缓存（子系统）要维持的保留缓存空间。 MDS 一旦开始\
       恢复其缓存保留值，它会回调客户端状态，直到它的缓存尺寸\
       也缩减到空出保留值。
:类型:  Float
:默认值: ``0.05``


``mds cache mid``

:描述: 把新条目插入缓存 LRU 时的插入点（从顶端）。
:类型:  Float
:默认值: ``0.7``


``mds dir commit ratio``

:描述: 目录的脏到什么程度时做完全更新（而不是部分更新）。
:类型:  Float
:默认值: ``0.5``


``mds dir max commit size``

:描述: 一个目录更新超过多大时要拆分为较小的事务（ MB ）。
:类型:  32-bit Integer
:默认值: ``90``


``mds decay halflife``

:描述: MDS 缓存热度的半衰期。
:类型:  Float
:默认值: ``5``


``mds beacon interval``

:描述: 标识消息发送给监视器的频率，秒。
:类型:  Float
:默认值: ``4``


``mds beacon grace``

:描述: 多久没收到标识消息就认为 MDS 落后了（并可能替换它）。
:类型:  Float
:默认值: ``15``


``mds blocklist interval``

:描述: OSD 运行图里的 MDS 失败后，把它留在黑名单里的时间。\
       注意，此选项控制着失败的 OSD 在 OSDMap 黑名单里呆多长\
       时间，它对管理员手动加进黑名单的东西没影响。例如，
       ``ceph osd blocklist add`` 仍将遵循默认的黑名单时间。
:类型:  Float
:默认值: ``24.0*60.0``


``mds reconnect timeout``

:描述: MDS 重启期间客户端等待时间，秒。
:类型:  Float
:默认值: ``45``


``mds tick interval``

:描述: MDS 执行内部周期性任务的间隔。
:类型:  Float
:默认值: ``5``


``mds dirstat min interval``

:描述: 在目录树中递归地查找目录信息的最小间隔，秒。
:类型:  Float
:默认值: ``1``


``mds scatter nudge interval``

:描述: dirstat 变更传播多快。
:类型:  Float
:默认值: ``5``


``mds client prealloc inos``

:描述: 为每个客户端会话预分配的索引节点数。
:类型:  32-bit Integer
:默认值: ``1000``


``mds early reply``

:描述: 请求结果成功提交到日志前是否应该先展示给客户端。
:类型:  Boolean
:默认值: ``true``


``mds default dir hash``

:描述: 用于哈希文件在目录中分布情况的函数。
:类型:  32-bit Integer
:默认值: ``2`` (i.e., rjenkins)


``mds log skip corrupt events``

:描述: 在日志重放时， MDS 是否应跳过损坏的日志事件。
:类型:  Boolean
:默认值:  ``false``


``mds log max events``

:描述: 日志里的事件达到多少时开始裁剪，设为 ``-1`` 取消限制。
:类型:  32-bit Integer
:默认值: ``-1``


``mds log max segments``

:描述: 日志里的片段（对象）达到多少时开始裁剪，设为 ``-1`` 取消限制。
:类型:  32-bit Integer
:默认值: ``30``


``mds bal sample interval``

:描述: 对目录热度取样的频率（碎片粒度）。
:类型:  Float
:默认值: ``3``


``mds bal replicate threshold``

:描述: 达到多大热度时 Ceph 就把元数据复制到其它节点。
:类型:  Float
:默认值: ``8000``


``mds bal unreplicate threshold``

:描述: 热度低到多少时 Ceph 就不再把元数据复制到其它节点。
:类型:  Float
:默认值: ``0``


``mds bal split size``

:描述: 目录尺寸大到多少时 MDS 就把片段拆分成更小的片段。
:类型:  32-bit Integer
:默认值: ``10000``


``mds bal split rd``

:描述: 目录的最大读取热度达到多大时 Ceph 将拆分此片段。
:类型:  Float
:默认值: ``25000``


``mds bal split wr``

:描述: 目录的最大写热度达到多大时 Ceph 将拆分此片段。
:类型:  Float
:默认值: ``10000``


``mds bal split bits``

:描述: 把一个目录片段再分割成多大。
:类型:  32-bit Integer
:默认值: ``3``


``mds bal merge size``

:描述: 目录尺寸小到多少时 Ceph 就把它合并到邻近目录片段。
:类型:  32-bit Integer
:默认值: ``50``


``mds bal interval``

:描述: MDS 服务器负荷交换频率，秒。
:类型:  32-bit Integer
:默认值: ``10``


``mds bal fragment interval``

:描述: 一个片段可以被拆分或合并，在执行分片变更前延迟的时间，\
       单位为秒。
:类型:  32-bit Integer
:默认值: ``5``


``mds bal fragment fast factor``

:描述: 分片的尺寸超过拆分尺寸阈值达到多少比例就立即执行拆分（\
       跳过 fragment interval 配置的延时）。
:类型:  Float
:默认值: ``1.5``


``mds bal fragment size max``

:描述: 片段的最大尺寸，要加入新条目时会收到 ENOSPC 拒绝代码。
:类型:  32-bit Integer
:默认值: ``100000``


``mds bal idle threshold``

:描述: 热度低于此值时 Ceph 把子树迁移回父节点。
:类型:  Float
:默认值: ``0``


``mds bal max``

:描述: 均衡器迭代到此数量时 Ceph 就停止（仅适用于测试）。
:类型:  32-bit Integer
:默认值: ``-1``


``mds bal max until``

:描述: 均衡器运行多久就停止（仅适用于测试）。
:类型:  32-bit Integer
:默认值: ``-1``


``mds bal mode``

:描述: 计算 MDS 负载的方法。

       - ``0`` = 混合；
       - ``1`` = 请求速率和延时；
       - ``2`` = CPU 负载。

:类型:  32-bit Integer
:默认值: ``0``


``mds bal min rebalance``

:描述: 子树热度最小多少时开始迁移。
:类型:  Float
:默认值: ``0.1``


``mds bal min start``

:描述: 子树热度最小多少时 Ceph 才去搜索。
:类型:  Float
:默认值: ``0.2``


``mds bal need min``

:描述: 接受的最小目标子树片段。
:类型:  Float
:默认值: ``0.8``


``mds bal need max``

:描述: 目标子树片段的最大尺寸。
:类型:  Float
:默认值: ``1.2``


``mds bal midchunk``

:描述: 尺寸大于目标子树片段的子树， Ceph 将迁移它。
:类型:  Float
:默认值: ``0.3``


``mds bal minchunk``

:描述: 尺寸小于目标子树片段的子树， Ceph 将忽略它。
:类型:  Float
:默认值: ``0.001``


``mds bal target removal min``

:描述: Ceph 从 MDS 运行图中剔除旧数据前，均衡器至少递归多少次。
:类型:  32-bit Integer
:默认值: ``5``


``mds bal target removal max``

:描述: Ceph 从MDS运行图中剔除旧数据前，均衡器最多递归多少次。
:类型:  32-bit Integer
:默认值: ``10``


``mds replay interval``

:描述: MDS 处于 standby-replay 模式（热备）下时的日志滚动间隔。
:类型:  Float
:默认值: ``1``


``mds shutdown check``

:描述: MDS 关闭期间缓存更新间隔。
:类型:  32-bit Integer
:默认值: ``0``


``mds thrash exports``

:描述: Ceph 会把子树随机地在节点间迁移。（仅用于测试）
:类型:  32-bit Integer
:默认值: ``0``


``mds thrash fragments``

:描述: Ceph 会随机地分片或合并目录。
:类型:  32-bit Integer
:默认值: ``0``


``mds dump cache on map``

:描述: Ceph 会把各 MDSMap 的 MDS 缓存内容转储到一文件。
:类型:  Boolean
:默认值:  ``false``


``mds dump cache after rejoin``

:描述: Ceph 重新加入缓存（恢复期间）后会把 MDS 缓存内容转储到一文件。
:类型:  Boolean
:默认值:  ``false``


``mds verify scatter``

:描述: Ceph 将把各种传播/聚集常量声明为true（仅适合开发者）。
:类型:  Boolean
:默认值:  ``false``


``mds debug scatterstat``

:描述: Ceph 将把各种递归统计常量声明为 ``true`` （仅适合开发者）。
:类型:  Boolean
:默认值:  ``false``


``mds debug frag``

:描述: Ceph 将在方便时校验目录分段（仅适合开发者）。
:类型:  Boolean
:默认值:  ``false``


``mds debug auth pins``

:描述: 常量 debug auth pin （仅适合开发者）。
:类型:  Boolean
:默认值:  ``false``


``mds debug subtrees``

:描述: 常量 debug subtree （仅适合开发者）。
:类型:  Boolean
:默认值:  ``false``


``mds kill mdstable at``

:描述: Ceph 将向 MDSTable 代码注入 MDS 失败事件（仅适合开发者）。
:类型:  32-bit Integer
:默认值: ``0``


``mds kill export at``

:描述: Ceph 将向子树出口代码注入 MDS 失败事件（仅适合开发者）。
:类型:  32-bit Integer
:默认值: ``0``


``mds kill import at``

:描述: Ceph 将向子树入口代码注入 MDS 失败事件（仅适合开发者）。
:类型:  32-bit Integer
:默认值: ``0``


``mds kill link at``

:描述: Ceph 将向硬链接代码注入 MDS 失败事件（仅适合开发者）。
:类型:  32-bit Integer
:默认值: ``0``


``mds kill rename at``

:描述: Ceph 将向重命名代码注入 MDS 失败事件（仅适合开发者）。
:类型:  32-bit Integer
:默认值: ``0``


``mds wipe sessions``

:描述: Ceph 将在启动时删除所有客户端会话（仅适合测试）。
:类型:  Boolean
:默认值: ``false``


``mds wipe ino prealloc``

:描述: Ceph 将在启动时删除索引节点号预分配元数据（仅适合测试）。
:类型:  Boolean
:默认值: ``false``


``mds skip ino``

:描述: 启动时要跳过的索引节点号数量（仅适合测试）。
:类型:  32-bit Integer
:默认值: ``0``


``mds min caps per client``

:描述: 设置一个客户端可以持有的最小容量。
:类型: Integer
:默认值: ``100``


``mds max ratio caps per client``

:描述: 设置在 MDS 缓存有压力时可以回调的、当前容量的最大比率。
:类型: Float
:默认值: ``0.8``

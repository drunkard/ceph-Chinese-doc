==============
 词语翻译惯例
==============

AMARK BMARK CMARK DMARK EMARK FMARK GMARK
HMARK IMARK JMARK KMARK LMARK MMARK NMARK
OMARK PMARK QMARK RMARK SMARK TMARK
UMARK VMARK WMARK XMARK YMARK ZMARK

标记符号含义：

- ``=>`` 表示正在更换翻译口径，如果您遇到请反馈给我。
- ``?``  表示尚未决定翻译还是不翻译。

.. glossary::

    access key
        访问密钥

    active-active
        (RGW) 多活

    active-passive
        (RGW) 主从

    active/standby
        活跃/备用

    advisory lock
        咨询锁
        https://www.cnblogs.com/wy123/archive/2020/08/14/13499526.html

    allocation-file
        分配信息文件
        BlueStore 内部的

    ancestor type
        父级类型

    array
        JSON 相关的为数组；

    assume role
        <暂未翻译>，AWS 术语。
        实操角色？它是执行实际任务时的角色。

    attach
        捆绑、绑
        s3: attach policy to role
        rbd -> qemu

    auth pinned
        加锁、锁定。
        资料： pinauth 口令认证。

    autoscaling
    autoscale
        自动伸缩，

    auxiliary device
        辅助设备。 BlueStore 术语，相对于 main device 。


    BMARK
    backfill
        回填

    backlog
        积压
        入栈但还没来得及处理的数据量、或最大空间。

    balancer
        均衡器、均化器？；
        active balancer 动态均衡器；

    beacon message
        信标消息
        MDS 和监视器之间发送的；

    behind shard
        落伍分片

    bitrot
        位翻转

    blocklist
        阻塞名单

    bootstrap
        自举引导

    bounce buffer
        回弹缓冲区。
        在早期的Linux内核(早期的2.4及先前的内核版本)中，设备驱动程序\
        无法直接访问高端内存中的虚址。换句话说，这些设备驱动程序无法对高端内存\
        执行直接内存访问I/O。相反，内核在低端内存中分配缓冲区，数据通过\
        内核缓冲区在高端内存和设备驱动程序之间传输。这个内核缓冲区通常称为\
        回弹缓冲区(bounce buffer)，该过程被称为回弹或回弹缓冲。

    bucket
    bucket index
    bucket policy
        桶、桶索引（ ``bi`` ）、桶策略

    bulk pool
        巨型池，一开始就拥有大量 PG 的存储池。


    CMARK
    cache reservation
        缓存预留量

    cache thrashing
        缓存颠簸。

    capability
        能力， cephfs 、 MDS 相关术语。本意是潜在能力。
        另一个常一起出现的 `release state (释放状态)` 。
        这里的 capability 和 state 都含有空间、容量的意思，只不过这个“内存空间”
        即使释放出来操作系统也不知道，还是 MDS 管理着。

    channel
        信道
        ``ceph --watch-channel cluster``
        可用信道有 cluster 、 audit 、 cephadm 、 * 表示所有

    chunk
        块、校验块。EC术语。

    clock drift
        时钟漂移

    clog
    cluster log
        集群日志（基础设施？）

    cluster map
        集群运行图

        释义：集群处于动态的运行中，配置会变更、 OSD 会 up/down ，所以把它理解\
        为静态的图是不对的；尤其对大型集群来说，当机、硬件故障是常态。但是在\
        理解、分析时，提取的片段都可以当作静态的，就像拍下的照片。

    colocating
        扎堆放置，把数据、 DB 、 WAL 都放在同一个硬盘上。

    column family
        列族。
        列族将相关的列（Column）分组在一起，存储在物理上连续的存储单元中，
        通常在底层文件系统或存储引擎中是连续存储的。这样，当你需要查询\
        某个列族的数据时，系统只需定位到这个列族所在的位置，而不用遍历整个表格，
        大大提高了查询效率。

        列族的概念使得分布式数据库能够更高效地存储和查询大规模数据，
        是分布式数据库中的重要设计原则之一。

    complete filter
        完整过滤器。 LDAP 术语，还有 partial filter

    compression hint
        压缩提示

    config-key
        <不翻译>，来自代码的名词

    corruption
        （数据）损坏

    crash-consistent
        崩溃一致

    CRUSH, Controlled Replication Under Scalable Hashing
        基于可伸缩哈希算法的受控复制
        RUSH, Replication Under Scalable Hashing, 基于可伸缩哈希算法的复制

    CRUSH map
        CRUSH 图


    DMARK
    deep copy
        深复制

    defer delete a block device
        延期删除一个块设备

    delta
        (pg) 增量

    demote (a image to non-primary)
        降级

    destroyed
        已销毁；
        OSD 状态，如 ``ceph osd destroy <id>`` 后的状态。

    device class
        设备类别

    device selector
        设备档位。一般翻译为设备选择器，但我觉得不够形象，它是设备树里面一个\
        定死的位置，这个位置有个编号，就像车的档位一样。

    discard
        <不翻译>，专业术语，尚未找到好译文。
        文件系统功能。

    display name
        显示名称，昵称。

        RGW 术语。

    down / up
        倒下、倒下了；起来了，活过来了；

    dump
        转储、倒出


    EMARK
    earmark
        <不翻译>。意思是标签，类似羊、兔子耳朵上打的标记。

    endpoint
        终结点

    ephemeral pinning
    ephemerally pinned
        临时挂单， CephFS 子树分区方面的术语；

        挂单是佛教术语，指行脚僧到寺院投宿；单，指僧堂里的名单；
        行脚僧把自己的衣挂在名单之下，故称挂单。

    epoch
        时间结 => <不翻译> ?

        epoch 原意是“新纪元，时代，时期，时间上的一点”，我想作者的意思大概就是\
        每隔一段时间总结一下，汇报下某段时间的事件。大概类似于朝代更迭，只是时\
        间短点而以。

        *last epoch start:*
        the last epoch at which all nodes in the acting set for a particular
        placement group agreed on an authoritative history. At this point,
        peering is deemed to have been successful.

        *last epoch clean:*
        the last epoch at which all nodes in the acting set for a particular
        placement group were completely up to date (both PG logs and object
        contents). At this point, recovery is deemed to have been completed.

    erasure coding
    erasure coded pool
        纠删码存储池

        Erasure coding (EC) is a method of data protection in which data is broken into fragments, expanded and encoded with redundant data pieces and stored across a set of different locations, such as disks, storage nodes or geographic locations.

        The goal of erasure coding is to enable data that becomes corrupted at some point in the disk storage process to be reconstructed by using information about the data that's stored elsewhere in the array.

        Erasure coding creates a mathematical function to describe a set of numbers so they can be checked for accuracy and recovered if one is lost. Referred to as polynomial interpolation or oversampling, this is the key concept behind erasure codes. In mathematical terms, the protection offered by erasure coding can be represented in simple form by the following equation: n = k + m. The variable “k” is the original amount of data or symbols. The variable “m” stands for the extra or redundant symbols that are added to provide protection from failures. The variable “n” is the total number of symbols created after the erasure coding process.

        For instance, in a 10 of 16 configuration, or EC 10/16, six extra symbols (m) would be added to the 10 base symbols (k). The 16 data fragments (n) would be spread across 16 drives, nodes or geographic locations. The original file could be reconstructed from 10 verified fragments.

        Erasure codes, also known as forward error correction (FEC) codes, were developed more than 50 years ago. Different types have emerged since that time. In one of the earliest and most common types, Reed-Solomon, the data can be reconstructed using any combination of “k” symbols, or pieces of data, even if “m” symbols are lost or unavailable. For example, in EC 10/16, six drives, nodes or geographic locations could be lost or unavailable, and the original file would still be recoverable.

        Erasure coding can be useful with large quantities of data and any applications or systems that need to tolerate failures, such as disk array systems, data grids, distributed storage applications, object stores and archival storage. One common current use case for erasure coding is object-based cloud storage

    eviction
        驱逐

        在 CephFS 部分，系统对客户端的屏蔽。

    exclusive lock
        互斥锁

    expirer
        逾期管理器， swift 对象若设置了生命周期，在过期时将被 expirer 清除；

    export pin
        (CephFS) 导出销

        释义：默认情况下， MDS 会动态地做负载均衡；而此功能可让目录绑死到一个
        rank ，就像用“销子”固定住了，不能再随便动。

    extent
        条带。 image extent => 映像条带

        data extent => 数据区
        理解：分配给了 RBD 映像但尚未使用，但仍然属于此映像，含义类似势力范围。


    FMARK
    failover
        故障恢复

    failsafe
        故障双保险，位于 architecture / Smart Daemons Enable Hyperscale

    failure domain
        失效域。 CRUSH 术语。

    fan-out
        扇出。
        扇出能力是指与非门输出端连接同类门的最多个数。它反映了与非门的带负载能力。
        扇出（fan-out）是一个定义单个逻辑门能够驱动的数字信号输入最大量的\
        专业术语。大多数的TTL逻辑门能够为10个其他数字门或驱动器提供信号。\
        所以，一个典型的TTL逻辑门有10个扇出信号。

    fast read
        （EC 存储池的）速读（功能）

    flapping osd
        打摆子的 osd
        抖动

        社区同仁讨论认为，这是随时间延续，不断地在 ``up`` 、 ``down``
        状态之间反复转换的情形，状态变动的时间间隔有规律或无规律，运动方向
        为“上下”，非“左右”、亦非“前后”，也可理解为打摆子、状态翻转。总之是
        一种病态的、非正常的状态，按行业惯性应该翻译为“状态抖动”之类的，但
        我觉得“打摆子”更能形象地表达 OSD 的这种病态现象。

        我把它翻译为“打摆子”的理由为：
            它是一种“病态”的现象，这种情形有其背后的原因，是可以“治愈”的；
            它变成 ``up`` 状态时会立马产生很多IO，足以使底层的硬盘过载，即忽然变“热”；
            ``down`` 状态时又只有极少的IO，很“冷”；

        总之，状态在 up/down 之间变化，由此导致后端存储器的访问热度也是“热/冷”
        交替，像极了“疟疾”（俗称打摆子）的症状，故翻译如是。

        我将视情况交替使用这两种翻译，以读起来押韵、顺口为目标。

    full ratio
        占满率


    GMARK
    get ... (eg: get user quota)
        查看... (如：查看用户配额)

    grace period
    grace time
        宽限期；宽限时间；

    guest disk
        客座磁盘

    guest OS
    guest operating system
        客座操作系统


    HMARK
    hypervisor
        虚拟化管理程序


    IMARK
    immutable object
        不可变对象

    individual bucket
        个人桶

    inline compression
        内联压缩、内联数据压缩；

    inode
        索引节点

    intent log
        意图日志

        *From src/rgw/rgw_rados.h:*
        to notify upper layer that we need to do some operation on an object,
        and it's up to the upper layer to schedule this operation.
        e.g., log intent in intent log

    inventory
        （存储空间）余量

    iSCSI initiator
        <不翻译>

        iSCSI 启动器，相当于客户端，由它向 iSCSI target 发起连接。

    iSCSI target
        <不翻译>

        相当于服务器、硬盘的代理，处理 iSCSI initiator 的连接。


    KMARK
    keystone
        <不翻译>

        Keystone 是 OpenStack 项目的子项目，提供身份识别、令牌、目录和策略服\
        务。实现了 OpenStack 的身份识别 API 。

    kvstore
        <键值存储，不翻译>


    LMARK
    laggy (osd)
    laggy estimation
        滞后的；滞后量；

    layout
        （ CephFS 的）布局

    Legal Hold status
    legal hold status
        依法保留状态
        https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/configure-inventory.html

    lifecycle
        生命周期

        RGW 术语。 bucket lifecycle => 桶生命周期

    link (bucket)
        链接（桶到用户）

    live migration
        在线迁移

        RBD 术语。


    MMARK
    main device
        主设备。 BlueStore 术语，相对的是 auxiliary device 。

    manifest
        载荷清单 ?
        还没准确理解含义，暂不翻译。

    manpage
        手册页

    master zone
    master zone group
        主域、主域组

    messenger
        信使

    messenger layer
        信使层

    monitor map
        监视器运行图

    multipart object
    multi-part
        多块对象 -> 分段对象

    multipart upload
        分段上传

    multisite
        多站、多站点


    NMARK
    nearfull ratio
        将满比率

    non-master zone
    non-master zone group
        副域、副域组


    OMARK
    object-info
        <不翻译>，因为它是专有名词，来自代码、JSON 输出。

    object map
        对象表
        RBD 术语，追踪对象数据是否真的存在；为支持稀疏数据；

    Object Retention
        对象保留时长

    objectstore
        对象存储器
        可用的有 filestore 、 bluestore

    object store
        对象存储库

    open file table
        打开文件表。当前正被打开的文件列表。

        此翻译不能准确表达原文的含义，但尚未想到更好的词。

    orphans
        孤儿对象

    orphans search, find orphans
        捡漏

        RGW 术语。

    osd draining
        osd 排空

    (osd) reporter
        报告者 => 报信的?

    out
        <不翻译> => 出列、出局?

    overlay pool
        马甲存储池


    PMARK
    partial filter
        局部过滤器，LDAP 术语

    peer
    peering
        互联点
        （归置组、 OSD ）互联、互联点、正在互联；

    period
        界期 => <不翻译>

        界期保存着组界当前状态的配置数据结构。每个界期都包含一个唯一标识符和一\
        个时间结（ epoch )，每个提交操作都会使界期的时间结递增。

    persistent cache
        持久缓存

        RBD 术语。父映像的缓存，只读的。


    pin, pinning
        销子，插入

    placement group
    pg
    PG
        归置组

        placement 意思是放置、配置的意思，是静态的；而归置含有整理、放好的意\
        思，是动态过程。但纵观全文，每次用 CRUSH 算法计算出的结果都是静态的，\
        经常变的只是 CRUSH 计算时的输入，所以从整体来说是“归置”，而从局部来说\
        都是“放置”。

        *pg log:*
        a list of recent updates made to objects in a PG. Note that these logs
        can be truncated after all OSDs in the acting set have acknowledged up
        to a certain point.

        *primary:*
        the (by convention first) member of the acting set, who is responsible
        for coordination peering, and is the only OSD that will accept client
        initiated writes to objects in a placement group.

        *recovery:*
        ensuring that copies of all of the objects in a PG are on all of the
        OSDs in the acting set. Once peering has been performed, the primary
        can start accepting write operations, and recovery can proceed in the
        background.

    placement target
        归置目标 => 归置靶

    point release
        小版本

    pool
        存储池

    prime PGMap
        捡回, ``mon_osd_prime_pg_temp``
        原文的 priming 翻译为“捡回”。
        因为此字意为：底漆、启动、起爆剂、点火装置等，我的理解是，
        旧版的 PGMap 已经一层层盖着压箱底了，新的本应从当前运行的集群里汇总，
        可这里启用了旧的，相当于扒了一层底漆，或者点燃了装填好的弹药，故译为捡回。

    priority set
        优先级组。
        暂理解为优先级相同的一类配置放入了同一集合。

    promote (an image to primary)
    promote (zone)
        晋级...

    proposal
    proposer
        (PAXOS) 提议、提案

    pubsub topic
        发布订阅话题， pubsub 话题？
        rgw 相关；

    purge
        擦净。
        如用命令 ``ceph osd purge <id>`` 擦净 OSD 。


    QMARK
    quiesce, quiesce set
        静默，静默集

    quorum
        法定人数

    quota scope
        配额作用域


    RMARK
    rank
        (CephFS) <不翻译> => 座席、销槽?

    realm
        组界 => <不翻译>

        组界，是域组的容器，有了它就能跨集群划分域组。系统允许创建多个组界，这\
        样就能轻易地在同一集群内跑多个不同的配置。

    region
        <不翻译> => 辖区?

        **此概念已废弃，取而代之的是 zonegroup 。**

        region 是地理空间的逻辑划分，它包含一个或多个 zone 。一个包含多个
        region 的集群必须指定一个主 region 。

    registry
        注册处
        cephadm 相关。

    replica
        副本

        a non-primary OSD in the acting set for a placement group (and who has
        been recognized as such and activated by the primary).

    replicated pool
        多副本存储池

    request entities
        请求实体？
        不满意，但还没有更好的。

    reshard
        重分片

    response entities
        响应内容解析。 HTTP 响应。

    RESTful
        符合 REST 规范的

    role
        角色。 AWS 术语？

    root squash
        根目录保护， CephFS 功能。

    round off
        对齐数据块。本义为四舍五入。

    rule mask
        ?
        crush 相关的。


    SMARK
    sanity check
        健全性检查

    scrub
        洗刷、洗刷操作

    secondary zone
    secondary zone group
        次域、次域组 => 副域、副域组

    secret key
        私钥

    \* set
        *acting set:*
        一个归置组的数据同时分布于多个 OSD ，也就是说这些 OSD 负责这个归置组，\
        这些 OSD 就称为 acting set 。也是个变化的集合。

        *hit set:*
        在 cache tering 中译为：命中集

        *missing set:*
        Each OSD notes update log entries and if they imply updates to the
        contents of an object, adds that object to a list of needed updates.
        This list is called the missing set for that <OSD,PG>.

        *up set:*
        是 acting set 中处于 up 状态的那部分 OSD 。

    shard
        分片

    Single Sign-On
    SSO
        单点登录

    slow request
        慢请求

    snap trim
        快照修剪

    snapset
        *未翻译*

    spawn
        分身，派生。
        完成类似工作的多个守护进程，需要时派生/分身出来，不需要时关闭。

    spread metadata load
        散布元数据负荷

    staging period
        暂存的 period

        RGW 术语。

    stale pg
        掉队、落伍的归置组

    standby
        灾备、备用

    standby-replay
    standby-replay daemon
        灾备重放、灾备重放守护进程； => 热备， MDS 术语。

    stopped set
        停止集。 MDS 术语。

    storage class
        存储类

        https://aws.amazon.com/cn/s3/storage-classes/
        按不同案例、访问频率、访问方式划分的？

    storage overhead
        存储开销
        假设数据存储了 3 个副本，其实我们只要保证一份完整即可，另外两份就是
        overhead 。

    store
        存储系统

    stray
        an OSD who is not a member of the current acting set, but has not yet
        been told that it can delete its copies of a particular placement group.

    stray directory
        流浪目录。 CephFS 术语。

        译者理解：
        脱离了目录树，不知道原来的上一级是谁的目录。
        和孤儿目录/文件（ orphan ）应该是同一个东西。

    stretch pool
        弹性存储池、跨区域存储池？

    string interpolation
        字符串插值， https://en.wikipedia.org/wiki/String_interpolation

        即把字符串替换成同名变量的值。

    striping period
        ?

    subuser
        (Swift API) 子用户


    TMARK
    tenant
        (OpenStack) 租户

    thin provisioning / thin provisioned
        简配
        thick provisioning -> 全配

    threading model
        线程池模型

    throttling
    throttle
        抑制、节流、节制，意思是要控制速度，不让它太快。
        throttler -> 减速器

    tiebreaker mon
        终裁监视器。

        tiebreaker 本意是当两队在比赛结束时打成平局而增加的决胜局、加时赛。

    tier type
        <不翻译> RGW 术语。

    tight coupling
        紧耦合

    token
        (OpenStack) 令牌

    transcript file
        笔录文件、目录文件？

    trim
    trimming
        裁剪、清理；
        裁截 => 清理?


    UMARK
    unlink bucket
        断开、切断桶链接、解绑桶、解除连接，视具体语境采用。


    WMARK
    write-ahead log, WAL
        预写日志。
        是关系数据库系统中用于提供原子性和持久性（ACID 属性中的两个）的一系列技术。
        在使用 WAL 的系统中，所有的修改在提交之前都要先写入 log 文件中。

        log 文件中通常包括 redo 和 undo 信息。这样做的目的，通过一个例子来说明：
        假设一个程序在执行某些操作的过程中机器掉电了。在重新启动时，
        程序可能需要知道当时执行的操作是成功了还是部分成功或者是失败了。
        如果使用了 WAL，程序就可以检查 log 文件，并对突然掉电时计划执行的\
        操作内容跟实际上执行的操作内容进行比较。在这个比较的基础上，
        程序就可以决定是撤销已做的操作还是继续完成已做的操作，或者是保持原样。

        WAL 允许用 in-place 方式更新数据库。另一种用来实现原子更新的方法是
        shadow paging ，它并不是 in-place 方式。用 in-place 方式做更新的\
        主要优点是减少索引和块列表的修改。ARIES 是 WAL 系列技术常用的算法。
        在文件系统中，WAL 通常称为 journaling 。
        PostgreSQL 也是用 WAL 来提供 point-in-time 恢复和数据库复制特性。

    writeback
        不译。通常译作回写模式，但由于配置时也要写 writeback ，干脆不译，在\
        首次出现时的旁边标注一下。


    ZMARK
    zap
        擦净、删除；（快速摧毁）
        <不译，需重新斟酌>
        zap 操作之后，物理的东西还是那个东西，但是上面的数据、逻辑变了，和删除\
        有区别。

    zone
        域，是一或多个 Ceph 对象网关例程的逻辑分组。每个域组应该指定一个域为主\
        域，由它负责所有桶和用户的创建。

    zonegroup
    zone group
        域组，由多个域组成，此概念大致相当于Jewel 版以前联盟部署中的辖区（
        region ）。应该有一个主域组，负责处理系统配置变更。

    zonegroup map
    zone group map
        域组映射图

        是个配置的数据结构，它保存着整个系统的映射图，也就是哪个域\
        组是主的、各个域组间的关系、以及其它可配置信息，如存储策略。


.. vim: set ts=4 sw=4 expandtab colorcolumn=80:

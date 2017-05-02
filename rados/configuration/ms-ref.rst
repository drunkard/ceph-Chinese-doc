==========
 消息传递
==========

常规选项
========


``ms tcp nodelay``

:描述: 在信差的 TCP 会话上禁用 nagle 算法。
:类型: Boolean
:是否必需: No
:默认值: ``true``


``ms initial backoff``

:描述: 出错时重连的初始等待时间。
:类型: Double
:是否必需: No
:默认值: ``.2``


``ms max backoff``

:描述: 出错重连时等待的最大时间。
:类型: Double
:是否必需: No
:默认值: ``15.0``


``ms nocrc``

:描述: 禁用网络消息的 crc 校验， CPU 不足时可提升性能。
:类型: Boolean
:是否必需: No
:默认值: ``false``


``ms die on bad msg``

:描述: 调试选项，不要配置。
:类型: Boolean
:是否必需: No
:默认值: ``false``


``ms dispatch throttle bytes``

:描述: 等着传送的消息尺寸阀值。
:类型: 64-bit Unsigned Integer
:是否必需: No
:默认值: ``100 << 20``


``ms bind ipv6``

:描述: 如果想让守护进程绑定到 IPv6 地址而非 IPv4 就得启用（如\
       果你指定了守护进程或集群 IP 就不必要了）
:类型: Boolean
:是否必需: No
:默认值: ``false``


``ms rwthread stack bytes``

:描述: 堆栈尺寸调试选项，不要配置。
:类型: 64-bit Unsigned Integer
:是否必需: No
:默认值: ``1024 << 10``


``ms tcp read timeout``

:描述: 控制信差关闭空闲连接前的等待秒数。
:类型: 64-bit Unsigned Integer
:是否必需: No
:默认值: ``900``


``ms inject socket failures``

:描述: 调试选项，别配置。
:类型: 64-bit Unsigned Integer
:是否必需: No
:默认值: ``0``


.. _Async messenger options:

异步信使选项
============


``ms async transport type``

:描述: Transport type used by Async Messenger. Can be ``posix``, ``dpdk``
              or ``rdma``. Posix uses standard TCP/IP networking and is default. 
              Other transports may be experimental and support may be limited.
:类型: String
:是否必需: No
:默认值: ``posix``


``ms async op threads``

:描述: Initial number of worker threads used by each Async Messenger instance.
              Should be at least equal to highest number of replicas, but you can
              decrease it if you're low on CPU core count and/or you host a lot of
              OSDs on single server.
:类型: 64-bit Unsigned Integer
:是否必需: No
:默认值: ``3``


``ms async max op threads``

:描述: Maximum number of worker threads used by each Async Messenger instance. 
              Set to lower values when your machine has limited CPU count, and increase 
              when your CPUs are underutilized (i. e. one or more of CPUs are
              constantly on 100% load during I/O operations).
:类型: 64-bit Unsigned Integer
:是否必需: No
:默认值: ``5``


``ms async set affinity``

:描述: Set to true to bind Async Messenger workers to particular CPU cores. 
:类型: Boolean
:是否必需: No
:默认值: ``true``


``ms async affinity cores``

:描述: When ``ms async set affinity`` is true, this string specifies how Async
              Messenger workers are bound to CPU cores. For example, "0,2" will bind
              workers #1 and #2 to CPU cores #0 and #2, respectively.
              NOTE: when manually setting affinity, make sure to not assign workers to
              processors that are virtual CPUs created as an effect of Hyperthreading
              or similar technology, because they're slower than regular CPU cores.
:类型: String
:是否必需: No
:默认值: ``(empty)``


``ms async send inline``

:描述: Send messages directly from the thread that generated them instead of
              queuing and sending from Async Messenger thread. This option is known
              to decrease performance on systems with a lot of CPU cores, so it's
              disabled by default.
:类型: Boolean
:是否必需: No
:默认值: ``false``



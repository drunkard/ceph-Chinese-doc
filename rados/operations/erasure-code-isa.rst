================
 ISA 纠删码插件
================

*isa* 插件封装了 `ISA
<https://01.org/intel%C2%AE-storage-acceleration-library-open-source-version/>`_
库。


创建 isa 配置
=============

要新建 *isa* 纠删码配置： ::

        ceph osd erasure-code-profile set {name} \
             plugin=isa \
             technique={reed_sol_van|cauchy} \
             [k={data-chunks}] \
             [m={coding-chunks}] \
             [crush-root={root}] \
             [crush-failure-domain={bucket-type}] \
             [crush-device-class={device-class}] \
             [directory={directory}] \
             [--force]

其中：


``k={data chunks}``

:描述: 各对象都被分割为\ **数据块**\ ，分别存储于不同 OSD 。
:类型: Integer
:是否必需: No.
:默认值: 7


``m={coding-chunks}``

:描述: 计算各对象的\ **编码块**\ 、并存储于不同 OSD 。编码块的\
       数量等同于在不丢数据的前提下允许同时失效的 OSD 数量。
:类型: Integer
:是否必需: No.
:默认值: 3


``technique={reed_sol_van|cauchy}``

:描述: ISA 插件包含两种 `Reed Solomon \
       <https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction>`_ \
       编码形式。设置为 *reed_sol_van* 表示用 \
       `Vandermonde <https://en.wikipedia.org/wiki/Vandermonde_matrix>`_ 算\
       法，设置为 *cauchy* 表示用 \
       `Cauchy <https://en.wikipedia.org/wiki/Cauchy_matrix>`_ 算法。

:类型: String
:是否必需: No.
:默认值: reed_sol_van


``crush-root={root}``

:描述: CRUSH 规则（如 **step take default** ）第一步要用的
       crush 桶的名字。
:类型: String
:是否必需: No.
:默认值: default


``crush-failure-domain={bucket-type}``

:描述: 确保两个编码块不会存在于同一故障域的桶中。比如，假设\
       故障域是 **host** ，就不会有两个编码块存储到同一主机；\
       此值用于在 CRUSH 规则中创建类似 **step chooseleaf host**
       的步骤。
:类型: String
:是否必需: No.
:默认值: host


``crush-device-class={device-class}``

:描述: 使归置限于指定的设备类（比如 ``ssd`` 或 ``hdd`` ）之\
       内，在 CRUSH 图里使用设备类的名字。

:类型: String
:是否必需: No.
:默认值:


``directory={directory}``

:描述: 设置纠删码插件的路径，需是\ **目录**\ 。
:类型: String
:是否必需: No.
:默认值: /usr/lib/ceph/erasure-code


``--force``

:描述: 覆盖同名配置。
:类型: String
:是否必需: No.

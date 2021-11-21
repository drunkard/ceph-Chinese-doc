==================
 为 Ceph 写作文档
==================

用户文档
========
.. User documentation

docs.ceph.com 上的文档是从 Ceph 的 git 源码库内 ``/doc/`` 目录\
下的 restructuredText 源码生成的。

请确保你的变更是面向这款软件的终端用户的；除非你是增加到
``/doc/dev/`` ，这里是面向开发者的。

所有与面向用户的功能相关的修订拉取请求（ PR ）必须包含对文档的\
相应更新：详情见\ `提交补丁`_\ 。

检查一下你的 .rst 文件语法是否正确，可以在查看 .rst 差异时点击
github 用户界面的 View 按钮；或者用 ``admin/build-doc`` 脚本\
自行构建文档。

关于为 Ceph 写作文档的更多信息，请参考
:doc:`/start/documenting-ceph` 。


代码文档
========
.. Code Documentation

C 和 C++ 可以用 Doxygen_ 生成文档，我们用 Breathe_ 工具，它\
支持 Doxygen 的部分功能。

.. _Doxygen: http://www.doxygen.nl/
.. _Breathe: https://github.com/michaeljones/breathe

函数文档的统一格式为：

.. code-block:: c

  /**
   * Short description
   *
   * Detailed description when necessary
   *
   * preconditons, postconditions, warnings, bugs or other notes
   *
   * parameter reference
   * return value (if non-void)
   */

这些应该在声明函数时写在函数头部，并且函数应该按逻辑分组，
`librados C API`_ 里面有完整实例。这些文档被 `librados.rst`_
拉进 Sphinx 、并在 :doc:`/rados/api/librados` 渲染。

生成 HTML 格式的 doxygen 文档用此命令：

::

   # cmake --build . --target doxygen

输出的 HTML 在此目录下： ``build-doc/doxygen/html`` 

.. _`librados C API`: https://github.com/ceph/ceph/blob/master/src/include/rados/librados.h
.. _`librados.rst`: https://github.com/ceph/ceph/raw/master/doc/rados/api/librados.rst


绘图
====

Graphviz
--------

你可以用 Graphviz_ ，其文档位于 `Graphviz 扩展文档`_\ 。

.. _Graphviz: http://graphviz.org/
.. _`Graphviz 扩展文档`: https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html

.. graphviz::

   digraph "example" {
     foo -> bar;
     bar -> baz;
     bar -> th;
   }

大多数时候，我们都会把实际的 DOT 文件放在单独的文件内，比如： ::

  .. graphviz:: myfile.dot


Ditaa
-----

也可以用 Ditaa_ 绘图：

.. _Ditaa: http://ditaa.sourceforge.net/

.. ditaa::

   +--------------+   /=----\
   | hello, world |-->| hi! |
   +--------------+   \-----/


Blockdiag
---------

如果有必要，还可以用 Blockdiag_ ，它是个 Graphviz 风格的申诉式\
绘图语言，包括：

- `框图`_\ ：方框和箭头（自动排版，相对于 Ditaa_ ）
- `时序图`_\ ：带说明信息的时间线
- `活动图`_\ ：子系统以及其内的活动
- `网络图`_\ ：主机、局域网、 IP 地址等（可选用 `Cisco 图标`_\ ）

.. _Blockdiag: http://blockdiag.com/en/
.. _`Cisco 图标`: https://pypi.python.org/pypi/blockdiagcontrib-cisco/
.. _`框图`: http://blockdiag.com/en/blockdiag/
.. _`时序图`: http://blockdiag.com/en/seqdiag/index.html
.. _`活动图`: http://blockdiag.com/en/actdiag/index.html
.. _`网络图`: http://blockdiag.com/en/nwdiag/


Inkscape
--------

你可以用 Inkscape 生成可伸缩矢量图。 restructedText 文档位于
https://inkscape.org/en/ 。

如果你是用 Inkscape 生成图表的，你应该同时提交可伸缩矢量图（ SVG ）和导出\
的流式网络图（ PNG ）文件。应该引用 PNG 文件。

如果提交的是 SVG 文件，其他人也能用 Inkscape 更新 SVG 图表。

HTML5 将内嵌对 SVG 的支持。


.. _`提交补丁`: https://github.com/ceph/ceph/blob/master/SubmittingPatches.rst

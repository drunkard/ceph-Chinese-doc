.. _orchestrator-modules:

.. py:currentmodule:: orchestrator

ceph-mgr orchestrator 模块
==========================

.. warning::

   这是开发者文档，描述的是 Ceph 内部机制，仅适用于编写
   ceph-mgr orchestrator 模块的人们。

In this context, *orchestrator* refers to some external service that
provides the ability to discover devices and create Ceph services.  This
includes external projects such as Rook.

An *orchestrator module* is a ceph-mgr module (:ref:`mgr-module-dev`)
which implements common management operations using a particular
orchestrator.

Orchestrator modules subclass the ``Orchestrator`` class: this class is
an interface, it only provides method definitions to be implemented
by subclasses.  The purpose of defining this common interface
for different orchestrators is to enable common UI code, such as
the dashboard, to work with various different backends.


.. graphviz::

    digraph G {
        subgraph cluster_1 {
            volumes [label="mgr/volumes"]
            rook [label="mgr/rook"]
            dashboard [label="mgr/dashboard"]
            orchestrator_cli [label="mgr/orchestrator"]
            orchestrator [label="Orchestrator Interface"]
            cephadm [label="mgr/cephadm"]

            label = "ceph-mgr";
        }

        volumes -> orchestrator
        dashboard -> orchestrator
        orchestrator_cli -> orchestrator
        orchestrator -> rook -> rook_io
        orchestrator -> cephadm


        rook_io [label="Rook"]

        rankdir="TB";
    }

Behind all the abstraction, the purpose of orchestrator modules is simple:
enable Ceph to do things like discover available hardware, create and
destroy OSDs, and run MDS and RGW services.

A tutorial is not included here: for full and concrete examples, see
the existing implemented orchestrator modules in the Ceph source tree.

.. Glossary

术语
----

Stateful service
  a daemon that uses local storage, such as OSD or mon.

Stateless service
  a daemon that doesn't use any local storage, such
  as an MDS, RGW, nfs-ganesha, iSCSI gateway.

Label
  arbitrary string tags that may be applied by administrators
  to nodes.  Typically administrators use labels to indicate
  which nodes should run which kinds of service.  Labels are
  advisory (from human input) and do not guarantee that nodes
  have particular physical capabilities.

Drive group
  collection of block devices with common/shared OSD
  formatting (typically one or more SSDs acting as
  journals/dbs for a group of HDDs).

Placement
  choice of which node is used to run a service.

.. Key Concepts

关键概念
--------

The underlying orchestrator remains the source of truth for information
about whether a service is running, what is running where, which
nodes are available, etc.  Orchestrator modules should avoid taking
any internal copies of this information, and read it directly from
the orchestrator backend as much as possible.

Bootstrapping nodes and adding them to the underlying orchestration
system is outside the scope of Ceph's orchestrator interface.  Ceph
can only work on nodes when the orchestrator is already aware of them.

Calls to orchestrator modules are all asynchronous, and return *completion*
objects (see below) rather than returning values immediately.

Where possible, placement of stateless services should be left up to the
orchestrator.

Completions and batching
------------------------

All methods that read or modify the state of the system can potentially
be long running.  To handle that, all such methods return a *Completion*
object.  Orchestrator modules
must implement the *process* method: this takes a list of completions, and
is responsible for checking if they're finished, and advancing the underlying
operations as needed.

Each orchestrator module implements its own underlying mechanisms
for completions.  This might involve running the underlying operations
in threads, or batching the operations up before later executing
in one go in the background.  If implementing such a batching pattern, the
module would do no work on any operation until it appeared in a list
of completions passed into *process*.

Some operations need to show a progress. Those operations need to add
a *ProgressReference* to the completion. At some point, the progress reference
becomes *effective*, meaning that the operation has really happened
(e.g. a service has actually been started).

.. automethod:: Orchestrator.process

.. autoclass:: Completion
   :members:

.. autoclass:: ProgressReference
   :members:


.. Error Handling

错误处理
--------

The main goal of error handling within orchestrator modules is to provide debug information to
assist users when dealing with deployment errors.

.. autoclass:: OrchestratorError
.. autoclass:: NoOrchestrator
.. autoclass:: OrchestratorValidationError


In detail, orchestrators need to explicitly deal with different kinds of errors:

1. No orchestrator configured

   See :class:`NoOrchestrator`.

2. An orchestrator doesn't implement a specific method.

   For example, an Orchestrator doesn't support ``add_host``.

   In this case, a ``NotImplementedError`` is raised.

3. Missing features within implemented methods.

   E.g. optional parameters to a command that are not supported by the
   backend (e.g. the hosts field in :func:`Orchestrator.update_mons` command with the rook backend).

   See :class:`OrchestratorValidationError`.

4. Input validation errors

   The ``orchestrator`` module and other calling modules are supposed to
   provide meaningful error messages.

   See :class:`OrchestratorValidationError`.

5. Errors when actually executing commands

   The resulting Completion should contain an error string that assists in understanding the
   problem. In addition, :func:`_Completion.is_errored` is set to ``True``

6. Invalid configuration in the orchestrator modules

   This can be tackled similar to 5.


All other errors are unexpected orchestrator issues and thus should raise an exception that are then
logged into the mgr log file. If there is a completion object at that point,
:func:`_Completion.result` may contain an error message.


.. Excluded functionality

排除的功能
----------

- Ceph's orchestrator interface is not a general purpose framework for
  managing linux servers -- it is deliberately constrained to manage
  the Ceph cluster's services only.
- Multipathed storage is not handled (multipathing is unnecessary for
  Ceph clusters).  Each drive is assumed to be visible only on
  a single node.

.. Host management

主机管理
--------

.. automethod:: Orchestrator.add_host
.. automethod:: Orchestrator.remove_host
.. automethod:: Orchestrator.get_hosts
.. automethod:: Orchestrator.update_host_addr
.. automethod:: Orchestrator.add_host_label
.. automethod:: Orchestrator.remove_host_label

.. autoclass:: HostSpec

.. Devices

设备
----

.. automethod:: Orchestrator.get_inventory
.. autoclass:: InventoryFilter

.. py:currentmodule:: ceph.deployment.inventory

.. autoclass:: Devices
   :members:

.. autoclass:: Device
   :members:

.. py:currentmodule:: orchestrator

Placement
---------

A :ref:`orchestrator-cli-placement-spec` defines the placement of
daemons of a specifc service.

In general, stateless services do not require any specific placement
rules as they can run anywhere that sufficient system resources
are available. However, some orchestrators may not include the
functionality to choose a location in this way. Optionally, you can
specify a location when creating a stateless service.


.. py:currentmodule:: ceph.deployment.service_spec

.. autoclass:: PlacementSpec
   :members:

.. py:currentmodule:: orchestrator

   
.. Services

服务
----

.. autoclass:: ServiceDescription

.. py:currentmodule:: ceph.deployment.service_spec

.. autoclass:: ServiceSpec

.. py:currentmodule:: orchestrator

.. automethod:: Orchestrator.describe_service

.. automethod:: Orchestrator.service_action
.. automethod:: Orchestrator.remove_service


.. Daemons

守护进程
--------

.. automethod:: Orchestrator.list_daemons
.. automethod:: Orchestrator.remove_daemons
.. automethod:: Orchestrator.daemon_action


.. OSD management

OSD 管理
--------

.. automethod:: Orchestrator.create_osds

.. automethod:: Orchestrator.blink_device_light
.. autoclass:: DeviceLightLoc


.. OSD Replacement
.. _orchestrator-osd-replace:

OSD 替换
^^^^^^^^

See :ref:`rados-replacing-an-osd` for the underlying process.

Replacing OSDs is fundamentally a two-staged process, as users need to
physically replace drives. The orchestrator therefor exposes this two-staged process.

Phase one is a call to :meth:`Orchestrator.remove_osds` with ``destroy=True`` in order to mark
the OSD as destroyed.


Phase two is a call to  :meth:`Orchestrator.create_osds` with a Drive Group with

.. py:currentmodule:: ceph.deployment.drive_group

:attr:`DriveGroupSpec.osd_id_claims` set to the destroyed OSD ids.

.. py:currentmodule:: orchestrator

.. Monitors

监视器
------

.. automethod:: Orchestrator.add_mon
.. automethod:: Orchestrator.apply_mon

.. Stateless Services

无状态服务
----------

.. automethod:: Orchestrator.add_mgr
.. automethod:: Orchestrator.apply_mgr
.. automethod:: Orchestrator.add_mds
.. automethod:: Orchestrator.apply_mds
.. automethod:: Orchestrator.add_rbd_mirror
.. automethod:: Orchestrator.apply_rbd_mirror

.. py:currentmodule:: ceph.deployment.service_spec

.. autoclass:: RGWSpec

.. py:currentmodule:: orchestrator

.. automethod:: Orchestrator.add_rgw
.. automethod:: Orchestrator.apply_rgw

.. py:currentmodule:: ceph.deployment.service_spec

.. autoclass:: NFSServiceSpec

.. py:currentmodule:: orchestrator

.. automethod:: Orchestrator.add_nfs
.. automethod:: Orchestrator.apply_nfs

.. Upgrades

升级
----

.. automethod:: Orchestrator.upgrade_available
.. automethod:: Orchestrator.upgrade_start
.. automethod:: Orchestrator.upgrade_status
.. autoclass:: UpgradeStatusSpec

.. Utility

工具
----

.. automethod:: Orchestrator.available
.. automethod:: Orchestrator.get_feature_set

.. Client Modules

客户端模块
----------

.. autoclass:: OrchestratorClientMixin
   :members:

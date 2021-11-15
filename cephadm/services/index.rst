==================
Service Management
==================

A service is a group of daemons configured together. See these chapters
for details on individual services:

.. toctree::
    :maxdepth: 1

    mon
    mgr
    osd
    rgw
    mds
    nfs
    iscsi
    custom-container
    monitoring

Service Status
==============


To see the status of one
of the services running in the Ceph cluster, do the following:

#. Use the command line to print a list of services. 
#. Locate the service whose status you want to check. 
#. Print the status of the service.

The following command prints a list of services known to the orchestrator. To
limit the output to services only on a specified host, use the optional
``--host`` parameter. To limit the output to services of only a particular
type, use the optional ``--type`` parameter (mon, osd, mgr, mds, rgw):

   .. prompt:: bash #

     ceph orch ls [--service_type type] [--service_name name] [--export] [--format f] [--refresh]

Discover the status of a particular service or daemon:

   .. prompt:: bash #

     ceph orch ls --service_type type --service_name <name> [--refresh]

To export the service specifications knows to the orchestrator, run the following command.

   .. prompt:: bash #

     ceph orch ls --export

The service specifications exported with this command will be exported as yaml
and that yaml can be used with the ``ceph orch apply -i`` command.

For information about retrieving the specifications of single services (including examples of commands), see :ref:`orchestrator-cli-service-spec-retrieve`.

Daemon Status
=============

A daemon is a systemd unit that is running and part of a service.

To see the status of a daemon, do the following:

#. Print a list of all daemons known to the orchestrator.
#. Query the status of the target daemon.

First, print a list of all daemons known to the orchestrator:

   .. prompt:: bash #

    ceph orch ps [--hostname host] [--daemon_type type] [--service_name name] [--daemon_id id] [--format f] [--refresh]

Then query the status of a particular service instance (mon, osd, mds, rgw).
For OSDs the id is the numeric OSD ID. For MDS services the id is the file
system name:

   .. prompt:: bash #

    ceph orch ps --daemon_type osd --daemon_id 0
    
.. _orchestrator-cli-service-spec:

Service Specification
=====================

A *Service Specification* is a data structure that is used to specify the
deployment of services.  Here is an example of a service specification in YAML:

.. code-block:: yaml

    service_type: rgw
    service_id: realm.zone
    placement:
      hosts:
        - host1
        - host2
        - host3
    unmanaged: false
    networks:
    - 192.169.142.0/24
    spec:
      # Additional service specific attributes.

In this example, the properties of this service specification are:

.. py:currentmodule:: ceph.deployment.service_spec

.. autoclass:: ServiceSpec
   :members:

Each service type can have additional service-specific properties.

Service specifications of type ``mon``, ``mgr``, and the monitoring
types do not require a ``service_id``.

A service of type ``osd`` is described in :ref:`drivegroups`

Many service specifications can be applied at once using ``ceph orch apply -i``
by submitting a multi-document YAML file::

    cat <<EOF | ceph orch apply -i -
    service_type: mon
    placement:
      host_pattern: "mon*"
    ---
    service_type: mgr
    placement:
      host_pattern: "mgr*"
    ---
    service_type: osd
    service_id: default_drive_group
    placement:
      host_pattern: "osd*"
    data_devices:
      all: true
    EOF

.. _orchestrator-cli-service-spec-retrieve:

Retrieving the running Service Specification
--------------------------------------------

If the services have been started via ``ceph orch apply...``, then directly changing
the Services Specification is complicated. Instead of attempting to directly change
the Services Specification, we suggest exporting the running Service Specification by
following these instructions:

   .. prompt:: bash #
    
    ceph orch ls --service-name rgw.<realm>.<zone> --export > rgw.<realm>.<zone>.yaml
    ceph orch ls --service-type mgr --export > mgr.yaml
    ceph orch ls --export > cluster.yaml

The Specification can then be changed and re-applied as above.

Updating Service Specifications
-------------------------------

The Ceph Orchestrator maintains a declarative state of each
service in a ``ServiceSpec``. For certain operations, like updating
the RGW HTTP port, we need to update the existing
specification.

1. List the current ``ServiceSpec``:

   .. prompt:: bash #

    ceph orch ls --service_name=<service-name> --export > myservice.yaml

2. Update the yaml file:

   .. prompt:: bash #

    vi myservice.yaml

3. Apply the new ``ServiceSpec``:

   .. prompt:: bash #

    ceph orch apply -i myservice.yaml [--dry-run]

.. _orchestrator-cli-placement-spec:

Daemon Placement
================

For the orchestrator to deploy a *service*, it needs to know where to deploy
*daemons*, and how many to deploy.  This is the role of a placement
specification.  Placement specifications can either be passed as command line arguments
or in a YAML files.

.. note::

   cephadm will not deploy daemons on hosts with the ``_no_schedule`` label; see :ref:`cephadm-special-host-labels`.

.. note::
   The **apply** command can be confusing. For this reason, we recommend using
   YAML specifications.

   Each ``ceph orch apply <service-name>`` command supersedes the one before it.
   If you do not use the proper syntax, you will clobber your work
   as you go.

   For example:

   .. prompt:: bash #

        ceph orch apply mon host1
        ceph orch apply mon host2
        ceph orch apply mon host3

   This results in only one host having a monitor applied to it: host 3.

   (The first command creates a monitor on host1. Then the second command
   clobbers the monitor on host1 and creates a monitor on host2. Then the
   third command clobbers the monitor on host2 and creates a monitor on
   host3. In this scenario, at this point, there is a monitor ONLY on
   host3.)

   To make certain that a monitor is applied to each of these three hosts,
   run a command like this:

   .. prompt:: bash #

     ceph orch apply mon "host1,host2,host3"

   There is another way to apply monitors to multiple hosts: a ``yaml`` file
   can be used. Instead of using the "ceph orch apply mon" commands, run a
   command of this form:

   .. prompt:: bash #

      ceph orch apply -i file.yaml

   Here is a sample **file.yaml** file

   .. code-block:: yaml

        service_type: mon
        placement:
          hosts:
           - host1
           - host2
           - host3

Explicit placements
-------------------

Daemons can be explicitly placed on hosts by simply specifying them:

   .. prompt:: bash #

    orch apply prometheus --placement="host1 host2 host3"

Or in YAML:

.. code-block:: yaml

    service_type: prometheus
    placement:
      hosts:
        - host1
        - host2
        - host3

MONs and other services may require some enhanced network specifications:

   .. prompt:: bash #

    orch daemon add mon --placement="myhost:[v2:1.2.3.4:3300,v1:1.2.3.4:6789]=name"

where ``[v2:1.2.3.4:3300,v1:1.2.3.4:6789]`` is the network address of the monitor
and ``=name`` specifies the name of the new monitor.

.. _orch-placement-by-labels:

Placement by labels
-------------------

Daemon placement can be limited to hosts that match a specific label. To set
a label ``mylabel`` to the appropriate hosts, run this command:

  .. prompt:: bash #

    ceph orch host label add *<hostname>* mylabel

  To view the current hosts and labels, run this command:

  .. prompt:: bash #

    ceph orch host ls

  For example:

  .. prompt:: bash #

    ceph orch host label add host1 mylabel
    ceph orch host label add host2 mylabel
    ceph orch host label add host3 mylabel
    ceph orch host ls

  .. code-block:: bash

    HOST   ADDR   LABELS  STATUS
    host1         mylabel
    host2         mylabel
    host3         mylabel
    host4
    host5

Now, Tell cephadm to deploy daemons based on the label by running
this command:

   .. prompt:: bash #

    orch apply prometheus --placement="label:mylabel"

Or in YAML:

.. code-block:: yaml

    service_type: prometheus
    placement:
      label: "mylabel"

* See :ref:`orchestrator-host-labels`

Placement by pattern matching
-----------------------------

Daemons can be placed on hosts as well:

   .. prompt:: bash #

    orch apply prometheus --placement='myhost[1-3]'

Or in YAML:

.. code-block:: yaml

    service_type: prometheus
    placement:
      host_pattern: "myhost[1-3]"

To place a service on *all* hosts, use ``"*"``:

   .. prompt:: bash #

    orch apply node-exporter --placement='*'

Or in YAML:

.. code-block:: yaml

    service_type: node-exporter
    placement:
      host_pattern: "*"


Changing the number of daemons
------------------------------

By specifying ``count``, only the number of daemons specified will be created:

   .. prompt:: bash #

    orch apply prometheus --placement=3

To deploy *daemons* on a subset of hosts, specify the count:

   .. prompt:: bash #

    orch apply prometheus --placement="2 host1 host2 host3"

If the count is bigger than the amount of hosts, cephadm deploys one per host:

   .. prompt:: bash #

    orch apply prometheus --placement="3 host1 host2"

The command immediately above results in two Prometheus daemons.

YAML can also be used to specify limits, in the following way:

.. code-block:: yaml

    service_type: prometheus
    placement:
      count: 3

YAML can also be used to specify limits on hosts:

.. code-block:: yaml

    service_type: prometheus
    placement:
      count: 2
      hosts:
        - host1
        - host2
        - host3

Algorithm description
---------------------

Cephadm's declarative state consists of a list of service specifications
containing placement specifications.

Cephadm continually compares a list of daemons actually running in the cluster
against the list in the service specifications. Cephadm adds new daemons and
removes old daemons as necessary in order to conform to the service
specifications.

Cephadm does the following to maintain compliance with the service
specifications.

Cephadm first selects a list of candidate hosts. Cephadm seeks explicit host
names and selects them. If cephadm finds no explicit host names, it looks for
label specifications. If no label is defined in the specification, cephadm
selects hosts based on a host pattern. If no host pattern is defined, as a last
resort, cephadm selects all known hosts as candidates.

Cephadm is aware of existing daemons running services and tries to avoid moving
them.

Cephadm supports the deployment of a specific amount of services.
Consider the following service specification:

.. code-block:: yaml

    service_type: mds
    service_name: myfs
    placement:
      count: 3
      label: myfs

This service specifcation instructs cephadm to deploy three daemons on hosts
labeled ``myfs`` across the cluster.

If there are fewer than three daemons deployed on the candidate hosts, cephadm
randomly chooses hosts on which to deploy new daemons.

If there are more than three daemons deployed on the candidate hosts, cephadm
removes existing daemons.

Finally, cephadm removes daemons on hosts that are outside of the list of
candidate hosts.

.. note::

   There is a special case that cephadm must consider.

   If there are fewer hosts selected by the placement specification than
   demanded by ``count``, cephadm will deploy only on the selected hosts.

.. _orch-rm:

Removing a Service
==================

In order to remove a service including the removal
of all daemons of that service, run

.. prompt:: bash

  ceph orch rm <service-name>

For example:

.. prompt:: bash

  ceph orch rm rgw.myrgw

.. _cephadm-spec-unmanaged:

Disabling automatic deployment of daemons
=========================================

Cephadm supports disabling the automated deployment and removal of daemons on a
per service basis. The CLI supports two commands for this.

In order to fully remove a service, see :ref:`orch-rm`.

Disabling automatic management of daemons
-----------------------------------------

To disable the automatic management of dameons, set ``unmanaged=True`` in the
:ref:`orchestrator-cli-service-spec` (``mgr.yaml``).

``mgr.yaml``:

.. code-block:: yaml

  service_type: mgr
  unmanaged: true
  placement:
    label: mgr


.. prompt:: bash #

   ceph orch apply -i mgr.yaml


.. note::

  After you apply this change in the Service Specification, cephadm will no
  longer deploy any new daemons (even if the placement specification matches
  additional hosts).

Deploying a daemon on a host manually
-------------------------------------

.. note::

  This workflow has a very limited use case and should only be used
  in rare circumstances. 

To manually deploy a daemon on a host, follow these steps:

Modify the service spec for a service by getting the 
existing spec, adding ``unmanaged: true``, and applying the modified spec. 

Then manually deploy the daemon using the following:

   .. prompt:: bash #

     ceph orch daemon add <daemon-type>  --placement=<placement spec>

For example :

   .. prompt:: bash #

     ceph orch daemon add mgr --placement=my_host

.. note:: 

  Removing ``unmanaged: true`` from the service spec will 
  enable the reconciliation loop for this service and will
  potentially lead to the removal of the daemon, depending
  on the placement spec. 

Removing a daemon from a host manually
--------------------------------------

To manually remove a daemon, run a command of the following form:

   .. prompt:: bash #

     ceph orch daemon rm <daemon name>... [--force]

For example:

   .. prompt:: bash #

     ceph orch daemon rm mgr.my_host.xyzxyz

.. note:: 

  For managed services (``unmanaged=False``), cephadm will automatically
  deploy a new daemon a few seconds later.

See also
--------
    
* See :ref:`cephadm-osd-declarative` for special handling of unmanaged OSDs. 
* See also :ref:`cephadm-pause`

===========
RGW Service
===========

.. _cephadm-deploy-rgw:

Deploy RGWs
===========

Cephadm deploys radosgw as a collection of daemons that manage a
single-cluster deployment or a particular *realm* and *zone* in a
multisite deployment.  (For more information about realms and zones,
see :ref:`multisite`.)

Note that with cephadm, radosgw daemons are configured via the monitor
configuration database instead of via a `ceph.conf` or the command line.  If
that configuration isn't already in place (usually in the
``client.rgw.<something>`` section), then the radosgw
daemons will start up with default settings (e.g., binding to port
80).

To deploy a set of radosgw daemons, with an arbitrary service name
*name*, run the following command:

.. prompt:: bash #

  ceph orch apply rgw *<name>* [--realm=*<realm-name>*] [--zone=*<zone-name>*] --placement="*<num-daemons>* [*<host1>* ...]"

Trivial setup
-------------

For example, to deploy 2 RGW daemons (the default) for a single-cluster RGW deployment
under the arbitrary service id *foo*:

.. prompt:: bash #

   ceph orch apply rgw foo

Designated gateways
-------------------

A common scenario is to have a labeled set of hosts that will act
as gateways, with multiple instances of radosgw running on consecutive
ports 8000 and 8001:

.. prompt:: bash #

   ceph orch host label add gwhost1 rgw  # the 'rgw' label can be anything
   ceph orch host label add gwhost2 rgw
   ceph orch apply rgw foo '--placement=label:rgw count-per-host:2' --port=8000

.. _cephadm-rgw-networks:

Specifying Networks
-------------------

The RGW service can have the network they bind to configured with a yaml service specification.

example spec file:

.. code-block:: yaml

    service_type: rgw
    service_name: foo
    placement:
      label: rgw
      count-per-host: 2
    networks:
    - 192.169.142.0/24
    spec:
      port: 8000


Multisite zones
---------------

To deploy RGWs serving the multisite *myorg* realm and the *us-east-1* zone on
*myhost1* and *myhost2*:

.. prompt:: bash #

   ceph orch apply rgw east --realm=myorg --zone=us-east-1 --placement="2 myhost1 myhost2"

Note that in a multisite situation, cephadm only deploys the daemons.  It does not create
or update the realm or zone configurations.  To create a new realm and zone, you need to do
something like:

.. prompt:: bash #

  radosgw-admin realm create --rgw-realm=<realm-name> --default
  
.. prompt:: bash #

  radosgw-admin zonegroup create --rgw-zonegroup=<zonegroup-name>  --master --default

.. prompt:: bash #

  radosgw-admin zone create --rgw-zonegroup=<zonegroup-name> --rgw-zone=<zone-name> --master --default

.. prompt:: bash #

  radosgw-admin period update --rgw-realm=<realm-name> --commit

See :ref:`orchestrator-cli-placement-spec` for details of the placement
specification.  See :ref:`multisite` for more information of setting up multisite RGW.

See also :ref:`multisite`.

Setting up HTTPS
----------------

In order to enable HTTPS for RGW services, apply a spec file following this scheme:

.. code-block:: yaml

  service_type: rgw
  service_id: myrgw
  spec:
    rgw_frontend_ssl_certificate: | 
      -----BEGIN PRIVATE KEY-----
      V2VyIGRhcyBsaWVzdCBpc3QgZG9vZi4gTG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFt
      ZXQsIGNvbnNldGV0dXIgc2FkaXBzY2luZyBlbGl0ciwgc2VkIGRpYW0gbm9udW15
      IGVpcm1vZCB0ZW1wb3IgaW52aWR1bnQgdXQgbGFib3JlIGV0IGRvbG9yZSBtYWdu
      YSBhbGlxdXlhbSBlcmF0LCBzZWQgZGlhbSB2b2x1cHR1YS4gQXQgdmVybyBlb3Mg
      ZXQgYWNjdXNhbSBldCBqdXN0byBkdW8=
      -----END PRIVATE KEY-----
      -----BEGIN CERTIFICATE-----
      V2VyIGRhcyBsaWVzdCBpc3QgZG9vZi4gTG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFt
      ZXQsIGNvbnNldGV0dXIgc2FkaXBzY2luZyBlbGl0ciwgc2VkIGRpYW0gbm9udW15
      IGVpcm1vZCB0ZW1wb3IgaW52aWR1bnQgdXQgbGFib3JlIGV0IGRvbG9yZSBtYWdu
      YSBhbGlxdXlhbSBlcmF0LCBzZWQgZGlhbSB2b2x1cHR1YS4gQXQgdmVybyBlb3Mg
      ZXQgYWNjdXNhbSBldCBqdXN0byBkdW8=
      -----END CERTIFICATE-----
    ssl: true

Then apply this yaml document:

.. prompt:: bash #

  ceph orch apply -i myrgw.yaml

Note the value of ``rgw_frontend_ssl_certificate`` is a literal string as
indicated by a ``|`` character preserving newline characters.

Service specification
---------------------

.. py:currentmodule:: ceph.deployment.service_spec

.. autoclass:: RGWSpec
   :members:

.. _orchestrator-haproxy-service-spec:

High availability service for RGW
=================================

The *ingress* service allows you to create a high availability endpoint
for RGW with a minumum set of configuration options.  The orchestrator will
deploy and manage a combination of haproxy and keepalived to provide load
balancing on a floating virtual IP.

If SSL is used, then SSL must be configured and terminated by the ingress service
and not RGW itself.

.. image:: ../../images/HAProxy_for_RGW.svg

There are N hosts where the ingress service is deployed.  Each host
has a haproxy daemon and a keepalived daemon.  A virtual IP is
automatically configured on only one of these hosts at a time.

Each keepalived daemon checks every few seconds whether the haproxy
daemon on the same host is responding.  Keepalived will also check
that the master keepalived daemon is running without problems.  If the
"master" keepalived daemon or the active haproxy is not responding,
one of the remaining keepalived daemons running in backup mode will be
elected as master, and the virtual IP will be moved to that node.

The active haproxy acts like a load balancer, distributing all RGW requests
between all the RGW daemons available.

Prerequisites
-------------

* An existing RGW service, without SSL.  (If you want SSL service, the certificate
  should be configured on the ingress service, not the RGW service.)

Deploying
---------

Use the command::

    ceph orch apply -i <ingress_spec_file>

Service specification
---------------------

It is a yaml format file with the following properties:

.. code-block:: yaml

    service_type: ingress
    service_id: rgw.something    # adjust to match your existing RGW service
    placement:
      hosts:
        - host1
        - host2
        - host3
    spec:
      backend_service: rgw.something      # adjust to match your existing RGW service
      virtual_ip: <string>/<string>       # ex: 192.168.20.1/24
      frontend_port: <integer>            # ex: 8080
      monitor_port: <integer>             # ex: 1967, used by haproxy for load balancer status
      virtual_interface_networks: [ ... ] # optional: list of CIDR networks
      ssl_cert: |                         # optional: SSL certificate and key
        -----BEGIN CERTIFICATE-----
        ...
        -----END CERTIFICATE-----
        -----BEGIN PRIVATE KEY-----
        ...
        -----END PRIVATE KEY-----

where the properties of this service specification are:

* ``service_type``
    Mandatory and set to "ingress"
* ``service_id``
    The name of the service.  We suggest naming this after the service you are
    controlling ingress for (e.g., ``rgw.foo``).
* ``placement hosts``
    The hosts where it is desired to run the HA daemons. An haproxy and a
    keepalived container will be deployed on these hosts.  These hosts do not need
    to match the nodes where RGW is deployed.
* ``virtual_ip``
    The virtual IP (and network) in CIDR format where the ingress service will be available.
* ``virtual_interface_networks``
    A list of networks to identify which ethernet interface to use for the virtual IP.
* ``frontend_port``
    The port used to access the ingress service.
* ``ssl_cert``:
    SSL certificate, if SSL is to be enabled. This must contain the both the certificate and
    private key blocks in .pem format.

.. _ingress-virtual-ip:

Selecting ethernet interfaces for the virtual IP
------------------------------------------------

You cannot simply provide the name of the network interface on which
to configure the virtual IP because interface names tend to vary
across hosts (and/or reboots).  Instead, cephadm will select
interfaces based on other existing IP addresses that are already
configured.

Normally, the virtual IP will be configured on the first network
interface that has an existing IP in the same subnet.  For example, if
the virtual IP is 192.168.0.80/24 and eth2 has the static IP
192.168.0.40/24, cephadm will use eth2.

In some cases, the virtual IP may not belong to the same subnet as an existing static
IP.  In such cases, you can provide a list of subnets to match against existing IPs,
and cephadm will put the virtual IP on the first network interface to match.  For example,
if the virtual IP is 192.168.0.80/24 and we want it on the same interface as the machine's
static IP in 10.10.0.0/16, you can use a spec like::

  service_type: ingress
  service_id: rgw.something
  spec:
    virtual_ip: 192.168.0.80/24
    virtual_interface_networks:
      - 10.10.0.0/16
    ...

A consequence of this strategy is that you cannot currently configure the virtual IP
on an interface that has no existing IP address.  In this situation, we suggest
configuring a "dummy" IP address is an unroutable network on the correct interface
and reference that dummy network in the networks list (see above).


Useful hints for ingress
------------------------

* It is good to have at least 3 RGW daemons.
* We recommend at least 3 hosts for the ingress service.

Further Reading
===============

* :ref:`object-gateway`

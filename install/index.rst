.. _install-overview:

===========
 安装 Ceph
===========

There are several different ways to install Ceph.  Choose the
method that best suits your needs.

建议的方法
~~~~~~~~~~
.. Recommended methods

:ref:`Cephadm <cephadm>` installs and manages a Ceph cluster using containers and
systemd, with tight integration with the CLI and dashboard GUI.

* cephadm only supports Octopus and newer releases.
* cephadm is fully integrated with the new orchestration API and
  fully supports the new CLI and dashboard features to manage
  cluster deployment.
* cephadm requires container support (podman or docker) and
  Python 3.

`Rook <https://rook.io/>`_ deploys and manages Ceph clusters running
in Kubernetes, while also enabling management of storage resources and
provisioning via Kubernetes APIs.  We recommend Rook as the way to run Ceph in
Kubernetes or to connect an existing Ceph storage cluster to Kubernetes.

* Rook only supports Nautilus and newer releases of Ceph.
* Rook is the preferred method for running Ceph on Kubernetes, or for
  connecting a Kubernetes cluster to an existing (external) Ceph
  cluster.
* Rook supports the new orchestrator API. New management features
  in the CLI and dashboard are fully supported.

其他方法
~~~~~~~~
.. Other methods

`ceph-ansible <https://docs.ceph.com/ceph-ansible/>`_ 使用
Ansible 来部署和管理 Ceph 集群。

* ceph-ansible is widely deployed.
* ceph-ansible is not integrated with the new orchestrator APIs,
  introduced in Nautlius and Octopus, which means that newer
  management features and dashboard integration are not available.


`ceph-deploy <https://docs.ceph.com/projects/ceph-deploy/en/latest/>`_ is a tool for quickly deploying clusters.

  .. IMPORTANT::

   ceph-deploy is no longer actively maintained. It is not tested on versions of Ceph newer than Nautilus. It does not support RHEL8, CentOS 8, or newer operating systems.

`ceph-salt <https://github.com/ceph/ceph-salt>`_ installs Ceph using Salt and cephadm.

`jaas.ai/ceph-mon <https://jaas.ai/ceph-mon>`_ installs Ceph using Juju.

`github.com/openstack/puppet-ceph <https://github.com/openstack/puppet-ceph>`_  installs Ceph via Puppet.

Ceph can also be :ref:`installed manually <install-manual>`.


.. toctree::
   :hidden:

   index_manual

Windows
~~~~~~~

For Windows installations, please consult this document:
`Windows installation guide`_.

.. _Windows installation guide: ./windows-install

=======================
Developing with cephadm
=======================

There are several ways to develop with cephadm.  Which you use depends
on what you're trying to accomplish.

vstart --cephadm
================

- Start a cluster with vstart, with cephadm configured
- Manage any additional daemons with cephadm
- Requires compiled ceph binaries

In this case, the mon and manager at a minimum are running in the usual
vstart way, not managed by cephadm.  But cephadm is enabled and the local
host is added, so you can deploy additional daemons or add additional hosts.

This works well for developing cephadm itself, because any mgr/cephadm
or cephadm/cephadm code changes can be applied by kicking ceph-mgr
with ``ceph mgr fail x``.  (When the mgr (re)starts, it loads the
cephadm/cephadm script into memory.)

::

   MON=1 MGR=1 OSD=0 MDS=0 ../src/vstart.sh -d -n -x --cephadm

- ``~/.ssh/id_dsa[.pub]`` is used as the cluster key.  It is assumed that
  this key is authorized to ssh with no passphrase to root@`hostname`.
- cephadm does not try to manage any daemons started by vstart.sh (any
  nonzero number in the environment variables).  No service spec is defined
  for mon or mgr.
- You'll see health warnings from cephadm about stray daemons--that's because
  the vstart-launched daemons aren't controlled by cephadm.
- The default image is ``quay.io/ceph-ci/ceph:master``, but you can change
  this by passing ``-o container_image=...`` or ``ceph config set global container_image ...``.


cstart and cpatch
=================

The ``cstart.sh`` script will launch a cluster using cephadm and put the
conf and keyring in your build dir, so that the ``bin/ceph ...`` CLI works
(just like with vstart).  The ``ckill.sh`` script will tear it down.

- A unique but stable fsid is stored in ``fsid`` (in the build dir).
- The mon port is random, just like with vstart.
- The container image is ``quay.io/ceph-ci/ceph:$tag`` where $tag is
  the first 8 chars of the fsid.
- If the container image doesn't exist yet when you run cstart for the
  first time, it is built with cpatch.

There are a few advantages here:

- The cluster is a "normal" cephadm cluster that looks and behaves
  just like a user's cluster would.  In contract, vstart and teuthology
  clusters tend to be special in subtle (and not-so-subtle) ways.

To start a test cluster::

  sudo ../src/cstart.sh

The last line of this will be a line you can cut+paste to update the
container image.  For instance::

  sudo ../src/script/cpatch -t quay.io/ceph-ci/ceph:8f509f4e

By default, cpatch will patch everything it can think of from the local
build dir into the container image.  If you are working on a specific
part of the system, though, can you get away with smaller changes so that
cpatch runs faster.  For instance::

  sudo ../src/script/cpatch -t quay.io/ceph-ci/ceph:8f509f4e --py

will update the mgr modules (minus the dashboard).  Or::

  sudo ../src/script/cpatch -t quay.io/ceph-ci/ceph:8f509f4e --core

will do most binaries and libraries.  Pass ``-h`` to cpatch for all options.

Once the container is updated, you can refresh/restart daemons by bouncing
them with::

  sudo systemctl restart ceph-`cat fsid`.target

When you're done, you can tear down the cluster with::

  sudo ../src/ckill.sh   # or,
  sudo ../src/cephadm/cephadm rm-cluster --force --fsid `cat fsid`

cephadm bootstrap --shared_ceph_folder
======================================

Cephadm can also be used directly without compiled ceph binaries.

Run cephadm like so::

  sudo ./cephadm bootstrap --mon-ip 127.0.0.1 \
    --ssh-private-key /home/<user>/.ssh/id_rsa \
    --skip-mon-network \
    --skip-monitoring-stack --single-host-defaults \
    --skip-dashboard \ 
    --shared_ceph_folder /home/<user>/path/to/ceph/

- ``~/.ssh/id_rsa`` is used as the cluster key.  It is assumed that
  this key is authorized to ssh with no passphrase to root@`hostname`.

Source code changes made in the ``pybind/mgr/`` directory then
require a daemon restart to take effect. 

Note regarding network calls from CLI handlers
==============================================

Executing any cephadm CLI commands like ``ceph orch ls`` will block the
mon command handler thread within the MGR, thus preventing any concurrent
CLI calls. Note that pressing ``^C`` will not resolve this situation,
as *only* the client will be aborted, but not execution of the command
within the orchestrator manager module itself. This means, cephadm will
be completely unresponsive until the execution of the CLI handler is
fully completed. Note that even ``ceph orch ps`` will not respond while
another handler is executing.

This means we should do very few synchronous calls to remote hosts.
As a guideline, cephadm should do at most ``O(1)`` network calls in CLI handlers.
Everything else should be done asynchronously in other threads, like ``serve()``.

Note regarding different variables used in the code
===================================================

* a ``service_type`` is something like mon, mgr, alertmanager etc defined 
  in ``ServiceSpec``
* a ``service_id`` is the name of the service. Some services don't have 
  names.
* a ``service_name`` is ``<service_type>.<service_id>``
* a ``daemon_type`` is the same as the service_type, except for ingress,
  which has the haproxy and keepalived daemon types.
* a ``daemon_id`` is typically ``<service_id>.<hostname>.<random-string>``. 
  (Not the case for e.g. OSDs. OSDs are always called OSD.N)
* a ``daemon_name`` is ``<daemon_type>.<daemon_id>``

Kcli: a virtualization management tool to make easy orchestrators development
=============================================================================
`Kcli <https://github.com/karmab/kcli>`_ is meant to interact with existing
virtualization providers (libvirt, KubeVirt, oVirt, OpenStack, VMware vSphere,
GCP and AWS) and to easily deploy and customize VMs from cloud images.

It allows you to setup an environment with several vms with your preferred
configuration (memory, cpus, disks) and OS flavor.

main advantages:
----------------
  - Fast. Typically you can have a completely new Ceph cluster ready to debug
    and develop orchestrator features in less than 5 minutes.
  - "Close to production" lab. The resulting lab is close to "real" clusters
    in QE labs or even production. It makes it easy to test "real things" in
    an almost "real" environment.
  - Safe and isolated. Does not depend of the things you have installed in 
    your machine. And the vms are isolated from your environment.
  - Easy to work "dev" environment. For "not compilated" software pieces,
    for example any mgr module. It is an environment that allow you to test your
    changes interactively.

Installation:
-------------
Complete documentation in `kcli installation <https://kcli.readthedocs.io/en/latest/#installation>`_
but we suggest to use the container image approach.

So things to do:
  - 1. Review `requeriments <https://kcli.readthedocs.io/en/latest/#libvirt-hypervisor-requisites>`_
    and install/configure whatever is needed to meet them.
  - 2. get the kcli image and create one alias for executing the kcli command
    ::

        # podman pull quay.io/karmab/kcli
        # alias kcli='podman run --net host -it --rm --security-opt label=disable -v $HOME/.ssh:/root/.ssh -v $HOME/.kcli:/root/.kcli -v /var/lib/libvirt/images:/var/lib/libvirt/images -v /var/run/libvirt:/var/run/libvirt -v $PWD:/workdir -v /var/tmp:/ignitiondir quay.io/karmab/kcli'

.. note:: This assumes that /var/lib/libvirt/images is your default libvirt pool.... Adjust if using a different path

.. note:: Once you have used your kcli tool to create and use different labs, we
   suggest you stick to a given container tag and update your kcli alias.
   Why? kcli uses a rolling release model and sticking to a specific
   container tag will improve overall stability.
   what we want is overall stability.

Test your kcli installation:
----------------------------
See the kcli `basic usage workflow <https://kcli.readthedocs.io/en/latest/#basic-workflow>`_

Create a Ceph lab cluster
-------------------------
In order to make this task simple, we are going to use a "plan".

A "plan" is a file where you can define a set of vms with different settings.
You can define hardware parameters (cpu, memory, disks ..), operating system and
it also allows you to automate the installation and configuration of any
software you want to have.

There is a `repository <https://github.com/karmab/kcli-plans>`_ with a collection of
plans that can be used for different purposes. And we have predefined plans to
install Ceph clusters using Ceph ansible or cephadm, so let's create our first Ceph
cluster using cephadm::

# kcli create plan -u https://github.com/karmab/kcli-plans/blob/master/ceph/ceph_cluster.yml

This will create a set of three vms using the plan file pointed by the url.
After a few minutes, let's check the cluster:

* Take a look to the vms created::

  # kcli list vms

* Enter in the bootstrap node::

  # kcli ssh ceph-node-00

* Take a look to the ceph cluster installed::

  [centos@ceph-node-00 ~]$ sudo -i
  [root@ceph-node-00 ~]# cephadm version
  [root@ceph-node-00 ~]# cephadm shell
  [ceph: root@ceph-node-00 /]# ceph orch host ls

Create a Ceph cluster to make easy developing in mgr modules (Orchestrators and Dashboard)
------------------------------------------------------------------------------------------
The cephadm kcli plan (and cephadm) are prepared to do that.

The idea behind this method is to replace several python mgr folders in each of
the ceph daemons with the source code folders in your host machine.
This "trick" will allow you to make changes in any orchestrator or dashboard
module and test them intermediately. (only needed to disable/enable the mgr module)

So in order to create a ceph cluster for development purposes you must use the
same cephadm plan but with a new parameter pointing to your Ceph source code folder::

  # kcli create plan -u https://github.com/karmab/kcli-plans/blob/master/ceph/ceph_cluster.yml -P ceph_dev_folder=/home/mycodefolder/ceph

Ceph Dashboard development
--------------------------
Ceph dashboard module is not going to be loaded if previously you have not
generated the frontend bundle.

For now, in order load properly the Ceph Dashboardmodule and to apply frontend
changes you have to run "ng build" on your laptop::

  # Start local frontend build with watcher (in background):
  sudo dnf install -y nodejs
  cd <path-to-your-ceph-repo>
  cd src/pybind/mgr/dashboard/frontend
  sudo chown -R <your-user>:root dist node_modules
  NG_CLI_ANALYTICS=false npm ci
  npm run build -- --deleteOutputPath=false --watch &

After saving your changes, the frontend bundle will be built again.
When completed, you'll see::

  "Localized bundle generation complete."

Then you can reload your Dashboard browser tab.

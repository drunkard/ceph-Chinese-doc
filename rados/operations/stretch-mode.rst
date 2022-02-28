.. _stretch_mode:

================
Stretch Clusters
================


Stretch Clusters
================
Ceph generally expects all parts of its network and overall cluster to be
equally reliable, with failures randomly distributed across the CRUSH map.
So you may lose a switch that knocks out a number of OSDs, but we expect
the remaining OSDs and monitors to route around that.

This is usually a good choice, but may not work well in some
stretched cluster configurations where a significant part of your cluster
is stuck behind a single network component. For instance, a single
cluster which is located in multiple data centers, and you want to
sustain the loss of a full DC.

There are two standard configurations we've seen deployed, with either
two or three data centers (or, in clouds, availability zones). With two
zones, we expect each site to hold a copy of the data, and for a third
site to have a tiebreaker monitor (this can be a VM or high-latency compared
to the main sites) to pick a winner if the network connection fails and both
DCs remain alive. For three sites, we expect a copy of the data and an equal
number of monitors in each site.

Note that the standard Ceph configuration will survive MANY failures of the
network or data centers and it will never compromise data consistency.  If you
bring back enough Ceph servers following a failure, it will recover. If you
lose a data center, but can still form a quorum of monitors and have all the data
available (with enough copies to satisfy pools' ``min_size``, or CRUSH rules
that will re-replicate to meet it), Ceph will maintain availability.

What can't it handle?

Stretch Cluster Issues
======================
No matter what happens, Ceph will not compromise on data integrity
and consistency. If there's a failure in your network or a loss of nodes and
you can restore service, Ceph will return to normal functionality on its own.

But there are scenarios where you lose data availability despite having
enough servers available to satisfy Ceph's consistency and sizing constraints, or
where you may be surprised to not satisfy Ceph's constraints.
The first important category of these failures resolve around inconsistent
networks -- if there's a netsplit, Ceph may be unable to mark OSDs down and kick
them out of the acting PG sets despite the primary being unable to replicate data.
If this happens, IO will not be permitted, because Ceph can't satisfy its durability
guarantees.

The second important category of failures is when you think you have data replicated
across data centers, but the constraints aren't sufficient to guarantee this.
For instance, you might have data centers A and B, and your CRUSH rule targets 3 copies
and places a copy in each data center with a ``min_size`` of 2. The PG may go active with
2 copies in site A and no copies in site B, which means that if you then lose site A you
have lost data and Ceph can't operate on it. This situation is surprisingly difficult
to avoid with standard CRUSH rules.

Stretch Mode
============
The new stretch mode is designed to handle the 2-site case. Three sites are
just as susceptible to netsplit issues, but are much more tolerant of
component availability outages than 2-site clusters are.

To enter stretch mode, you must set the location of each monitor, matching
your CRUSH map. For instance, to place ``mon.a`` in your first data center ::

  $ ceph mon set_location a datacenter=site1

Next, generate a CRUSH rule which will place 2 copies in each data center. This
will require editing the CRUSH map directly::

  $ ceph osd getcrushmap > crush.map.bin
  $ crushtool -d crush.map.bin -o crush.map.txt

Now edit the ``crush.map.txt`` file to add a new rule. Here
there is only one other rule, so this is ID 1, but you may need
to use a different rule ID. We also have two datacenter buckets
named ``site1`` and ``site2``::

  rule stretch_rule {
          id 1
          type replicated
          min_size 1
          max_size 10
          step take site1
          step chooseleaf firstn 2 type host
          step emit
          step take site2
          step chooseleaf firstn 2 type host
          step emit
  }

Finally, inject the CRUSH map to make the rule available to the cluster::

  $ crushtool -c crush.map.txt -o crush2.map.bin
  $ ceph osd setcrushmap -i crush2.map.bin

If you aren't already running your monitors in connectivity mode, do so with
the instructions in `Changing Monitor Elections`_.

.. _Changing Monitor elections: ../change-mon-elections

And lastly, tell the cluster to enter stretch mode. Here, ``mon.e`` is the
tiebreaker and we are splitting across data centers. ``mon.e`` should be also
set a datacenter, that will differ from ``site1`` and ``site2``. For this
purpose you can create another datacenter bucket named ```site3`` in your
CRUSH and place ``mon.e`` there ::

  $ ceph mon set_location e datacenter=site3
  $ ceph mon enable_stretch_mode e stretch_rule datacenter

When stretch mode is enabled, the OSDs will only take PGs active when
they peer across data centers (or whatever other CRUSH bucket type
you specified), assuming both are alive. Pools will increase in size
from the default 3 to 4, expecting 2 copies in each site. OSDs will only
be allowed to connect to monitors in the same data center. New monitors
will not be allowed to join the cluster if they do not specify a location.

If all the OSDs and monitors from a data center become inaccessible
at once, the surviving data center will enter a degraded stretch mode. This
will issue a warning, reduce the min_size to 1, and allow
the cluster to go active with data in the single remaining site. Note that
we do not change the pool size, so you will also get warnings that the
pools are too small -- but a special stretch mode flag will prevent the OSDs
from creating extra copies in the remaining data center (so it will only keep
2 copies, as before).

When the missing data center comes back, the cluster will enter
recovery stretch mode. This changes the warning and allows peering, but
still only requires OSDs from the data center which was up the whole time.
When all PGs are in a known state, and are neither degraded nor incomplete,
the cluster transitions back to regular stretch mode, ends the warning,
restores min_size to its starting value (2) and requires both sites to peer,
and stops requiring the always-alive site when peering (so that you can fail
over to the other site, if necessary).

Stretch Mode Limitations
========================
As implied by the setup, stretch mode only handles 2 sites with OSDs.

While it is not enforced, you should run 2 monitors in each site plus
a tiebreaker, for a total of 5. This is because OSDs can only connect
to monitors in their own site when in stretch mode.

You cannot use erasure coded pools with stretch mode. If you try, it will
refuse, and it will not allow you to create EC pools once in stretch mode.

You must create your own CRUSH rule which provides 2 copies in each site, and
you must use 4 total copies with 2 in each site. If you have existing pools
with non-default size/min_size, Ceph will object when you attempt to
enable stretch mode.

Because it runs with ``min_size 1`` when degraded, you should only use stretch
mode with all-flash OSDs.  This minimizes the time needed to recover once
connectivity is restored, and thus minimizes the potential for data loss.

Hopefully, future development will extend this feature to support EC pools and
running with more than 2 full sites.

Other commands
==============
If your tiebreaker monitor fails for some reason, you can replace it. Turn on
a new monitor and run ::

  $ ceph mon set_new_tiebreaker mon.<new_mon_name>

This command will protest if the new monitor is in the same location as existing
non-tiebreaker monitors. This command WILL NOT remove the previous tiebreaker
monitor; you should do so yourself.

If you are writing your own tooling for deploying Ceph, you can use a new
``--set-crush-location`` option when booting monitors, instead of running
``ceph mon set_location``. This option accepts only a single "bucket=loc" pair, eg
``ceph-mon --set-crush-location 'datacenter=a'``, which must match the
bucket type you specified when running ``enable_stretch_mode``.


When in stretch degraded mode, the cluster will go into "recovery" mode automatically
when the disconnected data center comes back. If that doesn't work, or you want to
enable recovery mode early, you can invoke ::

  $ ceph osd force_recovery_stretch_mode --yes-i-really-mean-it

But this command should not be necessary; it is included to deal with
unanticipated situations.

When in recovery mode, the cluster should go back into normal stretch mode
when the PGs are healthy. If this doesn't happen, or you want to force the
cross-data-center peering early and are willing to risk data downtime (or have
verified separately that all the PGs can peer, even if they aren't fully
recovered), you can invoke ::

  $ ceph osd force_healthy_stretch_mode --yes-i-really-mean-it

This command should not be necessary; it is included to deal with
unanticipated situations. But you might wish to invoke it to remove
the ``HEALTH_WARN`` state which recovery mode generates.

.. Device Management
.. _devices:

设备管理
========

Ceph tracks which hardware storage devices (e.g., HDDs, SSDs) are consumed by
which daemons, and collects health metrics about those devices in order to
provide tools to predict and/or automatically respond to hardware failure.


.. Device tracking

设备跟踪
--------

You can query which storage devices are in use with::

  ceph device ls

You can also list devices by daemon or by host::

  ceph device ls-by-daemon <daemon>
  ceph device ls-by-host <host>

For any individual device, you can query information about its
location and how it is being consumed with::

  ceph device info <devid>


Identifying physical devices
----------------------------

You can blink the drive LEDs on hardware enclosures to make the replacement of
failed disks easy and less error-prone.  Use the following command::

  device light on|off <devid> [ident|fault] [--force]

The ``<devid>`` parameter is the device identification. You can obtain this
information using the following command::

  ceph device ls

The ``[ident|fault]`` parameter is used to set the kind of light to blink.
By default, the `identification` light is used.

.. note::
   This command needs the Cephadm or the Rook `orchestrator <https://docs.ceph.com/docs/master/mgr/orchestrator/#orchestrator-cli-module>`_ module enabled.
   The orchestrator module enabled is shown by executing the following command::

     ceph orch status

The command behind the scene to blink the drive LEDs is `lsmcli`. If you need
to customize this command you can configure this via a Jinja2 template::

   ceph config-key set mgr/cephadm/blink_device_light_cmd "<template>"
   ceph config-key set mgr/cephadm/<host>/blink_device_light_cmd "lsmcli local-disk-{{ ident_fault }}-led-{{'on' if on else 'off'}} --path '{{ path or dev }}'"

The Jinja2 template is rendered using the following arguments:

* ``on``
    A boolean value.
* ``ident_fault``
    A string containing `ident` or `fault`.
* ``dev``
    A string containing the device ID, e.g. `SanDisk_X400_M.2_2280_512GB_162924424784`.
* ``path``
    A string containing the device path, e.g. `/dev/sda`.


.. Enabling monitoring
.. _enabling-monitoring:

打开监控
--------

Ceph can also monitor health metrics associated with your device.  For
example, SATA hard disks implement a standard called SMART that
provides a wide range of internal metrics about the device's usage and
health, like the number of hours powered on, number of power cycles,
or unrecoverable read errors.  Other device types like SAS and NVMe
implement a similar set of metrics (via slightly different standards).
All of these can be collected by Ceph via the ``smartctl`` tool.

You can enable or disable health monitoring with::

  ceph device monitoring on

or::

  ceph device monitoring off


Scraping
--------
如果打开了监控，指标会定期自动 scrape 。这个间隔时间可以这样\
配置： ::

  ceph config set mgr mgr/devicehealth/scrape_frequency <seconds>

The default is to scrape once every 24 hours.

You can manually trigger a scrape of all devices with::

  ceph device scrape-health-metrics

A single device can be scraped with::

  ceph device scrape-health-metrics <device-id>

Or a single daemon's devices can be scraped with::

  ceph device scrape-daemon-health-metrics <who>

The stored health metrics for a device can be retrieved (optionally
for a specific timestamp) with::

  ceph device get-health-metrics <devid> [sample-timestamp]


.. Failure prediction

失败预测
--------

Ceph can predict life expectancy and device failures based on the
health metrics it collects.  There are three modes:

* *none*: disable device failure prediction.
* *local*: use a pre-trained prediction model from the ceph-mgr daemon

The prediction mode can be configured with::

  ceph config set global device_failure_prediction_mode <mode>

Prediction normally runs in the background on a periodic basis, so it
may take some time before life expectancy values are populated.  You
can see the life expectancy of all devices in output from::

  ceph device ls

You can also query the metadata for a specific device with::

  ceph device info <devid>

You can explicitly force prediction of a device's life expectancy with::

  ceph device predict-life-expectancy <devid>

If you are not using Ceph's internal device failure prediction but
have some external source of information about device failures, you
can inform Ceph of a device's life expectancy with::

  ceph device set-life-expectancy <devid> <from> [<to>]

Life expectancies are expressed as a time interval so that
uncertainty can be expressed in the form of a wide interval. The
interval end can also be left unspecified.


.. Health alerts

健康警报
--------

The ``mgr/devicehealth/warn_threshold`` controls how soon an expected
device failure must be before we generate a health warning.

The stored life expectancy of all devices can be checked, and any
appropriate health alerts generated, with::

  ceph device check-health


.. Automatic Mitigation

自动化的迁移
------------

If the ``mgr/devicehealth/self_heal`` option is enabled (it is by
default), then for devices that are expected to fail soon the module
will automatically migrate data away from them by marking the devices
"out".

The ``mgr/devicehealth/mark_out_threshold`` controls how soon an
expected device failure must be before we automatically mark an osd
"out".



#                       IDENTIFICATION DIVISION



# FJ Data Collector

This is an aggregator for data collection that populates data in Graphiteapp and since Grafana integrates with Graphite you can draw your graphs in Grafana.

The Collector is a scheduler that collects information based in a YAML file, each schedule runs on it's own thread and it's completly free:
https://github.com/ajcpereira/fj-collector

Regarding the other 2 mention applications be aware of their licenses if you wish to use in your organization.
Our makefile installs both but they are not part of the code of the fj-collector, so you should check your policies or maybe you already have them in your organization so you can use them:

Graphite - https://graphiteapp.org/ - 26/07/2023: (...) Graphite was originally designed and written by Chris Davis at Orbitz in 2006 as side project that ultimately grew to be their foundational monitoring tool. In 2008, Orbitz allowed Graphite to be released under the open source Apache 2.0 license.(...)

Grafana - https://grafana.com/licensing/ - 26/07/2023: (...) On April 20, 2021, Grafana Labs announced that going forward, our core open source projects will be moving from the Apache License v2.0 to AGPLv3.
Users who don’t intend to modify Grafana code can simply use our Enterprise download. This is a free-to-use, proprietary-licensed, compiled binary that matches the features of the AGPL version, and can be upgraded to take advantage of all the commercial features in Grafana Enterprise (Enterprise plugins, advanced security, reporting, support, and more) with the purchase of a license key. (...)

### Requirements

Requires linux

Requires podman (also dnsmasq)
   In Ubuntu there's a bug with podman - https://bugs.launchpad.net/ubuntu/+source/libpod/+bug/2024394 - please rollback if not solved by the time you are using - apt install podman=3.4.4+ds1-1ubuntu1

Requires git

Internet access to github.com

Will install under folder /opt/fj-collector

Your user must have permissions in /opt and run podman

### Installation Procedure

Clone the git repository:

````
git clone https://github.com/ajcpereira/fj-collector.git
````

Now, just run the install

````
cd fj-collector
make setup
make start
````

edit /opt/fj-collector/collector/config/collector.yaml

For each IP that you access through ssh you will need the private key.
On the previous file (collector.yaml) you can specifie it's location (host_keys entry)
Be aware that since the code runs inside a container the collector.yaml uses the path inside of the container, so:
  /collector/fj-collector/config/
  is your
  /opt/fj-collector/collector/config/

  We recommend you use relative paths:
    host_keys: keys/id_rsa
    logfile: logs/fj-collector.log
 
### collector.yaml
````
systems:
  - name: MYCS8000
    resources_types: eternus_icp
    config:
      parameters:
          user: alex
          host_keys: keys/id_rsa
          poll: 1
          bastion: 172.21.69.166
      metrics:
          - name: fs
      ips:
          - ip: 172.21.69.166
            alias: icp0
          - ip: 172.21.69.166
            ip_host_keys: keys/id_rsa
            ip_bastion: 172.21.69.166
global_parameters:
  repository: graphite
  repository_port: 2003
  repository_protocol: tcp
  loglevel: INFO
  logfile: logs/fj-collector.log
````  

### Metrics

Atm we are collecting the iostat for each CS HE filesystem, so you will get filesystem, device multipath and raw device with metrics for:
type: fs
  - svctm
  - %util

### Metrics Retention

You MUST edit the /opt/fj-collector/graphite/data/conf/storage-schemas.conf to change retentions according to your needs:

````
[default_1min_for_1day]
pattern = .*
retentions = 10s:6d,1m:12d,10m:1800d
````

Changing this file will not affect already-created .wsp files. Use whisper-resize.py to change those.

The retentions line is saying that each datapoint represents 10 seconds, and we want to keep enough datapoints so that they add up to 6 hours of data, for 1 minute will keep 6 days and finally for 10 minutes will keep for 1800 days. It will properly downsample metrics (averaging by default) as thresholds for retention are crossed.

More info can be found - https://graphite.readthedocs.io/en/latest/config-carbon.html

### Architecture
![Design](https://github.com/ajcpereira/reporting/raw/main/img/design.png)
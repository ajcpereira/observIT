## FJ Data Collection
### Collects data and populate it in Graphite, using the native integration of Grafana dashboards can be drawn.
### Only uses ssh at the moment to collect data, but SNMP and RestAPI will be supported


### Requirements

Requires docker
Requires git

Requires folder /opt/fj-collector/collector/logs
Requires folder /opt/fj-collector/collector/config must include the "collector.yml" file:

### Installation Procedure

````
cd /opt
git clone https://github.com/ajcpereira/fj-collector.git
cd fj-collector
docker-compose up
````

inside /opt/fj-collector/collector/config create the following collector.yaml
 
### collector.yaml
````
solution: 
  platform: 
    - 
      type: CS8000    # Only CS8000 supported atm
      name: MYCS8000
      resources: 
        type: 
          - fs  # fs=filesystem only supported for now
        ip: 
          - 10.0.2.15
        user: report
        proxy: # Leave empty if not using otherwise insert IP/FQDN/HOSTNAME
        poll: 1 # Minute
    - 
      type: CS8000    # Only CS8000 supported
      name: SecondCS8000
      resources: 
        type: 
          - fs # fs=filesystem only supported for now
        ip: 
          - localhost
        user: report
        proxy: # Not supported yet
        poll: 2 # Minutes

parameters:
  repository: graphite
  repository_port: 2003
  repository_protocol: tcp
  host_keys: "/collector/fj-collector/config/id_rsa" # You will have to use a private key - ssh-copy-id username@remote_host, must be done previously
  known_hosts: "/collector/fj-collector/config/known_hosts" # If host is unknown the process will fail
  use_sudo: no
  log: INFO # The log level - DEBUG, INFO, WARNING, ERROR and CRITICAL
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
retentions = 10s:6h,1m:6d,10m:1800d
````

Changing this file will not affect already-created .wsp files. Use whisper-resize.py to change those.

The retentions line is saying that each datapoint represents 10 seconds, and we want to keep enough datapoints so that they add up to 6 hours of data, for 1 minute will keep 6 days and finally for 10 minutes will keep for 1800 days. It will properly downsample metrics (averaging by default) as thresholds for retention are crossed.

More info can be found - https://graphite.readthedocs.io/en/latest/config-carbon.html

### Architecture
![Design](https://github.com/ajcpereira/reporting/raw/main/img/design.png)



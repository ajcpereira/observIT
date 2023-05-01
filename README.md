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
      type: CS8000    # Only CS8000 supported
      name: MYCS8000
      resources: 
        type: 
          - fs  # fs=filesystem only supported for now
        ip: 
          - 10.0.2.15
        user: report
        proxy: # Not supported yet
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
````  

### Metrics

Atm we are collecting the iostat for each CS HE filesystem

### Architecture
![Design](https://github.com/ajcpereira/reporting/raw/main/img/design.png)



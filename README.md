## FJ Data Collection
### Collects data and populate it in Graphite, using the native integration of Grafana dashboards can be drawn.
### Only uses ssh at the moment to collect data, but SNMP and RestAPI will be supported


### Requirements

Requires docker

Requires folder /opt/fj-collector/collector/logs
Requires folder /opt/fj-collector/collector/config must include the "collector.yml" file:

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
  repository: 172.17.0.3
  repository_port: 2003
  repository_protocol: tcp
  host_keys: "/opt/fj-collector/collector/config/id_rsa" # You can use the public key here or the private - ssh-copy-id username@remote_host, must be done previously
  know_hosts: "/opt/fj-collector/collector/config/known_hosts" # If host is unknown the process will fail
  use_sudo: no
````  


### Installation Procedure

Copy the docker-compose.yml and run docker

````
docker compose up
````

### Architecture
![Design](https://github.com/ajcpereira/reporting/raw/main/img/design.png)



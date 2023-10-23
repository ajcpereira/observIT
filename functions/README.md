

#                       IDENTIFICATION DIVISION



# Available Functions

Here you will find the information for each resource type

## ETERNUS_ICP

Protocol: ssh<br>
Security: The user must be created previously and we recommend a common user with permissions only to sudo the following command: /opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out<br>
Database Structure:<br>
  system name<br>
  resources_types<br>
  hostname or alias<br>
  metric name<br>
  filesytem name from CS<br>
  dm disk from CS<br>
  raw disk from CS<br>
  svctm/r_await/w_await<br>

with the example config file structure would be:
MYCS8000.eternus_icp.localhost.fs.filesystem-name.dm-disk.rdisk.svctm
MYCS8000.eternus_icp.localhost.fs.filesystem-name.dm-disk.rdisk.r_await
MYCS8000.eternus_icp.localhost.fs.filesystem-name.dm-disk.rdisk.w_await

### TEST ENVIRONMENT

If file cafs_iostat exists under the dir tests it will be used instead of real data.

### Config File example

````
systems:
  - name: MYCS8000
    resources_types: eternus_icp
    config:
      parameters:
          user: myuser
          host_keys: keys/id_rsa
          poll: 1
          use_sudo: yes
          bastion: 127.0.0.1
      metrics:
          - name: fs
      ips:
          - ip: 127.0.0.1
            alias: localhost
            ip_use_sudo: yes
            ip_bastion: 127.0.0.1
          - ip: 10.10.1.2
          - ip: 10.10.2.3
            ip_use_sudo: no
            ip_host_keys: keys/mykey
````

## LINUX_OS

Protocol: ssh<br>
Security: A user with access to the remote server, no root privileges needed<br>
Database Structure:<br>
collector_root<br>
system<br>
resource_type<br>
host ip or alias<br>
metric category [cpu, mem, fs, net] <br>
monitored resource if any [fs name, net iface] <br>
metric name (depends of metric category)<br>


with the example config file structure would be:<br>
#### CPU metrics
tst-collector.LAB.linux_os.linux01.cpu.use<br>
tst-collector.LAB.linux_os.linux01.cpu.iowait<br>
tst-collector.LAB.linux_os.linux01.cpu.load1m<br>
tst-collector.LAB.linux_os.linux01.cpu.load5m<br>
tst-collector.LAB.linux_os.linux01.cpu.load15m<br>
#### Memory metrics
tst-collector.LAB.linux_os.linux01.mem.total<br>
tst-collector.LAB.linux_os.linux01.mem.used<br>
tst-collector.LAB.linux_os.linux01.mem.free<br>
tst-collector.LAB.linux_os.linux01.mem.shared<br>
tst-collector.LAB.linux_os.linux01.mem.buff<br>
tst-collector.LAB.linux_os.linux01.mem.avail<br>
#### Filesystem metrics
For each filesystem collects the following values in GB:<br>
tst-collector.LAB.linux_os.linux01.fs.{filesystem name}.available<br>
tst-collector.LAB.linux_os.linux01.fs.{filesystem name}.used<br>
tst-collector.LAB.linux_os.linux01.fs.{filesystem name}.total<br>

#### Network metrics
collects for each network interface in status connected values in Mbp<br>

tst-collector.LAB.linux_os.linux01.net.{iface}.rx_mbp<br>
tst-collector.LAB.linux_os.linux01.net.{iface}.tx_mbp<br>

{iface} is the interface name.<br>

### TEST ENVIRONMENT

No test data is available at the moment

### Config File example

````
systems:
  - name: LAB
    resources_types: linux_os
    config:
      parameters:
          user: super
          host_keys: keys/id_rsa
          poll: 1
      metrics:
          - name: cpu
          - name: mem
          - name: fs
          - name: net
      ips:
          - ip: 127.0.0.1
            alias: linux01
          - ip: 127.0.0.1
global_parameters:
  repository: 10.89.0.5
  repository_port: 2003
  repository_protocol: tcp
  collector_root: tst-collector
  loglevel: DEBUG
  logfile: logs/fj-collector.log
  grafana_auto_fun: yes
  grafana_api_key: *****
  grafana_server: localhost:3000
````
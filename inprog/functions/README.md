

#                       IDENTIFICATION DIVISION



# Available Functions

Here you will find the information for each resource type

### ETERNUS_ICP

Protocol: ssh
Security: The user must be created previously and we recommend a common user with permissions only to sudo the following command: /opt/fsc/CentricStor/bin/rdNsdInfos -a > /tmp/stats_nsd.out
Database Structure:
  system name
  resources_types
  hostname or alias
  metric name
  svctm/r_await/w_await

with the example config file structure would be:
MYCS8000.eternus_icp.localhost.fs.filesystem-name.disk.svctm
MYCS8000.eternus_icp.localhost.fs.filesystem-name.disk.r_await
MYCS8000.eternus_icp.localhost.fs.filesystem-name.disk.w_await

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
````

### LINUX_OS
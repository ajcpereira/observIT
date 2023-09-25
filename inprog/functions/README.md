

#                       IDENTIFICATION DIVISION



# Available Functions

Here you will find the information for each resource type

### ETERNUS_ICP

Protocol: ssh
Database Structure:
  system name
  resources_types
  hostname or alias
  metric name
  svctm/r_await/w_await

### TEST ENVIRONMENT

If file eternus_icp exists under the dir tests it will be used instead of real data.

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
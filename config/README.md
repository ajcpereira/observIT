# Configuration Manual

## Systems

The `systems` section contains a list of systems to be configured. Each system has the following properties:

- `name`: The name of the system.
- `resources_types`: The type of resource to be monitored (**linux_os**, **eternus_cs8000**).

## Config

The `config` section contains the configuration parameters for each resource_type in a system. It has the following properties:

### Parameters

- `user`: The username to be used to authenticate on the host we are retrieving metrics from.
- `host_keys`: The location of the host keys if ssh will be used.
- `poll`: The polling interval in minutes.
- `use_sudo`: Whether to use sudo for commands. Can be 'yes' or 'no'.
- `bastion`: The IP address of the bastion host (if used).

### Metrics

A list of metrics to be collected from the system. Each metric has a `name` property.

Available metrics are:
resource_type: linux_os<br>
```yaml
    - name: cpu
    - name: mem
    - name: fs
    - name: net
```

Available metrics are:
resource_type: eternus_cs8000<br>
```yaml
    - name: cpu
    - name: mem
    - name: fs
    - name: fs_io
    - name: drives
    - name: pvgprofile
    - name: medias
    - name: vtldirtycache
    - name: net
    - name: fc

```


### IPs

A list of IP addresses for the system. Each IP has the following properties:

- `ip`: The IP address of the host to observe.
- `alias`: The alias for the IP address (if specified will be presented in the dashboards and graphs).
- `ip_use_sudo`: Whether to use sudo for commands on this IP. Can be 'yes' or 'no'.
- `ip_host_keys`: The location of the host keys for this IP.
- `ip_bastion`: The IP address of the bastion host for this IP.

## Example

Here is an example of a system configuration:

```yaml
systems:
  - name: LAB
    resources_types: linux_os
    config:
      parameters:
          user: fjcollector
          host_keys: keys/id_rsa
          poll: 1
          use_sudo: no
          bastion: 127.0.0.1
      metrics:
          - name: cpu
          - name: mem
          - name: fs
          - name: net
      ips:
          - ip: 127.0.0.1
            alias: linux01
            ip_use_sudo: yes
            ip_host_keys: keys/127.0.0.1_rsa
            ip_bastion: 127.0.0.1
          - ip: 127.0.0.1
            alias: linux02
            ip_use_sudo: yes
            ip_host_keys: keys/127.0.0.1_rsa
            ip_bastion: 127.0.0.1
```
This configuration sets up a system named 'LAB' with the resource type 'linux_os'. It specifies the user, host keys, polling interval, sudo usage, and bastion host. It also specifies the metrics to be collected and the IP addresses for the system. Each IP address has its own alias, sudo usage, host keys, and bastion host.

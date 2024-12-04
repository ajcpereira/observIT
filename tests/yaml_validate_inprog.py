from pydantic import BaseModel, Field, ValidationError, root_validator, constr
from typing import List, Optional, Union, Literal
import yaml

# Define individual configurations for each system
class GlobalParameters(BaseModel):
    repository: str
    repository_port: int
    repository_protocol: Literal['tcp']
    repository_api_key: str
    loglevel: Literal['NOTSET', 'INFO', 'WARNING', 'DEBUG', 'ERROR', 'CRITICAL']
    logfile: str
    auto_fungraph: bool
    grafana_api_key: str
    grafana_server: str

class IPAddress(BaseModel):
    ip: str
    alias: str
    ip_host_keys: Optional[str] = None
    ip_user: Optional[str] = None
    ip_proxy: Optional[str] = None
    ip_protocol: Optional[Literal['http', 'https']] = None
    ip_pwd64: Optional[str] = None
    ip_unsecured: Optional[bool] = None

class Metric(BaseModel):
    name: str

class ConfigParametersLinux(BaseModel):
    user: str
    host_keys: str
    port: Optional[int] = None
    proxy: Optional[str] = None
    poll: int

class ConfigParametersPowerStor(BaseModel):
    protocol: Literal['http', 'https']
    port: Optional[int] = None
    user: str
    pwd64: str
    unsecured: Optional[bool] = None
    proxy: Optional[str] = None
    poll: int

class ConfigParametersRedfish(BaseModel):
    protocol: Literal['http', 'https']
    port: Optional[int] = None
    user: str
    pwd64: str
    unsecured: Optional[bool] = None
    proxy: Optional[str] = None
    poll: int

class SystemConfig(BaseModel):
    parameters: Union[ConfigParametersLinux, ConfigParametersPowerStor, ConfigParametersRedfish]
    metrics: List[Metric]
    ips: List[IPAddress]

class System(BaseModel):
    name: str
    resources_types: str
    config: SystemConfig

class RootModel(BaseModel):
    systems: List[System]
    global_parameters: GlobalParameters

# Example YAML Data
yaml_data = """
systems:
  - name: demo1
    resources_types: linux_os
    config:
      parameters:
        user: fjcollector
        host_keys: keys/id_rsa
        port: 
        proxy: 
        poll: 1
      metrics:
        - name: cpu
        - name: mem
        - name: fs
        - name: net
      ips:
        - ip: 10.8.1.1
          alias: linux1
        - ip: 10.8.1.2
          alias: linux2
  - name: powerstor1
    resources_types: powerstor
    config:
      parameters:
        protocol: http
        port: 
        user: apereira
        pwd64: TBD
        unsecured: True
        proxy: 
        poll: 1
      metrics:
        - name: node
      ips:
        - ip: 10.10.9.9
          alias: powerstor1
  - name: irmc
    resources_types: redfish
    config:
      parameters:
        protocol: https
        port: 
        user: apereira
        pwd64: TBD
        unsecured: False
        proxy: 
        poll: 1
      metrics:
        - name: power
        - name: temp
      ips:
        - ip: 10.10.10.1
          alias: server1
          ip_protocol: http
global_parameters:
  repository: influxdb
  repository_port: 8086
  repository_protocol: tcp
  repository_api_key: TBD
  loglevel: DEBUG
  logfile: logs/fjcollector.log
  auto_fungraph: True
  grafana_api_key: TBD
  grafana_server: grafana
"""

# Parse YAML into Python dict
data = yaml.safe_load(yaml_data)

# Validate
try:
    validated_data = RootModel(**data)
    print("YAML is valid!")
except ValidationError as e:
    print("Validation errors:", e)
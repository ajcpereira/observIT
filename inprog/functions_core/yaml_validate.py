import yaml
from typing import List, Literal, Optional
from pydantic import model_validator, BaseModel, StrictStr, PositiveInt, Field

class AllowedMetrics:
    allowed_metrics = {
        'eternus_icp': [['fs', 'tgt'], ['fs_name', 'tgt_name']],
        'linux_os': [['cpu', 'mem', 'disk', 'fs'], ['cpu_name', 'mem_name', 'disk_name', 'fs_name']],
        'windows_os': [['wcpu', 'wmem', 'wdisk'], ['cpu_name', 'mem_name', 'disk_name']]
    }
    
    @classmethod
    def is_metric_allowed(cls, resource_type, metric_name):
        return metric_name in cls.allowed_metrics.get(resource_type, [])

    @classmethod
    def get_metric_value(cls, resource_type, metric_name):
        metrics_list = cls.allowed_metrics.get(resource_type)
        if metrics_list:
            if metric_name in metrics_list[0]:
                index = metrics_list[0].index(metric_name)
                return metrics_list[1][index]
        return None

class Ip(BaseModel):
    ip: StrictStr
    alias: Optional[StrictStr] = None
    ip_snmp_community: Optional[StrictStr] = None

class Parameters(BaseModel):
    user: StrictStr
    host_keys: StrictStr
    poll: PositiveInt = Field(..., ge=1, le=1440, error_msg='Poll must be between 1 and 1440')

class Metrics(BaseModel):
    name: Literal['fs', 'tgt', 'cpu', 'mem', 'disk', 'wcpu', 'wmem', 'wdisk']

class Config(BaseModel):
    parameters: Parameters
    metrics: List[Metrics]
    ips: List[Ip]
    
    @model_validator(mode="before")
    @classmethod
    def validate_metrics(cls, values):
        resources_types = values.get('parameters', {}).get('resources_types')
        metrics = values.get('metrics', [])
        
        if resources_types and not AllowedMetrics.is_metric_allowed(resources_types, metric.name):
            raise ValueError(f"For {resources_types}, only {', '.join(AllowedMetrics.allowed_metrics[resources_types])} metrics are allowed")
        
        return values

class SystemsName(BaseModel):
    name: StrictStr
    resources_types: Literal['eternus_icp', 'linux_os', 'windows_os']
    config: Config

class GlobalParameters(BaseModel):
    repository: StrictStr
    repository_port: PositiveInt
    repository_protocol: StrictStr
    log: Literal['NOTSET', 'INFO', 'WARN', 'DEBUG', 'ERROR', 'CRITICAL']
    logfile: StrictStr

class ConfigFile(BaseModel):
    systems: List[SystemsName]
    global_parameters: GlobalParameters

def read_yaml(file_path: str) -> ConfigFile:
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    
    return ConfigFile(**config)

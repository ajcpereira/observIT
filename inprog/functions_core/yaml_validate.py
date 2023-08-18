import yaml
from typing import List, Literal, Optional
from pydantic import BaseModel, StrictStr, PositiveInt, Field

class AllowedMetrics:
    allowed_metrics = {
        'eternus_icp': [['fs', 'tgt'], ['fs_name', 'tgt_name']],
        'linux_os': [['cpu', 'mem', 'disk', 'fs'], ['cpu_name', 'mem_name', 'disk_name', 'fs_name']],
        'windows_os': [['wcpu', 'wmem', 'wdisk'], ['cpu_name', 'mem_name', 'disk_name']]
    }

    @classmethod
    def get_func_name(self, resource_type, metric_name):
    
        metrics_list = self.allowed_metrics.get(resource_type)

        if metric_name in metrics_list[0]:
            if metric_name in metrics_list[0]:
                index = metrics_list[0].index(metric_name)
                return metrics_list[1][index]
            else:
                raise ValueError("Selected metric - %s - is not allowed for this resource_type - %s" % (metric_name, resource_type))


    @classmethod
    def get_resource_name(self, resource_type):
    
        metrics_list = self.allowed_metrics.get(resource_type)

#        try:
        if metric_name in metrics_list[0]:
            if metric_name in metrics_list[0]:
                index = metrics_list[0].index(metric_name)
                return metrics_list[1][index]
            else:
                raise ValueError("Selected metric - %s - is not allowed for this resource_type - %s" % (metric_name, resource_type))
#        except:
#            raise ValueError("Metric - %s - does not exist in allowed resource type %s" % (resource_type, self.allowed_metrics.keys()))


class Ip(BaseModel):
    ip: StrictStr
    alias: Optional[StrictStr] = None
    ip_snmp_community: Optional[StrictStr] = None

class Parameters(BaseModel):
    user: StrictStr
    host_keys: StrictStr
    poll: PositiveInt = Field(..., ge=1, le=1440)

class Metrics(BaseModel):
    name: StrictStr #Literal['fs', 'tgt', 'cpu', 'mem', 'disk', 'wcpu', 'wmem', 'wdisk']

class Config(BaseModel):
    parameters: Parameters
    metrics: List[Metrics]
    ips: List[Ip]

class SystemsName(BaseModel):
    name: StrictStr
    resources_types: StrictStr #Literal['eternus_icp', 'linux_os', 'windows_os']
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

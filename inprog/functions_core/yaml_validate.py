#################################################################################
#                                                                               #
#                       ENVIRONMENT DIVISION                                    #
#                                                                               #
#################################################################################
import yaml
from typing import List, Literal, Optional
from pydantic import BaseModel, StrictStr, PositiveInt, Field
from pydantic.networks import IPvAnyAddress

#################################################################################
#                                                                               #
#                       PROCEDURE DIVISION                                      #
#                                                                               #
#################################################################################

########## CLASS VALIDATES MIXING OF RESOURCE TYPES AND METRICS FROM YAML #######
class AllowedMetrics:
    allowed_metrics = {
        'eternus_icp': [['fs', 'tgt'], ['fs_name', 'fs_name']],
        'linux_os': [['cpu', 'mem', 'disk', 'fs'], ['fs_name', 'fs_name', 'fs_name', 'fs_name']],
        'windows_os': [['wcpu', 'wmem', 'wdisk'], ['fs_name', 'fs_name', 'fs_name']]
    }

    @classmethod
    def get_func_name(self, resource_type, metric_name):
    
        metrics_list = self.allowed_metrics.get(resource_type)
        
        try:
            if metric_name in metrics_list[0]:
                index = metrics_list[0].index(metric_name)
        except TypeError:
            print("Selected resource_type - %s - is not allowed, values can be one of the following keys - %s" % (resource_type, self.allowed_metrics.keys()))
            exit()            

        if metric_name in metrics_list[0]:
            index = metrics_list[0].index(metric_name)
            return metrics_list[1][index]
        else:
            print("Selected metric - %s - is not allowed for this resource_type - %s - allowed values are - %s" % (metric_name, resource_type, metrics_list[0]))
            exit()
########## CLASS VALIDATES MIXING OF RESOURCE TYPES AND METRICS FROM YAML #######

########## CLASS FROM PYDANTIC TO VALIDATE YAML SCHEMA ##########################
class Ip(BaseModel):
    ip: IPvAnyAddress
    alias: Optional[StrictStr] = None
    ip_snmp_community: Optional[StrictStr] = None

class Parameters(BaseModel):
    user: StrictStr
    host_keys: Optional[str] = Field(None, max_length=10)
    poll: PositiveInt = Field(..., ge=1, le=1440)

class Metrics(BaseModel):
    name: StrictStr

class Config(BaseModel):
    parameters: Parameters
    metrics: List[Metrics]
    ips: List[Ip]

class SystemsName(BaseModel):
    name: StrictStr
    resources_types: StrictStr
    config: Config

class GlobalParameters(BaseModel):
    repository: StrictStr
    repository_port: PositiveInt
    repository_protocol: StrictStr
    loglevel: Literal['NOTSET', 'INFO', 'WARN', 'DEBUG', 'ERROR', 'CRITICAL']
    logfile: StrictStr

class ConfigFile(BaseModel):
    systems: List[SystemsName]
    global_parameters: GlobalParameters
########## CLASS FROM PYDANTIC TO VALIDATE YAML SCHEMA ##########################

########## FUNCTION VALIDATES YAML AND RETURNS DICT #############################
def create_metric_ip_dicts(config):
    result_dicts = []
    global_parms = config.global_parameters
    for system in config.systems:
        for metric in system.config.metrics:
            for ip in system.config.ips:
                ip_dict = vars(ip)
                result_dict = {
                    "name": system.name,
                    "resources_types": system.resources_types,
                    **system.config.parameters.model_dump(),
                    "metric_name": metric.name,
                    "ip": ip.ip,
                    **ip_dict,
                    "func": AllowedMetrics.get_func_name(system.resources_types, metric.name),
                    **global_parms.model_dump()
                }
                result_dicts.append(result_dict)
                
    return result_dicts, global_parms.model_dump()
########## FUNCTION VALIDATES YAML AND RETURNS DICT #############################

########## FUNCTION READ YAML AND PASS IT TO PYDANTIC CLASS #####################
def read_yaml(file_path: str) -> ConfigFile:
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    
    return ConfigFile(**config)
########## FUNCTION READ YAML AND PASS IT TO PYDANTIC CLASS #####################
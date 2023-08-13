import yaml
from typing import List, Literal, Optional
from pydantic import model_validator, BaseModel, StrictStr, PositiveInt, Field

class Ip(BaseModel):
    ip: StrictStr
    alias: Optional[StrictStr] = None

class Parameters(BaseModel):
    user: StrictStr
    host_keys: StrictStr
    poll: PositiveInt = Field(..., ge=1, le=1440, error_msg='Poll must be between 1 and 1440')

class Metrics(BaseModel):
    name: Literal['fs', 'tgt', 'cpu', 'mem', 'disk']

class Config(BaseModel):
    parameters: Parameters
    metrics: List[Metrics]
    ips: List[Ip]
    
    @model_validator(mode="before")
    @classmethod
    def validate_metrics(cls, values):
        resources_types = values.get('parameters', {}).get('resources_types')
        metrics = values.get('metrics', [])
        
        allowed_metrics = {
            'eternus_icp': [['fs', 'tgt'], ['fs_name1', 'tgt_name']],
            'linux_os': ['cpu', 'mem', 'disk'],
            'windows_os': ['cpu', 'mem', 'disk']
        }
        
        if resources_types in allowed_metrics:
            for metric in metrics:
                if metric.name not in allowed_metrics[resources_types]:
                    raise ValueError(f"For {resources_types}, only {', '.join(allowed_metrics[resources_types])} metrics are allowed")
        
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

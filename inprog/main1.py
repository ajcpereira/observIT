import yaml
from typing import List, Optional
from pydantic import BaseModel, StrictStr
from enum import Enum

class Resources(Enum):
    f_eternus_icp = 'eternus_icp'
    f_linux_os = 'fs'

class Config(BaseModel):
    user: StrictStr

class Systems_Name(BaseModel):
    name: StrictStr
    resources_types: Resources
    config: dict[str, Config]

class Systems(BaseModel):
    systems: List[Systems_Name]

def read_yaml(file_path: str) -> dict:
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    
    return Systems(**config).model_dump()


config = read_yaml('config1.yaml')
print(config)
#print(config['systems'][0]['resources_types'])
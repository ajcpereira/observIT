from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List 

class TestEnums(str, Enum):
    count_number_rows = 'count_number_rows'
    count_columns = 'count_columns'

class Tests(BaseModel):
    test: List[TestEnums] = Field(..., description="Table tests to run")

class Config(BaseModel):
    yaml_config: Dict[str, Tests]

#Config(yaml_config={
#  'table_name': {'test': ['count_columns', 'count_non_null_rows']}
#})

import yaml 

def parse_from_yaml(path_to_yaml):
    with open(path_to_yaml) as f:
        config = yaml.safe_load(f)

    return(config)

## Initialize a Pydantic class from the yaml config
Config(yaml_config=parse_from_yaml(parse_from_yaml('config3.yaml')))

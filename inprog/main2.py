import yaml
from typing import List, Optional
from pydantic import BaseModel, StrictStr


class Team(BaseModel):
    name: Optional[StrictStr] = None


class Sports(BaseModel):
    name: StrictStr
    team: Optional[Team]


class Person(BaseModel):
    name: StrictStr
    age: int
    sex: StrictStr
    sports: List[Sports]


def read_yaml(file_path: str) -> dict:
    with open(file_path, 'r') as stream:
        config = yaml.safe_load(stream)
    
    return Person(**config).model_dump()


config = read_yaml('config2.yaml')
print(config)
from mimesis import Fieldset
from pathlib import Path
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_file_as


class Column(BaseModel):
    """Basic DBT column"""
    name: str
    data_type: str
    data_tests: list[str]

class Table(BaseModel):
    """DBT Table"""
    name: str
    columns: list[Column]

class Schema(BaseModel):
    """DBT schema"""
    models: list[Table]

def gen_test_data():
    model_path = Path("models/schema.yml")
    schema = parse_yaml_file_as(model_type=Schema, file=model_path)

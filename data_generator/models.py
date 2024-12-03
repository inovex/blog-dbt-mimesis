from pydantic import BaseModel
from enum import Enum

class DataType(Enum):
    DATE = "date"
    VARCHAR = "varchar"

class DBTColumn(BaseModel):
    """Basic DBT column"""
    name: str
    data_type: DataType
    data_tests: list[str]

class DBTTable(BaseModel):
    """DBT Table"""
    name: str
    columns: list[DBTColumn]

class DBTSchema(BaseModel):
    """DBT Schema"""
    models: list[DBTTable]


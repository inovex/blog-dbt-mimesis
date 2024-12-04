from pydantic import BaseModel, Field, AliasChoices
from typing import Literal
from enum import Enum

class DataType(Enum):
    DATE = "date"
    VARCHAR = "varchar"
    INTEGER = "integer"



class DBTColumn(BaseModel):
    """Basic DBT column"""
    name: str
    data_type: DataType
    data_tests: list[str] = None
    meta: dict[Literal["primary_key"] | Literal["foreign_key"] | str, bool | str] = {}


class DBTTable(BaseModel):
    """DBT Table"""
    name: str
    columns: list[DBTColumn]


class DBTSchema(BaseModel):
    """DBT Schema"""
    models: list[DBTTable] = Field(validation_alias=AliasChoices("models", "seeds"))

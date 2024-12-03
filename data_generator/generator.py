from pathlib import Path
import datetime
from mimesis import Field, Locale, Schema
from pydantic_yaml import parse_yaml_file_as
import click
import pandas as pd

from models import DBTSchema, DBTTable

DATE_TYPE_MAPPING = {
    "VARCHAR": "text.word",
    "DATE": "datetime.date"
}

FIELD_ALIASES = {
    "OriginCityName": "city",
    "DestCityName": "city"
}

@click.command()
@click.option('--dbt-model-path', help="Path to the dbt model to create dummy data for")
@click.option('--num-rows', default=10, help="Number of rows to be generated")
@click.option('--output-path', help="Path to the directory where the generated .csv files are stored")
def main(dbt_model_path: str, num_rows: 10, output_path: str) -> None:
    model_path = Path(dbt_model_path)
    schema = parse_yaml_file_as(model_type=DBTSchema, file=model_path)
    for table in schema.models:
        df = generate_test_data(table, iterations=num_rows)
        df.to_csv(Path(output_path) / Path(f"{table.name}.csv"))

    

def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date): 
        return obj.isoformat()
    raise TypeError("Type not serializable") 


def generate_test_data(table: DBTTable, iterations: int) -> pd.DataFrame:
    field = Field(Locale.EN)
    schema_definition = lambda: {column.name: field(FIELD_ALIASES.get(column.name, DATE_TYPE_MAPPING[column.data_type.value.upper()])) for column in table.columns}
    schema = Schema(schema=schema_definition, iterations=iterations)
    test_data = schema.create()

    df = pd.DataFrame(test_data)
    
    return df


if __name__ == "__main__":
    main()

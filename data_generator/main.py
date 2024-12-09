from pathlib import Path

import click
from generator import TestDataGenerator
from models import DBTSchema
from pydantic_yaml import parse_yaml_file_as

FIELD_ALIASES = {"OriginCityName": "city", "DestCityName": "city"}


@click.command()
@click.option("--dbt-model-path", help="Path to the dbt model to create dummy data for")
@click.option(
    "--min-rows", default=10, help="Minumum number of rows to be generated for a table"
)
@click.option(
    "--max-rows", default=100, help="Maximum number of rows to be generated for a table"
)
@click.option(
    "--output-path",
    help="Path to the directory where the generated .csv files are stored",
)
def main(dbt_model_path: str, min_rows: int, max_rows: int, output_path: str) -> None:
    model_path = Path(dbt_model_path)
    schema = parse_yaml_file_as(model_type=DBTSchema, file=model_path)
    generator = TestDataGenerator(schema=schema, field_aliases=FIELD_ALIASES)
    generated_data = generator.generate_data(min_rows, max_rows)

    for table_name, test_data in generated_data.items():
        test_data.to_csv(Path(output_path) / Path(f"{table_name}.csv"))


if __name__ == "__main__":
    main()

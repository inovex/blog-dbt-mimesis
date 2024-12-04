from .models import DBTSchema, DBTTable, DBTColumn
from mimesis import Field, Locale, Fieldset
import pandas as pd
import random

# mapping of dbt data types to mimesis providers
DATA_TYPE_MAPPING = {
    "VARCHAR": "text.word",
    "DATE": "datetime.date",
    "INTEGER": "integer_number"
}


class TestDataGenerator:
    def __init__(self, schema: DBTSchema, locale: Locale = Locale.EN, data_type_mapping: dict = DATA_TYPE_MAPPING, field_aliases: dict = {}) -> None:
        self.schema = schema
        self.reproducible_id_store: dict[str, list] = {}
        self.field = Field(locale)
        self.fieldset = Fieldset(locale)
        self.field_aliases = field_aliases
        self.data_type_mapping = data_type_mapping

    def _generate_random_iterations(self, min_rows: int, max_rows: int) -> dict:
        """Generate a random number of iterations for each table within the specified limits

        Parameters
        ----------
        min_rows : int
            Minimum number of rows to be generated for a table
        max_rows : int
            Maximum number of rows to be generated for a table

        Returns
        -------
        dict
            Returns a dictionary with the table names as keys and their corresponding row numbers as values
        """

        return {table.name: random.randint(min_rows, max_rows) for table in self.schema.models}
    
    def _generate_unique_values(self, column: DBTColumn, iterations: int) -> list:
        """Generate a specified number of unique values using Mimesis

        Parameters
        ----------
        field_name : str
            _description_
        iterations : int
            _description_

        Returns
        -------
        list
            _description_
        """

        unique_values = set()
        while len(unique_values) < iterations:
            new_values = self.fieldset(self.field_aliases.get(column.name, self.data_type_mapping[column.data_type.value.upper()]),i=iterations*2)
            unique_values.update(new_values)
        
        return list(unique_values)[:iterations]

    def generate_data(self, min_rows: int = 10, max_rows: int = 100) -> dict[str, pd.DataFrame]:
        """Generate test data for a given schema
        
        Parameters
        ----------
        min_rows : int
            Minimum number of rows to be generated for a table
        max_rows : int
            Maximum number of rows to be generated for a table

        Returns
        -------
        dict[str, pd.DataFrame]
            Returns a dictionary with table names as keys and pandas DataFrames containing generated data as values
        """

        iterations = self._generate_random_iterations(min_rows, max_rows)
        generated_data = {}

        for table in self.schema.models:
            df = self._generate_test_data_for_table(table=table, iterations=iterations[table.name])
            generated_data[table.name] = df
        
        return generated_data

    
    def _generate_test_data_for_table(self, table: DBTTable, iterations: int) -> pd.DataFrame:
        """Generate test data for a given table

        Parameters
        ----------
        table : DBTTable
            pydantic model describing a dbt table
        iterations : int, optional
            Number of rows to be generated, by default 10

        Returns
        -------
        pd.DataFrame
            Returns a pandas DataFrame with the generated data based on the table's schema
        """    

        schema_data = {}

        for column in table.columns:
            primary_key = column.meta.get("primary_key", None)
            foreign_key = column.meta.get("foreign_key", None)

            if foreign_key:
                if foreign_key not in self.reproducible_id_store.keys():
                    self.reproducible_id_store[foreign_key] = self._generate_unique_values(column=column, iterations=iterations)
                schema_data[column.name] = random.choices(self.reproducible_id_store[foreign_key], k=iterations)
                continue
            elif primary_key:
                reproducible_id = f"{table.name}.{column.name}"
                if reproducible_id not in self.reproducible_id_store.keys():
                    self.reproducible_id_store[reproducible_id] = self._generate_unique_values(column=column, iterations=iterations)
                schema_data[column.name] = self.reproducible_id_store[reproducible_id]
                continue
        
            schema_data[column.name] = self.fieldset(self.field_aliases.get(column.name, self.data_type_mapping[column.data_type.value.upper()]), i=iterations)

        df = pd.DataFrame.from_dict(schema_data)
        return df

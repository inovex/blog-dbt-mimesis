import random

import pandas as pd
from mimesis import Fieldset, Locale
from mimesis.keys import maybe
from models import DBTColumn, DBTSchema, DBTTable

# mapping of dbt data types to mimesis providers
DATA_TYPE_MAPPING = {
    "VARCHAR": {"name": "text.word"},
    "DATE": {"name": "datetime.date"},
    "INTEGER": {"name": "integer_number", "start": 0, "end": 1000},
}


class TestDataGenerator:
    def __init__(
        self,
        schema: DBTSchema,
        locale: Locale = Locale.EN,
        data_type_mapping: dict = DATA_TYPE_MAPPING,
        field_aliases: dict = {},
    ) -> None:
        self.schema = schema
        self.reproducible_id_store: dict[str, list] = {}
        self.fieldset = Fieldset(locale)
        self.field_aliases = {
            key: {"name": value} for key, value in field_aliases.items()
        }
        self.data_type_mapping = data_type_mapping
        self.iterations = None

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

        return {
            table.name: random.randint(min_rows, max_rows)
            for table in self.schema.models
        }

    def _generate_unique_values(
        self, table: DBTTable, column: DBTColumn, iterations: int = None
    ) -> list:
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
        iterations = (
            iterations if iterations is not None else self.iterations[table.name]
        )
        unique_values = set()
        consecutive_no_increase = 0

        while len(unique_values) < iterations:
            previous_len = len(unique_values)
            new_values = self.fieldset(
                **self.field_aliases.get(
                    column.name, self.data_type_mapping[column.data_type.value.upper()]
                ),
                i=iterations * 2,
            )
            unique_values.update(new_values)

            # check whether any new values have been added since previous iteration
            if len(unique_values) == previous_len:
                consecutive_no_increase += 1
            else:
                consecutive_no_increase = 0

            if consecutive_no_increase == 3:
                # not enough values available, restarting with lower number of iterations for given table
                print(
                    f"Not enough unique values for {column.name}. Creating maximum number available."
                )
                self.iterations[table.name] = len(unique_values)
                self.generate_data()
                break

        return list(unique_values)[:iterations]

    def generate_data(
        self, min_rows: int = 10, max_rows: int = 100
    ) -> dict[str, pd.DataFrame]:
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
        if self.iterations is None:
            self.iterations = self._generate_random_iterations(min_rows, max_rows)

        generated_data = {}

        for table in self.schema.models:
            df = self._generate_test_data_for_table(table=table)
            generated_data[table.name] = df

        return generated_data

    def _generate_test_data_for_table(self, table: DBTTable) -> pd.DataFrame:
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
            # check if column has primary/foreign key constraints
            primary_key = column.meta.get("primary_key", None)
            foreign_key = column.meta.get("foreign_key", None)

            # generate data according to column type
            if foreign_key:
                schema_data[column.name] = self._handle_foreign_key(
                    foreign_key, column, table
                )
                continue

            elif primary_key:
                schema_data[column.name] = self._handle_primary_key(table, column)
                continue

            schema_data[column.name] = self._handle_regular_column(table, column)

        df = pd.DataFrame.from_dict(schema_data)
        return df

    def _handle_foreign_key(
        self, foreign_key: str, column: DBTColumn, table: DBTTable
    ) -> list:
        """Method to generate foreign key data


        Parameters
        ----------
        foreign_key : str
            Name of the foreign key in the format 'referenced_table.key_column'
        column : DBTColumn
            DBTColumn object
        table : DBTTable
            DBTTable object

        Returns
        -------
        list
            Returns a list of values for
        """

        if foreign_key not in self.reproducible_id_store.keys():
            # store generated data in reproducible_id_store
            self.reproducible_id_store[foreign_key] = self._generate_unique_values(
                table=table,
                column=column,
                iterations=self.iterations[foreign_key.split(".")[0]],
            )

        return random.choices(
            self.reproducible_id_store[foreign_key], k=self.iterations[table.name]
        )

    def _handle_primary_key(self, table: DBTTable, column: DBTColumn) -> list:
        """Method to generate data for primary keys

        Parameters
        ----------
        table : DBTTable
            DBTTable object
        column : DBTColumn
            DBTColumn object

        Returns
        -------
        list
            Returns a list of unique values
        """
        reproducible_id = f"{table.name}.{column.name}"
        if reproducible_id not in self.reproducible_id_store.keys():
            # store generated data in reproducible_id_store
            self.reproducible_id_store[reproducible_id] = self._generate_unique_values(
                table, column
            )

        return self.reproducible_id_store[reproducible_id]

    def _handle_regular_column(self, table: DBTTable, column: DBTColumn) -> list:
        """Method to generate data for regular columns, i.e., not primary/foreign key colums,
           and takes into account constraints wrt. nullability and uniqueness

        Parameters
        ----------
        table : DBTTable
            DBTTable object
        column : DBTColumn
            DBTColumn object

        Returns
        -------
        list
            Returns a list of generated values
        """
        if "unique" in column.data_tests:
            return self._generate_unique_values(table=table, column=column)
        else:
            probability_of_nones = 0 if "not_null" in column.data_tests else 0.1
            return self.fieldset(
                **self.field_aliases.get(
                    column.name,
                    self.data_type_mapping[column.data_type.value.upper()],
                ),
                i=self.iterations[table.name],
                key=maybe(None, probability=probability_of_nones),
            )

# dbt-mimesis

## Overview
This repository provides a framework for testing **dbt data pipelines** using:

- **[Mimesis](https://mimesis.name/master/)**: A Python library for generating realistic fake data.
- **[Pydantic](https://docs.pydantic.dev/latest/)**: For parsing and validating `schema.yml` files.
- **[dbt (data build tool)](https://www.getdbt.com/)**: To manage transformations and run tests agains data pipelines.

The goal is to enable robust pipeline testing with realistic, schema-complinat fake data - without relying on sensitive production datasets.

## Features

- **Test Data Generation:** Automatically generate fake data based on dbt schemas (e.g., including constraints such as primary keys, foreign keys, nullability, uniqueness).
- **Referential Integrity**: Ensure primary/foreign key relationships are respected in generated fake datasets.
- **CI/CD Integration**: Includes a GitHub Actions pipeline to automate test data generation and dbt commands.

## Prerequisites
- Python 3.10
- Poetry
- Docker (optional, for the development container)

## Quick Start
### 1. Clone the Repository
```bash
git clone https://github.com/inovex/dbt-mimesis
cd dbt-mimesis
```

### 2. Set Up Your Environment

#### Option 1: Use the Development Container (Recommended)
The repository includes a Development Container specification for quick setup.

#### Option 2: Manual Setup
Install the required dependencies:
```bash
# Install Python dependencies
poetry install

# Install dbt dependencies
cd dbt_mimesis_example
poetry run dbt deps
```

As this project uses duckdb, you also must install DuckDB CLI on your machine. You can follow [this guide](https://duckdb.org/docs/installation/) to install it. Then, run the following command to create a database file inside the `dbt_mimesis_example` directory:
```bash
duckdb dev.duckdb "SELECT 'Database created successfully';"

# navigate back to the root of the repository
cd ../
```

### 3. Generate Test Data
You can use the following command to generate some test data based on `dbt_mimesis_example/seeds/schema.yml`:
```bash
poetry run python data_generator/main.py \
    --dbt-model-path dbt_mimesis_example/seeds/schema.yml \
    --output-path dbt_mimesis_example/seeds/ \
    --min-rows <MIN_NUM_OF_ROWS> \
    --max-rows <MAX_NUM_OF_ROWS>
```

Using the `--min-rows` and `--max-rows` flags, you can specify the minimum/maximum amount of rows to be created for each table. Each table's row count will be a random number within the specified range.

### 4. Run dbt pipeline
You can now load the generated seed data to the duckdb database, execute downstream dbt models and perform dbt tests:

```bash
cd dbt_mimesis_example
# load seeds into duckdb
poetry run dbt seed

# run dbt models
poetry run dbt run

# perform dbt data tests
poetry run dbt test
```

## Repository Structure
```
.
├── data_generator              # Python code to generate data
│   ├── generator.py            # implements the TestDataGenerator class
│   ├── __init__.py
│   ├── main.py                 # implements the main method to generate data for a dbt schema
│   ├── models.py               # Pydantic models to validate dbt schemas
├── dbt_mimesis_example
│   ├── dbt_project.yml         # dbt project definition
│   ├── dependencies.yml        # dbt dependencies
│   ├── macros                  # dbt macros
│   ├── models                  # dbt models
│   │   ├── airplanes.sql       # model for the airplanes table
│   │   ├── cities.sql          # model for the cities table
│   │   ├── flights.sql         # model for the flights table
│   │   └── schema.yml          # schema definition for the dbt models
│   ├── profiles.yml            # dbt profile
│   ├── README.md
│   ├── seeds
│   │   └── schema.yml          # dbt Seeds schema definition
│   ├── snapshots               # dbt snapshots
│   └── tests                   # dbt tests
├── poetry.lock
├── pyproject.toml
└── README.md
```
## CI/CD Integration
This repository includes a GitHub Actions pipeline that:
1. Generates test data automatically.
2. Runs all `dbt` commands (e.g., `seed`, `run`, `test`) upon pull request or push to the `main` branch.
3. Fails if any of the `dbt` commands exits with a non zero exit code.

## Resources
For more details, check out:
- [Mimesis Documentation](https://mimesis.name/master/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [dbt Documentation](https://docs.getdbt.com/docs/build/documentation)

Happy testing! 🎉

with raw as (SELECT *
FROM read_csv('../flights.csv',
    delim = '|',
    header = true,
    columns = {
        'FlightDate': 'DATE',
        'UniqueCarrier': 'VARCHAR',
        'OriginCityName': 'VARCHAR',
        'DestCityName': 'VARCHAR'
    })),
origin_city as (SELECT DISTINCT OriginCityName FROM raw)
SELECT * FROM origin_city
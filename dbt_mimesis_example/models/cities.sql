WITH cities AS (
    SELECT DISTINCT OriginCityName AS CityName FROM {{ ref('raw_flights') }}
    UNION (SELECT DISTINCT DestCityName AS CityName FROM {{ ref('raw_flights') }})
)

SELECT DISTINCT
    CAST(ROW_NUMBER() OVER (ORDER BY CityName) AS INTEGER) AS Id
    , CityName
FROM cities

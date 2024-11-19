with raw as (SELECT * from {{ ref('raw_flights') }}),
origin_city as (SELECT DISTINCT OriginCityName FROM raw)
SELECT * FROM origin_city
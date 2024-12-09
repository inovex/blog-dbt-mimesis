SELECT DISTINCT
    CAST(ROW_NUMBER() OVER (ORDER BY AirplaneModel) AS INTEGER) AS Id
    , AirplaneModel
    , NumSeats
FROM {{ ref('raw_airplanes') }}

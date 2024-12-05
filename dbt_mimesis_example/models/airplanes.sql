SELECT DISTINCT
    ROW_NUMBER() OVER (ORDER BY AirplaneModel) AS Id
    , AirplaneModel
    , NumSeats
FROM {{ ref('raw_airplanes') }}

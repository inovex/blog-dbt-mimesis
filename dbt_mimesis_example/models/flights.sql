SELECT 
    f.FlightDate
    , f.CarrierName
    , a.Id AS AirplaneModelId
    , oc.Id AS OriginCityId
    , dc.Id AS DestCityId
FROM {{ ref('raw_flights') }} AS f
INNER JOIN {{ ref('cities') }} AS oc ON f.OriginCityName = oc.CityName
INNER JOIN {{ ref('cities') }} AS dc ON f.DestCityName = dc.CityName
INNER JOIN {{ ref('airplanes') }} AS a ON f.AirplaneModel = a.AirplaneModel
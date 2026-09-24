Goals:
- Fetch and cache the raw Open-Meteo JSON response.
- Consider daily weather records for the year 2022.
- Print different reports based on an `--action` argument.
- Support `--verbose` logging and basic resilience: timeout and retry.

Api documentation: https://open-meteo.com/en/docs/historical-weather-api

TODO list:
- [x] Create function to send query and just always save data to file without caching
- [x] Implement "report" function
- [x] Implement "rainfall" function
- [x] Implement "weather-codes"
- [x] Add caching
- [] Configure robustness for sending query
- [] Add robustness to data parsing
- [x] Add 'verbose' parameter and handle it
- [x] Add parameter parsing
- []
- []
- []

Tests - basic scenarios:
- [] successful fetch and cache write
- [] cache reuse
- [] --refresh
- [] timeout then successful retry
- [] non-200 response
- [] invalid cached JSON
- [] missing or mismatched daily arrays
- [] all three reports

Tests - regression:
- []
- []
- []
- []

Additional notes:
- exercise did only mention returning "weather codes". There is code to condition mapping available in API documentation as "Weather code descriptions as JSON", so "weather-codes" can be potentially exapanded to use it. Only 8 days of "clear sky", sounds like London :)
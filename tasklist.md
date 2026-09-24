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
- [x] Configure robustness for sending query
- [x] Add robustness to data parsing
- [x] Add 'verbose' parameter and handle it
- [x] Add parameter parsing
- []
- []
- []

Tests - basic scenarios:
- [x] successful fetch and cache write
- [x] cache reuse
- [x] --refresh
- [x] timeout then successful retry
- [x] non-200 response
- [x] invalid cached JSON
- [x] missing or mismatched daily arrays
- [x] all three reports

Tests - regression:
- []
- []
- []
- []

Additional notes:
- exercise did only mention returning "weather codes". There is code to condition mapping available in API documentation as "Weather code descriptions as JSON", so "weather-codes" can be potentially exapanded to use it, for description and validation. Only 8 days of "clear sky", sounds like London :)
- a lot of boilerplate in UTs, worth considering some subtests instead
- reasonable exceptions/scenarios to test - wrong cache filepath, like pointing to directory or file with missing permissions
- there is weird flow with cache handling:
    if file not exists -> request from API -> save to file
    always -> read from cache
 so as a side effect we read from file data we already have... may need to simplify if I have time
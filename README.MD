weather.py is a command-line tool that fetches historical daily weather for London from the public Open-Meteo Archive API and produces useful summaries.

You can read more about the API source at [open-meteo](https://open-meteo.com/en/docs/historical-weather-api) website

API query is not parameterized and downloads the data with specified parameters:

```text
latitude=51.5072
longitude=-0.1276
start_date=2022-01-01
end_date=2022-12-31
daily=temperature_2m_max,precipitation_sum,weather_code
timezone=UTC
```

Required modules:
`requests`

To print available modes and parameters:
`./weather.py --help`

Available modes under `--action` parameter:
- report
- rainfall
- weather-codes

Data downloaded from API is cached in "weather.json" file, unless other file is selected using the `--cache` parameter.

You can force refresh of cache using `--refresh` parameter

By default script only logs errors. You can enable debug logging by using `-v` or `--verbose` flag

Execute tests by running:
`python3 -m unittest`
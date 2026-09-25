#! /bin/env python3

"""
    weather.py fetches historical data about London weather from Open-Meteo Archive API
"""

import json
import argparse
import pathlib
import logging
import sys
import itertools
from datetime import datetime
from collections import defaultdict
import requests
from requests.exceptions import HTTPError,Timeout, RequestException

API_URL = "https://archive-api.open-meteo.com/v1/archive"
CACHE_FILE_PATH = pathlib.Path("weather.json")
QUERY = {
    "latitude" : "51.5072",
    "longitude" : "-0.1276",
    "start_date" : "2022-01-01",
    "end_date" : "2022-12-31",
    "daily" : "temperature_2m_max,precipitation_sum,weather_code",
    "timezone" : "UTC"}

DATEFORMAT = "%Y-%m-%d"
ACTIONS = ["report","rainfall","weather-codes"]

def parse_arguments():
    "Parse command line arguments"
    parser = argparse.ArgumentParser(
        prog='weather',
        description='weather.py fetches historical data about London weather from Open-Meteo Archive API')
    parser.add_argument('--action', choices = ACTIONS, required=True,
                        help="Action to be performed by script")
    parser.add_argument('--cache', default=CACHE_FILE_PATH, type=pathlib.Path,
                        help="Cache file for download of weather data from API")
    parser.add_argument('--refresh', action='store_true',
                        help="Ignore current cache contents and replace with data from API")
    parser.add_argument('--verbose', '-v', action='store_true',
                            help="Enable verbose logging")
    return parser.parse_args()

def get_api_data(path: pathlib.Path):
    """
    Get API data and cache it to file
    Raises exception if request or JSON parsing fails
    Retries once if request times out
    """
    # we are only retrying once on request
    # if more retry logic is needed we would need to introduce sessions, httpadapters and retries
    for retry in range(2):
        try:
            response = requests.get(API_URL, params=QUERY, timeout=15)
            break
        except Timeout:
            # more natural to see "1 try" that "0 retry"
            logging.debug("HTTP request timed out on %s try", retry+1)
            if retry == 1:
                raise
    if response.status_code != 200:
        raise HTTPError(f"API request return non-200 status code: {response.status_code}, {response.reason}")

    with open(path, 'w', encoding="utf-8") as cache_file:
        json_string = json.dumps(response.json(), indent=4)
        cache_file.write(json_string)

def get_data_from_cache(path):
    """
    Get API data from cache
    If cache contains invalid json raise exception
    """
    with open(path, 'r', encoding="utf-8") as cache_file:
        json_dictionary = json.load(cache_file)
    # preliminary check for lack of 'daily' data that will make parsing impossible
    if "daily" not in json_dictionary:
        raise ValueError("Cached file missing weather data")
    return json_dictionary

def check_required_keys(dictionary, keys):
    """
        Raises ValueError on missing keys
    """
    for key in keys:
        if key not in dictionary:
            raise ValueError(f"{key} entry missing in weather data")

def valid_date(date, date_format):
    """
        Validates (True/False) date string according to provided format
    """
    if date is None:
        return False
    try:
        datetime.strptime(date, date_format)
    except ValueError:
        logging.debug("Failed to parse date: %s", date)
        return False
    return True

def report_to_string(report_dict):
    """
    Return the weather summary based on report data:
    total days | dry days | rainy days | rainy-day ratio as a percentage;
    """
    return f"Total: {report_dict["total"]} | Dry: {report_dict["dry"]} | Rainy: {report_dict["rainy"]} | Rainy-day ratio: {report_dict["ratio"]:.0%}"

def create_report(data):
    """
    Return the dictionary with data used in weather report action:

    The denominator must exclude days whose precipitation value is missing or invalid.

    Return the dictionary with 

    Raises ValueError if either time or precipation_sum keys is missing

    """
    daily_data = data["daily"]
    check_required_keys(daily_data,("time","precipitation_sum"))
    # map the two lists into dictionary
    report = {"total" : 0, "dry" : 0, "rainy" : 0, "ratio" : 0.0}
    mapping = itertools.zip_longest(daily_data["time"],daily_data["precipitation_sum"])
    #only report data that has valid data and valid precipitation data
    processed_records = 0
    for date, precipitation in mapping:
        processed_records += 1
        if not valid_date(date, DATEFORMAT) or precipitation is None:
            continue
        try:
            precipitation_value = float(precipitation)
            if precipitation_value == 0:
                report["dry"] += 1
            elif precipitation_value > 0:
                report["rainy"] += 1
            else:
                logging.debug("Invalid precipitation value: %s", precipitation)
                continue
            report["total"] += 1

        except ValueError:
            logging.debug("Failed to parse precipitation: %s", precipitation)
            continue
    if report["total"] != 0:
        report["ratio"] = report["rainy"] / report["total"]

    logging.debug("create_report finished, processed records: %s", processed_records)
    return report

def rainfall_to_string(rainfall):
    """
    Return the rainfall report based on number:
    Average rainfall per day: X.XX mm
    """
    return f"Average rainfall per day: {rainfall:.2}"

def create_rainfall_data(data):
    """
    Return average precipitation per valid day. Treat missing precipitation values as 0.

    """
    daily_data = data["daily"]
    check_required_keys(daily_data,("time","precipitation_sum"))
    mapping = itertools.zip_longest(daily_data["time"],daily_data["precipitation_sum"])
    # slightly different behaviour - we are to treat missing percipation as 0
    # no note about invalid values, so I'll treat them as 0 too
    total_valid_days = 0
    rainfall_sum = 0
    processed_records = 0
    for date, precipitation in mapping:
        processed_records += 1
        if not valid_date(date, DATEFORMAT):
            continue
        try:
            precipitation_value = float(precipitation)
        except (TypeError, ValueError):
            logging.debug("Failed to parse precipitation: %s, treating as 0", precipitation)
            precipitation_value = 0
        # while not strictly defined, negative rainfall should not be possible
        if precipitation_value < 0:
            logging.debug("Negative precipitation: %s, treating as 0", precipitation)
            precipitation_value = 0
        rainfall_sum += precipitation_value
        total_valid_days += 1

    logging.debug("create_rainfall_data finished, processed records: %s", processed_records)
    if total_valid_days == 0:
        return 0.0
    return rainfall_sum/total_valid_days

def weather_codes_to_string(weather_dict):
    """
    Return the weather codes report based on dictionary:
    Sort descending by count.
    Use unknown if a weather code is missing.
    For equal counts, sort codes alphabetically.
    """
    # sort primarily by values descending, then by ascending (alphabetical) keys
    sorted_values = sorted(weather_dict.items(), key = lambda item: (-item[1], item[0]))
    codes_output = ""
    for key,value in sorted_values:
        codes_output += f"{key} - {value}\n"
    return codes_output

def create_weather_codes_data(data):
    """
    Return dictionary of weather codes

    """
    daily_data = data["daily"]
    check_required_keys(daily_data,("time","weather_code"))
    mapping = itertools.zip_longest(daily_data["time"],daily_data["weather_code"])
    weather_codes = defaultdict(int)
    processed_records = 0
    for date, weather_code in mapping:
        processed_records += 1
        if not valid_date(date, DATEFORMAT):
            continue
        if weather_code is None:
            weather_code = "unknown"
        weather_codes[weather_code] += 1
    logging.debug("create_weather_codes_data finished, processed records: %s", processed_records)
    return dict(weather_codes)

def handle_cache(cache_file, refresh):
    """
        Handles cache processing
        If JSON file exists it's data will be reused, 
        otherwise new data will be retrieved from API and saved to cache
        Refresh overrides this behaviour and forces replacing cache_file with new data
        Does not handle exceptions and pass them to upstream
    """
    # get fresh data only if asked for or cache file does not exist
    if refresh or not cache_file.exists():
        logging.debug("Refresh requested or cache file does not exist, requesting fresh data and saving to cache")
        get_api_data(cache_file)
    else:
        logging.debug("Cache file found and refresh not requested, reusing data from cache")
    logging.debug("Cache file path used: %s", cache_file.resolve())
    cached_data = get_data_from_cache(cache_file)
    return cached_data

def main():
    """
        General application flow:
        1. Parse parameters and configure logger
        2. If refresh is requested or cache data does not exist request is from Weather API and save to cache file
        3. Retrieve data from cache file
        4. Based on user input - parse and present data in one of three modes:
            - report - present a summary of dry and rainy days with ratio
            - rainfall - show an average daily precipitation
            - weather-codes - present sorted daily records by Open-Meteo weather_code
        Function handles gracefully possible JSON/HTTP exceptions, as well as issues in data validation

    """
    args = parse_arguments()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")
    try :
        cached_data = handle_cache(args.cache, args.refresh)
    except json.JSONDecodeError as jde:
        logging.error("Cannot parse JSON file in cache.")
        logging.debug(jde)
        sys.exit(1)
    except ValueError as val_exc:
        logging.error("Failed to get weather data from JSON file.")
        logging.debug(val_exc)
        sys.exit(1)
    except HTTPError as httperror:
        logging.error("API request returned non-200 return code.")
        logging.debug(httperror)
        sys.exit(1)
    except Timeout as timeout:
        logging.error("API request timed out.")
        logging.debug(timeout)
        sys.exit(1)
    # catch-all exception provided by requests library
    except RequestException as req_exc:
        logging.error("API request failed.")
        logging.debug(req_exc)
        sys.exit(1)
    # handle cases like Permission Denied
    # last because it is ancestor of RequestException
    except OSError as os_err:
        logging.error("Cannot open cache file.")
        logging.debug(os_err)
        sys.exit(1)

    # print results depending on mode
    try:
        logging.debug("Data retrieved successfully, proceeding with action: %s", args.action)
        match args.action:
            case "report":
                result = create_report(cached_data)
                print(report_to_string(result))
            case "rainfall":
                result = create_rainfall_data(cached_data)
                print(rainfall_to_string(result))
            case "weather_codes":
                result = create_weather_codes_data(cached_data)
                print(weather_codes_to_string(result))
    except ValueError as ve:
        logging.error("Data validation failed.")
        logging.debug(ve)
        sys.exit(2)

if __name__ == '__main__':
    main()

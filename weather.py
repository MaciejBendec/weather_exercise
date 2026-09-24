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
from collections import defaultdict #TODO Counter may also be a good idea 
import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive"
CACHE_FILE_PATH = pathlib.Path("weather.json")
QUERY = {
    "latitude" : "51.5072",
    "longitude" : "-0.1276",
    "start_date" : "2022-01-01",
    "end_date" : "2022-12-31", #TODO change to 2022-12-31, smaller now for testing run
    "daily" : "temperature_2m_max,precipitation_sum,weather_code",
    "timezone" : "UTC"}

DATEFORMAT = "%Y-%m-%d"
ACTIONS = ["report","rainfall","weather_codes"]

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
    """
    data = requests.get(API_URL, params=QUERY)
    with open(path, 'w', encoding="utf-8") as cache_file:
        #TODO pretty print for now, can be removed if it's only cache
        json_string = json.dumps(data.json(), indent=4)
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

def report_to_string(report_dict):
    """
    Return the weather summary based on report data:
    total days | dry days | rainy days | rainy-day ratio as a percentage;
    """
    return f"Total: {report_dict["total"]} | Dry: {report_dict["dry"]} | Rainy: {report_dict["rainy"]} | Rainy-day ratio: {report_dict["ratio"]:.0%}"

#TODO extract validation into separate function as we are approaching high function complexity (radon b/c)
def create_report(data):
    """
    Return the dictionary with data used in weather report action:

    The denominator must exclude days whose precipitation value is missing or invalid.

    Return the dictionary with 

    Raises ValueError if either time or precipation_sum keys is missing

    """
    report = {"total" : 0, "dry" : 0, "rainy" : 0, "ratio" : 0.0}
    # map the two lists into dictionary
    daily_data = data["daily"]
    if "time" not in daily_data:
        raise ValueError("Missing time records in weather data")
    if "precipitation_sum" not in daily_data:
        raise ValueError("Missing precipation records in weather data")
    mapping = itertools.zip_longest(daily_data["time"],daily_data["precipitation_sum"])
    #only report data that has valid data and valid precipitation data
    for date, precipitation in mapping:
        if date is None or precipitation is None:
            continue
        try:
            datetime.strptime(date, DATEFORMAT)
        except ValueError:
            logging.debug("Failed to parse date: %s", date)
            continue
        try:
            precipitation_value = float(precipitation)
            if precipitation_value == 0:
                report["dry"] += 1
            elif precipitation_value > 0:
                report["rainy"] += 1
            else:
                logging.debug("Invalid precipation value: %s", precipitation)
                continue
            report["total"] += 1

        except ValueError:
            logging.debug("Failed to parse precipitation: %s", precipitation)
            continue
    if report["total"] != 0:
        report["ratio"] = report["rainy"] / report["total"]
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
    if "time" not in daily_data:
        raise ValueError("Missing time records in weather data")
    if "precipitation_sum" not in daily_data:
        raise ValueError("Missing precipation records in weather data")
    mapping = itertools.zip_longest(daily_data["time"],daily_data["precipitation_sum"])
    # slightly different behaviour - we are to treat missing percipation as 0
    # no note about invalid values, so I'll treat them as 0 too
    total_valid_days = 0
    rainfall_sum = 0
    for date, precipitation in mapping:
        if date is None:
            continue
        try:
            datetime.strptime(date, DATEFORMAT)
        except ValueError:
            logging.debug("Failed to parse date: %s", date)
            continue
        try:
            precipitation_value = float(precipitation)
        except (TypeError, ValueError):
            logging.debug("Failed to parse precipitation: %s, treating as 0", precipitation)
            precipitation_value = 0
        rainfall_sum += precipitation_value
        total_valid_days += 1
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
    if "time" not in daily_data:
        raise ValueError("Missing time records in weather data")
    if "weather_code" not in daily_data:
        raise ValueError("Missing weather code records in weather data")
    mapping = itertools.zip_longest(daily_data["time"],daily_data["weather_code"])
    weather_codes = defaultdict(int)
    for date, weather_code in mapping:
        if date is None:
            continue
        try:
            datetime.strptime(date, DATEFORMAT)
        except ValueError:
            logging.debug("Failed to parse date: %s", date)
            continue
        if weather_code is None:
            weather_code = "unknown"
        weather_codes[weather_code] += 1
    return dict(weather_codes)


if __name__ == '__main__':
    args = parse_arguments()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")
    # get fresh data only if asked for or cache file does not exist
    cache_file = args.cache
    if args.refresh or not cache_file.exists():
        get_api_data(cache_file)
    try :
        cached_data = get_data_from_cache(cache_file)
    except json.JSONDecodeError:
        logging.error("Cannot parse JSON file in cache")
        sys.exit(1)
    except ValueError:
        logging.error("Failed to get weather data from JSON file")
        sys.exit(1)

    # print results depending on mode
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

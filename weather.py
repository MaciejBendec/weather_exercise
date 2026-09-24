#! /bin/env python3

"""
    weather.py fetches historical data about London weather from Open-Meteo Archive API
"""

import json
import argparse
import pathlib
import logging
import requests
import sys
import itertools
from datetime import datetime

API_URL = "https://archive-api.open-meteo.com/v1/archive"
CACHE_FILE_PATH = pathlib.Path("weather.json") #TODO this will be relative to workdir, not filedir
QUERY = {
    "latitude" : "51.5072",
    "longitude" : "-0.1276",
    "start_date" : "2022-01-01",
    "end_date" : "2022-01-07", #TODO change to 2022-12-31, smaller now for testing run
    "daily" : "temperature_2m_max,precipitation_sum,weather_code",
    "timezone" : "UTC"}

DATEFORMAT = "%Y-%m-%d"

def parse_arguments():
    pass

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
    return f"Total: {report_dict["total"]} | Dry: {report_dict["dry"]} | Rainy: {report_dict["rainy"]} | Rainy-day ratio: {report_dict["ratio"]:.2%}"

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
                logging.debug("Invalid preripation value: %s", precipitation)
                continue
            report["total"] += 1

        except ValueError:
            logging.debug("Failed to parse precipitation: %s", precipitation)
            continue
    if report["total"] != 0:
        report["ratio"] = report["rainy"] / report["total"]
    return report



#parse_arguments()
#if refresh mode or cache file does not exist:
#TODO base it on parameter from argparse
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s") 
    get_api_data(CACHE_FILE_PATH)
    try :
        cached_data = get_data_from_cache(CACHE_FILE_PATH)
    except json.JSONDecodeError:
        logging.error("Cannot parse JSON file in cache")
        sys.exit(1)
    except ValueError:
        logging.error("Failed to get weather data from JSON file")
        sys.exit(1)

    #depending on mode
    result = create_report(cached_data)
    print(report_to_string(result))

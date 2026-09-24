#! /bin/env python3

"""
    weather.py fetches historical data about London weather from Open-Meteo Archive API
"""

import json
import argparse
import pathlib

import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive"
CACHE_FILE_PATH = pathlib.Path("weather.json") #TODO this will be relative to workdir, not filedir
QUERY = {
    "latitude" : "51.5072",
    "longitude" : "-0.1276",
    "start_date" : "2022-01-01",
    "end_date" : "2022-01-07", #TODO change to 2022-12-31, smaller now for testing run
    "daily" : "temperature_2m_max,precipitation_sum,weather_code",
    "timezone" : "UTC"}

def get_api_data(path: pathlib.Path):
    """
        Get API data and cache it to file
    """
    data = requests.get(API_URL, params=QUERY)
    with open(path, 'w') as cache_file:
        #TODO pretty print for now, can be removed if it's only cache
        json_string = json.dumps(data.json(), indent=4)
        cache_file.write(json_string)

get_api_data(CACHE_FILE_PATH)

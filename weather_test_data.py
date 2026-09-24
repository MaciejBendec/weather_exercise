"""
    Test data to use with weather CLI tool tests
"""
# best case scenario, matching sizes, correct data, 1 rainy and 1 dry day
sunny_day_scenario = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}

# missing data scenarions
# they are symmetrical, more precipipations = less days
missing_days = {
    "daily": {
        "time": ["2022-01-01"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}

missing_precipitations = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [1.4],
        "weather_code": [3, 61]
    }
}

missing_codes = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [61]
    }
}

# missing whole arrays, processing should not start if any are needed

missing_time_array = {
    "daily": {
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}

missing_precipitation_array = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "weather_code": [3, 61]
    }
}

missing_codes_array = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
    }
}

# this should be caught by get_data_from_cache isntead of action functions
missing_daily_dict = {
    "timezone": "GMT"
}
# we can also add "missing temperature" scenario but currently no function use it 
# so it would be same as "sunny day scenario"

# invalid data scenarios

invalid_dateformat  = {
    "daily": {
        "time": ["2022-01-01", "22-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}

invalid_precipitation = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, "storm"],
        "weather_code": [3, 61]
    }
}

negative_precipitation = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, -1.4],
        "weather_code": [3, 61]
    }
}

divide_by_zero_precipitation = {
    "daily": {
        "time": [],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, -1.4],
        "weather_code": [3, 61]
    }
}

# we don't really have any definition of "invalid" code, only missing
# we could use exhaustive list from the API for validation if we want to 
# improve but for now let's assume that all possible keys are correct
#invalid_weather_code = 

correct_response = """
{
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}
"""
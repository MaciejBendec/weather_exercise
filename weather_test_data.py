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
# they are symmetrical, more precipacions = less days
missing_days = {
    "daily": {
        "time": ["2022-01-01"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}

missing_precipations = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0],
        "weather_code": [3, 61]
    }
}

missing_codes = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3]
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

missing_precipation = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}

missing_time_array = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}

missing_daily_dict = {
    "daily": {
        "time": ["2022-01-01", "2022-01-02"],
        "temperature_2m_max": [12.3, 11.8],
        "precipitation_sum": [0.0, 1.4],
        "weather_code": [3, 61]
    }
}
# we can also add "missing temperature" scenario but currently no function use it 
# so it would be same as "sunny day scenario"
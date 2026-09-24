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
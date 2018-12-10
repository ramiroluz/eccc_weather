from urllib import request
from urllib import parse
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.types import NVARCHAR

from db import engine
from stations import get_stations_df_from_ftp
from stations import get_stations_df_from_db
from utils import new_name


# https://github.com/csianglim/weather-gc-ca-python/blob/master/Part%20I%20-%20Data%20Extraction%20and%20Cleaning.ipynb
def get_data(stationID, year, month, timeframe, skiprows):
    base_url = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?"
    query_params = dict(
        format='csv',
        stationID=stationID,
        Year=year,
        Month=month,
        timeframe=timeframe
    )

    query_url = parse.urlencode(query_params)
    api_endpoint = base_url + query_url

    # Download the original. It is not required, but it may be good to have the
    # original file. After we get more confident the read_csv can be used with
    # the api_endpoint instead of the file name.
    filename = 'csv/{}{}{}.csv'.format(stationID, year, month)
    request.urlretrieve(api_endpoint, filename)

    return pd.read_csv(filename, skiprows=skiprows)


def get_hourly_data(stationID, year, month):
    HOURLY = 1
    return get_data(stationID, year, month, HOURLY, 15)


def get_daily_data(stationID, year, month):
    DAILY = 2
    df = get_data(stationID, year, month, DAILY, 25)
    return df


def get_monthly_data(stationID, year, month):
    MONTHLY = 3
    return get_data(stationID, year, month, MONTHLY)


def main():
    flags = {
        "max_temp_flag": NVARCHAR(1),
        "min_temp_flag": NVARCHAR(1),
        "mean_temp_flag": NVARCHAR(1),
        "heat_deg_days_flag": NVARCHAR(1),
        "cool_deg_days_flag": NVARCHAR(1),
        "total_rain_flag": NVARCHAR(1),
        "total_snow_flag": NVARCHAR(1),
        "total_precip_flag": NVARCHAR(1),
        "snow_on_grnd_flag": NVARCHAR(1),
        "dir_of_max_gust_flag": NVARCHAR(1),
        "spd_of_max_gust_km_h": NVARCHAR(5),
        "spd_of_max_gust_flag": NVARCHAR(1),
    }

    # stations_df = get_stations_df_from_ftp()
    stations_df = get_stations_df_from_db()

    COL_INDEX = 0
    COL_STATION_ID = 1
    COL_FIRST_YEAR = 2
    COL_LAST_YEAR = 3

    stations_df.rename(
        columns={old: new_name(old) for old in stations_df.columns},
        inplace=True
    )

    updated = datetime.now()
    max_days_before = timedelta(days=15)
    date_limit = updated - max_days_before

    # Get and import the current month. Also the month before(past 15 days)
    # when the current and the past month are different.
    params = sorted(set([
        (updated.year, updated.month), (date_limit.year, date_limit.month)
    ]))

    filtered_df = stations_df.query('last_year>={}'.format(date_limit.year))
    # To limit the first five observations for test, uncomment the next line and
    # comment the following one.
    # for row in filtered_df[["station_id","first_year","last_year"]][:5].itertuples():
    for row in filtered_df[["station_id","first_year","last_year"]].itertuples():
        for param in params:
            observation_df = get_daily_data(
                row[COL_STATION_ID], year=param[0], month=param[1]
            )

            observation_df.rename(
                columns={old: new_name(old) for old in observation_df.columns},
                inplace=True
            )

            observation_df['station_id'] = row[COL_STATION_ID]

            observation_df['updated'] = updated

            
            observation_df.to_sql(
                'observations',
                engine,
                dtype=flags,
                if_exists='append'
            )


if __name__ == '__main__':
    main()

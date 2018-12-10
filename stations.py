from urllib import request
from datetime import datetime

import pandas as pd

from db import engine
from utils import new_name


def get_stations_df_from_ftp(stations_url='ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Station%20Inventory%20EN.csv'):
    return pd.read_csv(stations_url, skiprows=3)


def get_stations_df_from_db(stations_table='stations'):
    return pd.read_sql_table(stations_table, engine)


def main():
    stations_df = get_stations_df_from_ftp()

    stations_df.rename(
        columns={old: new_name(old) for old in stations_df.columns},
        inplace=True
    )

    updated = datetime.now()

    stations_df['updated'] = updated

    try:
        stations_df.to_sql('stations', con=engine)
    except ValueError:
        print('Table already exists, skiping!!!')

    # print(engine.execute("SELECT * FROM stations").fetchall())


if __name__ == '__main__':
    main()

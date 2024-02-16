import analyser
import pandas as pd
import os
from math import radians, sin, cos, sqrt, atan2
import time


def distance(lat1, lon1, lat2, lon2):
    return distance2(lon2 - lon1, lat2 - lat1)


def distance2(dlon, dlat):
    # The math module contains a function named radians which converts from degrees to radians.
    # The radius of the Earth in Poland is 6363.564 km
    dlon = radians(dlon)
    dlat = radians(dlat)
    R = 6363.564
    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(dlat) * cos(dlat) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    dist = R * c
    return abs(dist)


def exceeded_limit(limit, dlon, dlat, time_diff, vehicle_number, vechicle_number_match):
    distance_diff = distance2(dlon, dlat)
    velocity = distance_diff / time_diff if time_diff != 0 else 0
    if vechicle_number_match:
        if velocity > limit:
            przekroczenie = {
                'vehicle_number': vehicle_number,
                'velocity': velocity - limit,
            }
            return przekroczenie
    return None


def exceeded_velocity(limit, locations_file):
    if not os.path.isfile(locations_file):
        print("File does not exist")
        return
    start = time.time()
    buses_locations = pd.read_csv(locations_file)
    time1 = time.time()
    print("Time to read csv: ", time1 - start)

    # convert time to datetime
    buses_locations['time'] = pd.to_datetime(buses_locations['time'])

    # sort by vehicle number and time
    buses_locations = buses_locations.sort_values(by=['vehicle_number', 'time'])
    time2 = time.time()
    print("Time to sort: ", time2 - time1)

    # calculate differences
    diff_pd = pd.DataFrame(buses_locations)
    diff_pd['time_diff'] = diff_pd['time'].shift(-1) - diff_pd['time']
    diff_pd['szer_geo_diff'] = diff_pd['szer_geo'].shift(-1) - diff_pd['szer_geo']
    diff_pd['dl_geo_diff'] = diff_pd['dl_geo'].shift(-1) - diff_pd['dl_geo']
    diff_pd['vehicle_number_match'] = diff_pd['vehicle_number'] == diff_pd['vehicle_number'].shift(-1)
    diff_pd['time_diff'] = diff_pd['time_diff'].dt.total_seconds() / 3600
    diff_pd['distance'] = diff_pd.apply(lambda row: distance2(row['szer_geo_diff'], row['dl_geo_diff']), axis=1)

    # for dl_geo and szer_geo take the average of the two
    diff_pd['szer_geo'] = diff_pd['szer_geo'] + diff_pd['szer_geo'].shift(-1)
    diff_pd['szer_geo'] = diff_pd['szer_geo'] / 2
    diff_pd['dl_geo'] = diff_pd['dl_geo'] + diff_pd['dl_geo'].shift(-1)
    diff_pd['dl_geo'] = diff_pd['dl_geo'] / 2
    time2a = time.time()
    print("Time to calculate distance: ", time2a - time2)

    diff_pd['velocity'] = diff_pd.apply(lambda row: row['distance'] / row['time_diff'] if row['time_diff'] != 0 else 0, axis=1)
    time2a1 = time.time()
    print("Time to calculate velocity: ", time2a1 - time2a)

    diff_pd['velocity_exceeded'] = diff_pd.apply(lambda row: row['velocity'] - limit
                                                                    if row['velocity'] > limit and row['vehicle_number_match'] else 0, axis=1)
    time2a2 = time.time()
    print("Time to calculate velocity exceeded: ", time2a2 - time2a1)

    diff_pd.set_index('vehicle_number')
    time2b = time.time()
    print("Time to calculate time difference: ", time2b - time2)

    # filter rows where velocity_exceeded is not 0 and type is 1
    diff_pd = diff_pd[(diff_pd['velocity_exceeded'] != 0) & (diff_pd['type'] == 1)]

    # discard columns szer_geo_diff, dl_geo_diff, distance, time_diff, type and brigade
    diff_pd = diff_pd.drop(columns=['szer_geo_diff', 'dl_geo_diff', 'distance', 'time_diff', 'type', 'brigade'])
    time2c = time.time()
    print("Time to filter: ", time2c - time2b)

    # print columns velocity_exceeded, vehicle_number_match, time, vehicle_number
    print(diff_pd[['velocity_exceeded', 'vehicle_number_match', 'time', 'vehicle_number']])
    meta_data = dict()
    meta_data['how_many_rows'] = len(diff_pd)
    meta_data['how_many_vehicles'] = len(diff_pd['vehicle_number'].unique())
    meta_data['exceeded_more_than_10'] = len(diff_pd[diff_pd['velocity_exceeded'] > 10]['vehicle_number'].unique())
    meta_data['exceeded_more_than_20'] = len(diff_pd[diff_pd['velocity_exceeded'] > 20]['vehicle_number'].unique())
    meta_data['exceeded_more_than_30'] = len(diff_pd[diff_pd['velocity_exceeded'] > 30]['vehicle_number'].unique())
    meta_data['exceeded_more_than_100'] = len(diff_pd[diff_pd['velocity_exceeded'] > 100]['vehicle_number'].unique())
    meta_data['percentage_of_wrong_rows'] = meta_data['exceeded_more_than_100'] / len(diff_pd) * 100

    # remove rows where velocity_exceeded is greater than 100
    diff_pd = diff_pd[diff_pd['velocity_exceeded'] <= 100]

    # save dataframe to csv
    diff_pd.to_csv('velocity_exceeded.csv', index=False)
    # save meta data to csv
    meta_data_df = pd.DataFrame([meta_data])
    meta_data_df.to_csv('meta_data.csv', index=False)


exceeded_velocity(50, '..\\locations20_40.csv')


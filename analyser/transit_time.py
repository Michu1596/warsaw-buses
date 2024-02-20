import pandas as pd
import os
import time
from analyser import distance2


def buses_on_bus_stops(locations_file, line, km_threshold=0.10):
    # from data directory import lcoations20_40.csv to dataframe
    point0 = time.time()
    # check if locations_file exists
    if not os.path.isfile('data\\' + locations_file):
        raise FileNotFoundError('Locations file not found')
    locations = pd.read_csv('data\\' + locations_file)
    # chceck if schedule + line + .csv exists and if not, throw an error
    if not os.path.isfile('data\\schedules' + line + '.csv'):
        raise FileNotFoundError('Schedules file not found')
    locations = locations[locations['lines'] == line]
    # remove duplicate rows
    locations = locations.drop_duplicates()
    locations = locations.rename(columns={'szer_geo': 'szer_geo_bus', 'dl_geo': 'dl_geo_bus',
                                          'time': 'time_bus'})
    bus_stops = pd.read_csv('data\\possible_bus_stops' + line + '.csv')
    bus_stops = bus_stops.rename(columns={'szer_geo': 'szer_geo_stop', 'dl_geo': 'dl_geo_stop',
                                          'time': 'time_stop'})
    buses_on_stops = bus_stops.merge(locations, how='cross')
    mask = buses_on_stops.apply(lambda row: distance2(row['dl_geo_stop'] - row['dl_geo_bus'],
                                        row['szer_geo_stop'] - row['szer_geo_bus']) < km_threshold, axis=1)
    buses_on_stops = buses_on_stops[mask]
    # remo columns id_ulicy, brigade, type
    buses_on_stops = buses_on_stops.drop(columns=['id_ulicy', 'brigade', 'type'])
    # sort by vehicle_number and time
    buses_on_stops = buses_on_stops.sort_values(by=['vehicle_number', 'time_bus'])
    # reorder columns make vehicle_number and time_bus first
    buses_on_stops = buses_on_stops[['vehicle_number', 'time_bus', 'zespol', 'slupek', 'nazwa_zespolu', 'szer_geo_stop',
                                     'dl_geo_stop', 'kierunek', 'szer_geo_bus', 'dl_geo_bus']]
    # remove duplicate rows where vehicle_number and zespol are the same
    buses_on_stops = buses_on_stops.drop_duplicates(subset=['vehicle_number', 'zespol'])
    buses_on_stops.to_csv('data\\buses_on_stops_simplified' + line + '.csv', index=False)
    return buses_on_stops


def calculate_transit_time(line):
    buses_on_stops = pd.read_csv('data\\buses_on_stops_simplified' + line + '.csv')
    buses_on_stops['time_bus'] = pd.to_datetime(buses_on_stops['time_bus'])
    buses_on_stops = buses_on_stops.sort_values(by=['vehicle_number', 'time_bus'])
    buses_on_stops['time_diff'] = buses_on_stops['time_bus'].shift(-1) - buses_on_stops['time_bus']
    buses_on_stops['time_diff'] = buses_on_stops['time_diff'].dt.total_seconds() / 60
    buses_on_stops['vechicle_number_match'] = (buses_on_stops['vehicle_number'] ==
                                               buses_on_stops['vehicle_number'].shift(-1))
    buses_on_stops['next_stop_name'] = buses_on_stops['nazwa_zespolu'].shift(-1)
    buses_on_stops['next_stop_id'] = buses_on_stops['zespol'].shift(-1)
    buses_on_stops = buses_on_stops.drop(columns=['szer_geo_bus', 'dl_geo_bus'])
    # remove rows where vehicle_number_match is False
    buses_on_stops = buses_on_stops[buses_on_stops['vechicle_number_match']]
    # group by zespol and next_stop_id and calculate mean of time_diff and count of vehicle_number
    aggr_by = ['zespol', 'nazwa_zespolu', 'next_stop_id', 'next_stop_name', 'szer_geo_stop', 'dl_geo_stop']
    # group by columns in aggr_by and calculate mean of time_diff and count of vehicle_number, but leave columns
    # specified in aggr_by
    buses_on_stops = buses_on_stops.groupby(aggr_by).agg({'time_diff': 'mean', 'vehicle_number': 'count'}).reset_index()
    # reset index is what makes columns in aggr_by stay in the dataframe
    # remove rows where vehicle_number is less than 3
    buses_on_stops = buses_on_stops[buses_on_stops['vehicle_number'] > 2]
    buses_on_stops.to_csv('data\\transit_time' + line + '.csv', index=False)
    return buses_on_stops


def fit_to_schedule(line):
    all_routes = pd.read_json('data\\all_routes.json')
    # read transit_time + line + .csv
    transit_time = pd.read_csv('data\\transit_time' + line + '.csv')
    # zespol to string
    transit_time['zespol'] = transit_time['zespol'].astype(str)
    # next_stop_id to string
    transit_time['next_stop_id'] = transit_time['next_stop_id'].astype(str)
    line_routes = all_routes['result'][line]
    for route in line_routes:
        df = pd.DataFrame(line_routes[route])
        # flip the dataframe
        df = df.T
        # index to int
        df.index = df.index.astype(int)
        # sort by index
        df = df.sort_index()
        df['next_stop_id'] = df['nr_zespolu'].shift(-1)
        # merge with transit_time by zespol and next_stop_id
        df = df.merge(transit_time, left_on=['nr_zespolu', 'next_stop_id'], right_on=['zespol', 'next_stop_id'])
        max_time_diff = df['time_diff'].max()
        min_time_diff = df['time_diff'].min()
        # round time_diff to 2 decimal places
        df['time_diff'] = df['time_diff'].round(2)
        yellow = (255, 255, 0)
        blue = (0, 0, 255)
        # make column color and set to gradient from blue to yellow
        df['color'] = df['time_diff'].apply(lambda x: gradient(min_time_diff, max_time_diff, x, blue, yellow))
        # df['color'] = df['time_diff'].apply(lambda x: "rgb(0, 0, 255)" if x < 1 else "rgb(255, 255, 0)")
        # save to csv
        df.to_csv('data\\fit_to_schedule' + line + route + '.csv', index=False)

    # print(line_routes)


def gradient(minimum, maximum, value, color1, color2):
    ratio = (value - minimum) / (maximum - minimum)
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return "rgb(" + str(r) + "," + str(g) + "," + str(b) + ")"


# buses_on_bus_stops('180')
# calculate_transit_time('180')
# fit_to_schedule('180')

import json
from shapely.geometry import shape, GeometryCollection, Point
import pandas as pd

# from data directory import warszawa-dzielnice.geojson
count = 0
with open('..\\data\\warszawa-dzielnice.geojson') as f:
    districts = json.load(f)


def district_of_point(point):
    global count
    count += 1
    if count % 1000 == 0:
        print(count)
    for district in districts['features']:
        polygon = shape(district['geometry'])
        # check if point is in district
        if polygon.contains(point) and district['properties']['name'] != 'Warszawa':
            # print(district['properties']['name'])
            return district['properties']['name']
    return None


def district_of_bus(location_file_name):
    buses_locations = pd.read_csv(location_file_name)
    buses_locations['district'] = buses_locations.apply(lambda row: district_of_point(Point(row['dl_geo'],
                                                                                            row['szer_geo'])), axis=1)
    buses_locations.to_csv('..\\data\\buses_locations_with_district.csv', index=False)


def buses_in_districts(location_file_name, sample_size=360):
    buses_locations = pd.read_csv(location_file_name)
    buses_locations = buses_locations.dropna()
    # group by district and count number of rows
    buses_locations = buses_locations.groupby('district').size().reset_index(name='count')
    buses_locations['count'] = buses_locations['count']
    buses_locations['count'] = buses_locations['count'] / sample_size
    # sum count column and print
    print(buses_locations['count'].sum())
    buses_locations.to_csv('..\\data\\buses_in_districts.csv', index=False)


# district_of_bus('..\\data\\locations20_40.csv')
buses_in_districts('..\\data\\buses_locations_with_district.csv')

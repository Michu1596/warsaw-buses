import pandas as pd
import os
import collecting_data

# https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&page=1&size=5&apikey=1b1f637d-b66e-41d2-96ea-69befbf53515
# wspolrzedne przystankow


def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_bus_stops():
    bus_stops = pd.read_json('https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3'
                             '&page=1&size=5&apikey=1b1f637d-b66e-41d2-96ea-69befbf53515')
    # url = 'https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&page=1&size=5
    # &apikey=1b1f637d-b66e-41d2-96ea-69befbf53515' data = json.loads(requests.get(url).text)

    print(bus_stops.result[0]['values'][5]['value'])
    bus_stops_normalised = pd.DataFrame(columns=['zespol', 'slupek', 'nazwa_zespolu', 'id_ulicy', 'szer_geo', 'dl_geo',
                                                 'kierunek'])
    for i in range(len(bus_stops.result)):
        zespol = bus_stops.result[i]['values'][0]['value']
        slupek = bus_stops.result[i]['values'][1]['value']
        nazwa_zespolu = bus_stops.result[i]['values'][2]['value']
        id_ulicy = bus_stops.result[i]['values'][3]['value']
        szer_geo = bus_stops.result[i]['values'][4]['value']
        dl_geo = bus_stops.result[i]['values'][5]['value']
        kierunek = bus_stops.result[i]['values'][6]['value']
        bus_stops_normalised.loc[i] = [zespol, slupek, nazwa_zespolu, id_ulicy, szer_geo, dl_geo, kierunek]

    # save to csv
    bus_stops_normalised.to_csv('bus_stops.csv', index=False)


# schedule rides to dict function
def schedule_rides_to_dict(schedule):
    return {
        'brigade': schedule.brigade,
        'route': schedule.route,
        'direction': schedule.direction,
        'time': schedule.time
    }


# check if file 'bus_stops.csv' exists
if not os.path.isfile('bus_stops.csv'):
    get_bus_stops()

# load bus_stops.csv
bus_stops = pd.read_csv('bus_stops.csv')
# set type of zespol and slupek to string
bus_stops['zespol'] = bus_stops['zespol'].astype(str)
bus_stops['slupek'] = bus_stops['slupek'].astype(str)
# index bus_stops by zespol and slupek
bus_stops = bus_stops.set_index(['zespol', 'slupek'])
# sort bus_stops by index
bus_stops = bus_stops.sort_index()
ztm = collecting_data.ztm
print("LOC")
print(bus_stops.loc['1001', '1'].nazwa_zespolu.iloc[0])


def get_all_schedules():
    dfs = []
    # iterate over bus_stops
    for i in range(10):
        success = False
        # save the i row of bus_stops to a dictionary
        bus_stop = {
            'zespol': bus_stops.zespol[i],
            'slupek': bus_stops.slupek[i],
            'nazwa_zespolu': bus_stops.nazwa_zespolu[i],
            'id_ulicy': bus_stops.id_ulicy[i],
            'szer_geo': bus_stops.szer_geo[i],
            'dl_geo': bus_stops.dl_geo[i],
            'kierunek': bus_stops.kierunek[i]
        }
        while not success:
            try:
                slupek = str(bus_stops.slupek[i])
                # if slupek is a single digit, add 0 before it
                if len(slupek) == 1:
                    slupek = '0' + slupek
                lines = ztm.get_lines_for_bus_stop_id(bus_stops.zespol[i], slupek)

                for line in lines:
                    success2 = False
                    # save the line to one element dictionary
                    linedict = {'line': line}
                    while not success2:
                        try:
                            departures = ztm.get_bus_stop_schedule_by_id(bus_stops.zespol[i], slupek, line).rides
                            # dataframe for departures, bus_stop and line
                            df = pd.DataFrame([{**schedule_rides_to_dict(departure), **bus_stop, **linedict} for departure in
                                               departures])
                            dfs.append(df)
                            success2 = True
                        except Exception as e:
                            print("Error while getting schedules for stop", bus_stops.zespol[i])
                            print(e)
                success = True
            except Exception as e:
                print("Error while getting lines for stop", bus_stops.zespol[i])
                print(e)
        print("finished stop", bus_stops.zespol[i])
    print("Success!")

    # concatenate dataframes
    collected_data = pd.concat(dfs, ignore_index=True)
    # save to csv
    collected_data.to_csv('schedules.csv', index=False)


def get_all_stops_for_line(line):
    line = str(line)
    stops_set = set()
    url = 'https://api.um.warszawa.pl/api/action/public_transport_routes/?apikey=1b1f637d-b66e-41d2-96ea-69befbf53515'
    data = pd.read_json(url)
    routes = data.result[line]
    # iterate over routes
    for route in routes:
        for stop in routes[route]:
            zespol = routes[route][stop]['nr_zespolu']
            slupek = routes[route][stop]['nr_przystanku']
            # remove leading zeros from slupek - without this, dataframe throws a key error
            slupek = str(int(slupek))
            stops_set.add((str(zespol), str(slupek)))
    return stops_set


def get_all_departures_from_stops_for_line(line, stops_set):
    line = str(line)
    dfs = []
    itr = 1
    for stop in stops_set:
        if not (stop[0], stop[1]) in bus_stops.index:
            print("Stop", stop[0], stop[1], "not found in bus_stops.csv")
            continue
        print("getting schedules for stop", stop[0], stop[1], "for line", line)
        # print percentage of stops done
        print("Percentage of stops done:", (itr / len(stops_set)) * 100, "%")
        success = False
        bus_stop = {
            'zespol': stop[0],
            'slupek': stop[1],
            # get the rest of the data from bus_stops
            'nazwa_zespolu': bus_stops.loc[stop[0], stop[1]].nazwa_zespolu.iloc[0],
            'id_ulicy': bus_stops.loc[stop[0], stop[1]].id_ulicy.iloc[0],
            'szer_geo': bus_stops.loc[stop[0], stop[1]].szer_geo.iloc[0],
            'dl_geo': bus_stops.loc[stop[0], stop[1]].dl_geo.iloc[0],
            'kierunek': bus_stops.loc[stop[0], stop[1]].kierunek.iloc[0]
        }
        while not success and isnumber(stop[0]) and isnumber(stop[1]):
            try:
                if len(stop[1]) == 1:
                    stop = (stop[0], '0' + stop[1]) # without leading zero, get_bus_stop_schedule_by_id does not work
                departures = ztm.get_bus_stop_schedule_by_id(stop[0], stop[1], line).rides
                df = pd.DataFrame([{**schedule_rides_to_dict(departure), **bus_stop} for departure in departures])
                if stop[0] == '5157':
                    print(df)
                dfs.append(df)
                success = True
            except Exception as e:
                print("Error while getting schedules for stop", stop[0])
                print(e)
        print("finished stop", stop[0])
        itr += 1
    print("Success!")

    # concatenate dataframes
    collected_data = pd.concat(dfs, ignore_index=True)
    # save to csv
    collected_data.to_csv('schedules' + line + '.csv', index=False)


stops = get_all_stops_for_line('180')
print(stops)
get_all_departures_from_stops_for_line('180', stops)


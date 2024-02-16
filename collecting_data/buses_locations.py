import pandas as pd
import time

import collecting_data


# function to transform bus into dictionary
def bus_to_dict(bus):
    return {
        'time': bus.time,
        'lines': bus.lines,
        'brigade': bus.brigade,
        'vehicle_number': bus.vehicle_number,
        'dl_geo': bus.location.longitude,
        'szer_geo': bus.location.latitude,
        'type': bus.type
    }


def get_buses_locations(interval=10, n=10, filename='buses_locations.csv',
                        apikey='1b1f637d-b66e-41d2-96ea-69befbf53515'):
    ztm = collecting_data.ztm
    success = False
    dfs = []

    for i in range(n):
        while not success:
            try:
                buses_locations = ztm.get_buses_location()
                # bus0 = buses_locations[512]
                # print("ile busów: ", len(buses_locations))
                # print(bus0.time)
                # print(bus0.lines)
                # print(bus0.brigade)
                # print(bus0.vehicle_number)
                # print(bus0.location)
                # print(bus0.type)
                success = True
                df = pd.DataFrame([bus_to_dict(bus) for bus in buses_locations])
                dfs.append(df)
            except Exception as e:
                print(e)
                print("Retrying...")
        print("Success!")
        success = False
        time.sleep(interval)
    collected_data = pd.concat(dfs, ignore_index=True)
    collected_data.to_csv(filename, index=False)
    print("Data collected and saved to", filename)

#
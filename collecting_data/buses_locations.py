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
        time0 = time.time()
        while not success:
            try:
                buses_locations = ztm.get_buses_location()
                success = True
                df = pd.DataFrame([bus_to_dict(bus) for bus in buses_locations])
                dfs.append(df)
            except Exception as e:
                print(e)
                print("Retrying...")
        success = False
        time1 = time.time()
        time.sleep(max(0, round(interval - (time1 - time0))))
        print("Success! Time to collect:", round(time1 - time0), "seconds")
    collected_data = pd.concat(dfs, ignore_index=True)
    collected_data.to_csv(filename, index=False)
    print("Data collected and saved to", filename)

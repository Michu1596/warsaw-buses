import pandas as pd

# https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&page=1&size=5&apikey=1b1f637d-b66e-41d2-96ea-69befbf53515
# wspolrzedne przystankow

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

import collecting_data.buses_locations
import analyser.velocity
import analyser.punctuality
import analyser.transit_time
import analyser.buses_in_districts
import collecting_data.bus_stops
import argparse
import cProfile
import pstats

# collecting_data.buses_locations.get_buses_locations(n=360, interval=10,filename="locations16_56.csv")
parser = argparse.ArgumentParser(description='basic analysis of buses in Warsaw')
parser.add_argument('operation', type=str, help='Operation to perform')
parser.add_argument('-n', type=int, help='How many times information will be collected', default=360)
parser.add_argument('-i', type=int, help='Interval between collecting data', default=10)
parser.add_argument('-fout', type=str, help='Output file name', default='output.csv')
parser.add_argument('-fin', type=str, help='Input file name', default='locations20_40.csv')
parser.add_argument('-limit', type=int, help='Speed limit', default=50)
parser.add_argument('-line', type=str, help='Lines to analyse', default='180')
parser.add_argument('-threshold', type=int, help='Threshold for punctuality', default=3)

# if operation is get_buses_locations then collect data
args = parser.parse_args()

with cProfile.Profile() as profile:
    if args.operation == 'get_buses_locations':
        collecting_data.buses_locations.get_buses_locations(n=args.n, interval=args.i, filename=args.fout)
    elif args.operation == 'exceeded_velocity':
        # if fout is specified then use it as output file
        if args.fout:
            analyser.velocity.exceeded_velocity(args.limit, args.fin, output_file=args.fout)
        else:
            analyser.velocity.exceeded_velocity(args.limit, args.fin)
    elif args.operation == 'punctuality':
        analyser.punctuality.punctuality_of_line(args.fin, args.line)
        if args.fout:
            analyser.punctuality.test_punctuality_of_line(args.line, output_file=args.fout)
        else:
            analyser.punctuality.test_punctuality_of_line(args.line)
    elif args.operation == 'transit_time':
        analyser.transit_time.buses_on_bus_stops(args.fin, args.line)
        analyser.transit_time.calculate_transit_time(args.line)
        if args.fout:
            analyser.transit_time.fit_to_schedule(args.line, output_file=args.fout)
        else:
            analyser.transit_time.fit_to_schedule(args.line)
    elif args.operation == 'buses_in_districts':
        analyser.buses_in_districts.district_of_bus(args.fin)
        if args.fout:
            analyser.buses_in_districts.buses_in_districts('buses_locations_with_district.csv',
                                                           output_file_name=args.fout)
        else:
            analyser.buses_in_districts.buses_in_districts('buses_locations_with_district.csv')
    elif args.operation == 'get_all_departures_from_stops_for_line':
        stop_ids = collecting_data.bus_stops.get_all_stops_for_line(args.line)
        collecting_data.bus_stops.get_all_departures_from_stops_for_line(args.line, stop_ids)
    elif args.operation == 'save_all_bus_stops_for_line':
        collecting_data.bus_stops.save_all_bus_stops_for_line(args.line)
    else:
        print("Operation not recognised")

stats = pstats.Stats(profile)
stats.sort_stats(pstats.SortKey.TIME)
# save to file
stats.dump_stats('profile_stats\\profile_stats_districts.prof')

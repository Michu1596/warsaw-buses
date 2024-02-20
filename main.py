import collecting_data.buses_locations
import analyser.velocity
import analyser.punctuality
import analyser.transit_time
import analyser.buses_in_districts
import argparse

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
if args.operation == 'get_buses_locations':
    collecting_data.buses_locations.get_buses_locations(n=args.n, interval=args.i, filename=args.fout)
elif args.operation == 'exceeded_velocity':
    # if fout is specified then use it as output file
    if args.fout:
        analyser.velocity.exceeded_velocity(args.limit, args.fin,output_file=args.fout)
    else:
        analyser.velocity.exceeded_velocity(args.limit, args.fin)
elif args.operation == 'punctuality':
    analyser.punctuality.punctuality_of_line(args.fin, args.line)
    analyser.punctuality.test_punctuality_of_line(args.line)
elif args.operation == 'transit_time':
    analyser.transit_time.buses_on_bus_stops(args.fin, args.line)
    analyser.transit_time.calculate_transit_time(args.line)
    analyser.transit_time.fit_to_schedule(args.line)
elif args.operation == 'buses_in_districts':
    analyser.buses_in_districts.buses_in_districts(args.fin)
    analyser.buses_in_districts.district_of_bus('buses_in_districts.csv')
else:
    print("Operation not recognised")

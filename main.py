# Load Distance Table
distance_matrix = []
address_list = []

def load_distance_data(filename):
    with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) # Skip header row
        for row in csv_reader:
            # Store the address
            address_list.append(row[0]) 
            row_distances = [float(d) if d != '' else 0.0 for d in row[1:]]
            distance_matrix.append(row_distances)

def get_distance(address1, address2):
    index1 = address_list.index(address1)
    index2 = address_list.index(address2)
    if distance_matrix[index1][index2] != 0:
        return distance_matrix[index1][index2]
    else:
        return distance_matrix[index2][index1]
    
from datetime import datetime, timedelta

# Truck class
class Truck:
    def __init__(self, truck_id, start_time, packages):
        self.truck_id = truck_id
        self.start_time = start_time
        self.packages = packages # List of package IDs assinged to a truck
        self.current_location = "4001 South 700 East" # Hub address
        self.miles_traveled = 0.0
        self.time = start_time # Track the time during deliveries 

    def add_miles(self, miles):
        self.miles_traveled += miles
        self.time += timedelta(hours = miles / 18) # Truck speed is 18mph

# Truck objects for the three trucks, manually assinged packages.

# Truck 1 leaves first for 9AM deadlines
truck1 = Truck(
    truck_id  = 1,
    start_time = datetime.strptime("08:05:00", "%H:%M:%S"),
       packages = [1, 7, 8, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40] # Early deadlines and no constraints (15 total)
)

# Truck 2 leaves once Truck 1 comes back or if delayed packages become available
truck2 = Truck(
    truck_id  = 2,
    start_time = datetime.strptime("09:15:00", "%H:%M:%S"),
    packages = [3, 5, 6, 10, 11, 12, 17, 18, 21, 22, 23, 24, 25,28, 36, 38] # Packages required to be on Truck 2 and the delayed package 6 (16 total)
)

# Truck 3 leaves last and finishes the EOD deliveries 
truck3 = Truck(
    truck_id  = 3,
    start_time = datetime.strptime("10:25:00", "%H:%M:%S"), # Delayed start time because driver on truck 1 returns and package 9 is ready
    packages = [2, 4, 9, 26, 27, 32, 33, 35, 39] # Package 9 was delayed until 10:20 AM plus remaining packages. (9 total)
)

# Citation: McGrath, M. (2022). Python in Easy Steps, 2nd Edition.
# Used datetime.strptime() example from pages 90-91 to set truck departure times. 


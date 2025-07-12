# Student ID: 011588831

import csv 

# Load Distance Table
distance_matrix = []
address_list = []

# This fuction loads the WGUPS Distance Table CSV into memory
# The funciton creates a 2 dimensional array (distance_matrix) and an address list (address_list)
# The function opens the CSV file, parses rows, and fills data structures (distance_matrix- 2D list array and address_list- list of all delivery addresses from the CSV file)
def load_distance_data(filename):
    with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            # Store the address
            address_list.append(row[0]) 
            row_distances = [float(d) if d != '' else 0.0 for d in row[1:]]
            distance_matrix.append(row_distances)

def get_distance(address1, address2):
    index1 = address_list.index(address1)
    index2 = address_list.index(address2)
# Check distance from address1 to address 2. 
# If distnace is missing/empty for address1 to address2, look up reverse (address 2 to address 1).
# If row 2, column 14 is empty on the distance table then it's not showing distance from address 2 to address 14, so the code clips it and checks the distance from address 14 to address 2 which is row 14 column 2. 
    if distance_matrix[index1][index2] != 0:
        return distance_matrix[index1][index2]
    else:
        return distance_matrix[index2][index1]
    
from datetime import datetime, timedelta

# Truck class
# This class models a delivery truck with truck ID, start time, assigned packages (manually loaded), current location, miles traveled, and the current time tracking.
# A new truck is initialized when a Truck object is created and time advances with deliveries. 
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

# Truck objects for the three trucks, manually assinged packages. These 3 trucks are created with preloaded packages and departure times from the Hub based on delivery constraints. 

# Truck 1 leaves first, Truck 2 leave after Truck 1 returns or delayed packages arrive, Truck 3 waits until package 9 address correction is made at 10:20 AM. 

# Truck 1 leaves first for 9 AM deadlines
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


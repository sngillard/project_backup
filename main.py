# Student ID: 011588831

from datetime import datetime, timedelta
from hash_table import HashTable
from package import Package
from load_packages import package_hash
from load_packages import load_package_data
import csv 

# Load Distance Table
distance_matrix = []
address_list = []

# Load addresses from wgups_address_file.csv
def load_address_file(filename):
    with open(filename, mode = 'r', encoding = 'utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            # row[1] is the address, skip row[0] because it's the hub
            address_list.append(row[1].strip())

# Load distance table from wgups_distance_file.csv
def load_distance_table(filename):
    with open(filename, mode = 'r', encoding = 'utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if row:
                row_distances = [float(d.strip()) if d.strip() else 0.0 for d in row]
                distance_matrix.append(row_distances)

# Get distance between two addresses from csv files for distance and addresses
def get_distance(address1, address2):
    try:
        index1 = address_list.index(address1)
        index2 = address_list.index(address2)
    except ValueError:
        print(f"Address not found: {address1} or {address2}")
        return 0.0
    
# Check distance from address1 to address 2. 
# If distnace is missing/empty for address1 to address2, look up reverse (address 2 to address 1).
# If row 2, column 14 is empty on the distance table then it's not showing distance from address 2 to address 14, so the code clips it and checks the distance from address 14 to address 2 which is row 14 column 2. 
    if distance_matrix[index1][index2] != 0:
        return distance_matrix[index1][index2]
    else:
        return distance_matrix[index2][index1]

# Constant for Hub address format to match from wgups_address_file.csv
HUB_ADDRESS = "Western Governors University,4001 South 700 East"

# Truck class
# This class models a delivery truck with truck ID, start time, assigned packages (manually loaded), current location, miles traveled, and the current time tracking.
# A new truck is initialized when a Truck object is created and time advances with deliveries. 
class Truck:
    def __init__(self, truck_id, start_time, packages):
        self.truck_id = truck_id
        self.start_time = start_time
        self.packages = packages # List of package IDs assinged to a truck
        self.current_location = HUB_ADDRESS
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

# Delivery simulation using Nearest-Neighbor Algorithm
def deliver_packages(truck):
    while truck.packages:
        # Get current location of truck
        current_address = truck.current_location
        closest_package = None
        shortest_distance = float('inf')

        # Find the closest package address
        for package_id in truck.packages:
            package = package_hash.get(package_id)
            distance = get_distance(current_address, package.address)
            if distance < shortest_distance:
                shortest_distance = distance
                closest_package = package

        # Drive to the closest package to be delivered on the truck
        truck.add_miles(shortest_distance)
        truck.current_location = (closest_package.address) 
        closest_package.time_delivered = truck.time
        closest_package.truck_departure_time = truck.start_time
        truck.packages.remove(closest_package.package_id) # Remove delivered package from truck's package list

    # Drive back to the Hub
    distance_to_hub = get_distance(truck.current_location, HUB_ADDRESS)
    truck.add_miles(distance_to_hub)
    truck.current_location = HUB_ADDRESS

''' WGUPS delivery program user interface loops through meny options until the user selects option 4- Exit program. Depending on the user's choice, the main_menu function calls other functions for package status lookups, single package search, or total miles calculation.
'''
def main_menu():
    while True: # Loop through options until user exists
        print("**************************************")
        print("Welcome to the WGUPS Delivery App!")
        print("**************************************")
        print("1. View all package statuses at a time")
        print("2. Look up a single package at a time")
        print("3. View total miles traveled by trucks")
        print("4. Exit program")
        print("**************************************")

        choice = input("enter your choice (1-4): ")

        if choice == "1":
            time_str = input("Enter time (HH:MM:SS or HH:MM): ")
            view_all_packages(time_str)
        elif choice == "2":
            time_str = input("Enter time (HH:MM:SS or HH:MM): ")
            package_id = int(input("Enter package ID # to look up: "))
            lookup_package(package_id, time_str)
        elif choice == "3":
            time_str = input("Enter time (HH:MM:SS or HH:MM):")
            show_total_miles(time_str)
        elif choice == "4":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Please enter a valid choice.\n")

# Function to parse time
def parse_time_input(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(time_str, "%H:%M")
        except ValueError:
            print("Invalid time format. Please enter time as HH:MM or HH:MM:SS.\n")
            return None


# Function to display all package statuses at a specific time
def view_all_packages(time_str):
    check_time = parse_time_input(time_str)
    if not check_time:
        return

    print(f"\nPackage statuses at {check_time.strftime('%H:%M:%S')}")
    for package_id in range(1, 41):
        package = package_hash.get(package_id)
        if package.time_delivered < check_time:
            status = f"Delivered at: {package.time_delivered.strftime('%H:%M:%S')}"
        elif package.truck_departure_time > check_time:
            status = "At Hub"
        else:
            status = "En Route"
        print(f"Package {package_id}: {status}")

# Function to look up a single package status
# This function displays the delivery status of a specific package (by package ID) at a time specified by the user.
def lookup_package(package_id, time_str):
    check_time = parse_time_input(time_str)
    if not check_time:
        return
# Lookup the package and print status
    package = package_hash.get(package_id)
    print(f"\nStatus of Package: {package_id} at {check_time.strftime('%H:%M:%S')}")
    if package.time_delivered < check_time:
        status = f"Delivered at: {package.time_delivered.strftime('%H:%M:%S')}"
    elif package.truck_departure_time > check_time:
        status = "At Hub"
    else:
        status = "En Route"
    print(f"Package {package_id}: {status}\n")

# Function to calculate total miles travled by all trucks at a specific time provided by the user.
def show_total_miles(time_str):
    check_time = parse_time_input(time_str)
    if not check_time:
        return
    total_miles = 0.0
    if truck1.time <= check_time:
        total_miles += truck1.miles_traveled
    if truck2.time <= check_time:
        total_miles += truck2.miles_traveled
    if truck3.time <= check_time:
        total_miles += truck3.miles_traveled
    print(f"\nTotal miles traveled by all trucks at {check_time.strftime('%H:%M:%S')}: {total_miles:.2f}\n")

# Load data from CSV files
load_address_file("wgups_address_file.csv")
load_distance_table("wgups_distance_table.csv")
load_package_data("wgups_package_file.csv")

# Simulate the deliveries for all trucks
deliver_packages(truck1)
deliver_packages(truck2)
deliver_packages(truck3)

# Start the command line program
if __name__ == "__main__":
    print(f"Truck 1 miles: {truck1.miles_traveled}")
    print(f"Truck 2 miles: {truck2.miles_traveled}")
    print(f"Truck 3 miles: {truck3.miles_traveled}")
    main_menu()
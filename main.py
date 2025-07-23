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
            address_list.append(row[2].strip())

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
    address1 = address1.strip()
    address2 = address2.strip()

    try:
        index1 = address_list.index(address1)
        index2 = address_list.index(address2)
    except ValueError:
        print(f"Address not found: '{address1}' or '{address2}'") 
        return 0.0
    
# Check distance from address1 to address 2. 
# If distance is missing/empty for address1 to address2, look up reverse (address 2 to address 1).
# If row 2, column 14 is empty on the distance table then it's not showing distance from address 2 to address 14, so the code clips it and checks the distance from address 14 to address 2 which is row 14 column 2. 
    distance = distance_matrix[index1][index2]
    if distance == 0.0:
        distance = distance_matrix[index2][index1]
    return distance 

# Constant for Hub address format to match from wgups_address_file.csv
HUB_ADDRESS = "4001 South 700 East"

# Truck class
# This class models a delivery truck with truck ID, start time, assigned packages (manually loaded), current location, miles traveled, and the current time tracking.
# A new truck is initialized when a Truck object is created and time advances with deliveries. 
class Truck:
    def __init__(self, truck_id, start_time, packages):
        self.truck_id = truck_id
        self.start_time = start_time
        self.packages = packages # List of package IDs assigned to a truck
        self.current_location = HUB_ADDRESS
        self.miles_traveled = 0.0
        self.time = start_time # Track the time during deliveries 

    def add_miles(self, miles):
        self.miles_traveled += miles
        self.time += timedelta(hours = miles / 18) # Truck speed is 18mph

# Truck objects for the three trucks, manually assigned packages. These 3 trucks are created with preloaded packages and departure times from the Hub based on delivery constraints. 

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
    packages = [3, 5, 10, 11, 12, 17, 18, 21, 22, 23, 24, 36, 38] 
)

# Truck 3 leaves last and finishes the EOD deliveries 
truck3 = Truck(
    truck_id  = 3,
    start_time = datetime.strptime("10:25:00", "%H:%M:%S"), # Delayed start time because driver on truck 1 returns and package 9 is ready
    packages = [2, 4, 9, 26, 27, 32, 33, 35, 39] # Package 9 was delayed until 10:20 AM plus remaining packages. (9 total)
)

# Delayed packages
delayed_packages = [6, 25, 28, 32]
delayed_package_ready_time = {
    6: datetime.strptime("09:05:00", "%H:%M:%S"),
    25: datetime.strptime("09:05:00", "%H:%M:%S"),
    28: datetime.strptime("09:05:00", "%H:%M:%S"),
    32: datetime.strptime("09:05:00", "%H:%M:%S"),
    9: datetime.strptime("10:20:00", "%H:%M:%S")
}

# Delivery simulation using Nearest-Neighbor Algorithm
def deliver_packages(truck, check_time):
    # Only simulate the deliveries if the truck has left
    if truck.start_time > check_time:
        return # Truck not departed yet
    
    # Check if any delayed packages are ready now and assign them to a truck
    for package_id in delayed_package_ready_time:
        ready_time = delayed_package_ready_time[package_id]
        if ready_time <= truck.start_time:
            package = package_hash.get(package_id)
            # If delpayed package isn't already assigned to a truck
            if package.truck_id is None: # Not assigned a truck yet
                # If possible, assign to Truck 2, else to Truck 3
                if truck.truck_id == 2: 
                    truck.packages.append(package_id)
                elif truck.truck_id == 3 and package_id not in truck2.packages:
                    truck.packages.append(package_id)
    
    # Assign truck number and departure time when truck leaves the hub
    for package_id in truck.packages:
            package = package_hash.get(package_id)
            if package.truck_id is None:
                package.truck_id = truck.truck_id
                package.truck_departure_time = truck.start_time
    
    while truck.packages:
        # Get current location of truck
        current_address = truck.current_location
        closest_package = None
        shortest_distance = float('inf')

        # Find the closest package to deliver 
        for package_id in truck.packages:
            package = package_hash.get(package_id)

            # Skip DELAYED packages until they are ready
            if package_id in delayed_package_ready_time:
                if delayed_package_ready_time[package_id] > check_time:
                    continue

            # Skip package 9 if address is not corrected yet
            if package_id == 9:
                if check_time < datetime.strptime("10:20:00", "%H:%M:%S"):
                    continue
                # Correct the address for package 9 at 10:20
                package.address = "410 S State St" # The corrected address

            # Skip packages that must be on Truck 2
            if package_id in [3, 18, 36, 38] and truck.truck_id != 2:
                continue

            # Skip packages that must be delivered together/grouped on same truck
            # Package 14 must be delivered with 15 & 19
            if package_id in [15, 19] and 14 in truck.packages:
                continue
            # Package 16 must be delivered with 13 and 19
            if package_id in [13, 19] and 16 in truck.packages:
                continue
            # Package 20 must be delivered with 13 & 15
            if package_id in [13, 15] and 20 in truck.packages:
                continue

            # Find distance to a package 
            distance = get_distance(current_address, package.address)
            if distance < shortest_distance:
                shortest_distance = distance
                closest_package = package

        if closest_package is None:
            break # Nothing close to deliver now
        
        travel_time = timedelta(hours = shortest_distance / 18) # Trucks travel at 18mph
        arrival_time = truck.time + travel_time

        # Stop if next delivery is beyond the check_time
        if arrival_time > check_time:
            break

        # Drive package location
        truck.add_miles(shortest_distance)
        truck.current_location = closest_package.address 
        closest_package.time_delivered = arrival_time
        closest_package.truck_departure_time = truck.start_time
        closest_package.truck_id = truck.truck_id # Assign truck number
        truck.time = arrival_time
        truck.packages.remove(closest_package.package_id) # Remove delivered package from truck's package list

        # Check for packages that must be delivered together and if they are all on the truck deliver them
        if closest_package.package_id == 14:
            for package_id in [15, 19]:
                if package_id in truck.packages:
                    group_packages = package_hash.get(package_id)
                    group_packages.time_delivered = arrival_time
                    group_packages.truck_departure_time = truck.start_time
                    group_packages.truck_id = truck.truck_id
                    truck.packages.remove(package_id)

        if closest_package.package_id == 16:
            for package_id in [13, 19]:
                if package_id in truck.packages:
                    group_packages = package_hash.get(package_id)
                    group_packages.time_delivered = arrival_time
                    group_packages.truck_departure_time = truck.start_time
                    group_packages.truck_id = truck.truck_id
                    truck.packages.remove(package_id)

        if closest_package.package_id == 20:
            for package_id in [13, 15]:
                if package_id in truck.packages:
                    group_packages = package_hash.get(package_id)
                    group_packages.time_delivered = arrival_time
                    group_packages.truck_departure_time = truck.start_time
                    group_packages.truck_id = truck.truck_id
                    truck.packages.remove(package_id)

    # Drive back to the Hub if finished early
    if truck.time < check_time and truck.current_location != HUB_ADDRESS:
        distance_to_hub = get_distance(truck.current_location, HUB_ADDRESS)
        truck.add_miles(distance_to_hub)
        truck.current_location = HUB_ADDRESS

''' WGUPS delivery program user interface loops through many options until the user selects option 4- Exit program. Depending on the user's choice, the main_menu function calls other functions for package status lookups, single package search, or total miles calculation.
'''
def main_menu():
    while True: # Loop through options until user exists
        print("**************************************")
        print("Welcome to the WGUPS Delivery App!")
        print("**************************************")
        print("1. View all package statuses at a time")
        print("2. Look up a single package at a time")
        print("3. View truck summary (packages & mileage)")
        print("4. Exit program")
        print("**************************************")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            time_str = input("Enter time (HH:MM:SS or HH:MM): ")
            view_all_packages(time_str)
        elif choice == "2":
            time_str = input("Enter time (HH:MM:SS or HH:MM): ")
            package_id = int(input("Enter package ID # to look up: "))
            lookup_package(package_id, time_str)
        elif choice == "3":
            time_str = input("Enter time (HH:MM:SS or HH:MM):")
            show_truck_summary(time_str)
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
    
    # Reset trucks and simulate deliveries up to the time selected by user
    reset_trucks()
    deliver_packages(truck1, check_time)
    deliver_packages(truck2, check_time)
    deliver_packages(truck3, check_time)

    print(f"\nPackage statuses at {check_time.strftime('%H:%M:%S')}")

    for package_id in range(1, 41):
        package = package_hash.get(package_id)

        # Determine the status of package
        if package_id in delayed_package_ready_time and delayed_package_ready_time[package_id] > check_time:
            # Delayed package logic
            if package_id == 9:
                status = f"DELAYED - Address correction at 10:20"
            else:
                ready_time = delayed_package_ready_time[package_id].strftime('%H:%M')
                status = f"DELAYED - Available at {ready_time}"

        elif package.time_delivered < check_time:
            # Package already delivered
            status = f"DELIVERED at {package.time_delivered.strftime('%H:%M:%S')}"

        elif package.truck_departure_time > check_time or package.truck_id is None:
            # Truck hasn't left yet or package is not yet assigned to a truck
            status = "AT HUB"

        else:
            # Truck has left and package is en route for delivery
            status = "EN ROUTE"

        print(f"Package {package_id} | "
              f"Address: {package.address} | " f"Deadline: {package.delivery_deadline} | " 
              f"Truck: {package.truck_id if package.truck_id else 'Not assigned'} | " 
              f"Delivery Time: {package.time_delivered.strftime('%H:%M:%S') if package.time_delivered != datetime.max else 'N/A'} | " 
              f"Weight (in kilos): {package.weight_kilo} | "
              f"Special Notes: {package.special_notes} | "
              f"Status: {status}\n")

    # Print total mileage for this time
    total_miles = truck1.miles_traveled + truck2.miles_traveled + truck3.miles_traveled
    print(f"\nTotal miles traveled by all trucks at {check_time.strftime('%H:%M:%S')}: {total_miles:.2f}")

# Function to look up a single package status
# This function displays the delivery status of a specific package (by package ID) at a time specified by the user.
def lookup_package(package_id, time_str):
    check_time = parse_time_input(time_str)
    if not check_time:
        return
    
    # Reset trucks and simulate deliveries up to time specified by user
    reset_trucks()
    deliver_packages(truck1, check_time)
    deliver_packages(truck2, check_time)
    deliver_packages(truck3, check_time)

    # Print the package and print status
    print(f"\nStatus of Package: {package_id} at {check_time.strftime('%H:%M:%S')}")

    for package_id in range(1, 41):
        package = package_hash.get(package_id)
    
        # Determine status of package
        if package_id in delayed_package_ready_time and delayed_package_ready_time[package_id] > check_time:
            # Logic if a pacakge is still delayed
            if package_id == 9:
                status = f"DELAYED - Address correction at 10:20"
            else:
                ready_time = delayed_package_ready_time[package_id].strftime('%H:%M')
                status = f"DELAYED - Available at {ready_time}"
        elif package.time_delivered < check_time:
            # Delayed package is now delivered 
            status = f"Delivered at: {package.time_delivered.strftime('%H:%M:%S')}"
        elif package.truck_departure_time > check_time:
            # Package is loaded but truck is still at hub
            status = "AT HUB"
        else:
            # Package is on truck and en route
            status = "EN ROUTE"
    else:
        # Package logic for non-delayed packages
        if package.time_delivered < check_time:
            status = f"DELIVERED at {package.time_delivered.strftime('%H:%M:%A')}"
        elif package.truck_departure_time > check_time or package.truck_is is None:
            status = "AT HUB"
        else:
            status = "EN ROUTE"

    print(f"Package {package.package_id} | "
          f"Address: {package.address} | "
          f"Deadline: {package.delivery_deadline} | "
          f"Truck: {package.truck_id if package.truck_id else 'Not assigned' } | "
          f"Delivery Time: {package.time_delivered.strftime('%H:%M:%S') if package.time_delivered != datetime.max else 'N/A'} | "
          f"Weight (in kilos): {package.weight_kilo} | "
          f"Special Notes: {package.special_notes} | "
          f"Status: {status}\n"
          )

    # Print total mileage for this time
    total_miles = truck1.miles_traveled + truck2.miles_traveled + truck3.miles_traveled
    print(f"\nTotal miles traveled by all trucks at {check_time.strftime('%H:%M:%S')}: {total_miles:.2f}\n")

def reset_trucks():
    # Reset trucks to initial state with original package assignments
    truck1.time = truck1.start_time
    truck2.time = truck2.start_time
    truck3.time = truck3.start_time
    truck1.miles_traveled = 0.0
    truck2.miles_traveled = 0.0
    truck3.miles_traveled = 0.0
    truck1.current_location = HUB_ADDRESS
    truck2.current_location = HUB_ADDRESS
    truck3.current_location = HUB_ADDRESS

    # Reload original package truck assignments
    truck1.packages = [1, 7, 8, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40]
    truck2.packages = [3, 5, 10, 11, 12, 17, 18, 21, 22, 23, 24, 36, 38]
    truck3.packages = [2, 4, 9, 26, 27, 32, 33, 35, 39]

    # Reset package delivery statuses
    for package_id in range(1, 41):
        package = package_hash.get(package_id)
        package.time_delivered = datetime.max
        package.truck_departure_time = datetime.min
        package.truck_id = None 

# Function to calculate total miles traveled by all trucks at a specific time provided by the user.
def show_total_miles(time_str):
    check_time = parse_time_input(time_str)
    if not check_time:
        return
    
    # Reset the trucks and package status
    reset_trucks() 

    # Simulate deliveries up to the check_time time
    deliver_packages(truck1, check_time)
    deliver_packages(truck2, check_time)
    deliver_packages(truck3, check_time)

    total_miles = truck1.miles_traveled + truck2.miles_traveled + truck3.miles_traveled
    print(f"\nTotal miles traveled by all trucks at {check_time.strftime('%H:%M:%S')}: {total_miles:.2f}\n")

# Show truck summary at specific time
def show_truck_summary(time_str):
    check_time = parse_time_input(time_str)
    if not check_time:
        return
    
    # Reset trucks and simulate deliveries
    reset_trucks()
    deliver_packages(truck1, check_time)
    deliver_packages(truck2, check_time)
    deliver_packages(truck3, check_time)

    # Print truck summary
    print("*************** TRUCK SUMMARY ***************")
    print(f"Summary at {check_time.strftime('%H:%M:%S')}")
    print("*********************************************")
    for truck in [truck1, truck2, truck3]:
        print(f"\nTruck {truck.truck_id} Summary:")
        print(f" Departure Time: {truck.start_time.strftime('%H:%M:%S')}")
        print(f" Current Location: {truck.current_location}")
        print(f" Miles Traveled: {truck.miles_traveled:.2f}")

        if check_time < truck.start_time:
            print(" Packages Loaded: None (Truck has not departed yet)")
            print( " Delayed Packages:")
            for package_id in truck.packages:
                # Check if package is delayed
                if package_id in delayed_package_ready_time and delayed_package_ready_time[package_id] > check_time:
                    ready_time = delayed_package_ready_time[package_id].strftime('%H:%M')
                    if package_id == 9:
                        print(f" - Package {package_id}: DELAYED - Address correction at 10:20")
                    else:
                        print(f" - Package {package_id}: DELAYED - Available at {ready_time}")
                else:
                    print(f" - Package {package_id}: Waiting at Hub")
            else:
                print(" Packages Loaded:")
                for package_id in truck.packages:
                    package = package_hash.get(package_id)
                    print(f" - Package {package.package_id}: "
                          f"Address: {package.address}, "
                          f"Deadline: {package.delivery_deadline}, " 
                          f"Weight: {package.weight_kilo}kg")
            
            # Print the delivered packages
            delivered = [package_hash.get(package_id) for package_id in range(1, 41)
                     if package_hash.get(package_id).truck_id == truck.truck_id and package_hash.get(package_id).time_delivered <= check_time]
        if delivered:
            print("Delivered Packages:")
            for p in delivered:
                print(f" - Package {p.package_id}: Delivered at {p.time_delivered.strftime('%H:%M:%S')}")
        else:
            print(" No packages delivered yet.")
        print("*********************************************")

    total_miles = truck1.miles_traveled + truck2.miles_traveled + truck3.miles_traveled
    print(f"\nTotal miles traveled by all trucks at {check_time.strftime('%H:%M:%S')}: {total_miles:.2f}")
    print("*********************************************")


# Load data from CSV files
load_address_file("wgups_address_file.csv")
load_distance_table("wgups_distance_table.csv")
load_package_data("wgups_package_file.csv")

# Simulate the delivery day
end_of_day = datetime.strptime("17:00:00", "%H:%M:%S") 

# Start the command line program
if __name__ == "__main__":
    print(f"Truck 1 miles: {truck1.miles_traveled}")
    print(f"Truck 2 miles: {truck2.miles_traveled}")
    print(f"Truck 3 miles: {truck3.miles_traveled}")
    main_menu()
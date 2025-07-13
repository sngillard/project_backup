# Loads CSV into HashTable

import csv
from hash_table import HashTable
from package import Package
from datetime import datetime, timedelta

# Create a new hash table instance
package_hash = HashTable()

# Load the package data from CSV
def load_package_data(filename):
    with open(filename, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) # Skip header row
        for row in csv_reader:
            # Get information from each row
            if not row or not row[0].strip().isdigit(): # Skip emoty rows
                continue
            package_id = int(row[0])
            address = row[1]
            city = row[2]
            state = row[3]
            zip_code = row[4]
            deadline = row[5]
            weight = row[6]
            special_notes = row[7] if len(row) > 7 else ""

            # Create new Package object
            package = Package(package_id, address, city, state, zip_code, deadline, weight, special_notes)
            
            # **Temporary times to test REMOVE- DEBUG ONLY**
            package.truck_departure_time = datetime.strptime("08:00:00", "%H:%M:%S")
            package.time_delivered = datetime.strptime("10:30:00", "%H:%M:%S")

            # Insert Package object into HashTable
            package_hash.add(package_id, package)

# Call the load_package_data function
load_package_data('wgups_package_file.csv')

# TO DEBUG- REMOVE LATER- PRINT ALL PACKAGES TO TEST
package_hash.print()
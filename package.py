# Create Package class to hold data from WGUPS package file (wgups_package_file.csv)

class Package: 
    def __init__(self, package_id, address, city, state, zip_code, delivery_deadline, weight_kilo, special_notes): 
        '''
        Initalize a Package object with these parameters:
        self
        package_id: the unique identifier for the package
        address: Street address for the delivery
        city: City of delivery location
        state: State of delivery location
        zip_code: Zip code of delivery location
        delivery_deadline: deadline for the package delivery (specific time deadline or by end of day/EOD)
        special_notes: Note with delivery constraints (needs to be on specific truck or part of a multi-package delivery, etc.)
        '''
        self.package_id = int(package_id) # Store each package as an integer for easy hashing
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.delivery_deadline = delivery_deadline
        self.weight_kilo = weight_kilo
        self.special_notes = special_notes
        self.time_delivered = None 
        self.truck_departure_time = None 

# Create and initalize a string containing the details of a Package object to print package details to command line interface. 
    def __str__(self):
        return (
            #Print package ID and address information on first list
            #Print delivery deadline, package weight, and notes on second line
            f"Package ID: {self.package_id},  Address: {self.address}, City: {self.city}, State: {self.state}, Zip Code: {self.zip_code}"
            f"Delivery Deadline: {self.delivery_deadline}, Weight (in kilo): {self.weight_kilo}, Special Notes: {self.special_notes}"
            )
    
# Output human readable package information, not object references!
def print(self):
    print('---WGUPS PACKAGE HASH TABLE---')
    for item in self.map:
        if item is not None:
            for pair in item:
                print(f"Package ID: {pair[0]}, Data: {pair[1]}")
    

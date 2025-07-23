# Create class HashTable to store the package data
class HashTable:
    def __init__(self, size = 41): # Prime number size of buckets helps spread out key-value pairs and reduce collisons.
        self.size = size
        self.count = 0 # Count the number of key-value pairs in table
        self.map = [None] * self.size # Initialize HashTable with empty buckets 

    def _get_hash(self, key):
            # Create a simple hash function to configure teh array index for a given package_id key
            hash = 0
            # Loop through the characters in a variable key
            for char in str(key):
                 hash += ord(char) # ord is the ASCII numerical value of a char in Python
            return hash % self.size # Modulus to get an index calue within the table size
    
    def add(self, key, value):
        ''' 
        Insertion function to add the key-value par to the HashTable.
        The add function takes the package_id as the key and stores the delivery address, deadline, city, state, zip code, package weight, delivery status, and delivery time.
        '''
        if self.count / self.size >= 0.7: 
              self._resize() # To improve scalability and reduce collisions as the dataset grows, the hash table will automaticaly double in size and rehash elements once it is 70% full (load factor exceeds 0.7)
        key_hash = self._get_hash(key)
        key_value = [key, value] # Store key and package data as a pair
    
        if self.map[key_hash] is None:
            self.map[key_hash] = [key_value] # Create a new bucket for this key_hash value
        else:
            for pair in self.map[key_hash]:
                 if pair[0] == key: # Update package data if already exists
                      pair[1] = value 
                      return True
            self.map[key_hash].append(key_value) # Append new key-value pair to bucket

        self.count += 1
        return True

    # Lookup function that takes the package ID as input and returns the delivery address, deadline, city, and zip code, plus package weight and delivery status inlcuding delivery time
    def get(self, key):
         # Get the package data for a given package_id
        key_hash = self._get_hash(key)
        if self.map[key_hash] is not None:
            for pair in self.map[key_hash]:
                if pair[0] == key:
                    return pair[1] # Return the package data
        return None

    def _resize(self):
         # Double the table size to the next prime number and rehash all the entries to allow for scalability/self-adjustment. 

        former_map = self.map
        self.size = self.size * 2 + 1 # Gets the next odd number
        self.map = [None] * self.size
        self.count = 0
        for bucket in former_map:
            if bucket is not None:
                for pair in bucket:
                    self.add(pair[0], pair[1]) # Re-add all key-value pairs to re-sized table

    def print(self):
         # Get all key-value pairs
        all_packages = []
        for bucket in self.map:
            if bucket is not None:
                for pair in bucket:
                    all_packages.append(pair)

        # Sort by package ID (key) so they print in numerical order
        all_packages.sort() 

         # Print the entire HashTable to debug
        ''' 
        print('---WGUPS PACKAGE HASH TABLE---')
        for pair in all_packages:
            key = pair[0]
            package = pair[1]
            print(f"Package ID: {key}")
            print(f"Address: {package.address}, City: {package.city}, State: {package.state}, Zip Code: {package.zip_code}")
            print(f"Delivery Deadline: {package.delivery_deadline}, Weight (in kilo): {package.weight_kilo}, Special Notes: {package.special_notes}\n")
        '''
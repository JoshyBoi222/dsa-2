# Student ID: 011353052
import csv
from datetime import datetime, timedelta





# Class to store the packages from the CSV file into a hash table
class HashTable:
    # Max capacity of the hash table
    def __init__(self, capacity=10):
        # Initialize the hash with empty lists
        self.table = [[] for i in range(capacity)]


    def indexValue(self, key):
        # Generate an index for the key using the hash function
        return hash(key) % len(self.table)


    def keyValues(self, key, value):
        # Return a list of a key and its value
        return [key, value]


    def insert(self, key, value):
        # Get the index for the key
        index = self.indexValue(key)
        keyValue = self.keyValues(key, value)


        # Check the if the key exists for the items in the hash table
        for item in self.table[index]:
            # If it does, then update the value
            if item[0] == key:
                item[1] = value
                return
        # If not, then add the key-value pair to the bucket
        self.table[index].append(keyValue)
        return


    def search(self, key):
        # Get the index for the key
        index = self.indexValue(key)
        # Check the if the key exists for the items in the hash table
        for item in self.table[index]:
            # If it does, then return the value
            if item[0] == key:
                return item[1]
            # If not, then return None
        return None


    def remove(self, key):
        # Get the index for the key
        index = self.indexValue(key)
        # Check the if the key exists for the items in the hash table
        for item in self.table[index]:
            #If it does, then remove the key-value pair
            if item[0] == key:
                self.table[index].remove(item)
                return





# Class to define and organize the package attributes
class Package:
    def __init__(self, packageID, address, city, state, zipCode, deadline, weight, notes=None):
        self.packageID = packageID
        self.address = address
        self.city = city
        self.state = state
        self.zipCode = zipCode
        self.deadline = deadline
        self.weight = weight
        # Update packages that have special notes
        self.notes = notes
        # Default package status is at the Hub
        self.status = "Package is still at the Hub"
        # Package time should update to the time it was delivered
        self.time = None
        # Truck name will be assigned when loading packages
        self.truck = None


    # Method to update the packages status
    def statusUpdate(self, status, time=None):
        self.status = status
        # Add the time for when a package is delivered
        if time:
            self.time = time




# Function to load the package data from the CSV file into the hash table class
def loadPackageData(filePath, packageHashTable):
    with open (filePath) as packageCSV:
        packageData = csv.reader(packageCSV, delimiter=',')
        # Iterate over the rows to get info for package attributes
        for row in packageData:
            packageID = int(row[0])
            address = row[1]
            city = row[2]
            state = row[3]
            zipCode = row[4]
            deadline = row[5]
            weight = row[6]
            notes = row[7]

            # Create a package object to store the data from that row
            package = Package(packageID, address, city, state, zipCode, deadline, weight, notes)
            # Add the package into a hash table with the package ID as the key and the package attributes as the value
            packageHashTable.insert(package.packageID, package)





# Function to load the distance data from the CSV file into a nested dictionary
def loadDistanceData(filePath):
    # Initialize an empty dictionary to store the location data
    locationsDictionary = {}

    with open(filePath) as distanceCSV:
        distanceData = csv.reader(distanceCSV)
        secondLocation = next(distanceData)[1:]  # Read the first row to get inner key (location B)
        # Iterate over the rows to extract location data
        for row in distanceData:
            firstLocation = row[0]  # The first element in the row is the outer key (location A)
            distances = row[1:]  # The rest of the elements in the row are the values for the inner key (location B)

            # Initialize an empty dictionary for the outer keys (location A) in the locationsDictionary
            locationsDictionary[firstLocation] = {}

            # Iterate over the distances and keep track of the index to access the inner Key
            for i, distance in enumerate(distances):
                # If the distance value is not empty
                if distance != '':
                    # Convert the value to a float to calculate miles later
                    distanceValue = float(distance)
                    # Assign the value to the inner dictionary of the first location
                    locationsDictionary[firstLocation][secondLocation[i]] = distanceValue
                    # Ensure that the dictionary is symmetric (the distance is the same from A to B and from B to A)
                    # Assign the value to the inner dictionary of the second location as well
                    locationsDictionary[secondLocation[i]][firstLocation] = distanceValue
    # Return the nested dictionary with all the location data
    return locationsDictionary





# Class to define and organize the truck attributes
class Truck:
    def __init__(self, name, currentTime=datetime.strptime("08:00 AM", "%I:%M %p")):
        # Add a name for the truck
        self.name = name
        # Max capacity of the truck
        self.capacity = 16
        # List for storing packages
        self.packages = []
        # Miles start at 0 and update as the truck start driving
        self.miles = 0.0
        # Speed of the truck in MPH
        self.speed = 18
        # Each truck starts at the Hub
        self.currentLocation = "Hub"
        # Can set start time for each truck
        self.currentTime = currentTime
        # Initialize empty dictionary to store the package ID and statuses by the delivery time
        self.statusDictionary = {}


    # Method to load packages onto trucks by package ID
    def loadPackages(self, packageIDs, packageHashTable):
        # Iterate over the package IDs
        for packageID in packageIDs:
            # Search for the package with the ID
            package = packageHashTable.search(packageID)
            # If the package exists
            if package:
                # Assign the truck name to the package
                package.truck = self.name
                # Check if the packages list does not exceed truck capacity
                if len(self.packages) < self.capacity:
                    # Add package to the packages list
                    self.packages.append(package)
                else:
                    # Error handling to deal with overloading truck
                    print(f"\nThe {self.name} is at max capacity. Unable to load more than 16 packages for a truck\n")


    # Method to deliver packages and update package status
    def deliverPackages(self, locationsDictionary, packageHashTable):
        # Iterate over packages in the truck
        for package in self.packages:
            # Correct package '9' to the right address after 10:20 AM
            if package.packageID == 9:
                if self.currentTime >= datetime.strptime("10:20 AM", "%I:%M %p"):
                    package.address = "410 S State St"
                # Otherwise keep the original address
                else:
                    package.address = "300 State St"
            # Insert the updated values for package '9' in the hash table
            packageHashTable.insert(package.packageID, package)
            # Update the statuses of packages that are loaded on the truck
            package.statusUpdate("Package is currently en route")

        # Loop until the truck has no more packages
        while self.packages:
            # Get the nearest distance and the package from the delivery algorithm
            nearestDistance, nearestPackage = self.nearestLocation(locationsDictionary, packageHashTable)
            # If a package exists
            if nearestPackage:
                # Call another method to update the trucks attributes
                currentPackage = self.currentUpdate(nearestDistance, nearestPackage.address)
                # Update the package status and add the time it was delivered
                nearestPackage.statusUpdate(f"Package was delivered at {currentPackage}", currentPackage)
                # Remove the delivered package from the packages list
                self.packages.remove(nearestPackage)

                # Use the delivered package time as an outer key for the nested status dictionary
                deliveryTime = self.currentTime.strftime("%I:%M %p")
                # Initialize an empty dictionary for the inner dictionary
                packageStatus = {}
                # Iterate over all package IDS
                for packageID in range(1, 41):
                    status = packageHashTable.search(packageID).status
                    # Set the package ID as the inner key and its status as the inner value
                    packageStatus[packageID] = status
                # Create a nested dictionary (delivery time as outer key, package ID as inner key, status as inner value)
                self.statusDictionary[deliveryTime] = packageStatus
                # If there are no more packages end the loop
            else:
                break


    # Method using the nearest neighbor algorithm to calculate which package should be delivered next based on the distances
    def nearestLocation(self, locationsDictionary, packageHashTable):
        # Initialize nearest distance to project mile constraint
        nearestDistance = 140
        nearestPackage = None

        # Iterate over all packages in the truck
        for package in self.packages:
            if package.status == "Package is currently en route":
                # Calculate the distance from the package location and the truck location
                distance = locationsDictionary[self.currentLocation][package.address]
                # If the distance is less than the nearest distance
                if distance < nearestDistance:
                    # Set nearest distance to that distance value and nearest package to that package
                    nearestDistance = distance
                    nearestPackage = package
        # Return the nearest distance and package
        return nearestDistance, nearestPackage


    # Method to update the miles, location and time of the truck
    def currentUpdate(self, nearestDistance, newLocation):
        # Update the truck miles by adding the nearest distance
        self.miles += nearestDistance
        # Change the truck location to the nearest package location
        self.currentLocation = newLocation
        # Divide distance by speed to calculate the time taken in hours
        totalHours = nearestDistance / self.speed
        # Convert the hours to minutes and convert value to int for whole number results
        totalMinutes = int(totalHours * 60)
        # Update the trucks current time
        self.currentTime += timedelta(minutes=totalMinutes)
        # Return the time in a readable format
        return self.currentTime.strftime("%I:%M %p")


    # Method to manage the delivery process for the trucks
    def startDelivery(firstTruck, secondTruck, thirdTruck, locationsDictionary, packageHashTable):
        # Initialize the driving status for the first two trucks delivering packages as True
        firstTruckDriving = True
        secondTruckDriving = True

        # Loop keeps running until both trucks finish delivering all their packages to ensure completion
        while firstTruckDriving or secondTruckDriving:
            # Check if the first truck still has packages
            if firstTruck.packages:
                # Set the starting time as the current default time for delivery
                firstStart = firstTruck.currentTime.strftime('%I:%M %p')
                # Call another method to start delivering packages
                firstTruck.deliverPackages(locationsDictionary, packageHashTable)
                # Calculate the ending time by adding the time it takes to return to the Hub after the last package
                firstEnd = firstTruck.currentUpdate(locationsDictionary[firstTruck.currentLocation]["Hub"], "Hub")
                # Get the total miles driven by the first truck
                firstMiles = int(firstTruck.miles)
                # Change the first trucks driving status to False
                firstTruckDriving = False

            # Check if the second truck still has packages
            if secondTruck.packages:
                # Set the starting time as the current default time for delivery
                secondStart = secondTruck.currentTime.strftime('%I:%M %p')
                # Call another method to start delivering packages
                secondTruck.deliverPackages(locationsDictionary, packageHashTable)
                # Calculate the ending time by adding the time it takes to return to the Hub after the last package
                secondEnd = secondTruck.currentUpdate(locationsDictionary[secondTruck.currentLocation]["Hub"], "Hub")
                # Get the total miles driven by the second truck
                secondMiles = int(secondTruck.miles)
                # Change the second trucks driving status to False
                secondTruckDriving = False

        thirdTruck.currentTime = min(firstTruck.currentTime, secondTruck.currentTime)
        # Set the starting time as the current time for delivery
        thirdStart = thirdTruck.currentTime.strftime('%I:%M %p')
        # Call another method to start delivering packages
        thirdTruck.deliverPackages(locationsDictionary, packageHashTable)
        # Calculate the ending time by adding the time it takes to return to the Hub after the last package
        thirdEnd = thirdTruck.currentUpdate(locationsDictionary[thirdTruck.currentLocation]["Hub"], "Hub")
        # Get the total miles driven by the third truck
        thirdMiles = int(thirdTruck.miles)

        # Print the trucks stats information for the user interface
        print("Information for the start time, end time and miles driven for each truck:")
        print(f"The {firstTruck.name}: {firstStart}, {firstEnd}, {firstMiles} miles")
        print(f"The {secondTruck.name}: {secondStart}, {secondEnd}, {secondMiles} miles")
        print(f"The {thirdTruck.name}: {thirdStart}, {thirdEnd}, {thirdMiles} miles")

        # Calculate the total mileage from all three trucks combined
        totalMiles = int(firstTruck.miles + secondTruck.miles + thirdTruck.miles)
        # Print the total mileage
        print(f"The total mileage for all three trucks: {totalMiles} miles")






# Create a hash table object for storing package details
packageHashTable = HashTable()
# Load the package data from the CSV file into the package hash table
loadPackageData('src/Packages.csv', packageHashTable)
# Load the distance data from the CSV file into a nested dictionary
locationsDictionary = loadDistanceData('src/Distances.csv')

# Create instances of Truck for each delivery truck
firstTruck = Truck("first truck")
secondTruck = Truck("second truck", datetime.strptime("09:05 AM", "%I:%M %p"))
thirdTruck = Truck("third truck", datetime.strptime("10:30 AM", "%I:%M %p"))
# List of trucks to iterate through later
trucks = [firstTruck, secondTruck, thirdTruck]

# Create valid lists for the trucks to meet the package constraints and deadlines
firstPackageIDs = [1, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 29, 30, 31, 34, 37]
secondPackageIDs = [3, 6, 18, 25, 26, 28, 32, 35, 36, 38, 40]
thirdPackageIDs = [2, 4, 5, 7, 8, 9, 10, 11, 12, 17, 27, 33, 39]

# Call another method to load the packages into the trucks
firstTruck.loadPackages(firstPackageIDs, packageHashTable)
secondTruck.loadPackages(secondPackageIDs, packageHashTable)
thirdTruck.loadPackages(thirdPackageIDs, packageHashTable)

# Start the delivery for the trucks
Truck.startDelivery(firstTruck, secondTruck, thirdTruck, locationsDictionary, packageHashTable)






# The interface code for the user to interact with the program
while True:
    # Keep asking the user for input until they quit
    userInput = input("\nEnter a time (HH:MM AM/PM) to check the statuses of all packages or to check the status of a single package. Type 'q' to quit the program:\n")
    # If the user input is 'q'
    if userInput.lower() == 'q':
        # End the loop and program
        break

    try:
        # Convert users input to a datetime object with readable format
        userTime = datetime.strptime(userInput, "%I:%M %p")
        # Initialize the nearest time to None
        nearestTime = None
        # Create a new dictionary to hold the statuses of all the packages at the nearest delivery time
        packageTime = {}

        # Iterate over each truck
        for truck in trucks:
            # Sort the delivery times in the status dictionary and iterate over each delivery time
            for deliveryTime in (truck.statusDictionary.keys()):
                # If the delivery time is less than or equal to the users time
                if deliveryTime <= userTime.strftime("%I:%M %p"):
                    # Check if nearest time has been set yet or check if the delivery time is greater than the nearest time to get the closest valid time to user time
                    if nearestTime is None or deliveryTime > nearestTime:
                        #  If either is true, then set the nearest time to that delivery time
                        nearestTime = deliveryTime
                        # Update the dictionary to hold the package statuses at the nearest time
                        packageTime = truck.statusDictionary[nearestTime]

        # If there was no nearest time found
        if nearestTime is None:
            # Iterate over each truck
            for truck in trucks:
                # Find the latest delivery time for the truck
                latestTime = max(truck.statusDictionary.keys())
                # Check if the latest delivery time exists
                if latestTime:
                    # If it does, then set the nearest time to the latest time
                    nearestTime = latestTime
                    # Update the dictionary to hold the package statuses at the nearest time
                    packageTime = truck.statusDictionary[nearestTime]


        # Let the user decide between two options
        userOption = input(f"Type 'a' to show the statuses of all packages at {userTime.strftime('%I:%M %p')}:\nType 'b' to show the status of a single package at {userTime.strftime('%I:%M %p')}:\n")
        # If the user input is 'a'
        if userOption.lower() == 'a':
            print(f"\nPackage information at {userTime.strftime('%I:%M %p')}:\n")
            # Iterate through every key-value pair from the nested dictionary using the nearest time outer key and print them
            for packageID in range(1, 41):
                package = packageHashTable.search(packageID)
                # If package ID is 9
                if packageID == 9:
                    # Check if time is 10:20 AM or later
                    if userTime >= datetime.strptime("10:20 AM", "%I:%M %p"):
                        # Correct the address
                        package.address = "410 S State St"
                        # Otherwise keep the current address
                    else:
                        package.address = "300 State St"


                packageStatus = packageTime.get(packageID)
                if package:
                    print(f"ID - {packageID}; Status - {packageStatus}; Address - {package.address}; Deadline - {package.deadline}; Truck - {package.truck}")



        # If the user input is 'b'
        elif userOption.lower() == 'b':
            # Keep asking the user for input until they quit
            while True:
                userPackage = input(f"Enter the package ID (1-40) you want to see. Type 'g' to go back:\n")
                # If the user input is 'g'
                if userPackage.lower() == 'g':
                    # End the inner loop and go back to the main program
                    break

                try:
                    # Convert value of the user input to an int
                    packageID = int(userPackage)

                    # Check if the user input is within the package ID range
                    if packageID in range(1, 41):
                        # If it is, then search for the package ID in the hash table
                        package = packageHashTable.search(packageID)
                        # Variable to hold the status of that package ID
                        userPackageStatus = packageTime.get(packageID)
                        # Print the package ID and the package status
                        if package:
                            print(f"ID - {packageID}; Status - {userPackageStatus}; Address - {package.address}; Deadline - {package.deadline}; Truck - {package.truck}")
                    else:
                        # Error handling to deal with numbers that are out of range
                        print("Please enter a number between 1 and 40.\n")
                # Error handling to deal with invalid input
                except ValueError:
                    print("Please enter a numeric value.\n")

    # Error handling to deal with invalid input
    except ValueError:
        print("Please enter the time in HH:MM AM/PM format. (Try something like '10:30 AM' or '12:00 PM')")













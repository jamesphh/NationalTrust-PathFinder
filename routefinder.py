import json
import time
from itertools import permutations
from math import radians, sin, asin, cos, sqrt
from geopy.geocoders import Nominatim


class RouteFinder:

    def __init__(self, activity, post_code, radius):
        self.activity = activity
        self.post_code = post_code
        self.radius = radius
        with open('ntdata.json') as json_data:
            self.data = json.load(json_data)

    def location(self, post_code):
        # Finds latitude and longitude of postcode
        loc = Nominatim(user_agent="GetLoc")
        getLoc = loc.geocode(post_code)
        return getLoc.latitude, getLoc.longitude

    def haversine(self, lat1, lon1, lat2, lon2):
        # Finds great-circle distance between two points
        # Uses map to convert latitudes and longitudes into radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of the earth in km
        r = 6371
        # Rounds answer to 2 decimal places
        return round(c * r, 2)

    def parameters(self, activity, post_code, radius):
        # Get the latitude and longitude of the given postcode
        lat, lon = self.location(post_code)

        # Create the filter_by_activity list of location IDs that have the given activity
        filter_by_activity = [
            id for id in self.data if activity in [
                tag.strip()
                for tag in self.data[id].get("activityTagsAsCsv", "").split(",")
            ]
        ]

        # Create the final_list of location IDs that are within the given radius of the given postcode
        final_list = [
            id for id in filter_by_activity
            if self.haversine(lat, lon, self.data[id]["location"]["latitude"],
                              self.data[id]["location"]["longitude"]) <= radius]

        # Create a dictionary for the starting location (the postcode)
        user_node_start = {"id": "start", "lat": lat, "lon": lon}
        # Create a dictionary for the ending location (also the postcode)
        user_node_end = {"id": "end", "lat": lat, "lon": lon}

        # Create a list of dictionaries that represent locations
        dictionaries = []
        # Add the dictionary for the starting location to the list
        dictionaries.append(user_node_start)

        # Iterate through the final_list of location IDs
        for id in final_list:
            # Get the current location dictionary from the data dictionary
            curr = self.data[id]
            # Get the object dictionary from the location dictionary
            object = curr["location"]
            # Create a dictionary for the current location with the ID, latitude, and longitude
            curr_dict = {
                "id": id,
                "lat": object["latitude"],
                "lon": object["longitude"]
            }

            dictionaries.append(curr_dict)

        dictionaries.append(user_node_end)

        return dictionaries

    # Returns 2D array of distances from each location to every other location
    def distances(self, array):
        size = len(array)
        # Create a square matrix of size n x n, where n is the length of the input array,
        # filled with zeros to store the distances between each pair of locations
        matrix = [[0] * size for _ in range(size)]
        # Iterate over each pair of nodes in the input array using nested for loops
        for i, node1 in enumerate(array):
            for j, node2 in enumerate(array):
                # If the nodes are not the same, calculate the Haversine distance between them
                if i != j:
                    dist = self.haversine(node1["lat"], node1["lon"], node2["lat"], node2["lon"])
                    # Store the resulting distance in the corresponding entry of the matrix
                    matrix[i][j] = dist
        # Return the matrix of distances
        return matrix

    # Generates every permutation of IDs
    def genPerms(self, dictionary):
        # Creates a list of all indices except the first and last
        indicies = []
        length = len(dictionary)
        for index in range(length - 2):
            indicies.append(index + 2)

        # Generates all possible permutations of the indices list
        perms = list(permutations(indicies))
        permsFinal = []

        # For each permutation tuple, create a new list with the first and last indices of the dictionary and the remaining indices in the order specified by the permutation tuple
        for tup in perms:
            newArr = [1]
            arr = list(tup)
            for ind in arr:
                newArr.append(ind)
            newArr.append(length)
            permsFinal.append(newArr)

        return permsFinal

    # Checks the distance of every permutation and returns the shortest path
    def bruteforce(self, distances, perms):
        # Initialize variables for tracking the shortest path and its corresponding permutation
        shortest = float("inf")
        shortest_permutation = None

        # Iterate over each permutation in the input list
        for perm in perms:
            # initialize the distance counter for this permutation
            distance_total = 0

            # Calculate the total distance for the path represented by this permutation
            for i in range(len(perm) - 1):
                node = perm[i] - 1
                next_node = perm[i + 1] - 1
                distance_total += distances[node][next_node]

                # If the current distance exceeds the current shortest path, stop calculating this path
                if distance_total > shortest:
                    break

            # If this path is shorter than the current shortest path, update the shortest path and permutation
            if distance_total < shortest:
                shortest = distance_total
                shortest_permutation = perm

        # Return the shortest path and the permutation that achieved it
        return shortest, shortest_permutation

    # Nearest neighbour algorithm for when there are more than 10 locations
    def nearest_neighbour(self, dictionary):
        # Initialize variables for tracking unvisited nodes, the current node, and the path taken so far
        unvisited = set(range(1, len(dictionary)))
        current_node = 0
        path = [0]

        # While there are still unvisited nodes, find the nearest unvisited node and add it to the path
        while unvisited:
            # Calculate distances between the current node and all unvisited nodes
            distances = [
                self.haversine(dictionary[current_node]["lat"], dictionary[current_node]["lon"], dictionary[i]["lat"],
                               dictionary[i]["lon"]) for i in unvisited]
            # Find the nearest unvisited node and set it as the new current node
            nearest_node = min(range(len(distances)), key=distances.__getitem__)
            current_node = list(unvisited)[nearest_node]
            # Remove the new current node from the list of unvisited nodes and add it to the path
            unvisited.remove(current_node)
            path.append(current_node)

        # Add the starting node to the end of the path to complete the loop
        path.append(0)

        # Calculate the total distance of the path found by the algorithm
        shortest = sum([self.haversine(dictionary[path[i]]["lat"], dictionary[path[i]]["lon"],
                                       dictionary[path[i + 1]]["lat"], dictionary[path[i + 1]]["lon"]) for i in
                        range(len(path) - 1)])

        # Return the shortest distance found and the path taken
        return shortest, path

    # Displays user friendly output from tsp algorithm
    def unpack(self, shortest, path, dictionary, time):
        # Create array of visited location IDs, skipping start and end nodes
        id_arr = [
            dictionary[i - 1]["id"] for i in path[1:-1]
            if i != 1 and i != len(dictionary)
        ]

        # Create array to hold output strings
        returned_array = []
        returned_array.append("Start")

        # Add location names to output array
        for id in id_arr:
            curr = self.data[id]
            returned_array.append(curr["title"])

        # Add end and summary information to output array
        returned_array.append("End")
        returned_array.append(f"Total distance: {shortest:.2f} km")
        returned_array.append(f"<br>Route found in {time:.3f} seconds.")

        # Combine output array into single string, separated by <br> tags
        returned = "<br>".join(returned_array)

        return returned

    # combines all the functions
    def solve(self):
        # Take the time when the program starts
        time1 = time.time()

        # Get the user input and prepare the data
        dictionary = self.parameters(self.activity, self.post_code, self.radius)

        # Check if there are more than 10 locations
        if len(dictionary) > 10:
            # Use the Nearest Neighbor Algorithm to find a near-optimal solution
            shortest, path = self.nearest_neighbour(dictionary)
            # Subtracts the starting time from the now current time to find the difference
            total_time = time.time() - time1
            return self.unpack(shortest, path, dictionary, total_time)
        # If there are less than 10 locations
        else:
            # Use the brute force method to solve the TSP problem
            distancesArr = self.distances(dictionary)
            perms = self.genPerms(dictionary)
            shortest, path = self.bruteforce(distancesArr, perms)
            # Subtracts the starting time from the now current time to find the difference
            total_time = time.time() - time1
            return self.unpack(shortest, path, dictionary, total_time)

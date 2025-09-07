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
        self._geocode_cache = {}
        with open('ntdata.json') as json_data:
            self.data = json.load(json_data)

    def location(self, post_code):
        if post_code in self._geocode_cache:
            return self._geocode_cache[post_code]
        loc = Nominatim(user_agent="GetLoc").geocode(post_code)
        coords = (loc.latitude, loc.longitude)
        self._geocode_cache[post_code] = coords
        return coords

    def haversine(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371
        return round(c * r, 2)

    def parameters(self, activity, post_code, radius):
        lat, lon = self.location(post_code)
        filter_by_activity = [
            id for id in self.data
            if activity in [tag.strip() for tag in self.data[id].get("activityTagsAsCsv", "").split(",")]
        ]
        final_list = [
            id for id in filter_by_activity
            if self.haversine(lat, lon, self.data[id]["location"]["latitude"],
                              self.data[id]["location"]["longitude"]) <= radius
        ]
        dictionaries = [{"id": "start", "lat": lat, "lon": lon}]
        for id in final_list:
            obj = self.data[id]["location"]
            dictionaries.append({"id": id, "lat": obj["latitude"], "lon": obj["longitude"]})
        dictionaries.append({"id": "end", "lat": lat, "lon": lon})
        return dictionaries

    def distances(self, array):
        size = len(array)
        matrix = [[0] * size for _ in range(size)]
        for i, node1 in enumerate(array):
            for j, node2 in enumerate(array):
                if i != j:
                    matrix[i][j] = self.haversine(node1["lat"], node1["lon"], node2["lat"], node2["lon"])
        return matrix

    def genPerms(self, dictionary):
        n = len(dictionary)
        middle_indices = list(range(1, n - 1))
        return [[0] + list(p) + [n - 1] for p in permutations(middle_indices)]

    def bruteforce(self, distances, perms):
        shortest = float("inf")
        best_path = None
        for perm in perms:
            dist = 0
            for i in range(len(perm) - 1):
                dist += distances[perm[i]][perm[i + 1]]
                if dist > shortest:
                    break
            if dist < shortest:
                shortest, best_path = dist, perm
        return shortest, best_path

    def nearest_neighbour(self, dictionary):
        n = len(dictionary)
        unvisited = set(range(1, n))
        current = 0
        path = [0]
        while unvisited:
            nearest = min(
                unvisited,
                key=lambda i: self.haversine(dictionary[current]["lat"], dictionary[current]["lon"],
                                             dictionary[i]["lat"], dictionary[i]["lon"])
            )
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        if path[-1] != n - 1:
            path.append(n - 1)
        total_dist = self.path_distance(path, dictionary)
        return total_dist, path

    def two_opt(self, path, dictionary):
        improved = True
        best_path = path
        best_dist = self.path_distance(best_path, dictionary)
        while improved:
            improved = False
            for i in range(1, len(best_path) - 2):
                for j in range(i + 1, len(best_path) - 1):
                    if j - i == 1:
                        continue
                    new_path = best_path[:]
                    new_path[i:j] = reversed(new_path[i:j])
                    new_dist = self.path_distance(new_path, dictionary)
                    if new_dist < best_dist:
                        best_path, best_dist = new_path, new_dist
                        improved = True
        return best_dist, best_path

    def path_distance(self, path, dictionary):
        return sum(
            self.haversine(dictionary[path[i]]["lat"], dictionary[path[i]]["lon"],
                           dictionary[path[i + 1]]["lat"], dictionary[path[i + 1]]["lon"])
            for i in range(len(path) - 1)
        )

    def unpack(self, shortest, path, dictionary, elapsed):
        id_arr = [dictionary[i]["id"] for i in path if i not in (0, len(dictionary) - 1)]
        output = ["Start"]
        for id in id_arr:
            if id in self.data:
                output.append(self.data[id]["title"])
        output.append("End")
        output.append(f"Total distance: {shortest:.2f} km")
        output.append(f"<br>Route found in {elapsed:.3f} seconds.")
        return "<br>".join(output), {"distance": shortest, "path": [dictionary[i]["id"] for i in path]}

    def solve(self):
        t0 = time.time()
        dictionary = self.parameters(self.activity, self.post_code, self.radius)
        if len(dictionary) > 10:
            shortest, path = self.nearest_neighbour(dictionary)
            shortest, path = self.two_opt(path, dictionary)
        else:
            distancesArr = self.distances(dictionary)
            perms = self.genPerms(dictionary)
            shortest, path = self.bruteforce(distancesArr, perms)
        elapsed = time.time() - t0
        return self.unpack(shortest, path, dictionary, elapsed)

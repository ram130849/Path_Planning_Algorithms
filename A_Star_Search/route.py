#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: Sai Charan Reddy Maram-saimaram, Siddhant Patil-sidpatil, Ramki Ramamurthy-ramrama
#
# Based on skeleton code by V. Mathur and D. Crandall, Fall 2022
#


# !/usr/bin/env python3
from queue import PriorityQueue
import sys
import math

# References:
'''
https://www.engati.com/glossary/admissible-heuristic
https://artint.info/2e/html/ArtInt2e.Ch3.S6.SS2.html
https://en.wikipedia.org/wiki/Great-circle_distance
https://www.igismap.com/haversine-formula-calculate-geographic-distance-earth/
'''

# Parsing the nodes and edges of the graph.


def load_graph():
    f = open("city-gps.txt", "r")
    nodes = {}
    for line in f.read().rstrip("\n").split("\n"):
        city = line.split(" ")[0]
        latitude = line.split(" ")[1]
        longtitude = line.split(" ")[2]
        nodes[city] = (latitude, longtitude)

    f.close()
    g = open('road-segments.txt', "r")
    edges = {}
    max_speed_limit = 0
    max_length = 0
    for edge in g.read().rstrip("\n").split("\n"):
        start_city = edge.split(" ")[0]
        end_city = edge.split(" ")[1]
        length = float(edge.split(" ")[2])
        speed_limit = None
        highway = None
        if(len(edge.split(" ")) == 5 and float(edge.split(" ")[3]) > 0):
            speed_limit = float(edge.split(" ")[3])
            highway = edge.split(" ")[4]
        else:
            speed_limit = 40
            highway = edge.split(" ")[3]
        max_length = max(max_length, length)
        max_speed_limit = max(max_speed_limit, speed_limit)
        if(edges.get(start_city, False) == False):
            edges[start_city] = {}
        if(edges[start_city].get(end_city, False) == False):
            edges[start_city][end_city] = [length, speed_limit, highway]
        if(edges.get(end_city, False) == False):
            edges[end_city] = {}
        if(edges[end_city].get(start_city, False) == False):
            edges[end_city][start_city] = [length, speed_limit, highway]
    g.close()
    return nodes, edges, max_length, max_speed_limit

# Get minimum among the latitude and longtitude of the neighbouring nodes and setting it as the coordinates
# of the current city.


def get_min_lat_long(start_city_name, target_city_name, nodes, edges):
    min_hs = float('inf')
    (min_latitude, min_longtitude) = (float("inf"), float("inf"))
    target_lat, target_long = nodes[target_city_name]
    for neighbors in edges[start_city_name]:
        if(neighbors in nodes):
            neighbor_lat, neighbor_long = nodes[neighbors]
            diff_lat = (float(neighbor_lat)-float(target_lat)) * math.pi / 180
            diff_long = (float(neighbor_long) -
                         float(target_long)) * math.pi / 180
            dist = (math.sin(diff_lat / 2) ** 2
                    + math.cos(float(target_lat) * math.pi / 180.0)
                    * math.cos(float(neighbor_lat) * math.pi / 180.0)
                    * math.sin(diff_long / 2) ** 2)
            haversine_distance = float(
                3961*2*math.atan2(math.sqrt(dist), math.sqrt(1-dist)))
            min_hs = min(min_hs, haversine_distance)
            if(min_hs == haversine_distance):
                min_latitude, min_longtitude = neighbor_lat, neighbor_long
    if(min_latitude == float("inf")):
        min_latitude = 0
    if(min_longtitude == float("inf")):
        min_longtitude = 0
    return (min_latitude, min_longtitude)

# Calculate the haverstine distance,time between current city and target city as the heuristic


def heuristic_function(next_city, end_city, cost, nodes, edges, max_speed_limit):
    hs = 0
    if cost == 'distance' or cost == 'time' or cost == 'delivery':
        if end_city not in nodes:
            end_city_lat, end_city_long = get_min_lat_long(
                end_city, next_city, nodes, edges)
            if(end_city_lat == 0 and end_city_long == 0):
                return 0
        else:
            end_city_lat, end_city_long = nodes[end_city]
        if next_city not in nodes:
            next_city_lat, next_city_long = get_min_lat_long(
                next_city, end_city, nodes, edges)
            if(next_city_lat == 0 and next_city_long == 0):
                return 0
        else:
            next_city_lat, next_city_long = nodes[next_city]
        diff_lat = (float(next_city_lat)-float(end_city_lat)) * math.pi / 180
        diff_long = (float(next_city_long) -
                     float(end_city_long)) * math.pi / 180
        dist = (math.sin(diff_lat / 2) ** 2
                + math.cos(float(end_city_lat) * math.pi / 180.0)
                * math.cos(float(next_city_lat) * math.pi / 180.0)
                * math.sin(diff_long / 2) ** 2)
        # Haversine distance formula.
        haversine_distance = float(
            3961*2*math.atan2(math.sqrt(dist), math.sqrt(1-dist)))
        hs = haversine_distance
        if(cost == 'distance'):
            return hs
        if(cost == 'time' or cost == 'delivery'):
            time = float(hs/max_speed_limit)
            return time
    return hs
# Update the shortest path to be traversed.


def get_path(curr_path, neighbors, highway, length):
    path = curr_path.copy()
    path.append(("{0}".format(neighbors),
                "{0} for {1} miles".format(highway, length)))
    return path
# neighboring nodes for the current city to be traversed for the successor function.


def successors(city, edges):
    return edges[city].items()

# Main Function to calculate the total cost and processing the shortest route to be traversed based on the
# cost function given.


def get_route(start, end, cost):
    """
    Find shortest driving route between start city and end city
    based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken 
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-delivery-hours": a float indicating the expected (average) time it will take a delivery driver who may need to return to get a new package
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    if(start == end):
        print("Please Input Different Cities.")
    nodes, edges, max_speed_limit, _ = load_graph()
    fringe = PriorityQueue() if(cost != 'segments') else []
    visited = set()
    if(cost != 'segments'):
        fringe.put((0, (start, [], 0, 0, 0)))
        while(fringe.empty() == False):
            (_, output) = fringe.get()
            # current city for which successor states should be traversed.
            curr_city = output[0]
            path = output[1]  # Calculate the path traversed.
            curr_dist = output[2]  # Total Distance travelled so far.
            curr_hrs = output[3]  # Total Time for the journey so far.
            # Total delivery time for the journey so far.
            curr_delivery_hrs = output[4]
            if(curr_city != end):
                for neighbors, edge_attr in successors(curr_city, edges):
                    if(neighbors not in visited):
                        time = int(edge_attr[0])/int(edge_attr[1])
                        t_road = float(int(edge_attr[0])/int(edge_attr[1]))
                        if(edge_attr[1] >= 50):
                            probability = float(
                                math.tanh(int(edge_attr[0])/1000))
                            delivery_hours = float(
                                t_road + 2*probability*(t_road+curr_delivery_hrs))
                        else:
                            delivery_hours = t_road
                        heuristic_func = heuristic_function(
                            neighbors, end, cost, nodes, edges, max_speed_limit)
                        if(cost == 'distance'):  # distance as cost function
                            fringe.put((float(curr_dist+int(edge_attr[0]))+heuristic_func, (neighbors, get_path(path, neighbors, edge_attr[2], edge_attr[0]), float(curr_dist+int(edge_attr[0])),
                                                                                            curr_hrs+time, curr_delivery_hrs+delivery_hours)))
                        elif(cost == 'time'):  # time as cost function
                            fringe.put((curr_hrs+time+heuristic_func, (neighbors, get_path(path, neighbors, edge_attr[2], edge_attr[0]), float(curr_dist+int(edge_attr[0])),
                                                                       curr_hrs+time, curr_delivery_hrs+delivery_hours)))
                        else:  # delivery time as cost function
                            fringe.put((curr_delivery_hrs+delivery_hours+heuristic_func, (neighbors, get_path(path, neighbors, edge_attr[2], edge_attr[0]), float(curr_dist+int(edge_attr[0])),
                                                                                          curr_hrs+time, curr_delivery_hrs+delivery_hours)))
                        visited.add(neighbors)
            else:
                return {
                    "total-segments": len(path),
                    "total-miles": curr_dist,
                    "total-hours": curr_hrs,
                    "total-delivery-hours": curr_delivery_hrs,
                    "route-taken": path
                }
    else:
        fringe.append((start, [], 0, 0, 0))
        while(fringe):
            output = fringe.pop(0)
            # current city for which successor states should be traversed.
            curr_city = output[0]
            path = output[1]  # Calculate the path traversed.
            curr_dist = output[2]  # Total Distance travelled so far.
            curr_hrs = output[3]  # Total Time for the journey so far.
            # Total delivery time for the journey so far.
            curr_delivery_hrs = output[4]
            if(curr_city != end):
                for neighbors, edge_attr in successors(curr_city, edges):
                    if(neighbors not in visited):
                        if int(edge_attr[1]) >= 50:
                            p = float(math.tanh(int(edge_attr[0]) / 1000))
                            t_road = float(
                                int(edge_attr[0]) / int(edge_attr[1]))
                            delivery_hours = float(
                                t_road + p * 2 * (t_road + curr_hrs))
                        else:
                            delivery_hours = float(
                                int(edge_attr[0]) / int(edge_attr[1]))

                        fringe.append(
                            (neighbors, get_path(path, neighbors, edge_attr[2], edge_attr[0]), float(curr_dist + int(edge_attr[0])),
                             curr_hrs + int(edge_attr[0]) / int(edge_attr[1]),
                             curr_delivery_hrs + delivery_hours))
                        visited.add(neighbors)
            else:
                return {
                    "total-segments": len(path),
                    "total-miles": curr_dist,
                    "total-hours": curr_hrs,
                    "total-delivery-hours": curr_delivery_hrs,
                    "route-taken": path
                }

    return {
        "total-segments": 0,
        "total-miles": 0,
        "total-hours": 0,
        "total-delivery-hours": 0,
        "route-taken": []
    }


# Please don't modify anything below this line
#
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    # print(result["route-taken"])
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])

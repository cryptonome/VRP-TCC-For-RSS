from __future__ import print_function
from six.moves import xrange
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
import csv

###########################
# Problem Data Definition #
###########################
def create_data_model():

    class AutoVivification(dict):
        """Implementation of perl's autovivification feature."""

        def __getitem__(self, item):
            try:
                return dict.__getitem__(self, item)
            except KeyError:
                value = self[item] = type(self)()
                return value

    data = AutoVivification()
    filename = 'Route_Distances2.csv'
    with open(filename, 'r+') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)  # skip the header
        for row in reader:
            data[row[1]][row[4]] = row[5]

        """Stores the data for the problem"""

        data["locations"] = [(l[0] * 1, l[1] * 1) for l in _locations]
        data["num_locations"] = len(data["locations"])
        data["num_vehicles"] = 4
        data["depot"] = 0



    """Stores the data for the problem"""
        data = {}
    # Locations in block units
  _locations = \
          [(4, 4), # depot
           (2, 0), (8, 0), # locations to visit
           (0, 1), (1, 1),
           (5, 2), (7, 2),
           (3, 3), (6, 3),
           (5, 5), (8, 5),
           (1, 6), (2, 6),
           (3, 7), (6, 7),
           (0, 8), (7, 8)]



        for row in reader:
            x = row[3]
            y = row[2]
            demands = row[4]
  capacities = [15, 15, 15, 15]

#######################
# Problem Constraints #
#######################
def manhattan_distance(position_1, position_2):
  """Computes the Manhattan distance between two points"""
  return (
      abs(position_1[0] - position_2[0]) + abs(position_1[1] - position_2[1]))
def create_distance_callback(data):
  """Creates callback to return distance between points."""
  _distances = {}

  for from_node in xrange(data["num_locations"]):
    _distances[from_node] = {}
    for to_node in xrange(data["num_locations"]):
      if from_node == to_node:
        _distances[from_node][to_node] = 0
      else:
        _distances[from_node][to_node] = (
            manhattan_distance(data["locations"][from_node],
                               data["locations"][to_node]))

  def distance_callback(from_node, to_node):
    """Returns the manhattan distance between the two nodes"""
    return _distances[from_node][to_node]

  return distance_callback

def create_demand_callback(data):
    """Creates callback to get demands at each location."""
    def demand_callback(from_node, to_node):
        return data["demands"][from_node]
    return demand_callback

def add_capacity_constraints(routing, data, demand_callback):
    """Adds capacity constraint"""
    capacity = "Capacity"
    routing.AddDimensionWithVehicleCapacity(
        demand_callback,
        0, # null capacity slack
        data["vehicle_capacities"], # vehicle maximum capacities
        True, # start cumul to zero
        capacity)
###########
# Printer #
###########
def print_solution(data, routing, assignment):
    """Print routes on console."""
    total_dist = 0
    for vehicle_id in xrange(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {0}:\n'.format(vehicle_id)
        route_dist = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = routing.IndexToNode(index)
            next_node_index = routing.IndexToNode(assignment.Value(routing.NextVar(index)))
            route_dist += manhattan_distance(
                data["locations"][node_index],
                data["locations"][next_node_index])
            route_load += data["demands"][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            index = assignment.Value(routing.NextVar(index))

        node_index = routing.IndexToNode(index)
        total_dist += route_dist
        plan_output += ' {0} Load({1})\n'.format(node_index, route_load)
        plan_output += 'Distance of the route: {0}m\n'.format(route_dist)
        plan_output += 'Load of the route: {0}\n'.format(route_load)
        print(plan_output)
    print('Total Distance of all routes: {0}m'.format(total_dist))
########
# Main #
########
def main():
  """Entry point of the program"""
  # Instantiate the data problem.
  data = create_data_model()
  # Create Routing Model
  routing = pywrapcp.RoutingModel(
      data["num_locations"],
      data["num_vehicles"],
      data["depot"])
  # Define weight of each edge
  distance_callback = create_distance_callback(data)
  routing.SetArcCostEvaluatorOfAllVehicles(distance_callback)
# Add Capacity constraint
  demand_callback = create_demand_callback(data)
  add_capacity_constraints(routing, data, demand_callback)
  # Setting first solution heuristic (cheapest addition).
  search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
  search_parameters.first_solution_strategy = (
      routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
  # Solve the problem.
  assignment = routing.SolveWithParameters(search_parameters)
  print_solution(data, routing, assignment)
if __name__ == '__main__':
  main()
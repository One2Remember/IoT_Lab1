import sys

sys.path.append('./**/IoT_Lab1/picar_4wd/')
import picar_4wd as fc
from my_utils import *  # my utility methods
from constants import *  # my constant values
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# track environment as 300x290 np array using the following encoding scheme:
# 0: clear 
# 1: obstacle 
# 2: car
# And where each square unit represents one centimeter squared
global environment

# tracks the car's heading, where car starts at heading 0, which points towards
# positive y  
global car_heading

# tracks the car's location (specifically the center of the ultrasonic sensor). 
# The car starts at (149,25), representing the car with the spoilers pressed 
# against the bottom of the map, in the center, and 25 being the y position of 
# the ultrasonic sensor
global car_location

# the set of angles we wish to cycle through in scan_180
global ANGLES
ANGLES = np.arange(-75, 76, 15)

# the destination cell
global DESTINATION
DESTINATION = np.array([ROOM_WIDTH_CM * 3 // 4, ROOM_HEIGHT_CM * 9 // 10])

# whether there is a stop sign in view
global stop_sign

# whether there is a pedestrian in view
global pedestrian

# update environment by redrawing the car's current position based on
# car_heading and car_location
def update_car_position_in_environment():
    global environment, car_location

    # reset the car's position so no car in environment
    environment[environment == 2] = 0

    # set car's new position in environment (as point)
    set_neighborhood_around_point(car_location[0], car_location[1], 2)

    return


# initialize environment as empty room (walls as obstacles)
def init_environment():
    # import globs
    global environment, car_heading, car_location, ROOM_HEIGHT_CM
    global ROOM_WIDTH_CM, CAR_HEIGHT_CM, DESTINATION, stop_sign, pedestrian
    
    # assume no stop sign or pedestrian 
    stop_sign = False 
    pedestrian = False 

    # init environment with all zeros
    environment = np.zeros((ROOM_HEIGHT_CM, ROOM_WIDTH_CM))
    # set 4 walls as being obstacles 
    environment[0] = np.ones(ROOM_WIDTH_CM)
    environment[-1] = np.ones(ROOM_WIDTH_CM)
    environment[:, 0] = np.ones(ROOM_HEIGHT_CM)
    environment[:, -1] = np.ones(ROOM_HEIGHT_CM)

    # set car initial heading to 0
    car_heading = 0
    # set car initial location to top of grid, middle position
    car_location = np.array([ROOM_WIDTH_CM // 2, CAR_HEIGHT_CM])
    # set car's initial location
    update_car_position_in_environment()

    # set the destination to a point near the opposite side of the room, and
    # about 3/4 of the way to the right
    set_neighborhood_around_point(DESTINATION[0], DESTINATION[1], 3)

    return


# print the environment with rows reversed to match cartesian coordinates
def print_environment_to_file(file_name_no_type):
    global environment

    reversed_environment = np.flip(environment, axis=0)

    plt.imshow(reversed_environment, interpolation='none')
    plt.savefig(file_name_no_type + ".png")

    return


# neatly print sensor readings
def print_readings(readings):
    print("Readings:")
    for reading in readings:
        if reading >= INF - 1:
            print("INF", end=' ')
        else:
            print(reading, end=' ')
    print()


# update environment using the readings from a 180 deg scan from the US sensor
# along with interpolation
def update_environment(readings, angles=ANGLES):
    global environment, car_heading, car_location
    global ANGLES, ROOM_HEIGHT_CM, ROOM_WIDTH_CM, FUZZ_FACTOR, INTERPOLATION_THRESHOLD

    # get true angle measurements of each sensor reading in range (0,359)
    true_angles_radians = np.radians((angles + 90 + car_heading) % 360)

    # convert sensor readings to coordinate locations assuming car is at the
    # origin (0,0)
    centered_coords = polar_to_cartesian(readings, true_angles_radians)

    # convert coordinates to actual obstacle locations with knowledge of car's
    # true location
    true_coords = np.add(centered_coords, car_location)

    # now, use interpolation to fill in any obstacles (ignoring edge readings)
    for i in range(1,true_coords[:, 0].size - 1):
        x_0, y_0 = int(round(true_coords[i][0])), int(round(true_coords[i][1]))
        x_1, y_1 = int(round(true_coords[i + 1][0])), int(round(true_coords[i + 1][1]))

        # if x_0 is not to the left of x_1, swap the two points
        if x_0 > x_1:
            x_0, y_0, x_1, y_1 = x_1, y_1, x_0, y_0

        # interpolate the points between the two if both are valid and close
        # enough together
        if (x_1 != x_0
                and coord_in_bounds(true_coords[i-1])
                and coord_in_bounds(true_coords[i])
                and coord_in_bounds(true_coords[i+1])
                and abs(readings[i] - readings[i+1]) <= INTERPOLATION_THRESHOLD
                and abs(readings[i-1] - readings[i] <= INTERPOLATION_THRESHOLD)):
            m = (y_1 - y_0) / (x_1 - x_0)
            b = y_0 - m * x_0
            # interpolate the points between them as well
            for x in range(x_0 + 1, x_1, FUZZ_FACTOR):
                y = m * x + b
                set_neighborhood_around_point(x, y)
    return


# set the neighborhood of points around an obstacle as also being obstacles
def set_neighborhood_around_point(x, y, character=1):
    global environment, FUZZ_FACTOR, ROOM_HEIGHT_CM, ROOM_WIDTH_CM
    round_x, round_y = round(x), round(y)

    x_s = np.arange(round_x - FUZZ_FACTOR, round_x + FUZZ_FACTOR + 1, dtype=np.int32)
    y_s = np.arange(round_y - FUZZ_FACTOR, round_y + FUZZ_FACTOR + 1, dtype=np.int32)

    selected_x_s = x_s[(x_s >= 0) & (x_s < ROOM_WIDTH_CM)]
    selected_y_s = y_s[(y_s >= 0) & (y_s < ROOM_HEIGHT_CM)]

    points = np.array(np.meshgrid(selected_x_s, selected_y_s)).T.reshape(-1, 2)

    environment[points[:, 1], points[:, 0]] = character


# return whether a coordinate pair (y,x) is in room bounds    
def coord_in_bounds(coord):
    global ROOM_HEIGHT_CM, ROOM_WIDTH_CM

    return 0 <= coord[0] < ROOM_HEIGHT_CM and 0 <= coord[1] < ROOM_WIDTH_CM


# perform a 150 degree scan from the current location and heading
# return np array of all readings at 15 degree intervals from -90 to 90
# NOTE: if the distance is beyond our obstacle threshold, we simply say it is 
# infinity
def scan_angles(angles=ANGLES):
    global ANGLES, OBSTACLE_THRESHOLD, INF, MIN_OBSTACLE_THRESHOLD, SERVO_BIAS

    angles = angles - SERVO_BIAS  # correct for servo bias

    readings = np.empty(len(angles))
    i = 0
    for angle in angles:
        distance = fc.get_distance_at(angle)
        readings[i] = distance if MIN_OBSTACLE_THRESHOLD <= distance <= OBSTACLE_THRESHOLD else INF
        delay(100)
        i += 1

    servo.set_angle(0)

    return readings

# parses the environment and returns a downsized version     
def downsize_environment():
    global environment, DOWNSIZED_ENV_SIDE_LENGTH
    downsized_environment = environment.reshape(DOWNSIZED_ENV_SIDE_LENGTH, environment.shape[0]//DOWNSIZED_ENV_SIDE_LENGTH,DOWNSIZED_ENV_SIDE_LENGTH,environment.shape[1]//DOWNSIZED_ENV_SIDE_LENGTH).sum(axis=1).sum(axis=2)

    for i in range(downsized_environment.shape[0]):
        for j in range(downsized_environment.shape[1]):
            downsized_environment[i,j] = 1 if downsized_environment[i,j] > 0 else 0

    return downsized_environment
    
# construct an adjacency matrix from our downsized, 30x30 environment
def construct_adjacency_matrix(downsized_environment):
    r,c = downsized_environment.shape
    adjacency_matrix = np.ones((r*c, r*c))
    for a in range(r*c):
        for b in range(a,r*c):
            x_1, y_1 = adjacency_position_to_downsized_coordinates(a)
            x_2, y_2 = adjacency_position_to_downsized_coordinates(b)
            if (x_1, y_1) != (x_2, y_2):
                points = generate_line_points((x_1, y_1), (x_2, y_2))
                for point in points:
                    if downsized_environment[point[1]][point[0]] == 1:
                        adjacency_matrix[a][b] = 0
                        adjacency_matrix[b][a] = 0
                        break
    return adjacency_matrix


# generate the closest set of integer points that lie between these two
# coordinates
# uses a python implementation of Bresenham's Line Algorithm as described in
# the wikipedia page: https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
# and built upon an adapted then modified version of a C++
# implementation for this algorithm given by stackoverflow user dogear at:
# https://stackoverflow.com/questions/16028752/how-do-i-get-all-the-points-between-two-point-objects/34142336
def generate_line_points(a, b):
    points = []
    # if slope is vertical, just generate all the points vertically between them
    if a[0] == b[0]:
        # swap if a[y] > b[y]
        if a[1] > b[1]:
            a, b = b, a
        points = [(a[0], y) for y in range(a[1] + 1, b[1])]
    else:
        # swap if a_x > b_x
        if a[0] > b[0]:
            a, b = b, a
        # compute change in x, y for slope
        delta_x = b[0] - a[0]
        delta_y = b[1] - a[1]
        # init error to -1 and slope to abs(slope)
        error = -1
        positive_slope = delta_y / delta_x >= 0
        abs_slope = abs(delta_y / delta_x)
        # init y to a_y
        y = a[1]
        # for x values between a_x and y_x
        for x in range(a[0] + 1, b[0] + 1):
            # append our new point
            points.append((x, y))
            # increment our error by our slope (to determine how many new points
            # we will need to add to correct our line)
            error += abs_slope
            # use error to append other (x,y) points as needed
            while error >= 0:
                # increase or decrease y by 1 based on slope
                y += 1 if positive_slope else -1
                if x < 30 and y < 30:
                    points.append((x, y))
                error -= 1
    return points

# given a position in an adjacency matrix, return the x,y coordinates 
# corresponding to that position
def adjacency_position_to_downsized_coordinates(position):
    global DOWNSIZED_ENV_SIDE_LENGTH
    return position % DOWNSIZED_ENV_SIDE_LENGTH, position // DOWNSIZED_ENV_SIDE_LENGTH

# transform a downsized coordinate to its appropriate node number in the 
# adjacency graph    
def downsized_coordinate_to_adjacency_position(coordinates):
    global DOWNSIZED_ENV_SIDE_LENGTH
    return coordinates[1] * DOWNSIZED_ENV_SIDE_LENGTH + coordinates[0]

# given the a coordinate location in the downsized, environment, return the 
# corresponding coordinate of the cell in the center of the corresponding full
# sized environment    
def downsized_coordinate_to_full_size_coordinate(coord):
    global DOWNSIZED_ENV_SIDE_LENGTH, environment
    
    # the scaling factor we used to downsize our environment
    scaling_factor = environment.shape[0] // DOWNSIZED_ENV_SIDE_LENGTH
    # the offset we are going to use to center the new coordinate 
    offset = scaling_factor // 2
    # compute and return new x, new y
    return coord[0] * scaling_factor + offset, coord[1] * scaling_factor + offset 

# inverse of the above operation    
def full_size_coordinate_to_downsized_coordinate(coord):
    global DOWNSIZED_ENV_SIDE_LENGTH, environment
    
    # the scaling factor we used to downsize our environment
    scaling_factor = environment.shape[0] // DOWNSIZED_ENV_SIDE_LENGTH
    # compute and return new x, new y
    return coord[0] // scaling_factor, coord[1] // scaling_factor

# given two nodes in a graph built from an adjacency matrix, compute the 
# distance between them
def dist_nodes(a,b):
    (x_1,y_1) = adjacency_position_to_downsized_coordinates(a)
    (x_2,y_2) = adjacency_position_to_downsized_coordinates(b)
    return ((x_1 - x_2)**2 + (y_1 - y_2)**2)**0.5

# compute the distance between the car's current location and the goal    
def distance_to(coordinate):
    global DESTINATION, car_location
    x_1, y_1 = car_location[0], car_location[1]
    x_2, y_2 = DESTINATION[0], DESTINATION[1]
    return ((x_1 - x_2)**2 + (y_1 - y_2)**2)**0.5

# go to the next coordinate, while watching for pedestrians or stop signs
def go_to(next_coordinate):
    global stop_sign, pedestrian, STOP_SIGN_DELAY, PEDESTRIAN_DELAY_INCR
    
    # turn toward next coordinate 
    turn_toward(next_coordinate)
    
    # calculate the number of 2.5cm steps it will take to get from here to there
    steps = int(math.round(distance_to(DESTINATION) / 2.5))
    
    # proceed toward that destination while watching for pedestrians or stop signs 
    while steps > 0:
        # if we see a stop sign, wait for 5 seconds 
        if stop_sign:  
            delay(STOP_SIGN_DELAY)
        # keep waiting for a second as long as there's a pedestrian around
        while pedestrian:
            delay(PEDESTRIAN_DELAY_INCR)
        # move forward up to 1 foot (or less if objective is less than 1 foot away)
        if steps <= 12:
            forward_2_5_cm(steps)
            steps = 0
        else:
            forward_2_5_cm(12)
            steps -= 12


# protocol to run car
def main():
    global EPSILON, ANGLES, DESTINATION, car_location 
    
    # initialize environment with car and print
    init_environment()
    print_environment_to_file("initial_env")
    
    # transform the destination to the corresponding node in our downsized 
    # environment's adjacency graph 
    graph_destination = downsized_coordinate_to_adjacency_position(
        full_size_coordinate_to_downsized_coordinate(DESTINATION))

    # init number of scans we've done to 0
    num_scans = 0
    
    # main loop runs until we reach our goal 
    while distance_to(DESINTATION) > EPSILON:
        # perform scan of the environment 
        readings = scan_angles(ANGLES)
        update_environment(readings, ANGLES)
        num_scans += 1
        # print environment
        print_environment_to_file("env_after_scan_" + str(num_scans))
        # construct downsized version of environment
        downsized_environment = downsize_environment(environment)
        # construct adjacency matrix from downsized environment
        adjacency_matrix = construct_adjacency_matrix(environment)
        # build graph from matrix
        graph = nx.convert_matrix.from_numpy_array(adjacency_matrix)
        # transform the current location coordinates to the corresponding node 
        # in our downsized environment's adjacency graph 
        graph_car_location = downsized_coordinate_to_adjacency_position(
            full_size_coordinate_to_downsized_coordinate(car_location))
        # compute shortest path from graph (as sequence of nodes in adjacency 
        # graph) given the current location and destination 
        shortest_path = nx.astar_path(graph, graph_car_location, 
            graph_destination, heuristic=dist_nodes)
        # strip off only the next node in the path and transform it to downsized 
        # coordinate then to full sized coordinate 
        next_coordinates = downsized_coordinate_to_full_size_coordinate(
            adjacency_position_to_downsized_coordinates(shortest_path[0]))
        # go to the next coordinate while watching for pedestrians/stop signs
        go_to(next_coordinate)


if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()

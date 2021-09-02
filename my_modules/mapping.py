import sys
sys.path.append('./**/IoT_Lab1/picar_4wd/')
import picar_4wd as fc
from my_utils import *  # my utility methods
import numpy as np
import matplotlib.pyplot as plt
from constants import * # my constant values

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
# The car starts at (25,149), representing the car with the spoilers pressed 
# against the bottom of the map, in the center, and 25 being the y position of 
# the ultrasonic sensor
global car_location

# the set of angles we wish to cycle through in scan_180
global ANGLES

ANGLES = np.arange(-90,91,15)

# update environment by redrawing the car's current position based on 
# car_heading and car_location
def update_car_position_in_environment():

    # CODE GOES HERE

    return
    
# initialize environment as empty room (walls as obstacles)
def init_environment():
    global environment, car_heading, car_location, ROOM_HEIGHT_CM, ROOM_WIDTH_CM, CAR_HEIGHT_CM
    
    # init environment with all zeros
    environment = np.zeros((ROOM_HEIGHT_CM,ROOM_WIDTH_CM))
    # set 4 walls as being obstacles 
    environment[0] = np.ones(ROOM_WIDTH_CM)
    environment[-1] = np.ones(ROOM_WIDTH_CM)
    environment[:,0] = np.ones(ROOM_HEIGHT_CM)
    environment[:,-1] = np.ones(ROOM_HEIGHT_CM)
    
    # set car initial heading to 0
    car_heading = 0 
    # set car initial location to top of grid, middle position
    car_location = np.array([CAR_HEIGHT_CM, ROOM_WIDTH_CM // 2])
    
    return
    
# print the environment with rows reversed to match cartesian coordinates
def print_environment_to_file(file_name_no_type):
    global environment 
    
    reversed_environment = np.flip(environment, axis=0)
    
    plt.imshow(reversed_environment, interpolation='none')
    plt.savefig(file_name_no_type + ".png")
    
    return

# update environment using the readings from a 180 deg scan from the US sensor
# along with interpolation
def update_environment(readings):
    global environment, car_heading, car_location, ANGLES, ROOM_HEIGHT_CM, ROOM_WIDTH_CM
    
    # get true angle measurements of each sensor reading in range (0,359)
    true_angles = ((ANGLES * -1 + 90) + car_heading) % 360
    
    # convert sensor readings to coordinate locations assuming car is at the
    # origin (0,0)
    centered_coords = polar_to_cartesian(readings, true_angles).reshape(-1,2)
    
    # convert coordinates to actual obstacle locations with knowledge of car's 
    # true location
    true_coords = np.add(centered_coords, car_location)
    
    # filter out any obstacles detected out of bounds of our array 
    #true_coords = true_coords[(true_coords[:,0] >= 0 and 
    #true_coords[:,0] < ROOM_HEIGHT_CM and true_coords[:,1] >= 0 and 
    #true_coords[:,1] < ROOM_WIDTH_CM)]
    
    # now, use interpolation to fill in any obstacles 
    for i in range(true_coords[:0].size - 1):
        x_0, y_0 = true_coords[i][0], true_coords[i][1]
        x_1, y_1 = true_coords[i+1][0], true_coords[i+1][1]
        
        # if x_0 is not to the left of x_1, swap the two points
        if x_0 > x_1:
            x_0, y_0, x_1, y_1 = x_1, y_1, x_0, y_0
    
        # set the current point as obstacle if valid
        if coord_in_bounds(true_coords[i]):
            set_neighborhood_around_obstacle(x_0,y_0)
        # set the next point as obstacle if valid 
        if coord_in_bounds(true_coords[i+1]):
            set_neighborhood_around_obstacle(x_1,y_1)
        # interpolate the points between the two if both are valid 
        if coord_in_bounds(true_coords[i]) and coord_inbounds(true_coords[i+1]):
            m = (y_1 - y_0) / (x_1 - x_0)
            b = y_0 - m * x_0
            # interpolate the points between them as well
            for x in range(x_0 + 1, x_1):
                y = m * x + b
                set_neighborhood_around_obstacle(x,y)
            
    return

# set the neighborhood of points around an obstacle as also being obstacles    
def set_neighborhood_around_obstacle(x, y):
    global environment, FUZZ_FACTOR, ROOM_HEIGHT_CM, ROOM_WIDTH_CM
    round_x, round_y = round(x), round(y)
    
    x_s = np.arange(round_x - FUZZ_FACTOR, round_x + FUZZ_FACTOR + 1)
    y_s = np.arange(round_y - FUZZ_FACTOR, round_y + FUZZ_FACTOR + 1)
    x_s = x_s[x_s >= 0 and x_s < ROOM_WIDTH_CM]
    y_s = y_s[y_s >=0 and y_s < ROOM_HEIGHT_CM]
    
    environment[y_s,x_s] = 1
    
    
# return whether a coordinate pair (y,x) is in room bounds    
def coord_in_bounds(coord):
    global ROOM_HEIGHT_CM, ROOM_WIDTH_CM

    return (coord[0] >= 0 and coord[0] < ROOM_HEIGHT_CM and coord[1] >= 0 and 
    coord[1] < ROOM_WIDTH_CM)

# perform a 180 degree scan from the current location and heading
# return np array of all readings at 15 degree intervals from -90 to 90
# NOTE: if the distance is beyond our obstacle threshold, we simply say it is 
# infinity
def scan_180():
    global ANGLES, OBSTACLE_THRESHOLD, INF
    
    readings = np.empty(len(ANGLES))
    i = 0
    for angle in ANGLES:
        distance = fc.get_distance_at(angle)
        readings[i] = distance if distance <= OBSTACLE_THRESHOLD else INF
        i += 1
    return readings


def main():
    # initialize environment with car at (299,149) and print
    init_environment()
    print_environment()
    
    # perform scan and print
    update_environment(scan_180())
    delay(1000)
    print_environment()
    
    # move forward 25cm then repeat scan and print
    #forward_2_5_cm(10)
    #update_environment(scan_180())
    #print_environment()
    
    # keep running until quit_thread pressed
    #while not get_quit_pressed():
    #    continue
    #sys.exit()

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
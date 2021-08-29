import sys
sys.path.append('./**/IoT_Lab1/picar_4wd/')
import picar_4wd as fc
from my_utils import *  # my utility methods
import numpy as np
from constants import * # my constant values

# track environment as 300x300 np array using the following encoding scheme:
# 0: clear 
# 1: obstacle 
# 2: car
global environment

# tracks the car's heading, where car starts at heading 0, which points towards
# positive y  
global car_heading

# tracks the car's location (specifically the point halfway between the 
# spoilers). The car starts at (0,149), representing the bottom of the map, in # the center
global car_location


# update environment by redrawing the car's current position based on 
# car_heading and car_location
def update_car_position_in_environment():

    # CODE GOES HERE

    return
    
# initialize environment as empty 3m x 3m grid (no obstacles)
def init_environment():
    global environment, car_heading, car_location
    
    environment = np.zeros((300,300))
    heading = 0             # corresponds to facing 'north'
    location = (0, 149)     # corresponds to top of grid, middle position
    return
    
# print the environment with rows reversed to match cartesian coordinates
def print_environment():
    global environment 
    
    reversed_environment = np.flip(environment, axis=0)
    print(reversed_environment)
    return

# update environment using the readings from a 180 deg scan from the US sensor
# along with interpolation
def update_environment(readings):
    global environment, car_heading, car_location
    
    # CODE GOES HERE
    
    return

# perform a 180 degree scan from the current location and heading
# return np array of all readings at 15 degree intervals from -90 to 90
def scan_180():
    readings = np.empty(12)
    angles = np.arange(-90,91,15)
    i = 0
    for angle in angles:
        readings[i] = fc.get_distance_at(angle)
        i += 1
    return readings


def main():
    # initialize environment with car at (299,149)
    init_environment()
    print_environment()
    
    forward_2_5_cm(10)
    print_environment()
    
    # keep running until quit_thread pressed
    #while not get_quit_pressed():
    #    continue
    #sys.exit()

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
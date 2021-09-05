import sys

sys.path.append('./**/IoT_Lab1/picar_4wd/')
import picar_4wd as fc
from my_modules.my_utils import *  # my utility methods
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
    global environment, car_heading, car_location, ROOM_HEIGHT_CM, ROOM_WIDTH_CM, CAR_HEIGHT_CM

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

    # now, use interpolation to fill in any obstacles 
    for i in range(true_coords[:, 0].size - 1):
        x_0, y_0 = int(round(true_coords[i][0])), int(round(true_coords[i][1]))
        x_1, y_1 = int(round(true_coords[i + 1][0])), int(round(true_coords[i + 1][1]))

        # if x_0 is not to the left of x_1, swap the two points
        if x_0 > x_1:
            x_0, y_0, x_1, y_1 = x_1, y_1, x_0, y_0

        # set the current point as obstacle if valid
        if coord_in_bounds(true_coords[i]):
            set_neighborhood_around_point(x_0, y_0)
        # set the next point as obstacle if valid 
        if coord_in_bounds(true_coords[i + 1]):
            set_neighborhood_around_point(x_1, y_1)
        # interpolate the points between the two if both are valid and close 
        # enough together
        if (coord_in_bounds(true_coords[i]) and
                coord_in_bounds(true_coords[i + 1]) and x_1 != x_0 and
                abs(readings[i] - readings[i + 1]) <= INTERPOLATION_THRESHOLD):
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


def main():
    # initialize environment with car at (299,149) and print
    init_environment()
    print_environment_to_file("initial_env")

    test_angles = np.arange(-75, 76, 5)

    # perform scan and print
    readings = scan_angles(test_angles)
    print_readings(readings)
    update_environment(readings, test_angles)
    delay(1000)
    print_environment_to_file("env_after_180_scan")

    # move forward 25cm then repeat scan and print
    # forward_2_5_cm(10)
    # update_environment(scan_180())
    # print_environment()

    # keep running until quit_thread pressed
    # while not get_quit_pressed():
    #    continue
    # sys.exit()


if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()

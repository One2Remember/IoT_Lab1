global NO_OBSTACLE, OBSTACLE, INF, ANGLE_STEP, MAX_ANGLE, MIN_ANGLE, OBSTACLE_THRESHOLD, MIN_OBSTACLE_THRESHOLD
global SERVO_BIAS, CAR_WIDTH_CM, CAR_HEIGHT_CM, ROOM_WIDTH_CM, ROOM_HEIGHT_CM, FUZZ_FACTOR, INTERPOLATION_THRESHOLD
global DOWNSIZED_ENV_SIDE_LENGTH, EPSILON, STOP_SIGN_DELAY, PEDESTRIAN_DELAY_INCR, US_RANGE_STEPS

NO_OBSTACLE = 0     # if there is no obstacle in the environment at a specific loc
OBSTACLE = 1        # if there is an obstacle in the environment at a specific loc
INF = 99999         # to track an US reading > OBSTACLE_THRESHOLD
ANGLE_STEP = 15     # number of degrees to turn when scanning on us sensor
MAX_ANGLE = +45     # max servo angle for ultrasonic sensor
MIN_ANGLE = -45     # min servo angle for ultrasonic sensor
OBSTACLE_THRESHOLD = 300    # distance at which an obstacle is considered detected
MIN_OBSTACLE_THRESHOLD = 10     # min distance at which an obstacle is detected
SERVO_BIAS = 10     # the bias that the servo has (it turns +10 more degrees than it should)
CAR_WIDTH_CM = 20   # approximate width of car in cm
CAR_HEIGHT_CM = 25  # approximate height of car in cm
ROOM_WIDTH_CM = 300     # approximate width of room in cm
ROOM_HEIGHT_CM = 300    # approximate height of room in cm
FUZZ_FACTOR = 5     # the number of cm around an obstacle that we want to mark as also being an obstacle
INTERPOLATION_THRESHOLD = 30    # the number of cm difference we allow between two adjacent distances to interpolate
DOWNSIZED_ENV_SIDE_LENGTH = 15  # the side length of the downsized environment (30x30 square from 300x300)
EPSILON = 40    # the distance away from the goal at which point we consider having arrived
STOP_SIGN_DELAY = 5000  # the amount of time (in ms) to wait at a stop sign
PEDESTRIAN_DELAY_INCR = 1000    # the increments of time (in ms) we spend waiting for a pedestrian
US_RANGE_STEPS = 60 # the range of the US sensor (in inches)
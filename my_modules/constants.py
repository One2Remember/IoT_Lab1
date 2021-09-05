global NO_OBSTACLE, OBSTACLE, INF, ANGLE_STEP, MAX_ANGLE, MIN_ANGLE, OBSTACLE_THRESHOLD, MIN_OBSTACLE_THRESHOLD
global SERVO_BIAS, CAR_WIDTH_CM, CAR_HEIGHT_CM, ROOM_WIDTH_CM, ROOM_HEIGHT_CM, FUZZ_FACTOR, INTERPOLATION_THRESHOLD

NO_OBSTACLE = 0     # if there is no obstacle in the environment at a specific loc
OBSTACLE = 1        # if there is an obstacle in the environment at a specific loc
INF = 99999         # to track an US reading > OBSTACLE_THRESHOLD
ANGLE_STEP = 15     # number of degrees to turn when scanning on us sensor
MAX_ANGLE = +45     # max servo angle for ultrasonic sensor
MIN_ANGLE = -45     # min servo angle for ultrasonic sensor
OBSTACLE_THRESHOLD = 200    # distance at which an obstacle is considered detected
MIN_OBSTACLE_THRESHOLD = 10     # min distance at which an obstacle is detected
SERVO_BIAS = 10     # the bias that the servo has (it turns +10 more degrees than it should)
CAR_WIDTH_CM = 20   # approximate width of car in cm
CAR_HEIGHT_CM = 25  # approximate height of car in cm
ROOM_WIDTH_CM = 290     # approximate width of room in cm
ROOM_HEIGHT_CM = 300    # approximate height of room in cm
FUZZ_FACTOR = 5     # the number of cm around an obstacle that we want to mark as also being an obstacle
INTERPOLATION_THRESHOLD = 30    # the number of cm difference we allow between two adjacent distances to interpolate

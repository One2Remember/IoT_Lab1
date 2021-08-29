global MAX_ANGLE, MIN_ANGLE, OBSTACLE_THRESHOLD, ANGLE_STEP, CAR_WIDTH_CM, CAR_HEIGHT_CM

ANGLE_STEP = 15 # number of degrees to turn when scanning on us sensor
MAX_ANGLE = +45 # max servo angle for ultrasonic sensor
MIN_ANGLE = -45 # min servo angle for ultrasonic sensor 
OBSTACLE_THRESHOLD = 30 # distance at which an obstacle is considered detected
CAR_WIDTH_CM = 20   # approximate width of car in cm
CAR_HEIGHT_CM = 25  # approximate height of car in cm
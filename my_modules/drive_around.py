import sys
sys.path.append('./**/IoT_Lab1/picar_4wd/')
from constants import * # my constant values
from my_utils import *  # my utility methods
import picar_4wd as fc
from threading import Thread

global obstacle_detected, quit_pressed

obstacle_detected = False    # for tracking if there is an obstacle at any point
quit_pressed = False    # for tracking if user has hit 'quit' key

# drive around, if there is an obstacle, pick a random direction, back up then 
# turn to face that direction
def drive_around():
    global obstacle_detected, quit_pressed
    
    while not quit_pressed:
        # print("OBSTACLE detected in drive_around: " + str(obstacle_detected))
        if obstacle_detected:
            fc.stop()   # stop the car
            delay(500)  # delay for half a second
            direction = random.randrange(90, 270)   # pick a new direction
            while obstacle_detected:    # backup until no longer detect obstacle
                backward(5, 1)
            turn(direction) # turn in the chosen direction
            delay(500)  # hold for half a second
            
        else:
            forward(1, 1)
    return

# continuously scan for obstacles and update obstacle status
# @param threshold - range on ultrasonic sensor at which an obstacle is 
#   considered detected   
def scan_for_obstacles(threshold):
    global obstacle_detected, quit_pressed, MAX_ANGLE, MIN_ANGLE
    
    # set angle 0 by default
    angle = 0
    scanning_right = True   # start by scanning to the right
    while not quit_pressed:
        # detect an obstacle if object detected at or beyond threshold distance
        distance = fc.get_distance_at(angle)
        obstacle_detected = distance != -2 and distance <= threshold
        # adjust angle, switching directions if hit MIN and MAX angle bounds
        if scanning_right:
            angle += ANGLE_STEP
            if angle == MAX_ANGLE:
                scanning_right = False
        else:
            angle -= ANGLE_STEP
            if angle == MIN_ANGLE:
                scanning_right = True
    return  
    
# drive around while scanning for obstacles, if one is found, pick a random 
# direction, back up, then turn to that direction and continue 
# press 'q' to quit
def run_obstacle_avoidance():
    global obstacle_detected, quit_pressed, OBSTACLE_THRESHOLD
    
    quit_thread = Thread(target=utils.read_keyboard_for_quit, daemon=True)
    drive_thread = Thread(target=drive_around, daemon=True)
    scan_thread = Thread(target=scan_for_obstacles, args=(OBSTACLE_THRESHOLD,), daemon=True)
    drive_thread.start()
    scan_thread.start()
    quit_thread.start()


def main():
    global quit_pressed 
    
    run_obstacle_avoidance()
    
    # keep running until quit_thread pressed
    while not quit_pressed:
        continue
    sys.exit()

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()

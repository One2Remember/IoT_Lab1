import sys
import tty
import termios
import asyncio
import time
import random
import picar_4wd as fc
from threading import Thread

global obstacle_detected, quit_pressed, MAX_ANGLE, MIN_ANGLE, 
OBSTACLE_THRESHOLD, ANGLE_STEP

obstacle_detected = False    # for tracking if there is an obstacle at any point
quit_pressed = False    # for tracking if user has hit 'quit' key

ANGLE_STEP = 15 # number of degrees to turn when scanning on us sensor
MAX_ANGLE = +45 # max servo angle for ultrasonic sensor
MIN_ANGLE = -45 # min servo angle for ultrasonic sensor 
OBSTACLE_THRESHOLD = 30 # distance at which an obstacle is considered detected


# sleep for a pre-set amount of time, car will continue to do what it was doing:
# turning, moving forward, etc. We want to avoid sleeping for more than 0.1
# second increments, so if our time is greater than that, we will sleep in 0.1 
# second increments and then sleep the remaining (<100) milliseconds     
# @param milliseconds - the number of milliseconds (.001 seconds) to delay for
def delay(milliseconds):
    if milliseconds > 100:
        deciseconds = milliseconds // 100
        milliseconds = milliseconds % 100
        for _ in range(deciseconds):
            time.sleep(0.1)
    time.sleep(0.001 * milliseconds)
    return
        
        
# read char from keyboard
# note: this method is taken directly from Sunfounder's picar-4wd module
def read_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# read key press
# note: this method is taken directly from Sunfounder's picar-4wd module
def read_key(getchar_fn=None):
    getchar = getchar_fn or read_char
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)

# turns the car any number of degrees in [-inf, inf]
# NOTE: this needs to be updated because just sleeping doesn't do it
# The speed at which the car moves heavily depends on the battery charge
# need to instead use wheel turning amount, which means we need a fixed speed
# sensor. UGH
def turn(deg):
    # stop the car and delay for a moment
    fc.stop()
    delay(100)
    
    # normalize deg to value in [0,359]
    deg = deg % 360
    
    # check if we should turn left or right
    turn_right = True
    if deg >= 180:
        turn_right = False
        deg = 360 - deg
    # calculate the number of steps to turn (different for left vs right because
    # of misaligned wheels - time should be in ratio of 23:20)
    if(turn_right):
        delay_steps = round(deg * (5 + (1/3)))
    else:
        delay_steps = round(deg * 4.8)
    # now we turn left or right based on number of steps to sleep
    if turn_right:  # if deg > 180, we turn right
        #print("\nTurning right " + str(deg) + " degrees", flush=True)
        fc.turn_right(100)
    else:   # else, turn left
        #print("\nTurning left " + str(deg) + " degrees", flush=True)
        fc.turn_left(100)
    delay(delay_steps)  # delay 
    fc.stop()   # stop car
    
# move the car forward
# @param power - power level to move forward
# @param steps - number of deciseconds to move for
def forward(power, steps):
    fc.forward(power)   # set car to move forward
    delay(steps)    # delay
    fc.stop()   # stop car
   
# move the car backward
# @param power - power level to move forward
# @param steps - number of deciseconds to move for   
def backward(power, steps):
    fc.backward(power)  # set car to move backward
    delay(steps)    # delay 
    fc.stop()   # stop car
    return
    
# TODO
# move the car forward some given number of cm
def forward_dist(cm):
    return
    
    
# TODO
# move the car backward some given number of cm
def backward_dist(cm):
    return


       
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
    
    
# poll keyboard for q key to quit program (set quit_pressed to True)     
def read_keyboard_for_quit():
    global quit_pressed
    
    print("Press q to quit")
    while not quit_pressed:
        key = read_key()
        if key == 'q':
            print("Done") 
            quit_pressed = True
    return

# drive around while scanning for obstacles, if one is found, pick a random 
# direction, back up, then turn to that direction and continue 
# press 'q' to quit
def run_obstacle_avoidance():
    global obstacle_detected, quit_pressed, OBSTACLE_THRESHOLD
    
    quit_thread = Thread(target=read_keyboard_for_quit, daemon=True)
    drive_thread = Thread(target=drive_around, daemon=True)
    scan_thread = Thread(target=scan_for_obstacles, args=(OBSTACLE_THRESHOLD,), daemon=True)
    drive_thread.start()
    scan_thread.start()
    quit_thread.start()
    

# make a simple square     
def make_square():
    forward(5,5)
    delay(200)
    turn(90)
    delay(200)
    backward(5,5)
    delay(200)
    turn(90)
    delay(200)
    
# test method, simply makes a square over and over again by going forward,
# turning right 90, going backward, then turning right 90 repeatedly
def test_square():
    global quit_pressed
    
    quit_thread = Thread(target=read_keyboard_for_quit, daemon=True)
    square_thread = Thread(target=make_square, daemon=True)
    quit_thread.start()
    square_thread.start()
        

# test methods    
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
        
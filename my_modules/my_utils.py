import sys
sys.path.append('./**/IoT_Lab1/picar_4wd/')
import picar_4wd as fc
import tty
import termios
import asyncio
import time
import random
import numpy as np
from picar_4wd.pwm import PWM
from picar_4wd.adc import ADC
from picar_4wd.pin import Pin
from picar_4wd.motor import Motor
from picar_4wd.servo import Servo
from picar_4wd.ultrasonic import Ultrasonic 
from picar_4wd.speed import Speed
from picar_4wd.filedb import FileDB  
from picar_4wd.utils import *
from constants import * # my constant values
from threading import Thread

quit_pressed = False    # for tracking if user has hit 'quit' key

# init servo
servo = Servo(PWM("P0"))

# for getting if quit has been pressed
def get_quit_pressed():
    return quit_pressed

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
    
# neatly print sensor readings
def print_readings(readings):
    print("Readings:")
    for reading in readings:
        if reading >= INF - 1:
            print("INF", end=' ')
        else:
            print(reading, end=' ')
    return

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
    if turn_right:
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
    

# my adaptation of professors code to move forward by some multiple of 2.5cm
# @param steps - how many multiples of 2.5cm the car should move forward
def forward_2_5_cm(steps):
    fc.forward(100)
    delay(int(round(steps * 100 / 3.264)))
    fc.stop()  
    
# convert polar coordinates to cartesian coordinates    
def polar_to_cartesian(r, theta):
    x_s = r * np.cos(theta)
    y_s = r * np.sin(theta)
    return np.column_stack((x_s, y_s))
     
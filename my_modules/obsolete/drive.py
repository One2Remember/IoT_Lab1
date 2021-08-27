import picar_4wd as fc
import time

POWER = 100 
BACK_UP_STEPS = 5
TURN_STEPS = 100

def back_up():
    backing_up = True
    while(backing_up):
        fc.backward(POWER)
        for _ in range(BACK_UP_STEPS):
            time.sleep(0.1)
        backing_up = False 
        
def turn_right():
    turning_right = True
    while(turning_right):
        fc.turn_right(POWER)
        for _ in range(TURN_STEPS):
            time.sleep(0.1)
        turning_right = False

def main():
    fc.forward(POWER)
    while True:
        scan_list = fc.scan_step(5)
        if not scan_list:
            continue

        tmp = scan_list[3:7]
        print(tmp)
        if tmp != [2,2,2,2]:
            back_up()
            turn_right()
        else:
            fc.forward(POWER)

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
import picar_4wd as fc

def main():

    speed = 30
    ANGLE_RANGE = 180
    STEP = 18
    us_step = STEP
    angle_distance = [0,0]
    current_angle = 0
    max_angle = ANGLE_RANGE/2
    min_angle = -ANGLE_RANGE/2
    scan_list = []

    while True:
        print(fc.get_distance_at(current_angle))
        

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()

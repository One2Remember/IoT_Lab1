import my_utils

def main():
    power = 30
    turning = False
    while not turning:
        scan_list = fc.scan_step(5)  # as long as we're over 5, we return 2, so we should be good
        if not scan_list:
            continue

        tmp = scan_list[3:7]
        print(tmp)
        if tmp != [2,2,2,2]:
            try:
                turning = True
                back_up(5)
                random_turn(5)
                turning = False
            except OSError:
                print("OS Error")
                continue
        else:
            forward_step(5)

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()

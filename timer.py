import time


interval_time = 60.0  #Seconds
start_time = time.time()
while True:
    print("Tick", time.strftime("%H:%M:%S"))
    time.sleep(interval_time - ((time.time() - start_time) % interval_time))

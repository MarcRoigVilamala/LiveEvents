import os
import requests
import time

SERVER_IP = 'http://192.168.8.224'

# Get System Time
system_time = time.time()

count = 0
response = -1


# Get Time from server
def sync():
    global count, response
    count += 1
    try:
        print("Connecting to time server... Try #", count)
        response = int(requests.get(SERVER_IP, timeout=5).text) / 1000.0
    except Exception as e:
        print("EXPECTION", e)
        pass
    return response


# Changes the system clock to server's time
def setClock():
    os.system("sudo date -s '@{}'".format(now()))


# Gets the current time, assuming we were able to get a response at least once
def now():
    while response == -1:
        sync()
        time.sleep(5)
    return (response - system_time) + time.time()


if __name__ == "__main__":
    # setClock()
    while True:
        time.sleep(1)
        print("Time:", now())
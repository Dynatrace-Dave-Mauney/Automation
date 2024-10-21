import psutil
import time

while True:
    print('The CPU usage is: ', psutil.cpu_percent(4))
    print('RAM memory % used:', psutil.virtual_memory()[2])
    print('RAM Used (GB):', psutil.virtual_memory()[3] / 1000000000)
    time.sleep(60)
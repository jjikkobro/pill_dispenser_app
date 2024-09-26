import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)
time.sleep(1)

for i in range(10):
    ser.write(b'1')
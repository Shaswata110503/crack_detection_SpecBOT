import serial
import time

arduino = serial.Serial('COM9', 9600, timeout=1)

time.sleep(2)

print("Connected")

while True:

    cmd = input("A/B: ")

    if cmd == "A":
        arduino.write(b'A')

    elif cmd == "B":
        arduino.write(b'B')
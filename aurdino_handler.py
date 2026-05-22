import serial
import time
# ===================
# CONFIGURATION OF COMMUNICATION PORT AND BAUD RATE 
# ===================

PORT = "COM6"
BAUD = 9600

# ===================
# SERIAL CONNECTION WITH AURDINO
# ===================

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)

    print(f" Bluetooth Connected on {PORT}")

    connected = True

# except:

#     print(" Bluetooth not connected")

#     ser = None
#     connected = False
except Exception as e:
    print("Bluetooth not connected")
    print(e)

# ===================
# SEND COMMAND
# ===================

def send_command(command):

    if connected and ser:

        ser.write((command + '\n').encode())

        print("Sent:", command)

    else:

        print("Bluetooth not connected")


# ===================
# ROBOT FUNCTIONS
# ===================

def robot_forward():

    send_command("robot on")


def robot_backward():

    send_command("robot back")


def robot_stop():

    send_command("robot off")


def light_on():

    send_command("light on")


def light_off():

    send_command("light off")
# ===================
# SPEED CONTROL
# ===================

def set_speed(speed):

    send_command(f"speed:{speed}")

# ===================
# CLEANUP
# ===================

def close_serial():

    global ser

    if ser:

        ser.close()

        print(" Serial closed.")
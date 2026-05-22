import socket

# HOST = "192.168.1.5"   # CHANGE THIS to  ESP32 IP shown in Serial Monitor.
# PORT = 1234
HOST = "10.50.141.46"
PORT = 1234

client_socket = None


def connect_esp32():

    global client_socket

    try:

        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.connect((HOST, PORT))

        print("Connected to ESP32")

        return True

    except Exception as e:

        print("ESP32 Connection Error:", e)

        return False


def receive_message():

    global client_socket

    try:

        data = client_socket.recv(1024).decode().strip()

        return data

    except:

        return None
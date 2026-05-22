from esp32_handler import connect_esp32, receive_message

connected = connect_esp32()

if connected:

    while True:

        message = receive_message()

        if message:

            print("Received:", message)
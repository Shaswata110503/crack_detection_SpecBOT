# =========================
# PIPELINE ROBOT GUI LAYOUT
# CustomTkinter
# =========================
from CNN_predict import predict_image
import csv
import os
from datetime import datetime
from PIL import Image
import requests
import threading
import winsound
from esp32_handler import connect_esp32, receive_message
import customtkinter as ctk
from camera_handler import start_camera, stop_camera
from aurdino_handler import (
    robot_forward,
    robot_backward,
    robot_stop,
    light_on,
    light_off,
    set_speed,
    read_encoder
)
# ################################################
# =========================
# CREATE FOLDERS
# =========================

os.makedirs("captured_images", exist_ok=True)

csv_file = "sensor_data.csv"
# =========================
# CREATE CSV FILE
# =========================

if not os.path.exists(csv_file):

    with open(csv_file, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Timestamp",
            "Temperature",
            "Humidity",
            "GasLevel",
            "Prediction",
            "Confidence",
            "ImagePath"
        ])
# ########################################################

# -------------------------
# Window Setup
# -------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Pipeline Inspection Robot")
app.geometry("1400x800")

# Make main window expandable
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=0)   # Left
app.grid_columnconfigure(1, weight=1)   # Middle
app.grid_columnconfigure(2, weight=0)   # Right

# =====================================================
# LEFT SECTION
# =====================================================

left_frame = ctk.CTkFrame(app, corner_radius=15)
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=0)
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_propagate(False)
left_frame.configure(width=200)
# ALERT BOX
alert_box = ctk.CTkFrame(left_frame, corner_radius=12)
alert_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

alert_label = ctk.CTkLabel(
    alert_box,
    text="SAFE",
    font=("Arial", 28, "bold"),
    text_color="green"
)

alert_label.pack(pady=30)

# ==========================
# BLINKING ALERT
# ==========================
is_blinking = False

def blink_alert():

    global is_blinking

    if is_blinking:

        current_color = alert_label.cget("text_color")

        if current_color == "red":
            alert_label.configure(text_color="white")
        else:
            alert_label.configure(text_color="red")

        alert_label.after(500, blink_alert)

def monitor_esp32():

    global is_blinking

    connected = connect_esp32()

    if not connected:

        alert_label.configure(
            text="ESP32 OFFLINE",
            text_color="orange"
        )

        return

    while True:

        message = receive_message()

        if not message:
            continue

        print("Received:", message)

        # ==================================
        # CRACK ALERT
        # ==================================

        if message == "CRACK_ALERT":

            winsound.Beep(1500, 1000)

            alert_label.configure(
                text="⚠ CRACK DETECTED"
            )

            if not is_blinking:

                is_blinking = True
                blink_alert()

        # ==================================
        # SAFE
        # ==================================

        elif message == "SAFE":

            is_blinking = False

            alert_label.configure(
                text="SAFE",
                text_color="green"
            )

        # ==================================
        # SENSOR DATA
        # ==================================

        # ==================================
        # SENSOR DATA
        # ==================================

        elif "Gas" in message:

            try:

                # Example:
                # Gas:4095,Temp:35.20,Humidity:75.00

                parts = message.split(",")

                gas = parts[0].split(":")[1]
                temp = parts[1].split(":")[1]
                hum = parts[2].split(":")[1]

                gas_value = int(gas)

                # ==================================
                # AQI CALCULATION
                # ==================================

                if gas_value <= 100:

                    aqi = gas_value
                    status = "Good"
                    color = "green"

                elif gas_value <= 500:

                    aqi = gas_value
                    status = "Moderate"
                    color = "yellow"

                elif gas_value <= 1500:

                    aqi = gas_value
                    status = "Poor"
                    color = "orange"

                elif gas_value <= 3000:

                    aqi = gas_value
                    status = "Very Poor"
                    color = "red"

                else:

                    aqi = gas_value
                    status = "Severe"
                    color = "darkred"

                # ==================================
                # UPDATE GUI
                # ==================================

                temp_label.configure(
                    text=f"Temperature: {temp} °C"
                )

                hum_label.configure(
                    text=f"Humidity: {hum} %"
                )

                gas_label.configure(
                    text=f"Gas Level: {gas}"
                )

                aqi_label.configure(
                    text=f"AQI : {aqi}"
                )

                aqi_status_label.configure(
                    text=f"Status : {status}",
                    text_color=color
                )
                with open(csv_file, "a", newline="") as file:
                    writer=csv.writer(file)
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        temp,
                        hum,
                        gas,
                        latest_prediction,
                        latest_confidence,
                        latest_image_path
                    ])

            except Exception as e:

                print("Sensor Parsing Error:", e)

# Prediction FUnction

# #######################
latest_prediction = "Unknown"
latest_confidence = 0
latest_image_path = ""
# #######################



def show_prediction(img_path):
    global latest_prediction, latest_confidence, latest_image_path

    predicted_class, confidence = predict_image(img_path)
    # ###################
    latest_prediction=predicted_class
    latest_confidence=confidence
    latest_image_path=img_path
    # ###################
    # RESULT TEXT
    if predicted_class == "cracked":
        result_text = f"⚠ CRACK DETECTED\nConfidence: {confidence}%"
    else:
        result_text = f"✅ PIPE HEALTHY\nConfidence: {confidence}%"

    result_label.configure(text=result_text)

    # LOAD IMAGE
    img = Image.open(img_path)

    # RESIZE IMAGE
    img = img.resize((256,256))

    # CTK IMAGE
    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=(256,256)
    )

    # SHOW IMAGE
    image_label.configure(image=ctk_img)
    image_label.image = ctk_img

# #################################
def capture_and_predict():

    # ESP32-CAM URL
    url = "http://192.168.139.99/capture"

    # Save path
    # img_path = "esp32_capture.jpg"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_path = f"captured_images/{timestamp}.jpg"

    try:

        # Get image from ESP32
        response = requests.get(url, timeout=10)

        # Save image
        with open(img_path, "wb") as f:
            f.write(response.content)

        # Show prediction
        show_prediction(img_path)

    except Exception as e:

        result_label.configure(
            text=f"ERROR\n{e}"
        )
# =========================
# UPDATE ENCODER UI
# =========================


# ================
# STATUS BOX
# ================
status_box = ctk.CTkFrame(
    left_frame,
    corner_radius=12,
    width=180,
    height=320
)

status_box.grid(
    row=1,
    column=0,
    padx=10,
    pady=10
)

# VERY IMPORTANT
status_box.grid_propagate(False)
status_box.pack_propagate(False)

# IMPORTANT
status_box.grid_propagate(False)

status_label = ctk.CTkLabel(
    status_box,
    text="STATUS",
    font=("Arial", 20, "bold")
)
status_label.pack(pady=10)
# ===================================
# STATUS CONTROL BUTTONS
# ===================================

forward_btn = ctk.CTkButton(
    status_box,
    text="Robot Forward",
    fg_color="#00A86B",
    hover_color="#00C9FF",
    command=robot_forward
)

forward_btn.pack(padx=10, pady=8, fill="x")


backward_btn = ctk.CTkButton(
    status_box,
    text="Robot Backward",
    fg_color="#FF8C00",
    hover_color="#00C9FF",
    command=robot_backward
)

backward_btn.pack(padx=10, pady=8, fill="x")


stop_btn = ctk.CTkButton(
    status_box,
    text="Robot Stop",
    fg_color="#FF3131",
    hover_color="#00C9FF",
    command=robot_stop
)

stop_btn.pack(padx=10, pady=8, fill="x")

# THIRD BOX
third_box = ctk.CTkFrame(left_frame, corner_radius=12)
third_box.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

title_label = ctk.CTkLabel(
    third_box,
    text="AQI Index",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=10)

# SENSOR LABELS
temp_label = ctk.CTkLabel(
    third_box,
    text="Temperature: -- °C",
    font=("Arial", 16)
)
temp_label.pack(pady=5)

hum_label = ctk.CTkLabel(
    third_box,
    text="Humidity: -- %",
    font=("Arial", 16)
)
hum_label.pack(pady=5)

gas_label = ctk.CTkLabel(
    third_box,
    text="Gas Level: --",
    font=("Arial", 16)
)
gas_label.pack(pady=5)
# #############


aqi_label = ctk.CTkLabel(
    third_box,
    text="AQI : --",
    font=("Arial", 18, "bold")
)

aqi_label.pack(pady=8)

aqi_status_label = ctk.CTkLabel(
    third_box,
    text="Status : --",
    font=("Arial", 16, "bold")
)

aqi_status_label.pack(pady=5)




# =====================================================
# MIDDLE SECTION
# =====================================================

middle_frame = ctk.CTkFrame(app, corner_radius=15)
middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# FIX SIZE
middle_frame.grid_propagate(False)

# TWO EQUAL ROWS
middle_frame.grid_rowconfigure(0, weight=1, uniform="group1")
middle_frame.grid_rowconfigure(1, weight=1, uniform="group1")

middle_frame.grid_columnconfigure(0, weight=1)

# =====================================================
# LIVE CAMERA SECTION
# =====================================================

camera_frame = ctk.CTkFrame(
    middle_frame,
    corner_radius=12
)

camera_frame.grid(
    row=0,
    column=0,
    padx=10,
    pady=(10, 5),
    sticky="nsew"
)

# VERY IMPORTANT
camera_frame.grid_propagate(False)

camera_label = ctk.CTkLabel(
    camera_frame,
    text="LIVE CAMERA",
    font=("Arial", 28, "bold")
)

camera_label.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# =====================================================
# AI RESULT SECTION
# =====================================================

result_frame = ctk.CTkFrame(
    middle_frame,
    corner_radius=12
)

result_frame.grid(
    row=1,
    column=0,
    padx=10,
    pady=(5, 10),
    sticky="nsew"
)

result_frame.grid_propagate(False)

# RESULT TEXT
result_label = ctk.CTkLabel(
    result_frame,
    text="AI PREDICTED RESULT",
    font=("Arial", 28, "bold")
)

result_label.pack(pady=(10,5))

# IMAGE LABEL
image_label = ctk.CTkLabel(
    result_frame,
    text=""
)

image_label.pack(pady=10)


# =====================================================
# RIGHT SECTION
# =====================================================

right_frame = ctk.CTkFrame(app, corner_radius=15)
right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

# Ratio 4 : 1 : 1
right_frame.grid_rowconfigure(0, weight=4)
right_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_rowconfigure(2, weight=1)

right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_propagate(False)
right_frame.configure(width=300)
# -------------------------
# BUTTON BOX
# -------------------------

button_box = ctk.CTkFrame(right_frame, corner_radius=12)
button_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Configure rows
for i in range(7):
    button_box.grid_rowconfigure(i, weight=1)

button_box.grid_columnconfigure(0, weight=1)

# TITLE
button_title = ctk.CTkLabel(
    button_box,
    text="CONTROL PANEL",
    font=("Arial", 20, "bold")
)
button_title.grid(row=0, column=0, pady=10, sticky="ew")


# BUTTONS

btn1 = ctk.CTkButton(
    button_box,
    text="Start Robot",
    fg_color="#D849CA",
    hover_color="#00C9FF"
)
btn1.grid(row=1, column=0, padx=20, pady=8, sticky="ew")


btn2 = ctk.CTkButton(
    button_box,
    text="Stop Robot",
    fg_color="#FF5733",
    hover_color="#00C9FF"
)
btn2.grid(row=2, column=0, padx=20, pady=8, sticky="ew")


btn3 = ctk.CTkButton(
    button_box,
    text="Capture Image",
    fg_color="#DF2494",
    hover_color="#00C9FF",
    command=capture_and_predict
)
btn3.grid(row=3, column=0, padx=20, pady=8, sticky="ew")


btn4 = ctk.CTkButton(
    button_box,
    text="Live YOLO Mode",
    fg_color="#1AAD00",
    hover_color="#00C9FF",
    command=lambda: start_camera(camera_label)
)
btn4.grid(row=4, column=0, padx=20, pady=8, sticky="ew")


btn5 = ctk.CTkButton(
    button_box,
    text="Live YOLO OFF",
    fg_color="#85CA79",
    hover_color="#00C9FF",
    command=lambda: stop_camera(camera_label)
)
btn5.grid(row=5, column=0, padx=20, pady=8, sticky="ew")


btn6 = ctk.CTkButton(
    button_box,
    text="Light ON",
    fg_color="#9400D3",
    hover_color="#00C9FF",
    command=light_on
)
btn6.grid(row=6, column=0, padx=20, pady=8, sticky="ew")


btn7 = ctk.CTkButton(
    button_box,
    text="Light OFF",
    fg_color="#FFAD14",
    hover_color="#00C9FF",
    command=light_off
)
btn7.grid(row=7, column=0, padx=20, pady=8, sticky="ew")
# -------------------------
# BOX 2 -> ENCODER
# -------------------------

# ==========================
# LIVE ENCODER UPDATE
# ==========================

def update_encoder_data():

    count, distance = read_encoder()

    if count is not None:

        count_label.configure(
            text=f"Live Count : {count}"
        )

        distance_label.configure(
            text=f"Distance : {distance} cm"
        )

    app.after(100, update_encoder_data)

# ==========================
# ENCODER BOX
# ==========================

encoder_box = ctk.CTkFrame(
    right_frame,
    corner_radius=12
)

encoder_box.grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="nsew"
)

# ==========================
# TITLE
# ==========================

encoder_title = ctk.CTkLabel(
    encoder_box,
    text="ENCODER",
    font=("Arial", 18, "bold")
)

encoder_title.pack(pady=5)

# ==========================
# COUNT LABEL
# ==========================

count_label = ctk.CTkLabel(
    encoder_box,
    text="Live Count : 0",
    font=("Arial", 16)
)

count_label.pack(pady=5)

# ==========================
# DISTANCE LABEL
# ==========================

distance_label = ctk.CTkLabel(
    encoder_box,
    text="Distance : 0 cm",
    font=("Arial", 16)
)

distance_label.pack(pady=5)

# ==========================
# START LIVE UPDATE
# ==========================

update_encoder_data()





# -------------------------
# BOX 3 -> IMU
# -------------------------

imu_box = ctk.CTkFrame(right_frame, corner_radius=12)
imu_box.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

imu_title = ctk.CTkLabel(
    imu_box,
    text="IMU",
    font=("Arial", 18, "bold")
)
imu_title.pack(pady=5)

imu_data1 = ctk.CTkLabel(
    imu_box,
    text="Data 1",
    font=("Arial", 14)
)
imu_data1.pack(pady=2)

imu_data2 = ctk.CTkLabel(
    imu_box,
    text="Data 2",
    font=("Arial", 14)
)
imu_data2.pack(pady=2)

imu_data3 = ctk.CTkLabel(
    imu_box,
    text="Data 3",
    font=("Arial", 14)
)
imu_data3.pack(pady=2)

# =====================================================
# RUN FROM MAIN LOOP
# =====================================================
esp32_thread = threading.Thread(
    target=monitor_esp32,
    daemon=True
)

esp32_thread.start()


app.mainloop()
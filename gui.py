# =========================
# PIPELINE ROBOT GUI LAYOUT
# CustomTkinter
# =========================
import threading
import threading
from esp32_handler import connect_esp32, receive_message
import customtkinter as ctk
from camera_handler import start_camera, stop_camera
from aurdino_handler import (
    robot_forward,
    robot_backward,
    robot_stop,
    light_on,
    light_off,
    set_speed
)
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

# alert_label = ctk.CTkLabel(
#     alert_box,
#     text="ALERT",
#     font=("Arial", 20, "bold")
# )
# alert_label.pack(pady=10)

alert_label = ctk.CTkLabel(
    alert_box,
    text="SAFE",
    font=("Arial", 28, "bold"),
    text_color="green"
)

alert_label.pack(pady=30)

def monitor_esp32():

    connected = connect_esp32()

    if not connected:

        alert_label.configure(
            text="ESP32 OFFLINE",
            text_color="orange"
        )

        return

    while True:

        message = receive_message()

        if message == "CRACK_ALERT":

            alert_label.configure(
                text="⚠ CRACK DETECTED",
                text_color="red"
            )

        elif message == "SAFE":

            alert_label.configure(
                text="SAFE",
                text_color="green"
            )



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
# ===================================
# SPEED CONTROL
# ===================================

speed_value_label = ctk.CTkLabel(
    status_box,
    text="Speed : 5",
    font=("Arial", 16, "bold")
)

speed_value_label.pack(pady=(15, 5))


def update_speed(value):

    speed = int(float(value))

    speed_value_label.configure(
        text=f"Speed : {speed}"
    )

    set_speed(speed)


speed_slider = ctk.CTkSlider(
    status_box,
    from_=0,
    to=10,
    number_of_steps=10,
    command=update_speed
)

speed_slider.set(3)

speed_slider.pack(
    padx=15,
    pady=10,
    fill="x"
)

# THIRD BOX
third_box = ctk.CTkFrame(left_frame, corner_radius=12)
third_box.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

third_label = ctk.CTkLabel(
    third_box,
    text="FUTURE BOX",
    font=("Arial", 20, "bold")
)
third_label.pack(pady=10)

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

# VERY IMPORTANT
result_frame.grid_propagate(False)

result_label = ctk.CTkLabel(
    result_frame,
    text="AI PREDICTED RESULT",
    font=("Arial", 28, "bold")
)

result_label.pack(
    fill="both",
    expand=True
)
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
    hover_color="#00C9FF"
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

encoder_box = ctk.CTkFrame(right_frame, corner_radius=12)
encoder_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

encoder_title = ctk.CTkLabel(
    encoder_box,
    text="ENCODER",
    font=("Arial", 18, "bold")
)
encoder_title.pack(pady=5)

count_label = ctk.CTkLabel(
    encoder_box,
    text="Live Count : 0",
    font=("Arial", 16)
)
count_label.pack(pady=5)

distance_label = ctk.CTkLabel(
    encoder_box,
    text="Distance : 0 cm",
    font=("Arial", 16)
)
distance_label.pack(pady=5)

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
import cv2
from PIL import Image, ImageTk

# =========================================
# ESP32-CAM STREAM URL
# =========================================

ESP32_CAM_URL = "http://192.168.137.99:81/stream"

cap = None
camera_running = False


# =========================================
# START CAMERA
# =========================================

def start_camera(camera_label):

    global cap, camera_running

    if camera_running:
        return

    # Connect to ESP32-CAM stream
    cap = cv2.VideoCapture(ESP32_CAM_URL)

    if not cap.isOpened():

        print("Cannot connect to ESP32-CAM")

        return

    print("ESP32-CAM Connected")

    camera_running = True

    update_frame(camera_label)


# =========================================
# UPDATE FRAME
# =========================================

def update_frame(camera_label):

    global cap, camera_running

    if not camera_running or cap is None:
        return

    ret, frame = cap.read()

    if ret:

        # Convert BGR → RGB
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Get label size
        width = camera_label.winfo_width()
        height = camera_label.winfo_height()

        # Prevent zero-size crash
        if width < 10 or height < 10:
            width = 640
            height = 480

        # Resize frame
        frame = cv2.resize(
            frame,
            (width, height)
        )

        # Convert to PIL image
        img = Image.fromarray(frame)

        # Convert to Tkinter image
        imgtk = ImageTk.PhotoImage(image=img)

        # Update GUI label
        camera_label.configure(
            image=imgtk,
            text=""
        )

        # Keep reference
        camera_label.image = imgtk

    # Repeat continuously
    camera_label.after(
        10,
        lambda: update_frame(camera_label)
    )


# =========================================
# STOP CAMERA
# =========================================

def stop_camera(camera_label):

    global cap, camera_running

    camera_running = False

    if cap is not None:

        cap.release()

        cap = None

    # Clear GUI image
    camera_label.configure(
        image="",
        text="LIVE CAMERA",
        font=("Arial", 28, "bold")
    )

    camera_label.image = None

    cv2.destroyAllWindows()

    print("ESP32-CAM Stopped")
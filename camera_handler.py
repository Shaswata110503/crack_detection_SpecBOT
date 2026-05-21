import cv2
from PIL import Image, ImageTk

cap = None
camera_running = False


# =========================================
# START CAMERA
# =========================================
def start_camera(camera_label):

    global cap, camera_running

    if camera_running:
        return

    cap = cv2.VideoCapture(0)

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
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize frame
        width = camera_label.winfo_width()
        height = camera_label.winfo_height()

        frame = cv2.resize(frame, (width, height))

        # Convert to PIL image
        img = Image.fromarray(frame)

        # Convert to Tkinter image
        imgtk = ImageTk.PhotoImage(image=img)

        # Update label
        camera_label.configure(
            image=imgtk,
            text=""
        )

        # Keep reference
        camera_label.image = imgtk

    # Repeat
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

    # Clear image safely
    camera_label.configure(
        image="",
        text="LIVE CAMERA",
        font=("Arial", 28, "bold")
    )

    camera_label.image = None

    cv2.destroyAllWindows()
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# Load model
model = tf.keras.models.load_model(r"C:\Users\desha\OneDrive\Desktop\ZYRO_CNN_M\crack_detection_model2.keras")

class_names = ['Healthy_pipes', 'cracked']

def predict_image(img_path):

    img = image.load_img(
        img_path,
        target_size=(256,256)
    )

    img_array = image.img_to_array(img)

    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)

    predicted_class = class_names[np.argmax(prediction)]

    confidence = round(100 * np.max(prediction), 2)

    return predicted_class, confidence


# # ==========================================
# # TEST
# # ==========================================

# img_path = r"C:\Users\desha\Downloads\WhatsApp Image 2026-05-30 at 13.08.52.jpeg"

# result, confidence = predict_image(img_path)

# print("Prediction:", result)
# print("Confidence:", confidence, "%")
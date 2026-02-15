import urllib.request
import os

model_url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
model_path = "pose_landmarker_lite.task"

if not os.path.exists(model_path):
    print("Downloading pose landmarker model...")
    try:
        urllib.request.urlretrieve(model_url, model_path)
        print(f"✓ Model downloaded successfully to {model_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Please download manually from:")
        print(model_url)
else:
    print(f"✓ Model already exists at {model_path}")
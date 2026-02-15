from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from videoAnalyzer import analyze_video
from aisummarizer import summarize_feedback

import os
import tempfile
import cv2

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision



REFERENCE_VIDEO = os.path.join(os.path.dirname(__file__), "models", "shoulder_press_reference.mp4") #This is for the video upload 


app = FastAPI(title="Pushup Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "pose_landmarker_lite.task")

@app.get("/health")
def health():
    return {"ok": True, "modelFound": os.path.exists(MODEL_PATH)}

def run_pose_on_video(video_path: str):
    if not os.path.exists(MODEL_PATH):
        return {"error": f"Model not found at {MODEL_PATH}. Download the .task model into backend/models/"}

    # Create PoseLandmarker (VIDEO mode)
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1
    )
    landmarker = vision.PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    frames_processed = 0
    frames_with_pose = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frames_processed += 1

            # OpenCV gives BGR; convert to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # timestamp in ms required for VIDEO mode
            timestamp_ms = int((frames_processed / fps) * 1000)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                frames_with_pose += 1

        return {
            "framesProcessed": frames_processed,
            "framesWithPose": frames_with_pose
        }

    finally:
        cap.release()
        landmarker.close()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[-1].lower() or ".mp4"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        video_path = tmp.name
        tmp.write(await file.read())

    try:
        result = analyze_video(video_path)
        result["filename"] = file.filename

        ai_summary = summarize_feedback(result)
        result["ai_summary"] = ai_summary

        return JSONResponse(result)
    finally:
        try:
            os.remove(video_path)
        except Exception:
            pass

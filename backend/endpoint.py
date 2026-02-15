from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from videoAnalyzer import analyze_video
from aisummarizer import summarize_feedback

import os
import tempfile
import cv2
import logging

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REFERENCE_VIDEO = os.path.join(os.path.dirname(__file__), "models", "shoulder_press_reference.mp4")

app = FastAPI(title="Pushup Analyzer API")

# CRITICAL: Custom middleware BEFORE everything else to catch ALL requests
@app.middleware("http")
async def universal_cors_handler(request: Request, call_next):
    """Catch-all CORS handler - runs before everything"""
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    # Handle OPTIONS immediately
    if request.method == "OPTIONS":
        logger.info("Handling OPTIONS preflight request")
        return Response(
            content="",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "86400",  # 24 hours
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add CORS headers to ALL responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    logger.info(f"Response status: {response.status_code}")
    return response

# Add standard CORS middleware as backup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "pose_landmarker_lite.task")

@app.get("/")
def root():
    return {"message": "Fitness Analyzer API", "status": "running"}

@app.get("/health")
def health():
    return {"ok": True, "modelFound": os.path.exists(MODEL_PATH)}

def run_pose_on_video(video_path: str):
    if not os.path.exists(MODEL_PATH):
        return {"error": f"Model not found at {MODEL_PATH}. Download the .task model into backend/models/"}

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
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
    """Analyze uploaded video for form feedback"""
    
    logger.info(f"=== ANALYZE ENDPOINT HIT ===")
    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")
    
    suffix = os.path.splitext(file.filename)[-1].lower() or ".mp4"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        video_path = tmp.name
        content = await file.read()
        file_size = len(content)
        logger.info(f"File size: {file_size / 1024:.2f} KB ({file_size / (1024*1024):.2f} MB)")
        tmp.write(content)

    try:
        logger.info(f"Analyzing video at: {video_path}")
        result = analyze_video(video_path)
        result["filename"] = file.filename
        result["file_size_kb"] = round(file_size / 1024, 2)

        logger.info("Video analysis complete, generating AI summary...")
        ai_summary = summarize_feedback(result)
        result["ai_summary"] = ai_summary

        logger.info("Analysis successful!")
        return JSONResponse(
            content=result,
            headers={
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": str(e), "type": type(e).__name__},
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
            }
        )
    finally:
        try:
            os.remove(video_path)
            logger.info(f"Cleaned up temp file: {video_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file: {e}")

# Debug endpoint
@app.get("/analyze")
async def analyze_get_debug():
    return JSONResponse({
        "error": "This endpoint requires POST with a video file",
        "usage": "POST /analyze with multipart/form-data containing 'file' field"
    })
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import tempfile
import os
import cv2
import numpy as np
import mediapipe as mp

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

@app.get("/health")
def health():
    return {"ok": True}

mp_pose = mp.solutions.pose

def angle_deg(a, b, c) -> float:
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    c = np.array(c, dtype=np.float32)
    ba = a - b
    bc = c - b
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-8
    cosang = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def analyze_video(video_path: str):
    UP_TH = 160.0
    DOWN_TH = 95.0
    MIN_VIS = 0.5

    reps = 0
    state = "UP"
    down_reached = False

    min_elbow = 180.0
    max_flare = 0.0
    top_elbow = 0.0

    rep_summaries = []

    cap = cv2.VideoCapture(video_path)

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)
            if not res.pose_landmarks:
                continue

            lm = res.pose_landmarks.landmark

            s = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            e = lm[mp_pose.PoseLandmark.LEFT_ELBOW]
            w = lm[mp_pose.PoseLandmark.LEFT_WRIST]
            h = lm[mp_pose.PoseLandmark.LEFT_HIP]

            if min(s.visibility, e.visibility, w.visibility, h.visibility) < MIN_VIS:
                continue

            shoulder = (s.x, s.y)
            elbow = (e.x, e.y)
            wrist = (w.x, w.y)
            hip = (h.x, h.y)

            elbow_angle = angle_deg(shoulder, elbow, wrist)
            flare_angle = angle_deg(elbow, shoulder, hip)

            min_elbow = min(min_elbow, elbow_angle)
            max_flare = max(max_flare, flare_angle)
            top_elbow = max(top_elbow, elbow_angle)

            if state == "UP":
                if elbow_angle < DOWN_TH:
                    state = "DOWN"
                    down_reached = True
            else:  # DOWN
                if elbow_angle > UP_TH and down_reached:
                    reps += 1

                    reasons = []
                    if max_flare > 70:
                        reasons.append("elbows flaring sideways")
                    if top_elbow < UP_TH:
                        reasons.append("not fully extending at the top")
                    if min_elbow > DOWN_TH:
                        reasons.append("not going low enough")

                    grade = "good" if not reasons else "bad"

                    rep_summaries.append({
                        "rep": reps,
                        "minElbowAngle": round(min_elbow, 1),
                        "maxFlareAngle": round(max_flare, 1),
                        "topElbowAngle": round(top_elbow, 1),
                        "grade": grade,
                        "reasons": reasons[:2],
                    })

                    state = "UP"
                    down_reached = False
                    min_elbow = 180.0
                    max_flare = 0.0
                    top_elbow = 0.0

    cap.release()
    return {"totalReps": reps, "repSummaries": rep_summaries}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[-1].lower() or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        tmp.write(await file.read())

    try:
        result = analyze_video(tmp_path)
        return JSONResponse(result)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

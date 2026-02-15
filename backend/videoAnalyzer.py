import cv2
import numpy as np
import PoseModule as pm

# ========================================
# YOUR SPECIFIED THRESHOLDS
# ========================================

# REP COUNTING (Very Lenient)
EXTENSION_THRESHOLD = 150      # Easy to trigger
BENT_THRESHOLD = 120           # Very lenient
WRIST_CLEARANCE = 10           # Good
ELBOW_TOLERANCE = 170          # Way too lenient - arms can be anywhere

# SWEET SPOT
SWEET_SPOT_MIN = 70            # Too low
SWEET_SPOT_MAX = 90            # Good

# FORM GRADING
FEEDBACK_MAX_ELBOW = 155       # Good
FEEDBACK_DIFF = 20             # Good
FEEDBACK_SHOULDER = 180        # Way too lenient

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Could not open video file"}
    
    detector = pm.poseDetector()
    count = 0
    direction = 0
    form = 0
    
    rep_min_elbow = []
    rep_max_elbow = []
    rep_max_diff = []
    rep_max_shoulder = []
    
    min_elbow = 180
    max_elbow = 0
    max_diff = 0
    max_shoulder = 0
    
    rep_feedbacks = []
    
    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break
        
        img = cv2.flip(img, 1)
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        
        if len(lmList) != 0:
            # LEFT SIDE
            left_elbow = detector.findAngle(img, 11, 13, 15)
            left_shoulder = detector.findAngle(img, 13, 11, 23)
            
            # RIGHT SIDE
            right_elbow = detector.findAngle(img, 12, 14, 16)
            right_shoulder = detector.findAngle(img, 24, 12, 14)
            
            avg_elbow = (left_elbow + right_elbow) / 2
            elbow_diff = abs(left_elbow - right_elbow)
            max_shoulder_current = max(left_shoulder, right_shoulder)
            
            # Vertical checks (using your specified thresholds)
            left_wrist_y = lmList[15][2]
            left_elbow_y = lmList[13][2]
            right_wrist_y = lmList[16][2]
            right_elbow_y = lmList[14][2]
            
            wrists_above_elbows = (left_wrist_y < left_elbow_y - WRIST_CLEARANCE) and \
                                  (right_wrist_y < right_elbow_y - WRIST_CLEARANCE)
            
            left_shoulder_y = lmList[11][2]
            right_shoulder_y = lmList[12][2]
            
            elbows_at_shoulder_height = (left_elbow_y <= left_shoulder_y + ELBOW_TOLERANCE) and \
                                        (right_elbow_y <= right_shoulder_y + ELBOW_TOLERANCE)
            
            # Track values
            min_elbow = min(min_elbow, avg_elbow)
            max_elbow = max(max_elbow, avg_elbow)
            max_diff = max(max_diff, elbow_diff)
            max_shoulder = max(max_shoulder, max_shoulder_current)
            
            # Shoulder press logic (using your specified thresholds)
            if avg_elbow > EXTENSION_THRESHOLD and wrists_above_elbows and elbows_at_shoulder_height:
                form = 1
            
            if form == 1:
                if avg_elbow < BENT_THRESHOLD and direction == 0 and elbows_at_shoulder_height:
                    direction = 1
                
                if avg_elbow > EXTENSION_THRESHOLD and direction == 1 and wrists_above_elbows and elbows_at_shoulder_height:
                    count += 1
                    direction = 0
                    
                    # Feedback for this rep (using your specified thresholds)
                    feedback_items = []
                    
                    # Sweet spot check
                    if min_elbow > SWEET_SPOT_MAX:
                        feedback_items.append(f"Not deep enough ({min_elbow:.0f}°)")
                    elif min_elbow < SWEET_SPOT_MIN:
                        feedback_items.append(f"Too deep ({min_elbow:.0f}°) - upper chest")
                    else:
                        feedback_items.append(f"Perfect depth ({min_elbow:.0f}°)")
                    
                    # Other form checks
                    if max_elbow < FEEDBACK_MAX_ELBOW:
                        feedback_items.append(f"Did not fully extend ({max_elbow:.0f}°)")
                    if max_diff > FEEDBACK_DIFF:
                        feedback_items.append(f"Arms uneven ({max_diff:.0f}°)")
                    if max_shoulder > FEEDBACK_SHOULDER:
                        feedback_items.append(f"Elbows flaring ({max_shoulder:.0f}°)")
                    
                    # Check if perfect rep
                    is_perfect = (SWEET_SPOT_MIN <= min_elbow <= SWEET_SPOT_MAX and 
                                 max_elbow >= FEEDBACK_MAX_ELBOW and 
                                 max_diff <= FEEDBACK_DIFF and 
                                 max_shoulder <= FEEDBACK_SHOULDER)
                    
                    feedback = "✓ Perfect form!" if is_perfect else " | ".join(feedback_items)
                    rep_feedbacks.append(feedback)
                    
                    rep_min_elbow.append(min_elbow)
                    rep_max_elbow.append(max_elbow)
                    rep_max_diff.append(max_diff)
                    rep_max_shoulder.append(max_shoulder)
                    
                    # Reset trackers
                    min_elbow = 180
                    max_elbow = 0
                    max_diff = 0
                    max_shoulder = 0
                
                if not elbows_at_shoulder_height:
                    form = 0
                    direction = 0
                    min_elbow = 180
                    max_elbow = 0
                    max_diff = 0
                    max_shoulder = 0
    
    cap.release()
    
    if count == 0:
        good_reps = 0
        sweet_spot_reps = 0
    else:
        good_reps = sum([1 for fb in rep_feedbacks if fb == "✓ Perfect form!"])
        sweet_spot_reps = sum([1 for elbow in rep_min_elbow if SWEET_SPOT_MIN <= elbow <= SWEET_SPOT_MAX])
    
    result = {
        "totalReps": count,
        "perfectFormReps": good_reps,
        "sweetSpotReps": sweet_spot_reps,
        "repMetrics": [
            {
                "rep": i + 1,
                "minElbow": round(rep_min_elbow[i], 1),
                "maxElbow": round(rep_max_elbow[i], 1),
                "maxDiff": round(rep_max_diff[i], 1),
                "maxShoulder": round(rep_max_shoulder[i], 1),
                "feedback": rep_feedbacks[i],
                "inSweetSpot": SWEET_SPOT_MIN <= rep_min_elbow[i] <= SWEET_SPOT_MAX
            }
            for i in range(count)
        ],
        "avgMinElbow": round(np.mean(rep_min_elbow), 1) if rep_min_elbow else None,
        "avgMaxElbow": round(np.mean(rep_max_elbow), 1) if rep_max_elbow else None,
        "avgElbowDiff": round(np.mean(rep_max_diff), 1) if rep_max_diff else None,
        "avgMaxShoulder": round(np.mean(rep_max_shoulder), 1) if rep_max_shoulder else None,
        "thresholds": {
            "extension": EXTENSION_THRESHOLD,
            "bent": BENT_THRESHOLD,
            "sweetSpotMin": SWEET_SPOT_MIN,
            "sweetSpotMax": SWEET_SPOT_MAX,
            "feedbackMaxElbow": FEEDBACK_MAX_ELBOW,
            "feedbackDiff": FEEDBACK_DIFF,
            "feedbackShoulder": FEEDBACK_SHOULDER
        }
    }
    
    return result
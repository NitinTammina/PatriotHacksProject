import cv2
import numpy as np
import PoseModule as pm

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

            # Vertical checks
            left_wrist_y = lmList[15][2]
            left_elbow_y = lmList[13][2]
            right_wrist_y = lmList[16][2]
            right_elbow_y = lmList[14][2]

            wrists_above_elbows = (left_wrist_y < left_elbow_y - 20) and \
                                  (right_wrist_y < right_elbow_y - 20)

            left_shoulder_y = lmList[11][2]
            right_shoulder_y = lmList[12][2]

            elbows_at_shoulder_height = (left_elbow_y <= left_shoulder_y + 50) and \
                                        (right_elbow_y <= right_shoulder_y + 50)

            # Track values
            min_elbow = min(min_elbow, avg_elbow)
            max_elbow = max(max_elbow, avg_elbow)
            max_diff = max(max_diff, elbow_diff)
            max_shoulder = max(max_shoulder, max_shoulder_current)

            # Shoulder press logic
            if avg_elbow > 160 and wrists_above_elbows and elbows_at_shoulder_height:
                form = 1

            if form == 1:
                if avg_elbow < 90 and direction == 0 and elbows_at_shoulder_height:
                    direction = 1

                if avg_elbow > 160 and direction == 1 and wrists_above_elbows and elbows_at_shoulder_height:
                    count += 1
                    direction = 0

                    # Feedback for this rep
                    feedback_items = []
                    if min_elbow > 100:
                        feedback_items.append("Not deep enough")
                    if max_elbow < 160:
                        feedback_items.append("Did not fully extend")
                    if max_diff > 15:
                        feedback_items.append("Arms uneven")
                    if max_shoulder > 70:
                        feedback_items.append("Elbows flaring")
                    feedback = "✓ Good rep!" if not feedback_items else ", ".join(feedback_items)
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
    else:
        good_reps = sum([1 for fb in rep_feedbacks if fb == "✓ Good rep!"])

    result = {
        "totalReps": count,
        "goodReps": good_reps,
        "repMetrics": [
            {
                "rep": i + 1,
                "minElbow": rep_min_elbow[i],
                "maxElbow": rep_max_elbow[i],
                "maxDiff": rep_max_diff[i],
                "maxShoulder": rep_max_shoulder[i],
                "feedback": rep_feedbacks[i]
            }
            for i in range(count)
        ],
        "avgMinElbow": np.mean(rep_min_elbow) if rep_min_elbow else None,
        "avgMaxElbow": np.mean(rep_max_elbow) if rep_max_elbow else None,
        "avgElbowDiff": np.mean(rep_max_diff) if rep_max_diff else None,
        "avgMaxShoulder": np.mean(rep_max_shoulder) if rep_max_shoulder else None
    }

    return result

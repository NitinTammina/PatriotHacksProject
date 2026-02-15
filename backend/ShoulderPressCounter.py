import cv2 as cv2
import mediapipe as mp
import numpy as np
import PoseModule as pm



cap = cv2.VideoCapture(0)
detector = pm.poseDetector()

count = 0
direction = 0
form = 0

# Store metrics per rep
rep_min_elbow = []
rep_max_elbow = []
rep_max_diff = []
rep_max_shoulder = []

# Temporary trackers during a rep
min_elbow = 180
max_elbow = 0
max_diff = 0
max_shoulder = 0

while cap.isOpened():
    ret, img = cap.read() #640 x 480
    #Determine dimensions of video - Help with creation of box in Line 43
    width  = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    # print(width, height)
    
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    # print(lmList)


    if len(lmList) != 0:

        # LEFT_SIDE
        left_elbow = detector.findAngle(img, 11, 13, 15)
        left_shoulder = detector.findAngle(img, 13, 11, 23)

        #RIGHT_SIDE
        right_elbow = detector.findAngle(img, 12, 14, 16)
        right_shoulder = detector.findAngle(img, 24, 12, 14)
        
        #average elbow angle
        avg_elbow = (left_elbow + right_elbow) / 2 
        elbow_diff = abs(left_elbow - right_elbow)
        max_shoulder_current = max(left_shoulder, right_shoulder)

        # Track Values for current rep
        min_elbow = min(min_elbow, avg_elbow)
        max_elbow = max(max_elbow, avg_elbow)
        max_diff = max(max_diff, elbow_diff)
        max_shoulder = max(max_shoulder, max_shoulder_current)

        # -------------------------------
        # Shoulder Press Logic
        # -------------------------------
        # Start position (arms extended)
        if avg_elbow > 160:
            form = 1

        if form == 1:
            # Down phase
            if avg_elbow < 90 and direction == 0:
                direction = 1

            # Up phase → rep completed
            if avg_elbow > 160 and direction == 1:
                count += 1
                direction = 0

                # Save metrics for this rep
                rep_min_elbow.append(min_elbow)
                rep_max_elbow.append(max_elbow)
                rep_max_diff.append(max_diff)
                rep_max_shoulder.append(max_shoulder)

                # Reset temporary trackers
                min_elbow = 180
                max_elbow = 0
                max_diff = 0
                max_shoulder = 0

        # -------------------------------
        # Progress bar (optional)
        # -------------------------------

        per = np.interp(avg_elbow, (90, 160), (0, 100))
        bar = np.interp(avg_elbow, (90, 160), (380, 50))

        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)

        cv2.imshow('Shoulder Press Tracker', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        
print("\n=== Shoulder Press Set Summary ===\n")
for i in range(len(rep_min_elbow)):
    feedback = "Good rep!"

    if rep_min_elbow[i] > 100:
        feedback = f"Rep {i+1}: Not deep enough"
    elif rep_max_elbow[i] < 160:
        feedback = f"Rep {i+1}: Did not fully extend"
    elif rep_max_diff[i] > 15:
        feedback = f"Rep {i+1}: Arms uneven"
    elif rep_max_shoulder[i] > 70:
        feedback = f"Rep {i+1}: Elbows flaring"

    print(feedback)
 
cap.release()
cv2.destroyAllWindows()
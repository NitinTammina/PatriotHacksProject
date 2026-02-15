import cv2 as cv2
import mediapipe as mp
import numpy as np
import PoseModule as pm

# ========================================
# WEBCAM VERSION - Live Testing
# ========================================
cap = cv2.VideoCapture(0)

# Check if webcam opened successfully
if not cap.isOpened():
    print("Error: Could not access webcam")
    print("Please check your camera connection and permissions.")
    exit()

print("\n=== Shoulder Press Webcam Tracker ===")
print("Controls:")
print("  'q' - Quit")
print("  'r' - Reset counter")
print("  's' - Save current session report")
print("\nPosition yourself so your full upper body is visible")
print("Start with arms extended overhead\n")

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
    ret, img = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    
    # Flip image for mirror effect (more intuitive)
    img = cv2.flip(img, 1)
    
    width = cap.get(3)
    height = cap.get(4)
    
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    
    if len(lmList) != 0:
        # LEFT SIDE
        left_elbow = detector.findAngle(img, 11, 13, 15)
        left_shoulder = detector.findAngle(img, 13, 11, 23)
        
        # RIGHT SIDE
        right_elbow = detector.findAngle(img, 12, 14, 16)
        right_shoulder = detector.findAngle(img, 24, 12, 14)
        
        # Average elbow angle
        avg_elbow = (left_elbow + right_elbow) / 2
        elbow_diff = abs(left_elbow - right_elbow)
        max_shoulder_current = max(left_shoulder, right_shoulder)
        
        # =======================================
        # Vertical position checks
        # =======================================
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
        
        # Track values for current rep
        min_elbow = min(min_elbow, avg_elbow)
        max_elbow = max(max_elbow, avg_elbow)
        max_diff = max(max_diff, elbow_diff)
        max_shoulder = max(max_shoulder, max_shoulder_current)
        
        # -------------------------------
        # Shoulder Press Logic
        # -------------------------------
        if avg_elbow > 160 and wrists_above_elbows and elbows_at_shoulder_height:
            form = 1
        
        if form == 1:
            if avg_elbow < 90 and direction == 0 and elbows_at_shoulder_height:
                direction = 1
            
            if avg_elbow > 160 and direction == 1 and wrists_above_elbows and elbows_at_shoulder_height:
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
            
            if not elbows_at_shoulder_height:
                form = 0
                direction = 0
                min_elbow = 180
                max_elbow = 0
                max_diff = 0
                max_shoulder = 0
        
        # -------------------------------
        # Enhanced Visual Feedback
        # -------------------------------
        # Status indicator
        status_text = "Ready" if form == 0 else ("Down" if direction == 1 else "Up")
        status_color = (0, 255, 0) if form == 1 else (0, 165, 255)
        cv2.putText(img, status_text, (10, 40), 
                    cv2.FONT_HERSHEY_PLAIN, 2, status_color, 3)
        
        # Real-time angle display
        cv2.putText(img, f"Elbow: {int(avg_elbow)}", (10, 80),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        cv2.putText(img, f"Diff: {int(elbow_diff)}", (10, 110),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        
        # Position check indicators
        check_y = 140
        if wrists_above_elbows:
            cv2.putText(img, "Wrists: OK", (10, check_y),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
        else:
            cv2.putText(img, "Wrists: LOW", (10, check_y),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 2)
        
        check_y += 30
        if elbows_at_shoulder_height:
            cv2.putText(img, "Elbows: OK", (10, check_y),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
        else:
            cv2.putText(img, "Elbows: LOW", (10, check_y),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 2)
        
        # Progress bar
        per = np.interp(avg_elbow, (90, 160), (0, 100))
        bar = np.interp(avg_elbow, (90, 160), (380, 50))
        
        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        
        # Rep counter (large display)
        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)
        
        # Instructions
        cv2.putText(img, "Press 'r' to reset | 's' to save | 'q' to quit", 
                    (120, 470), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    else:
        # No pose detected
        cv2.putText(img, "No pose detected - step back!", (100, 240),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    cv2.imshow('Shoulder Press Tracker', img)
    
    # Key controls
    key = cv2.waitKey(10) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        # Reset counter
        count = 0
        rep_min_elbow = []
        rep_max_elbow = []
        rep_max_diff = []
        rep_max_shoulder = []
        min_elbow = 180
        max_elbow = 0
        max_diff = 0
        max_shoulder = 0
        form = 0
        direction = 0
        print("\n>>> Counter reset!\n")
    elif key == ord('s'):
        # Save current session
        print("\n" + "="*50)
        print("=== SESSION REPORT ===")
        print("="*50)
        print(f"\nTotal Reps: {count}")
        
        if len(rep_min_elbow) > 0:
            good_reps = 0
            for i in range(len(rep_min_elbow)):
                feedback_items = []
                
                if rep_min_elbow[i] > 100:
                    feedback_items.append("Not deep enough")
                if rep_max_elbow[i] < 160:
                    feedback_items.append("Did not fully extend")
                if rep_max_diff[i] > 15:
                    feedback_items.append("Arms uneven")
                if rep_max_shoulder[i] > 70:
                    feedback_items.append("Elbows flaring")
                
                if not feedback_items:
                    feedback = "✓ Good rep!"
                    good_reps += 1
                else:
                    feedback = ", ".join(feedback_items)
                
                print(f"\nRep {i+1}: {feedback}")
                print(f"  Min Elbow: {rep_min_elbow[i]:.1f}°")
                print(f"  Max Elbow: {rep_max_elbow[i]:.1f}°")
            
            print(f"\n--- Summary ---")
            print(f"Good Reps: {good_reps}/{count} ({100*good_reps/count:.1f}%)")
        print("\n" + "="*50 + "\n")

# ========================================
# FINAL REPORT
# ========================================
print("\n" + "="*50)
print("=== FINAL SHOULDER PRESS REPORT ===")
print("="*50)

print(f"\nTotal Reps Completed: {count}")

if len(rep_min_elbow) > 0:
    print("\n--- Rep-by-Rep Analysis ---\n")
    
    good_reps = 0
    for i in range(len(rep_min_elbow)):
        feedback_items = []
        
        if rep_min_elbow[i] > 100:
            feedback_items.append("⚠️ Not deep enough")
        if rep_max_elbow[i] < 160:
            feedback_items.append("⚠️ Did not fully extend")
        if rep_max_diff[i] > 15:
            feedback_items.append("⚠️ Arms uneven")
        if rep_max_shoulder[i] > 70:
            feedback_items.append("⚠️ Elbows flaring")
        
        if not feedback_items:
            feedback = "✓ Good rep!"
            good_reps += 1
        else:
            feedback = ", ".join(feedback_items)
        
        print(f"Rep {i+1}:")
        print(f"  Min Elbow: {rep_min_elbow[i]:.1f}°")
        print(f"  Max Elbow: {rep_max_elbow[i]:.1f}°")
        print(f"  Max Difference: {rep_max_diff[i]:.1f}°")
        print(f"  Max Shoulder: {rep_max_shoulder[i]:.1f}°")
        print(f"  Feedback: {feedback}\n")
    
    print("\n--- Overall Statistics ---")
    print(f"Good Reps: {good_reps}/{count} ({100*good_reps/count:.1f}%)")
    print(f"Average Min Elbow: {np.mean(rep_min_elbow):.1f}°")
    print(f"Average Max Elbow: {np.mean(rep_max_elbow):.1f}°")
    print(f"Average Elbow Difference: {np.mean(rep_max_diff):.1f}°")
    print(f"Average Max Shoulder: {np.mean(rep_max_shoulder):.1f}°")
else:
    print("\nNo reps detected.")

print("\n" + "="*50)

cap.release()
cv2.destroyAllWindows()
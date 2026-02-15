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
print("SWEET SPOT: Lower to 85-98° for optimal shoulder activation")
print("   • Above 98° = Not deep enough")
print("   • 85-98° = Perfect depth!")
print("   • Below 85° = Too deep (upper chest focus)\n")

detector = pm.poseDetector()
count = 0
direction = 0  # 0 = up position, 1 = down position
form = 0       # 0 = not started, 1 = exercise in progress

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

# ========================================
# LENIENT REP COUNTING THRESHOLDS
# ========================================
EXTENSION_THRESHOLD = 150      # Easy to reach "extended" position
BENT_THRESHOLD = 120           # Don't need to go super deep to count
WRIST_CLEARANCE = 10           # Minimal clearance needed
ELBOW_TOLERANCE = 170           # Generous tolerance for elbow height

# ========================================
# SWEET SPOT DETECTION
# ========================================
SWEET_SPOT_MIN = 70            # Below this = too deep (upper chest)
SWEET_SPOT_MAX = 90            # Above this = not deep enough

# ========================================
# STRICT FORM GRADING THRESHOLDS
# ========================================
FEEDBACK_MAX_ELBOW = 155       # Should fully extend to 160° (strict)
FEEDBACK_DIFF = 20             # Arms should be even (strict symmetry)
FEEDBACK_SHOULDER = 180       # Elbows shouldn't flare much (strict)

while cap.isOpened():
    ret, img = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    
    # Flip image for mirror effect
    img = cv2.flip(img, 1)
    
    width = cap.get(3)
    height = cap.get(4)
    
    # Get pose landmarks
    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    
    if len(lmList) != 0:
        # =======================================
        # STEP 1: Get landmark positions
        # =======================================
        left_wrist_y = lmList[15][2]
        left_elbow_y = lmList[13][2]
        left_shoulder_y = lmList[11][2]
        
        right_wrist_y = lmList[16][2]
        right_elbow_y = lmList[14][2]
        right_shoulder_y = lmList[12][2]
        
        # =======================================
        # STEP 2: Calculate joint angles
        # =======================================
        left_elbow = detector.findAngle(img, 11, 13, 15)
        right_elbow = detector.findAngle(img, 12, 14, 16)
        avg_elbow = (left_elbow + right_elbow) / 2
        elbow_diff = abs(left_elbow - right_elbow)
        
        left_shoulder = detector.findAngle(img, 13, 11, 23)
        right_shoulder = detector.findAngle(img, 24, 12, 14)
        max_shoulder_current = max(left_shoulder, right_shoulder)
        
        # =======================================
        # STEP 3: Check positions (LENIENT for counting)
        # =======================================
        left_wrist_above = left_wrist_y < (left_elbow_y - WRIST_CLEARANCE)
        right_wrist_above = right_wrist_y < (right_elbow_y - WRIST_CLEARANCE)
        wrists_above_elbows = left_wrist_above and right_wrist_above
        
        left_elbow_high = left_elbow_y <= (left_shoulder_y + ELBOW_TOLERANCE)
        right_elbow_high = right_elbow_y <= (right_shoulder_y + ELBOW_TOLERANCE)
        elbows_at_shoulder_height = left_elbow_high and right_elbow_high
        
        # =======================================
        # STEP 4: Track metrics
        # =======================================
        min_elbow = min(min_elbow, avg_elbow)
        max_elbow = max(max_elbow, avg_elbow)
        max_diff = max(max_diff, elbow_diff)
        max_shoulder = max(max_shoulder, max_shoulder_current)
        
        # =======================================
        # STEP 5: LENIENT Rep counting
        # =======================================
        
        # Arms extended overhead? (LENIENT: 150°)
        if avg_elbow > EXTENSION_THRESHOLD and wrists_above_elbows and elbows_at_shoulder_height:
            form = 1
        
        if form == 1:
            # Down phase (LENIENT: only to 100°)
            if avg_elbow < BENT_THRESHOLD and direction == 0 and elbows_at_shoulder_height:
                direction = 1
            
            # Rep completed (LENIENT: back to 150°)
            if avg_elbow > EXTENSION_THRESHOLD and direction == 1 and wrists_above_elbows and elbows_at_shoulder_height:
                count += 1
                direction = 0
                
                # Save rep data
                rep_min_elbow.append(min_elbow)
                rep_max_elbow.append(max_elbow)
                rep_max_diff.append(max_diff)
                rep_max_shoulder.append(max_shoulder)
                
                # Reset trackers
                min_elbow = 180
                max_elbow = 0
                max_diff = 0
                max_shoulder = 0
            
            # Reset if arms drop too low
            if not elbows_at_shoulder_height:
                form = 0
                direction = 0
                min_elbow = 180
                max_elbow = 0
                max_diff = 0
                max_shoulder = 0
        
        # =======================================
        # STEP 6: Real-time Sweet Spot Indicator
        # =======================================
        depth_status = ""
        depth_color = (255, 255, 255)
        
        if form == 1 and direction == 1:  # Only show when in down phase
            if avg_elbow > SWEET_SPOT_MAX:
                depth_status = "Go deeper!"
                depth_color = (0, 165, 255)  # Orange
            elif avg_elbow < SWEET_SPOT_MIN:
                depth_status = "Too deep!"
                depth_color = (0, 0, 255)  # Red
            else:
                depth_status = "PERFECT DEPTH!"
                depth_color = (0, 255, 0)  # Green
        
        # =======================================
        # STEP 7: Visual Feedback
        # =======================================
        status_text = "Ready" if form == 0 else ("Down" if direction == 1 else "Up")
        status_color = (0, 255, 0) if form == 1 else (0, 165, 255)
        cv2.putText(img, status_text, (10, 40), 
                    cv2.FONT_HERSHEY_PLAIN, 2, status_color, 3)
        
        # Real-time angle display
        cv2.putText(img, f"Elbow: {int(avg_elbow)}", (10, 80),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        
        # Show sweet spot indicator during down phase
        if depth_status:
            cv2.putText(img, depth_status, (10, 110),
                        cv2.FONT_HERSHEY_PLAIN, 1.8, depth_color, 3)
        else:
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
        per = np.interp(avg_elbow, (BENT_THRESHOLD, EXTENSION_THRESHOLD), (0, 100))
        bar = np.interp(avg_elbow, (BENT_THRESHOLD, EXTENSION_THRESHOLD), (380, 50))
        
        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            
            # Add sweet spot zone marker on progress bar
            sweet_spot_top = np.interp(SWEET_SPOT_MAX, (BENT_THRESHOLD, EXTENSION_THRESHOLD), (380, 50))
            sweet_spot_bottom = np.interp(SWEET_SPOT_MIN, (BENT_THRESHOLD, EXTENSION_THRESHOLD), (380, 50))
            cv2.rectangle(img, (605, int(sweet_spot_top)), (610, int(sweet_spot_bottom)), (0, 255, 0), cv2.FILLED)
        
        # Rep counter
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
        print("\n" + "="*50)
        print("=== SESSION REPORT ===")
        print("="*50)
        print(f"\nTotal Reps: {count}")
        
        if len(rep_min_elbow) > 0:
            perfect_reps = 0
            for i in range(len(rep_min_elbow)):
                feedback_items = []
                
                # SWEET SPOT CHECK
                if rep_min_elbow[i] > SWEET_SPOT_MAX:
                    feedback_items.append(f"Not deep enough ({rep_min_elbow[i]:.0f}°) - need 85-98°")
                elif rep_min_elbow[i] < SWEET_SPOT_MIN:
                    feedback_items.append(f"Too deep ({rep_min_elbow[i]:.0f}°) - working upper chest now")
                else:
                    feedback_items.append(f"Perfect depth ({rep_min_elbow[i]:.0f}°) - sweet spot!")
                
                # OTHER FORM CHECKS
                if rep_max_elbow[i] < FEEDBACK_MAX_ELBOW:
                    feedback_items.append(f"Did not fully extend (reached {rep_max_elbow[i]:.0f}°, need 160°)")
                if rep_max_diff[i] > FEEDBACK_DIFF:
                    feedback_items.append(f"Arms uneven ({rep_max_diff[i]:.0f}° difference)")
                if rep_max_shoulder[i] > FEEDBACK_SHOULDER:
                    feedback_items.append(f"Elbows flaring ({rep_max_shoulder[i]:.0f}°, keep under 75°)")
                
                # Count perfect reps (in sweet spot + good form)
                is_perfect = (SWEET_SPOT_MIN <= rep_min_elbow[i] <= SWEET_SPOT_MAX and 
                             rep_max_elbow[i] >= FEEDBACK_MAX_ELBOW and 
                             rep_max_diff[i] <= FEEDBACK_DIFF and 
                             rep_max_shoulder[i] <= FEEDBACK_SHOULDER)
                
                if is_perfect:
                    perfect_reps += 1
                
                print(f"\nRep {i+1}:")
                for item in feedback_items:
                    print(f"  • {item}")
                print(f"  Stats: Min {rep_min_elbow[i]:.0f}° | Max {rep_max_elbow[i]:.0f}° | Diff {rep_max_diff[i]:.0f}° | Shoulder {rep_max_shoulder[i]:.0f}°")
            
            print(f"\n--- Summary ---")
            print(f"Perfect Form Reps: {perfect_reps}/{count} ({100*perfect_reps/count:.1f}%)")
            
            # Calculate how many hit sweet spot
            sweet_spot_reps = sum(1 for elbow in rep_min_elbow if SWEET_SPOT_MIN <= elbow <= SWEET_SPOT_MAX)
            print(f"Sweet Spot Reps (85-98°): {sweet_spot_reps}/{count} ({100*sweet_spot_reps/count:.1f}%)")
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
    
    perfect_reps = 0
    sweet_spot_reps = 0
    
    for i in range(len(rep_min_elbow)):
        feedback_items = []
        
        # SWEET SPOT CHECK
        if rep_min_elbow[i] > SWEET_SPOT_MAX:
            feedback_items.append(f"Not deep enough ({rep_min_elbow[i]:.0f}°) - need 85-98° sweet spot")
        elif rep_min_elbow[i] < SWEET_SPOT_MIN:
            feedback_items.append(f"Too deep ({rep_min_elbow[i]:.0f}°) - working upper chest now")
        else:
            feedback_items.append(f"PERFECT DEPTH ({rep_min_elbow[i]:.0f}°) - in the sweet spot!")
            sweet_spot_reps += 1
        
        # OTHER FORM CHECKS
        if rep_max_elbow[i] < FEEDBACK_MAX_ELBOW:
            feedback_items.append(f"Did not fully extend (reached {rep_max_elbow[i]:.0f}°, need 160°)")
        if rep_max_diff[i] > FEEDBACK_DIFF:
            feedback_items.append(f"Arms uneven ({rep_max_diff[i]:.0f}° difference)")
        if rep_max_shoulder[i] > FEEDBACK_SHOULDER:
            feedback_items.append(f"Elbows flaring ({rep_max_shoulder[i]:.0f}°)")
        
        # Count perfect reps
        is_perfect = (SWEET_SPOT_MIN <= rep_min_elbow[i] <= SWEET_SPOT_MAX and 
                     rep_max_elbow[i] >= FEEDBACK_MAX_ELBOW and 
                     rep_max_diff[i] <= FEEDBACK_DIFF and 
                     rep_max_shoulder[i] <= FEEDBACK_SHOULDER)
        
        if is_perfect:
            perfect_reps += 1
        
        print(f"Rep {i+1}:")
        for item in feedback_items:
            print(f"  • {item}")
        print(f"  Stats: Min {rep_min_elbow[i]:.0f}° | Max {rep_max_elbow[i]:.0f}° | Diff {rep_max_diff[i]:.0f}° | Shoulder {rep_max_shoulder[i]:.0f}°\n")
    
    print("\n--- Overall Statistics ---")
    print(f"Perfect Form Reps: {perfect_reps}/{count} ({100*perfect_reps/count:.1f}%)")
    print(f"Sweet Spot Reps (85-98°): {sweet_spot_reps}/{count} ({100*sweet_spot_reps/count:.1f}%)")
    print(f"Average Min Elbow: {np.mean(rep_min_elbow):.1f}°")
    print(f"Average Max Elbow: {np.mean(rep_max_elbow):.1f}°")
    print(f"Average Elbow Difference: {np.mean(rep_max_diff):.1f}°")
    print(f"Average Max Shoulder: {np.mean(rep_max_shoulder):.1f}°")
else:
    print("\nNo reps detected.")

print("\n" + "="*50)

cap.release()
cv2.destroyAllWindows()
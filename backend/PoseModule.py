import cv2
import math
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class poseDetector():
    
    def __init__(self, mode=False, complexity=1, smooth_landmarks=True,
                 enable_segmentation=False, smooth_segmentation=True,
                 detectionCon=0.5, trackCon=0.5):
        
        self.mode = mode 
        self.complexity = complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        # Create PoseLandmarker options
        base_options = python.BaseOptions(model_asset_path='pose_landmarker_lite.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=detectionCon,
            min_pose_presence_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )
        
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.results = None
        self.lmList = []
        self.frame_count = 0
        
        print("Pose detector initialized successfully with new MediaPipe Tasks API!")
        
    def findPose(self, img, draw=True):
        """Process the image and detect pose landmarks"""
        self.frame_count += 1
        
        # Convert to RGB and create MediaPipe Image
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
        
        # Process with timestamp
        timestamp_ms = int(self.frame_count * 33.33)  # Assuming ~30fps
        self.results = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        # Draw landmarks if requested
        if draw and self.results.pose_landmarks:
            self.draw_landmarks_on_image(img, self.results)
                
        return img
    
    def draw_landmarks_on_image(self, img, detection_result):
        """Custom drawing function for pose landmarks"""
        if not detection_result.pose_landmarks:
            return
        
        pose_landmarks = detection_result.pose_landmarks[0]
        h, w, c = img.shape
        
        # Define connections (pose skeleton)
        POSE_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
            (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
            (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
            (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (27, 29), (29, 31),
            (27, 31), (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
        ]
        
        # Draw connections
        for connection in POSE_CONNECTIONS:
            start_idx, end_idx = connection
            if start_idx < len(pose_landmarks) and end_idx < len(pose_landmarks):
                start_point = pose_landmarks[start_idx]
                end_point = pose_landmarks[end_idx]
                
                start_x, start_y = int(start_point.x * w), int(start_point.y * h)
                end_x, end_y = int(end_point.x * w), int(end_point.y * h)
                
                cv2.line(img, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)
        
        # Draw landmarks
        for landmark in pose_landmarks:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(img, (x, y), 5, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x, y), 7, (0, 255, 0), 2)
    
    def findPosition(self, img, draw=True):
        """Extract landmark positions"""
        self.lmList = []
        
        if self.results and self.results.pose_landmarks:
            pose_landmarks = self.results.pose_landmarks[0]
            h, w, c = img.shape
            
            for id, landmark in enumerate(pose_landmarks):
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        
        return self.lmList
        
    def findAngle(self, img, p1, p2, p3, draw=True):
        """Calculate angle between three points"""
        if len(self.lmList) == 0:
            return 0
            
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]
        
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - 
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
            if angle > 180:
                angle = 360 - angle
        elif angle > 180:
            angle = 360 - angle
        
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            
            cv2.circle(img, (x1, y1), 5, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 5, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 5, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle
        
def main():
    detector = poseDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot access camera")
        return
    
    while cap.isOpened():
        ret, img = cap.read()
        if ret:    
            img = detector.findPose(img)
            lmList = detector.findPosition(img, draw=False)
            
            if len(lmList) != 0:
                # Example: track right elbow
                print(f"Right elbow position: {lmList[14]}")
            
            cv2.imshow('Pose Detection', img)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()
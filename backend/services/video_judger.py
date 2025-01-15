import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
import time

@dataclass
class PerformanceMetrics:
    facial_engagement: float = 0.0
    body_movement: float = 0.0
    hand_activity: float = 0.0
    total_score: float = 0.0
    
class PerformanceAnalyzer:
    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize detectors with custom configs
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
    def process_video(self, video_path, display=True):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Error opening video file")
            
        metrics_history = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with all detectors
            face_results = self.face_mesh.process(frame_rgb)
            pose_results = self.pose.process(frame_rgb)
            hands_results = self.hands.process(frame_rgb)
            
            # Calculate metrics for this frame
            metrics = PerformanceMetrics()
            
            # Analyze facial engagement
            if face_results.multi_face_landmarks:
                metrics.facial_engagement = self._analyze_facial_movement(
                    face_results.multi_face_landmarks[0])
                
            # Analyze body movement
            if pose_results.pose_landmarks:
                metrics.body_movement = self._analyze_body_movement(
                    pose_results.pose_landmarks)
                
            # Analyze hand activity
            if hands_results.multi_hand_landmarks:
                metrics.hand_activity = self._analyze_hand_movement(
                    hands_results.multi_hand_landmarks)
            
            # Calculate total score
            metrics.total_score = self._calculate_total_score(metrics)
            metrics_history.append(metrics)
            
            # Draw visual feedback if display is enabled
            if display:
                self._draw_landmarks(frame, face_results, pose_results, hands_results)
                self._draw_scores(frame, metrics)
                cv2.imshow('Performance Analysis', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            frame_count += 1
            
        cap.release()
        cv2.destroyAllWindows()
        
        return self._summarize_performance(metrics_history)
    
    def _analyze_facial_movement(self, face_landmarks):
        # Calculate facial movement score based on key landmarks
        # Focus on mouth, eyes, and eyebrows
        mouth_movement = self._calculate_mouth_movement(face_landmarks)
        eye_movement = self._calculate_eye_movement(face_landmarks)
        return (mouth_movement + eye_movement) / 2
    
    def _analyze_body_movement(self, pose_landmarks):
        # Calculate body movement score
        # Consider upper body movement for instrument playing
        upper_body_movement = self._calculate_upper_body_movement(pose_landmarks)
        overall_movement = self._calculate_overall_movement(pose_landmarks)
        return (upper_body_movement + overall_movement) / 2
    
    def _analyze_hand_movement(self, hand_landmarks_list):
        # Calculate hand movement score
        # Important for instrument playing detection
        total_movement = 0
        for hand_landmarks in hand_landmarks_list:
            movement = self._calculate_hand_movement(hand_landmarks)
            total_movement += movement
        return total_movement / len(hand_landmarks_list)
    
    def _calculate_total_score(self, metrics):
        # Weight the different components
        weights = {
            'facial': 0.3,
            'body': 0.4,
            'hands': 0.3
        }
        
        return (
            metrics.facial_engagement * weights['facial'] +
            metrics.body_movement * weights['body'] +
            metrics.hand_activity * weights['hands']
        )
    
    def _draw_landmarks(self, frame, face_results, pose_results, hands_results):
        # Draw face mesh
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS)
        
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        # Draw hand landmarks
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
    
    def _draw_scores(self, frame, metrics):
        # Draw performance scores on the frame
        h, w = frame.shape[:2]
        cv2.putText(frame, f'Face: {metrics.facial_engagement:.2f}', 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Body: {metrics.body_movement:.2f}', 
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Hands: {metrics.hand_activity:.2f}', 
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Total: {metrics.total_score:.2f}', 
                    (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    def _summarize_performance(self, metrics_history):
        # Calculate overall performance statistics
        avg_metrics = PerformanceMetrics(
            facial_engagement=np.mean([m.facial_engagement for m in metrics_history]),
            body_movement=np.mean([m.body_movement for m in metrics_history]),
            hand_activity=np.mean([m.hand_activity for m in metrics_history]),
            total_score=np.mean([m.total_score for m in metrics_history])
        )
        
        return {
            'average_metrics': avg_metrics,
            'frame_by_frame': metrics_history
        }
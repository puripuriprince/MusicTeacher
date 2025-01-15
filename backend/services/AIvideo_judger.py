import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
import time
import os
from openai import OpenAI

@dataclass
class PerformanceMetrics:
    facial_engagement: float = 0.0
    body_movement: float = 0.0
    hand_activity: float = 0.0
    ai_score: float = 0.0
    total_score: float = 0.0

class PerformanceAnalyzer:
    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize Nebius AI client
        self.nebius_client = OpenAI(
            base_url="https://api.studio.nebius.ai/v1/",
            api_key=os.environ.get("NEBIUS_API_KEY"),
        )
        
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
        
        # Frame skip settings
        self.frame_sample_rate = 0.1  # Analyze 10% of frames
        
    def _analyze_frame_with_nebius(self, frame):
        # Convert frame to base64
        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            return 0.0
            
        base64_image = encoded_image.tobytes()
        
        try:
            response = self.nebius_client.chat.completions.create(
                model="Qwen/Qwen2-VL-72B-Instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this performer's engagement and technique. Rate from 0-1."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=100,
            )
            
            # Extract score from response
            score_text = response.choices[0].message.content
            try:
                score = float(score_text)
                return min(max(score, 0.0), 1.0)  # Ensure score is between 0 and 1
            except ValueError:
                return 0.0
                
        except Exception as e:
            print(f"Error in Nebius AI analysis: {e}")
            return 0.0
    
    def process_video(self, video_path, display=True):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Error opening video file")
            
        metrics_history = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = int(1 / self.frame_sample_rate)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Skip frames based on sample rate
            if frame_count % frame_interval != 0:
                frame_count += 1
                continue
                
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with all detectors
            face_results = self.face_mesh.process(frame_rgb)
            pose_results = self.pose.process(frame_rgb)
            hands_results = self.hands.process(frame_rgb)
            
            # Get AI analysis for this frame
            ai_score = self._analyze_frame_with_nebius(frame)
            
            # Calculate metrics for this frame
            metrics = PerformanceMetrics()
            
            if face_results.multi_face_landmarks:
                metrics.facial_engagement = self._analyze_facial_movement(
                    face_results.multi_face_landmarks[0])
                
            if pose_results.pose_landmarks:
                metrics.body_movement = self._analyze_body_movement(
                    pose_results.pose_landmarks)
                
            if hands_results.multi_hand_landmarks:
                metrics.hand_activity = self._analyze_hand_movement(
                    hands_results.multi_hand_landmarks)
            
            metrics.ai_score = ai_score
            metrics.total_score = self._calculate_total_score(metrics)
            metrics_history.append(metrics)
            
            if display:
                self._draw_landmarks(frame, face_results, pose_results, hands_results)
                self._draw_scores(frame, metrics)
                cv2.imshow('Performance Analysis', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            frame_count += 1
            print(f"Processed frame {frame_count}/{total_frames} ({(frame_count/total_frames*100):.1f}%)")
            
        cap.release()
        cv2.destroyAllWindows()
        
        return self._summarize_performance(metrics_history)
    
    def _calculate_total_score(self, metrics):
        # Updated weights to include AI score
        weights = {
            'facial': 0.2,
            'body': 0.3,
            'hands': 0.2,
            'ai': 0.3
        }
        
        return (
            metrics.facial_engagement * weights['facial'] +
            metrics.body_movement * weights['body'] +
            metrics.hand_activity * weights['hands'] +
            metrics.ai_score * weights['ai']
        )
    
    def _draw_scores(self, frame, metrics):
        # Updated to include AI score
        h, w = frame.shape[:2]
        cv2.putText(frame, f'Face: {metrics.facial_engagement:.2f}', 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Body: {metrics.body_movement:.2f}', 
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Hands: {metrics.hand_activity:.2f}', 
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'AI: {metrics.ai_score:.2f}', 
                    (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Total: {metrics.total_score:.2f}', 
                    (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
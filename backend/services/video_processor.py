import cv2
import tempfile
import numpy as np
from PIL import Image
import io
import base64

def extract_frames(video_file, interval=5):
    """
    Extracts key frames with very permissive quality checks
    Always returns at least one frame
    """
    frames = []
    backup_frames = []  # Store all frames as backup
    
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp.write(video_file.read())
    temp.close()
    
    cap = cv2.VideoCapture(temp.name)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate key moments to analyze
    key_moments = [
        int(total_frames * 0.25),  # Quarter way through
        int(total_frames * 0.5),   # Midpoint
        int(total_frames * 0.75)   # Three-quarters through
    ]
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert frame to base64
        success, buffer = cv2.imencode('.jpg', frame)
        if success:
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            
            if frame_count in key_moments:
                if is_frame_usable(frame):
                    frames.append(base64_frame)
                backup_frames.append(base64_frame)
                
        frame_count += 1
    
    cap.release()
    
    # If no good frames found, use backup frames
    if not frames and backup_frames:
        # Use middle frame as fallback
        middle_idx = len(backup_frames) // 2
        frames = [backup_frames[middle_idx]]
    
    return frames

def is_frame_usable(frame):
    """
    Very permissive quality checks
    """
    try:
        # Check if frame is completely black or white
        brightness = np.mean(frame)
        if brightness < 5 or brightness > 250:
            return False
        
        # Basic blur check (very permissive)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < 10:  # Much more permissive blur threshold
            return False
        
        # Minimal size check
        height, width = frame.shape[:2]
        if width < 240 or height < 180:  # More permissive size requirement
            return False
        
        return True
        
    except Exception as e:
        print(f"Frame quality check error: {e}")
        return True  # On error, accept frame anyway 
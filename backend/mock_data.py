import random

def get_style_rating(score):
    if score >= 9.5: return ("SSS", "#FF0000")  # Red
    elif score >= 9.0: return ("SS", "#FF0000")  # Red
    elif score >= 8.5: return ("S", "#FF0000")   # Red
    elif score >= 8.0: return ("A", "#FFA500")   # Orange
    elif score >= 7.0: return ("B", "#FFD700")   # Yellow
    elif score >= 6.0: return ("C", "#00FF00")   # Green
    else: return ("D", "#0000FF")                # Blue

def mock_visual_feedback():
    return {
        "score": random.uniform(9.0, 9.8),  # Overall score
        "posture": {
            "score": random.uniform(8.0, 10.0),  # Individual aspect score
            "feedback": [
                "Shoulders and back alignment are excellent, Slight tension noticed in neck position, Good eye level with the instrument"
            ]
        },
        "finger_position": {
            "score": random.uniform(8.0, 10.0),
            "feedback": [
                "Clean chord transitions in most sections, Some hesitation in complex finger patterns, Right hand strumming is consistent"
            ]
        },
        "confidence": {
            "score": random.uniform(8.0, 10.0),
            "feedback": [
                "Natural stage presence developing well, Performance becomes hesitant in difficult passages, Good recovery from minor mistakes"
            ]
        }
    }

def mock_audio_feedback():
    return {
        "score": random.uniform(9.0, 9.8),  # Overall score
        "tempo": {
            "score": random.uniform(8.0, 10.0),  # Individual aspect score
            "feedback": [
                "Steady rhythm in main sections, Slight rushing in chorus transitions, Good use of dynamic pacing"
            ]
        },
        "pitch": {
            "score": random.uniform(8.0, 10.0),
            "feedback": [
                "Excellent intonation in middle register, Minor pitch variations in higher notes, Strong sense of key maintenance"
            ]
        },
        "rhythm": {
            "score": random.uniform(8.0, 10.0),
            "feedback": [
                "Consistent strumming patterns, Complex rhythms handled well, Some syncopation needs attention"
            ]
        }
    }

def mock_education_tips():
    return {
        "immediate_focus": [
            "Practice difficult transitions at 70 precent speed, Record yourself to analyze neck tension points"
        ],
        "technical_development": [
            "Incorporate finger exercises for complex patterns, Use a metronome for chorus transition sections"
        ],
        "performance_growth": [
            "Try performing the difficult sections for friends, Practice recovery techniques for common mistakes"
        ]
    }

def get_mock_feedback(skill_level='intermediate'):
    if skill_level == 'beginner':
        visual_score = 6.5
        audio_score = 6.2
    elif skill_level == 'intermediate':
        visual_score = 7.8
        audio_score = 8.1
    else:  # advanced
        visual_score = 9.2
        audio_score = 9.5
    
    return {
        'visual_feedback': {
            "score": visual_score,
            # ... rest of visual feedback
        },
        'audio_feedback': {
            "score": audio_score,
            # ... rest of audio feedback
        }
    } 
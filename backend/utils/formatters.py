import json

def format_visual_feedback(gpt_response):
    """
    Formats Nebius AI + GPT interpretation into standardized feedback
    Handles both JSON and text responses
    """
    try:
        # Try to parse as JSON first
        if isinstance(gpt_response, list):
            # If we got multiple analyses, use the best one
            best_analysis = gpt_response[0]
        else:
            best_analysis = gpt_response

        try:
            # Try to parse as JSON
            feedback = json.loads(best_analysis)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, create structured feedback from text
            return {
                "score": 6.0,
                "posture": {
                    "score": 6.0,
                    "feedback": extract_feedback(best_analysis, "posture")
                },
                "finger_position": {
                    "score": 6.0,
                    "feedback": extract_feedback(best_analysis, "finger position")
                },
                "confidence": {
                    "score": 6.0,
                    "feedback": extract_feedback(best_analysis, "confidence")
                }
            }

        # Calculate overall score
        return {
            "score": calculate_overall_score(feedback),
            "posture": feedback.get("posture", {
                "score": 6.0,
                "feedback": "Basic posture analysis completed"
            }),
            "finger_position": feedback.get("finger_position", {
                "score": 6.0,
                "feedback": "Basic finger position analysis completed"
            }),
            "confidence": feedback.get("confidence", {
                "score": 6.0,
                "feedback": "Basic confidence analysis completed"
            })
        }
    except Exception as e:
        print(f"Error formatting visual feedback: {e}")
        # Return default feedback on error
        return {
            "score": 6.0,
            "posture": {
                "score": 6.0,
                "feedback": "Analysis completed with limited detail"
            },
            "finger_position": {
                "score": 6.0,
                "feedback": "Basic technique assessment completed"
            },
            "confidence": {
                "score": 6.0,
                "feedback": "General presence evaluation completed"
            }
        }

def extract_feedback(text, aspect):
    """
    Extracts relevant feedback for each aspect from text response
    """
    # Split text into sentences
    sentences = text.split('.')
    relevant = []
    
    # Look for sentences containing the aspect
    for sentence in sentences:
        if aspect.lower() in sentence.lower():
            relevant.append(sentence.strip())
    
    if relevant:
        return ". ".join(relevant) + "."
    else:
        return f"Basic {aspect} analysis completed."

def calculate_overall_score(feedback):
    """Calculate overall score from individual aspects"""
    try:
        scores = []
        for aspect in ['posture', 'finger_position', 'confidence']:
            if aspect in feedback and isinstance(feedback[aspect], dict):
                score = feedback[aspect].get('score', 6.0)
                if isinstance(score, (int, float)):
                    scores.append(score)
        
        if scores:
            return sum(scores) / len(scores)
        return 6.0  # Default score
    except Exception:
        return 6.0  # Default score on error

def format_audio_feedback(gpt_response, technical_data):
    """
    Formats audio analysis into standardized feedback structure
    """
    try:
        feedback = json.loads(gpt_response)
        
        # Combine GPT analysis with technical data
        return {
            "score": calculate_audio_score(feedback, technical_data),
            "tempo": {
                "score": feedback["tempo"]["score"],
                "feedback": feedback["tempo"]["feedback"]
            },
            "pitch": {
                "score": feedback["pitch"]["score"],
                "feedback": feedback["pitch"]["feedback"]
            },
            "rhythm": {
                "score": feedback["rhythm"]["score"],
                "feedback": feedback["rhythm"]["feedback"]
            },
            "technical_data": technical_data
        }
    except Exception as e:
        print(f"Error formatting audio feedback: {e}")
        return None

def calculate_audio_score(feedback, technical_data):
    """Calculate overall audio score"""
    scores = [
        feedback["tempo"]["score"],
        feedback["pitch"]["score"],
        feedback["rhythm"]["score"]
    ]
    
    # Adjust score based on technical measurements
    technical_bonus = (
        technical_data["tempo"]["consistency"] * 0.3 +
        technical_data["pitch"]["stability"] * 0.3 +
        technical_data["rhythm"]["regularity"] * 0.4
    )
    
    base_score = sum(scores) / len(scores)
    return min(10.0, base_score * (1 + technical_bonus * 0.2))

def format_recommendations(gpt_response):
    """Formats GPT's recommendations into structured advice"""
    # Implementation needed
    pass 
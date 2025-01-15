from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from services.ai_services import (
    analyze_visual_performance,
    analyze_audio_performance,
    generate_practice_recommendations,
    generate_performance_summary
)
from services.music_generator import music_generator
from utils.formatters import (
    format_visual_feedback,
    format_audio_feedback,
    format_recommendations
)
from dotenv import load_dotenv
import sys
import os

# Add the parent directory to sys.path to import from Main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Main import get_style_rating

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/analyze-performance', methods=['POST'])
def analyze_performance():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if not video_file.filename:
            return jsonify({'error': 'Empty video file'}), 400
            
        # Check file type
        if not video_file.filename.lower().endswith(('.mp4', '.mov')):
            return jsonify({'error': 'Invalid file type. Please upload MP4 or MOV file'}), 400
        
        # Get raw feedback without style ratings
        visual_feedback = analyze_visual_performance(video_file)
        if not visual_feedback:
            return jsonify({'error': 'Visual analysis failed. Please ensure good lighting and clear video'}), 500
        
        # Reset file pointer for audio analysis
        video_file.seek(0)
        audio_feedback = analyze_audio_performance(video_file)
        if not audio_feedback:
            return jsonify({'error': 'Audio analysis failed. Please ensure clear audio'}), 500
        
        # Add style ratings to each aspect of visual feedback
        for aspect in visual_feedback:
            if aspect != "score":
                visual_feedback[aspect]["style_rating"] = get_style_rating(visual_feedback[aspect]["score"])
                
        # Add style ratings to each aspect of audio feedback
        for aspect in audio_feedback:
            if aspect != "score":
                audio_feedback[aspect]["style_rating"] = get_style_rating(audio_feedback[aspect]["score"])
        
        education_tips = generate_practice_recommendations(
            visual_feedback,
            audio_feedback,
            skill_level='intermediate'
        )
        
        # Calculate grades using the imported get_style_rating
        visual_grade = get_style_rating(visual_feedback["score"])
        audio_grade = get_style_rating(audio_feedback["score"])
        
        # Calculate overall grade with ULTRA condition
        if visual_grade[0] == "SSS" and audio_grade[0] == "SSS":
            overall_grade = ("ULTRA", "#FFD700")
        else:
            overall_score = (visual_feedback["score"] + audio_feedback["score"]) / 2
            overall_grade = get_style_rating(overall_score)
        
        # Generate overall performance summary
        performance_summary = generate_performance_summary(visual_feedback, audio_feedback)
        
        return jsonify({
            'visual_feedback': visual_feedback,
            'audio_feedback': audio_feedback,
            'education_tips': education_tips,
            'summary': {
                'visual_grade': visual_grade,
                'audio_grade': audio_grade,
                'overall_grade': overall_grade,
                'performance_summary': performance_summary
            }
        })
    except Exception as e:
        print(f"Error in analyze_performance: {e}")
        return jsonify({'error': 'Analysis failed. Please try again'}), 500

@app.route('/api/generate-practice-song', methods=['POST'])
def generate_practice_song():
    data = request.get_json()
    skill_level = data.get('skill_level')
    instrument = data.get('instrument')
    genre = data.get('genre', 'Pop')
    
    # Validate instrument
    if instrument not in ["Piano", "Guitar", "Ukelele", "Voice"]:
        return jsonify({'error': 'Invalid instrument selected'}), 400
    
    practice_material = music_generator.generate_practice_material(
        performance_data=None,
        skill_level=skill_level,
        instrument=instrument
    )
    
    if not practice_material:
        return jsonify({'error': 'Failed to generate practice song'}), 500
        
    return jsonify(practice_material)

@app.route('/api/generate-practice-material', methods=['POST'])
def generate_practice_material():
    data = request.get_json()
    performance_data = data.get('performance_data')
    skill_level = data.get('skill_level', 'intermediate')
    instrument = data.get('instrument', 'piano')
    
    practice_material = music_generator.generate_practice_material(
        performance_data,
        skill_level,
        instrument
    )
    
    if not practice_material:
        return jsonify({'error': 'Failed to generate practice materials'}), 500
        
    return jsonify(practice_material)

@app.route('/api/test-sheet-music', methods=['GET'])
def test_sheet_music():
    try:
        result = music_generator.generate_test_sheet_music()
        if result:
            return jsonify(result)
        return jsonify({'error': 'Failed to generate test sheet music'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/generated/<path:filename>')
def serve_generated_file(filename):
    return send_from_directory('static/generated', filename)

if __name__ == '__main__':
    app.run(debug=True)

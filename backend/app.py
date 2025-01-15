from flask import Flask, request, jsonify
from flask_cors import CORS
import os
# Temporarily comment out Supabase
# from supabase import create_client, Client
from dotenv import load_dotenv
import requests
from mock_data import mock_visual_feedback, mock_audio_feedback, mock_education_tips, get_style_rating

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Temporarily comment out Supabase initialization
# supabase: Client = create_client(
#     os.getenv('SUPABASE_URL'),
#     os.getenv('SUPABASE_KEY')
# )

# Initialize AI service clients
NEBIUS_API_KEY = os.getenv('NEBIUS_API_KEY')
OPENNOTE_API_KEY = os.getenv('OPENNOTE_API_KEY')
BEETHOVEN_API_KEY = os.getenv('BEETHOVEN_API_KEY')

@app.route('/api/analyze-performance', methods=['POST'])
def analyze_performance():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    
    # Get individual feedback
    visual_feedback = analyze_visual_performance(video_file)
    audio_feedback = analyze_audio_performance(video_file)
    education_tips = get_education_tips(visual_feedback, audio_feedback)
    
    # Get grades directly from the section scores
    visual_grade = get_style_rating(visual_feedback["score"])
    audio_grade = get_style_rating(audio_feedback["score"])
    
    # Calculate overall grade with ULTRA condition
    if visual_grade[0] == "SSS" and audio_grade[0] == "SSS":
        overall_grade = ("ULTRA", "#FFD700")  # Gold color for ULTRA
    else:
        overall_score = (visual_feedback["score"] + audio_feedback["score"]) / 2
        overall_grade = get_style_rating(overall_score)
    
    return jsonify({
        'visual_feedback': visual_feedback,
        'audio_feedback': audio_feedback,
        'education_tips': education_tips,
        'summary': {
            'visual_grade': visual_grade,
            'audio_grade': audio_grade,
            'overall_grade': overall_grade
        }
    })

@app.route('/api/generate-practice-song', methods=['POST'])
def generate_practice_song():
    data = request.get_json()
    skill_level = data.get('skill_level')
    instrument = data.get('instrument')
    genre = data.get('genre', 'Pop')  # Default to 'Pop' if not specified
    
    song = generate_song(skill_level, instrument, genre)
    
    return jsonify({
        'song_url': song['url'],
        'sheet_music': song['sheet_music']
    })

def analyze_visual_performance(video_file):
    # During testing, return mock data
    return mock_visual_feedback()

def analyze_audio_performance(video_file):
    # During testing, return mock data
    return mock_audio_feedback()

def get_education_tips(visual_data, audio_data):
    # During testing, return mock data
    return mock_education_tips()

def generate_song(skill_level, instrument, genre):
    # Mock response during testing
    return {
        'url': 'https://example.com/mock-song.mp3',
        'sheet_music': 'https://example.com/mock-sheet-music.png'
    }

if __name__ == '__main__':
    app.run(debug=True)

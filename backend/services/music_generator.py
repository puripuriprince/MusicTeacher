import os
from dotenv import load_dotenv
import json
import requests
from pathlib import Path
import base64
from io import BytesIO
import tempfile
import librosa
import numpy as np
from music21 import converter, stream, note

# Load environment variables
load_dotenv()
TOPMEDIA_API_KEY = os.getenv('TOPMEDIA_API_KEY')

class MusicGenerator:
    API_URL = "https://api.topmediai.com/v1/music"

    def generate_practice_material(self, performance_data, skill_level, instrument, style='classical'):
        try:
            session_id = f"{instrument}_{skill_level}_{os.urandom(4).hex()}"
            
            # Generate music using TopMediaAI
            audio_data = self._generate_with_topmedia(skill_level, instrument, style)
            
            if audio_data:
                # Convert to MIDI and generate sheet music
                midi_data = self._audio_to_midi(audio_data)
                sheet_music_path = self._midi_to_sheet_music(midi_data, session_id)

                return {
                    'sheet_music': {
                        'audio_data': audio_data,
                        'audio_filename': f"{session_id}.wav",
                        'sheet_music_path': sheet_music_path
                    },
                    'exercises': [
                        f"Practice this {style} piece slowly at first",
                        f"Focus on the {instrument}-specific techniques",
                        f"Pay attention to dynamics and expression"
                    ],
                    'notes': f"A {style} piece designed for {skill_level} level {instrument} practice"
                }
            else:
                raise Exception("Failed to generate audio data")

        except Exception as e:
            print(f"Error generating practice materials: {e}")
            return None

    def _audio_to_midi(self, audio_data):
        """Convert audio to MIDI using librosa"""
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name

            print(f"Loading audio file from: {temp_audio_path}")
            # Load the audio file with specific parameters
            y, sr = librosa.load(temp_audio_path, sr=22050, mono=True)
            
            print("Extracting pitch information...")
            # Use more robust pitch detection
            pitches, magnitudes = librosa.piptrack(
                y=y, 
                sr=sr,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7')
            )
            
            print("Detecting onsets...")
            # Improve onset detection
            onset_frames = librosa.onset.onset_detect(
                y=y, 
                sr=sr,
                wait=3,
                pre_avg=3,
                post_avg=3,
                pre_max=3,
                post_max=3
            )
            
            print("Creating MIDI file...")
            # Create MIDI file
            pm = pretty_midi.PrettyMIDI(initial_tempo=120)
            piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
            piano = pretty_midi.Instrument(program=piano_program)

            # Convert detected pitches to MIDI notes
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            print(f"Found {len(onset_times)} onsets")
            
            for i in range(len(onset_times)-1):
                start_time = onset_times[i]
                end_time = onset_times[i+1]
                
                # Find the strongest pitch in this time frame
                frame_start = librosa.time_to_frames(start_time, sr=sr)
                frame_end = librosa.time_to_frames(end_time, sr=sr)
                
                if frame_start >= len(pitches) or frame_end >= len(pitches):
                    continue
                    
                pitch_segment = pitches[frame_start:frame_end]
                mag_segment = magnitudes[frame_start:frame_end]
                
                if len(pitch_segment) > 0:
                    # Get the pitch with the highest magnitude
                    pitch_idx = np.unravel_index(mag_segment.argmax(), mag_segment.shape)
                    midi_pitch = int(round(pitch_segment[pitch_idx]))
                    
                    # Ensure pitch is in valid MIDI range (0-127)
                    if 0 <= midi_pitch <= 127:
                        # Create note with normalized velocity
                        note = pretty_midi.Note(
                            velocity=int(min(max(mag_segment.max() * 100, 30), 100)),
                            pitch=midi_pitch,
                            start=float(start_time),
                            end=float(end_time)
                        )
                        piano.notes.append(note)

            pm.instruments.append(piano)
            
            # Clean up
            os.unlink(temp_audio_path)
            
            # Ensure we have some notes
            if not piano.notes:
                print("No valid notes detected in the audio")
                return None
                
            print(f"Successfully created MIDI with {len(piano.notes)} notes")
            
            # Convert to bytes
            midi_buffer = BytesIO()
            pm.write(midi_buffer)
            midi_buffer.seek(0)
            return midi_buffer.read()

        except Exception as e:
            print(f"Error converting audio to MIDI: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _midi_to_sheet_music(self, midi_data, session_id):
        """Convert audio to sheet music using music21"""
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_audio.write(base64.b64decode(midi_data))
                audio_path = temp_audio.name

            # Load the audio file
            y, sr = librosa.load(audio_path)
            
            # Extract pitch
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Get the most prominent pitch at each time
            pitches_mean = pitches.mean(axis=0)
            
            # Convert frequency to MIDI notes
            midi_notes = librosa.hz_to_midi(pitches_mean[pitches_mean > 0])
            
            # Round to nearest semitone
            midi_notes = np.round(midi_notes)
            
            # Create a music21 stream
            score_stream = stream.Stream()
            
            # Convert MIDI notes to music21 notes
            for midi_note in midi_notes:
                if np.isnan(midi_note):
                    continue
                    
                new_note = note.Note(int(midi_note), quarterLength=1.0)
                score_stream.append(new_note)

            # Set up output path
            output_dir = Path("static/sheet_music").resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{session_id}.pdf"
            
            # Save as PDF
            score_stream.write('musicxml.pdf', fp=str(output_path))
            
            # Clean up
            os.unlink(audio_path)
            
            if output_path.exists():
                print(f"Successfully created sheet music at: {output_path}")
                return str(output_path)
            else:
                print(f"Failed to create sheet music at {output_path}")
                return None

        except Exception as e:
            print(f"Error converting to sheet music: {e}")
            return None

    def _generate_with_topmedia(self, skill_level, instrument, style):
        """Generate music using TopMediaAI API"""
        try:
            # Check credits first
            credits = self._check_credits()
            if not credits:
                raise Exception("No API credits remaining. Please check your TopMediaAI account.")

            # Create prompt based on parameters
            prompt = self._create_music_prompt(skill_level, instrument, style)

            # Make API request
            response = requests.post(
                self.API_URL,
                headers={
                    "x-api-key": TOPMEDIA_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "is_auto": 1,
                    "prompt": prompt,
                    "title": f"{style.capitalize()} {instrument} Practice - {skill_level}",
                    "instrumental": 1,
                    "duration": 60,
                    "style": style,
                    "instrument": instrument.lower(),
                    "tempo": self._get_tempo(skill_level),
                    "complexity": self._get_complexity(skill_level),
                    "parameters": {
                        "duration_seconds": 60,
                        "strict_timing": True,
                        "form": "structured",
                        "ending_type": "conclusive"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 200 and result.get('data'):
                    audio_file = result['data'][0]['audio_file']
                    audio_response = requests.get(audio_file)
                    if audio_response.status_code == 200:
                        return base64.b64encode(audio_response.content).decode('utf-8')
                    print(f"Failed to download audio from {audio_file}")
                elif result.get('status') == 400 and "left counts" in result.get('message', '').lower():
                    raise Exception("API credits exhausted. Please check your TopMediaAI account balance.")
                else:
                    print(f"Unexpected response format: {result}")
            
            raise Exception(f"TopMediaAI API error: {response.text}")

        except Exception as e:
            print(f"Error in TopMediaAI generation: {e}")
            raise

    def _check_credits(self):
        """Check remaining API credits"""
        try:
            response = requests.get(
                "https://api.topmediai.com/v1/music/limit",
                headers={
                    "x-api-key": TOPMEDIA_API_KEY
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                credits = result.get('data', {}).get('credits_left', 0)
                print(f"Remaining TopMediaAI credits: {credits}")
                return credits > 0
            return False
        except Exception as e:
            print(f"Error checking credits: {e}")
            return False

    def _create_music_prompt(self, skill_level, instrument, style):
        """Create detailed prompt for TopMediaAI"""
        # Base structure for a 1-minute piece
        time_structure = {
            'beginner': "Create a 60-second piece with clear 4-bar phrases. Include an intro (8s), main theme (30s), variation (15s), and ending (7s).",
            'intermediate': "Compose a 60-second piece with 8-bar phrases. Structure: intro (8s), theme A (20s), theme B (20s), return to A (8s), coda (4s).",
            'advanced': "Generate a 60-second virtuosic piece. Complex structure: intro (8s), theme A (16s), development (20s), climax (12s), coda (4s)."
        }

        # Instrument-specific techniques
        instrument_techniques = {
            'Piano': {
                'beginner': "Use simple two-hand coordination, basic pedaling, clear articulation.",
                'intermediate': "Include arpeggios, moderate pedaling, dynamic contrasts, hand crossing.",
                'advanced': "Complex fingering patterns, sophisticated pedaling, full dynamic range, rapid hand movements."
            },
            'Guitar': {
                'beginner': "Use open positions, simple strumming patterns, basic fingerpicking.",
                'intermediate': "Include barre chords, mixed strumming/picking, moderate position shifts.",
                'advanced': "Complex fingerstyle, advanced techniques, full fretboard navigation."
            },
            'Violin': {
                'beginner': "Stay in first position, simple bowing patterns, clear string crossings.",
                'intermediate': "Include position shifts, varied bow strokes, moderate double stops.",
                'advanced': "Advanced positions, complex bow techniques, virtuosic passages."
            }
        }

        # Style-specific characteristics
        style_elements = {
            'classical': {
                'beginner': "Simple classical form, clear cadences, basic ornaments.",
                'intermediate': "Traditional harmony, balanced phrases, moderate counterpoint.",
                'advanced': "Complex harmonies, intricate counterpoint, sophisticated form."
            },
            'jazz': {
                'beginner': "Basic swing feel, simple jazz chords, clear rhythmic patterns.",
                'intermediate': "Moderate syncopation, extended chords, blues elements.",
                'advanced': "Complex rhythmic interplay, advanced harmony, bebop elements."
            },
            'pop': {
                'beginner': "Catchy hooks, simple chord progressions, steady rhythms.",
                'intermediate': "Modern harmonies, syncopated rhythms, dynamic builds.",
                'advanced': "Complex arrangements, contemporary techniques, dramatic contrasts."
            }
        }

        # Get the appropriate techniques and elements
        time_guide = time_structure[skill_level]
        tech_guide = instrument_techniques.get(instrument, instrument_techniques['Piano'])[skill_level]
        style_guide = style_elements[style][skill_level]

        # Combine into a detailed prompt
        prompt = f"""
Create a precisely 60-second {style} piece for {instrument} at {skill_level} level.

Structure and Timing:
{time_guide}

Instrument-Specific Requirements:
{tech_guide}

Style and Musical Elements:
{style_guide}

Additional Requirements:
- Maintain consistent tempo appropriate for {skill_level} level
- Include clear dynamic markings and expressive elements
- Ensure all phrases connect smoothly
- Create musical interest throughout the full minute
- End with a satisfying conclusion

Focus on creating a complete musical journey that develops within exactly one minute."""

        return prompt

    def _get_tempo(self, skill_level):
        """Get appropriate tempo based on skill level"""
        return {
            'beginner': 80,
            'intermediate': 100,
            'advanced': 120
        }.get(skill_level, 100)

    def _get_complexity(self, skill_level):
        """Get complexity parameter based on skill level"""
        return {
            'beginner': 0.3,
            'intermediate': 0.6,
            'advanced': 0.9
        }.get(skill_level, 0.6)

    def generate_test_sheet_music(self):
        """Generate test sheet music from existing MP3 file"""
        try:
            # Use correct path for test file
            test_file = Path("static/generated/test1.mp3").resolve()
            print(f"Looking for test file at: {test_file}")
            
            if not test_file.exists():
                # Create directory if it doesn't exist
                test_dir = Path("static/generated").resolve()
                test_dir.mkdir(parents=True, exist_ok=True)
                
                # Try alternative path
                alt_test_file = Path("static/generated/AI Music-audio(1).mp3").resolve()
                if alt_test_file.exists():
                    test_file = alt_test_file
                else:
                    raise Exception(f"Test MP3 file not found at {test_file}")

            # Generate a session ID
            session_id = f"test_{os.urandom(4).hex()}"

            # Read the MP3 file
            with open(test_file, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')

            # Generate sheet music
            sheet_music_path = self._midi_to_sheet_music(audio_data, session_id)

            if sheet_music_path:
                return {
                    'sheet_music': {
                        'audio_data': audio_data,
                        'audio_filename': f"{session_id}.mp3",
                        'sheet_music_path': sheet_music_path
                    }
                }
            else:
                raise Exception("Failed to generate sheet music")

        except Exception as e:
            print(f"Error generating test sheet music: {e}")
            return None

# Create singleton instance
music_generator = MusicGenerator()
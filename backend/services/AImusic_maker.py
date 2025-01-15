import asyncio
import os
import aiohttp
import aiofiles
import base64
from pathlib import Path
import tempfile
import librosa
import numpy as np
from music21 import converter, stream, note, instrument, tablature
from dotenv import load_dotenv

class EnhancedMusicGenerator:
    def __init__(self):
        load_dotenv()
        self.BEATOVEN_API_KEY = os.getenv("BEATOVEN_API_KEY", "")
        self.BACKEND_V1_API_URL = "https://public-api.beatoven.ai/api/v1"
        
    async def generate_music(self, duration=30000, genre="cinematic", mood="happy", tempo="medium"):
        """Generate music using Beatoven.ai"""
        track_meta = {
            "prompt": {"text": f"{duration//1000} seconds {genre} {mood} track at {tempo} tempo"}
        }
        
        # Generate the track
        track_obj = await self._create_track(track_meta)
        track_id = track_obj["tracks"][0]
        
        # Compose the track
        compose_res = await self._compose_track(track_meta, track_id)
        task_id = compose_res["task_id"]
        
        # Wait for completion
        generation_meta = await self._watch_task_status(task_id)
        track_url = generation_meta["meta"]["track_url"]
        
        # Download the track
        output_path = os.path.join(os.getcwd(), "generated_music")
        os.makedirs(output_path, exist_ok=True)
        audio_path = os.path.join(output_path, "composed_track.mp3")
        await self._handle_track_file(audio_path, track_url)
        
        return audio_path

    async def generate_sheet_music(self, audio_path, instrument_type='piano'):
        """Generate sheet music for different instruments"""
        try:
            # Convert audio to MIDI
            midi_data = await self._audio_to_midi(audio_path)
            if not midi_data:
                raise Exception("Failed to convert audio to MIDI")

            # Create base score from MIDI
            score = converter.parse(midi_data)
            
            # Generate different formats based on instrument type
            output_dir = Path("generated_sheet_music").resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            
            results = {}
            
            if instrument_type == 'piano':
                # Piano score (grand staff)
                piano_part = instrument.Piano()
                score.insert(0, piano_part)
                piano_path = output_dir / "piano_score.pdf"
                score.write('musicxml.pdf', fp=str(piano_path))
                results['piano'] = str(piano_path)
                
            elif instrument_type == 'guitar':
                # Guitar tablature
                guitar_score = self._create_guitar_tab(score)
                tab_path = output_dir / "guitar_tab.pdf"
                guitar_score.write('musicxml.pdf', fp=str(tab_path))
                results['guitar'] = str(tab_path)
                
            elif instrument_type == 'ukulele':
                # Ukulele tablature
                ukulele_score = self._create_ukulele_tab(score)
                uke_tab_path = output_dir / "ukulele_tab.pdf"
                ukulele_score.write('musicxml.pdf', fp=str(uke_tab_path))
                results['ukulele'] = str(uke_tab_path)
                
            elif instrument_type == 'voice':
                # Vocal score (melody line with lyrics placeholder)
                voice_score = self._create_voice_score(score)
                voice_path = output_dir / "voice_score.pdf"
                voice_score.write('musicxml.pdf', fp=str(voice_path))
                results['voice'] = str(voice_path)
            
            return results
            
        except Exception as e:
            print(f"Error generating sheet music: {e}")
            return None

    def _create_guitar_tab(self, score):
        """Convert score to guitar tablature"""
        guitar_score = stream.Score()
        guitar = instrument.Guitar()
        tab_staff = tablature.TabStaff(stringTunings=guitar.stringTunings)
        
        for n in score.flatten().notes:
            if isinstance(n, note.Note):
                tab_note = self._map_note_to_guitar(n)
                tab_staff.append(tab_note)
        
        guitar_score.append(tab_staff)
        return guitar_score

    def _create_ukulele_tab(self, score):
        """Convert score to ukulele tablature"""
        ukulele_score = stream.Score()
        ukulele = instrument.Ukulele()
        tab_staff = tablature.TabStaff(stringTunings=ukulele.stringTunings)
        
        for n in score.flatten().notes:
            if isinstance(n, note.Note):
                tab_note = self._map_note_to_ukulele(n)
                tab_staff.append(tab_note)
        
        ukulele_score.append(tab_staff)
        return ukulele_score

    def _create_voice_score(self, score):
        """Create vocal score with melody line"""
        voice_score = stream.Score()
        voice_part = stream.Part()
        voice_part.append(instrument.Vocalist())
        
        # Extract the highest notes as melody
        for n in score.flatten().notes:
            if isinstance(n, note.Note):
                voice_part.append(n)
        
        voice_score.append(voice_part)
        return voice_score

    def _map_note_to_guitar(self, note_obj):
        """Map a note to guitar fret position"""
        # Simplified mapping - in practice would need more sophisticated algorithm
        tab_note = note.Note(note_obj.pitch, quarterLength=note_obj.quarterLength)
        tab_note.stemDirection = 'up'
        return tab_note

    def _map_note_to_ukulele(self, note_obj):
        """Map a note to ukulele fret position"""
        # Simplified mapping - in practice would need more sophisticated algorithm
        tab_note = note.Note(note_obj.pitch, quarterLength=note_obj.quarterLength)
        tab_note.stemDirection = 'up'
        return tab_note

    # Beatoven.ai API methods
    async def _create_track(self, request_data):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.BACKEND_V1_API_URL}/tracks",
                    json=request_data,
                    headers={"Authorization": f"Bearer {self.BEATOVEN_API_KEY}"},
                ) as response:
                    data = await response.json()
                    return data
            except Exception as e:
                raise Exception({"error": f"Failed to create track: {str(e)}"})

    async def _compose_track(self, request_data, track_id):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.BACKEND_V1_API_URL}/tracks/compose/{track_id}",
                    json=request_data,
                    headers={"Authorization": f"Bearer {self.BEATOVEN_API_KEY}"},
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    raise Exception({"error": "Composition failed"})
            except Exception as e:
                raise Exception({"error": f"Failed to compose track: {str(e)}"})

    async def _watch_task_status(self, task_id, interval=10):
        while True:
            track_status = await self._get_track_status(task_id)
            if track_status.get("status") == "composing":
                await asyncio.sleep(interval)
            elif track_status.get("status") == "failed":
                raise Exception({"error": "Task failed"})
            else:
                return track_status

    async def _get_track_status(self, task_id):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.BACKEND_V1_API_URL}/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {self.BEATOVEN_API_KEY}"},
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    raise Exception({"error": "Failed to get track status"})
            except Exception as e:
                raise Exception({"error": f"Failed to get track status: {str(e)}"})

    async def _handle_track_file(self, track_path, track_url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(track_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(track_path, "wb+") as f:
                            await f.write(await response.read())
                            return {}
            except Exception as e:
                raise Exception({"error": f"Failed to download track: {str(e)}"})

    async def _audio_to_midi(self, audio_path):
        """Convert audio to MIDI using librosa"""
        try:
            # Load the audio file
            y, sr = librosa.load(audio_path, sr=22050, mono=True)
            
            # Extract pitch and onset information
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            
            # Create MIDI data
            midi_stream = stream.Stream()
            
            # Convert detected pitches to notes
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            for i in range(len(onset_times)-1):
                start_time = onset_times[i]
                end_time = onset_times[i+1]
                
                frame_start = librosa.time_to_frames(start_time, sr=sr)
                frame_end = librosa.time_to_frames(end_time, sr=sr)
                
                if frame_start >= len(pitches) or frame_end >= len(pitches):
                    continue
                    
                pitch_segment = pitches[frame_start:frame_end]
                mag_segment = magnitudes[frame_start:frame_end]
                
                if len(pitch_segment) > 0:
                    pitch_idx = np.unravel_index(mag_segment.argmax(), mag_segment.shape)
                    midi_pitch = int(round(pitch_segment[pitch_idx]))
                    
                    if 0 <= midi_pitch <= 127:
                        new_note = note.Note(midi_pitch)
                        new_note.quarterLength = end_time - start_time
                        midi_stream.append(new_note)
            
            # Convert to MIDI file
            return midi_stream
            
        except Exception as e:
            print(f"Error converting audio to MIDI: {e}")
            return None

# Example usage
async def main():
    generator = EnhancedMusicGenerator()
    
    # Generate music
    audio_path = await generator.generate_music(
        duration=30000,
        genre="classical",
        mood="peaceful",
        tempo="medium"
    )
    
    # Generate sheet music for different instruments
    sheet_music = await generator.generate_sheet_music(audio_path, 'piano')
    sheet_music_guitar = await generator.generate_sheet_music(audio_path, 'guitar')
    sheet_music_ukulele = await generator.generate_sheet_music(audio_path, 'ukulele')
    sheet_music_voice = await generator.generate_sheet_music(audio_path, 'voice')
    
    print("Generated files:", {
        "audio": audio_path,
        "piano_sheet": sheet_music,
        "guitar_tab": sheet_music_guitar,
        "ukulele_tab": sheet_music_ukulele,
        "voice_sheet": sheet_music_voice
    })

if __name__ == "__main__":
    asyncio.run(main())
from transformers import pipeline, AutoFeatureExtractor, AutoModelForAudioClassification
import librosa
import numpy as np
import torch
from typing import Dict, List, Tuple

class MusicAIAnalyzer:
    def __init__(self):
        # Initialize music classification model
        self.feature_extractor = AutoFeatureExtractor.from_pretrained("anton-l/music_genre_classification")
        self.genre_model = AutoModelForAudioClassification.from_pretrained("anton-l/music_genre_classification")
        
        # Initialize instrument detection model
        self.instrument_classifier = pipeline(
            "audio-classification",
            model="daurin/music-instrument-classifier"
        )
        
        # Initialize music quality assessment model
        self.quality_model = AutoModelForAudioClassification.from_pretrained(
            "microsoft/music-audio-detection"
        )
        
    def analyze_performance(self, audio_file: str) -> Dict:
        """Analyze a music performance and provide detailed feedback"""
        # Load audio file
        y, sr = librosa.load(audio_file, sr=22050)
        
        # Get various analyses
        instrument = self._detect_instrument(audio_file)
        tune_analysis = self._analyze_tune(y, sr)
        quality_score = self._assess_quality(y, sr)
        technical_analysis = self._analyze_technical_aspects(y, sr)
        
        # Compile feedback
        feedback = self._generate_feedback(
            instrument,
            tune_analysis,
            quality_score,
            technical_analysis
        )
        
        return {
            "instrument": instrument,
            "tune_analysis": tune_analysis,
            "quality_score": quality_score,
            "technical_analysis": technical_analysis,
            "feedback": feedback
        }
    
    def _detect_instrument(self, audio_file: str) -> Dict:
        """Detect the primary instrument in the audio"""
        predictions = self.instrument_classifier(audio_file)
        return {
            "primary_instrument": predictions[0]["label"],
            "confidence": predictions[0]["score"],
            "possible_others": [p["label"] for p in predictions[1:3]]
        }
    
    def _analyze_tune(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze the tuning and pitch accuracy"""
        # Extract pitch
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Get the most prominent pitches
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch_values.append(pitches[index, t])
        
        # Calculate pitch stability
        pitch_std = np.std(pitch_values)
        pitch_stability = np.exp(-pitch_std)
        
        # Detect key
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_correlation = np.corrcoef(chroma)
        key_stability = np.mean(np.diag(key_correlation, k=1))
        
        return {
            "pitch_stability": float(pitch_stability),
            "key_stability": float(key_stability),
            "overall_tune_score": float((pitch_stability + key_stability) / 2)
        }
    
    def _assess_quality(self, y: np.ndarray, sr: int) -> Dict:
        """Assess overall audio quality and musical expression"""
        # Convert audio to model input format
        inputs = self.feature_extractor(
            y, 
            sampling_rate=sr,
            return_tensors="pt"
        )
        
        with torch.no_grad():
            outputs = self.quality_model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        return {
            "overall_quality": float(scores[0][1]),  # Assuming binary classification
            "confidence": float(torch.max(scores))
        }
    
    def _analyze_technical_aspects(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze technical aspects of the performance"""
        # Rhythm analysis
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        # Timing consistency
        beat_intervals = np.diff(beats)
        timing_consistency = 1.0 - (np.std(beat_intervals) / np.mean(beat_intervals))
        
        # Dynamic range
        rms = librosa.feature.rms(y=y)[0]
        dynamic_range = np.max(rms) - np.min(rms)
        
        return {
            "tempo": float(tempo),
            "timing_consistency": float(timing_consistency),
            "dynamic_range": float(dynamic_range)
        }
    
    def _generate_feedback(self, 
                         instrument: Dict,
                         tune_analysis: Dict,
                         quality_score: Dict,
                         technical_analysis: Dict) -> Dict:
        """Generate detailed feedback and advice"""
        feedback = {
            "main_points": [],
            "technical_feedback": [],
            "improvement_suggestions": []
        }
        
        # Instrument-specific feedback
        feedback["main_points"].append(
            f"Primary instrument detected: {instrument['primary_instrument']} "
            f"(Confidence: {instrument['confidence']:.2%})"
        )
        
        # Tuning feedback
        if tune_analysis["overall_tune_score"] > 0.8:
            feedback["main_points"].append("Excellent tuning and pitch control")
        elif tune_analysis["overall_tune_score"] > 0.6:
            feedback["technical_feedback"].append(
                "Good tuning with some inconsistencies. Consider working on pitch stability"
            )
        else:
            feedback["improvement_suggestions"].append(
                "Focus on improving pitch accuracy and tuning stability"
            )
        
        # Technical feedback
        if technical_analysis["timing_consistency"] > 0.8:
            feedback["technical_feedback"].append("Strong rhythmic precision")
        else:
            feedback["improvement_suggestions"].append(
                f"Practice with a metronome at {technical_analysis['tempo']:.0f} BPM "
                "to improve timing consistency"
            )
        
        # Dynamic range feedback
        if technical_analysis["dynamic_range"] > 0.5:
            feedback["technical_feedback"].append("Good use of dynamics")
        else:
            feedback["improvement_suggestions"].append(
                "Experiment with more dynamic contrast in your playing"
            )
        
        # Overall quality feedback
        if quality_score["overall_quality"] > 0.8:
            feedback["main_points"].append("Outstanding overall performance quality")
        elif quality_score["overall_quality"] > 0.6:
            feedback["main_points"].append("Good performance with room for improvement")
        else:
            feedback["improvement_suggestions"].append(
                "Focus on overall sound quality and expression"
            )
        
        return feedback

# Example usage
if __name__ == "__main__":
    analyzer = MusicAIAnalyzer()
    analysis = analyzer.analyze_performance("performance.wav")
    
    print("\nPerformance Analysis Results:")
    print("\nMain Points:")
    for point in analysis["feedback"]["main_points"]:
        print(f"- {point}")
        
    print("\nTechnical Feedback:")
    for feedback in analysis["feedback"]["technical_feedback"]:
        print(f"- {feedback}")
        
    print("\nSuggestions for Improvement:")
    for suggestion in analysis["feedback"]["improvement_suggestions"]:
        print(f"- {suggestion}")
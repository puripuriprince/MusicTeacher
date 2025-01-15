import magenta.music as mm
from magenta.models.music_vae import configs, TrainedModel
from magenta.protobuf import music_pb2
import tensorflow as tf
import numpy as np
from typing import Dict, List, Optional

class AdaptiveMusicGenerator:
    def __init__(self):
        # Initialize music generation models
        self.melody_model = TrainedModel(
            configs.CONFIG_MAP['mel_16bar_hi_vae'],
            batch_size=1,
            checkpoint_dir_or_path='mel_16bar_checkpoint'
        )
        
        self.rhythm_model = TrainedModel(
            configs.CONFIG_MAP['drums_2bar_hi_vae'],
            batch_size=1,
            checkpoint_dir_or_path='drums_checkpoint'
        )
        
    def generate_practice_content(self, 
                                analysis_results: Dict,
                                instrument: str,
                                difficulty_target: float = 0.5) -> Dict:
        """Generate personalized practice content based on analysis"""
        
        # Extract key metrics from analysis
        current_level = self._calculate_skill_level(analysis_results)
        weak_points = self._identify_weak_points(analysis_results)
        
        # Generate appropriate practice material
        practice_pieces = self._generate_targeted_pieces(
            current_level,
            weak_points,
            instrument,
            difficulty_target
        )
        
        return {
            "practice_pieces": practice_pieces,
            "difficulty_progression": self._create_difficulty_progression(current_level),
            "focus_areas": weak_points,
            "practice_plan": self._create_practice_plan(practice_pieces, weak_points)
        }
    
    def _calculate_skill_level(self, analysis: Dict) -> float:
        """Calculate overall skill level from analysis results"""
        weights = {
            'tune_analysis': 0.3,
            'technical_analysis': 0.4,
            'quality_score': 0.3
        }
        
        skill_score = (
            analysis['tune_analysis']['overall_tune_score'] * weights['tune_analysis'] +
            analysis['technical_analysis']['timing_consistency'] * weights['technical_analysis'] +
            analysis['quality_score']['overall_quality'] * weights['quality_score']
        )
        
        return float(skill_score)
    
    def _identify_weak_points(self, analysis: Dict) -> List[Dict]:
        """Identify areas needing improvement"""
        weak_points = []
        
        # Check pitch stability
        if analysis['tune_analysis']['pitch_stability'] < 0.7:
            weak_points.append({
                'aspect': 'pitch',
                'score': analysis['tune_analysis']['pitch_stability'],
                'priority': 'high' if analysis['tune_analysis']['pitch_stability'] < 0.5 else 'medium'
            })
            
        # Check rhythm
        if analysis['technical_analysis']['timing_consistency'] < 0.7:
            weak_points.append({
                'aspect': 'rhythm',
                'score': analysis['technical_analysis']['timing_consistency'],
                'priority': 'high' if analysis['technical_analysis']['timing_consistency'] < 0.5 else 'medium'
            })
            
        return weak_points
    
    def _generate_targeted_pieces(self,
                                skill_level: float,
                                weak_points: List[Dict],
                                instrument: str,
                                target_difficulty: float) -> List[Dict]:
        """Generate practice pieces targeting specific improvements"""
        practice_pieces = []
        
        # Adjust generation parameters based on skill level and weak points
        temperature = self._calculate_temperature(skill_level, target_difficulty)
        
        # Generate pieces focusing on each weak point
        for weak_point in weak_points:
            if weak_point['aspect'] == 'pitch':
                piece = self._generate_pitch_focused_piece(
                    temperature,
                    instrument,
                    weak_point['score']
                )
                practice_pieces.append(piece)
                
            elif weak_point['aspect'] == 'rhythm':
                piece = self._generate_rhythm_focused_piece(
                    temperature,
                    instrument,
                    weak_point['score']
                )
                practice_pieces.append(piece)
        
        # Generate general practice piece
        practice_pieces.append(
            self._generate_balanced_piece(temperature, instrument)
        )
        
        return practice_pieces
    
    def _generate_pitch_focused_piece(self,
                                    temperature: float,
                                    instrument: str,
                                    current_skill: float) -> Dict:
        """Generate a piece focusing on pitch practice"""
        # Adjust melody model parameters
        z = np.random.normal(size=[1, self.melody_model._config.hparams.z_size])
        
        # Generate melody sequence
        melody_sequence = self.melody_model.decode(
            length=64,
            z=z,
            temperature=temperature
        )[0]
        
        # Adjust for instrument and skill level
        adjusted_sequence = self._adjust_for_instrument(
            melody_sequence,
            instrument,
            current_skill
        )
        
        return {
            'type': 'pitch_practice',
            'sequence': adjusted_sequence,
            'difficulty': temperature,
            'focus': 'Pitch control and intonation',
            'instructions': self._generate_pitch_instructions(current_skill)
        }
    
    def _generate_rhythm_focused_piece(self,
                                     temperature: float,
                                     instrument: str,
                                     current_skill: float) -> Dict:
        """Generate a piece focusing on rhythm practice"""
        # Generate rhythm sequence
        z = np.random.normal(size=[1, self.rhythm_model._config.hparams.z_size])
        rhythm_sequence = self.rhythm_model.decode(
            length=32,
            z=z,
            temperature=temperature
        )[0]
        
        # Adjust for instrument and skill level
        adjusted_sequence = self._adjust_for_instrument(
            rhythm_sequence,
            instrument,
            current_skill
        )
        
        return {
            'type': 'rhythm_practice',
            'sequence': adjusted_sequence,
            'difficulty': temperature,
            'focus': 'Rhythm and timing',
            'instructions': self._generate_rhythm_instructions(current_skill)
        }
    
    def _adjust_for_instrument(self,
                             sequence: music_pb2.NoteSequence,
                             instrument: str,
                             skill_level: float) -> music_pb2.NoteSequence:
        """Adjust the generated sequence for specific instrument"""
        adjusted_sequence = music_pb2.NoteSequence()
        adjusted_sequence.CopyFrom(sequence)
        
        # Adjust note range based on instrument
        if instrument.lower() in ['piano', 'keyboard']:
            self._adjust_piano_range(adjusted_sequence)
        elif instrument.lower() in ['guitar', 'bass']:
            self._adjust_guitar_range(adjusted_sequence)
        elif instrument.lower() in ['violin', 'viola', 'cello']:
            self._adjust_string_range(adjusted_sequence)
        
        return adjusted_sequence
    
    def _create_practice_plan(self,
                            pieces: List[Dict],
                            weak_points: List[Dict]) -> List[Dict]:
        """Create structured practice plan"""
        practice_plan = []
        
        for piece in pieces:
            plan_item = {
                'piece_type': piece['type'],
                'duration': '15 minutes',
                'focus_points': piece['focus'],
                'instructions': piece['instructions'],
                'progression': [
                    'Start at 70% tempo',
                    'Increase tempo gradually',
                    'Practice difficult sections in isolation',
                    'Combine sections at full tempo'
                ]
            }
            practice_plan.append(plan_item)
        
        return practice_plan
    
    def _generate_pitch_instructions(self, skill_level: float) -> List[str]:
        """Generate specific instructions for pitch practice"""
        instructions = [
            "Focus on maintaining consistent intonation",
            "Pay attention to key changes",
            "Practice problematic intervals slowly"
        ]
        
        if skill_level < 0.5:
            instructions.extend([
                "Use a tuner for reference",
                "Record yourself and analyze pitch accuracy"
            ])
            
        return instructions
    
    def _generate_rhythm_instructions(self, skill_level: float) -> List[str]:
        """Generate specific instructions for rhythm practice"""
        instructions = [
            "Practice with a metronome",
            "Count out loud while playing",
            "Focus on maintaining steady tempo"
        ]
        
        if skill_level < 0.5:
            instructions.extend([
                "Start at a slower tempo",
                "Clap the rhythm before playing"
            ])
            
        return instructions
    
    def _calculate_temperature(self,
                             current_level: float,
                             target_difficulty: float) -> float:
        """Calculate generation temperature based on skill level"""
        base_temperature = 0.8
        skill_adjustment = (target_difficulty - current_level) * 0.2
        return min(max(base_temperature + skill_adjustment, 0.1), 1.0)

# Example usage
if __name__ == "__main__":
    generator = AdaptiveMusicGenerator()
    
    # Example analysis results
    analysis_results = {
        'tune_analysis': {'overall_tune_score': 0.7, 'pitch_stability': 0.6},
        'technical_analysis': {'timing_consistency': 0.8},
        'quality_score': {'overall_quality': 0.75}
    }
    
    # Generate practice content
    practice_content = generator.generate_practice_content(
        analysis_results,
        instrument="piano",
        difficulty_target=0.8
    )
    
    # Print practice plan
    print("\nPersonalized Practice Plan:")
    for i, session in enumerate(practice_content['practice_plan'], 1):
        print(f"\nSession {i}:")
        print(f"Focus: {session['focus_points']}")
        print("Instructions:")
        for instruction in session['instructions']:
            print(f"- {instruction}")
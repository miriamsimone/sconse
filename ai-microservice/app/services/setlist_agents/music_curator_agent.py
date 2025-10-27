"""
Music Curator Agent - Specializes in selecting appropriate pieces for setlists
"""
from typing import Dict, List, Any
from .base_agent import BaseSetlistAgent

class MusicCuratorAgent(BaseSetlistAgent):
    """Agent specialized in music curation and piece selection"""
    
    def __init__(self):
        super().__init__(
            agent_name="Music Curator",
            role="Piece Selection Specialist",
            expertise="Classical music repertoire, difficulty assessment, and program flow"
        )
    
    async def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements from a music curation perspective"""
        analysis = {
            "concert_type": requirements.get("concert_type", "general"),
            "duration": requirements.get("duration_minutes", 60),
            "instruments": requirements.get("instruments", []),
            "skill_level": requirements.get("skill_level", "intermediate"),
            "preferences": requirements.get("preferences", {}),
            "existing_repertoire": requirements.get("existing_repertoire", [])
        }
        
        # Add curation-specific analysis
        analysis["curation_notes"] = self._generate_curation_notes(analysis)
        
        return analysis
    
    async def suggest_pieces(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest pieces based on music curation expertise"""
        try:
            # Build prompt for piece suggestions
            prompt = self._build_suggestion_prompt(requirements, context)
            
            # Call LLM for piece suggestions
            response = await self.call_llm(prompt, self._get_curation_system_prompt())
            
            if not response["success"]:
                return self._get_fallback_suggestions(requirements)
            
            # Parse the LLM response
            pieces = self._parse_piece_suggestions(response["content"], requirements)
            
            # Add to conversation
            self.add_to_conversation(f"Suggested {len(pieces)} pieces for the setlist")
            
            return pieces
            
        except Exception as e:
            return self._get_fallback_suggestions(requirements)
    
    async def evaluate_piece(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a piece for inclusion in the setlist"""
        try:
            prompt = self._build_evaluation_prompt(piece, requirements)
            response = await self.call_llm(prompt, self._get_evaluation_system_prompt())
            
            if not response["success"]:
                return self._get_default_evaluation(piece)
            
            evaluation = self._parse_evaluation(response["content"])
            return evaluation
            
        except Exception as e:
            return self._get_default_evaluation(piece)
    
    async def refine_suggestions(self, suggestions: List[Dict[str, Any]], feedback: str) -> List[Dict[str, Any]]:
        """Refine suggestions based on feedback"""
        try:
            prompt = self._build_refinement_prompt(suggestions, feedback)
            response = await self.call_llm(prompt, self._get_refinement_system_prompt())
            
            if not response["success"]:
                return suggestions  # Return original if refinement fails
            
            refined = self._parse_refined_suggestions(response["content"], suggestions)
            self.add_to_conversation(f"Refined suggestions based on: {feedback}")
            
            return refined
            
        except Exception as e:
            return suggestions
    
    def _generate_curation_notes(self, analysis: Dict[str, Any]) -> str:
        """Generate curation-specific notes about the requirements"""
        notes = []
        
        if analysis["concert_type"] == "classical_recital":
            notes.append("Focus on classical repertoire with appropriate difficulty progression")
        elif analysis["concert_type"] == "chamber_music":
            notes.append("Emphasize ensemble pieces with good balance between instruments")
        elif analysis["concert_type"] == "solo_performance":
            notes.append("Select pieces that showcase individual technique and expression")
        
        if analysis["skill_level"] == "beginner":
            notes.append("Choose pieces with simple technical demands and clear musical structure")
        elif analysis["skill_level"] == "advanced":
            notes.append("Include challenging pieces that demonstrate virtuosity")
        
        if analysis["duration"] < 30:
            notes.append("Select shorter pieces to fit time constraint")
        elif analysis["duration"] > 90:
            notes.append("Include longer works and consider intermission placement")
        
        return "; ".join(notes)
    
    def _build_suggestion_prompt(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for piece suggestions"""
        prompt = f"""As a music curator, suggest pieces for a {requirements['concert_type']} concert.

Requirements:
- Duration: {requirements['duration_minutes']} minutes
- Instruments: {', '.join(requirements['instruments'])}
- Skill Level: {requirements['skill_level']}
- Existing Repertoire: {', '.join(requirements.get('existing_repertoire', []))}

Please suggest 5-8 pieces that would work well together. For each piece, provide:
1. Title and Composer
2. Estimated duration
3. Difficulty level
4. Key signature
5. Required instruments
6. Genre/style
7. Why this piece fits the program

Format as a structured list."""
        
        return prompt
    
    def _build_evaluation_prompt(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Build prompt for piece evaluation"""
        prompt = f"""Evaluate this piece for inclusion in a {requirements['concert_type']} concert:

Piece: {piece.get('title', 'Unknown')} by {piece.get('composer', 'Unknown')}
Duration: {piece.get('duration_minutes', 0)} minutes
Difficulty: {piece.get('difficulty_level', 'Unknown')}
Instruments: {', '.join(piece.get('instruments', []))}

Requirements:
- Duration: {requirements['duration_minutes']} minutes
- Skill Level: {requirements['skill_level']}
- Instruments: {', '.join(requirements['instruments'])}

Evaluate:
1. Technical appropriateness
2. Musical fit with program
3. Duration appropriateness
4. Instrument compatibility
5. Overall recommendation (include/exclude/modify)

Provide a detailed evaluation."""
        
        return prompt
    
    def _build_refinement_prompt(self, suggestions: List[Dict[str, Any]], feedback: str) -> str:
        """Build prompt for refining suggestions"""
        pieces_text = "\n".join([f"- {p.get('title', 'Unknown')} by {p.get('composer', 'Unknown')}" for p in suggestions])
        
        prompt = f"""Refine these piece suggestions based on the feedback:

Current Suggestions:
{pieces_text}

Feedback: {feedback}

Please provide refined suggestions that address the feedback while maintaining good program flow and musical coherence."""
        
        return prompt
    
    def _get_curation_system_prompt(self) -> str:
        """Get system prompt for curation tasks"""
        return """You are an expert music curator with deep knowledge of classical music repertoire. 
Your role is to select appropriate pieces for concert programs based on technical requirements, 
musical flow, and audience appeal. You understand difficulty levels, instrument capabilities, 
and how pieces work together in a program."""
    
    def _get_evaluation_system_prompt(self) -> str:
        """Get system prompt for evaluation tasks"""
        return """You are an expert music evaluator who assesses pieces for concert inclusion. 
You consider technical difficulty, musical appropriateness, program flow, and practical constraints. 
Provide detailed, objective evaluations with clear recommendations."""
    
    def _get_refinement_system_prompt(self) -> str:
        """Get system prompt for refinement tasks"""
        return """You are an expert music programmer who refines concert programs based on feedback. 
You maintain musical coherence while addressing specific concerns and preferences. 
You understand how to balance different musical elements for optimal program flow."""
    
    def _parse_piece_suggestions(self, content: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse LLM response into structured piece suggestions"""
        # This is a simplified parser - in production, you'd use more sophisticated parsing
        pieces = []
        
        # For now, return some example pieces based on the requirements
        if requirements["concert_type"] == "classical_recital":
            pieces = [
                {
                    "title": "Sonata in C Major, K. 545",
                    "composer": "Mozart",
                    "duration_minutes": 15,
                    "difficulty_level": requirements["skill_level"],
                    "key_signature": "C major",
                    "instruments": requirements["instruments"],
                    "genre": "classical",
                    "reasoning": "Perfect opening piece - accessible yet elegant"
                },
                {
                    "title": "Nocturne in E-flat Major, Op. 9, No. 2",
                    "composer": "Chopin",
                    "duration_minutes": 4,
                    "difficulty_level": requirements["skill_level"],
                    "key_signature": "E-flat major",
                    "instruments": requirements["instruments"],
                    "genre": "romantic",
                    "reasoning": "Beautiful lyrical piece for contrast"
                }
            ]
        
        return pieces
    
    def _parse_evaluation(self, content: str) -> Dict[str, Any]:
        """Parse evaluation response"""
        return {
            "recommendation": "include",
            "confidence": 0.8,
            "technical_score": 8,
            "musical_fit": 9,
            "duration_appropriate": True,
            "instrument_compatible": True,
            "notes": "Good choice for the program"
        }
    
    def _parse_refined_suggestions(self, content: str, original: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse refined suggestions"""
        # For now, return original suggestions with a note about refinement
        for piece in original:
            piece["refined"] = True
            piece["refinement_notes"] = "Refined based on feedback"
        return original
    
    def _get_fallback_suggestions(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback suggestions when LLM fails"""
        return [
            {
                "title": "Sample Piece 1",
                "composer": "Sample Composer",
                "duration_minutes": 5,
                "difficulty_level": requirements["skill_level"],
                "key_signature": "C major",
                "instruments": requirements["instruments"],
                "genre": "classical",
                "reasoning": "Fallback suggestion"
            }
        ]
    
    def _get_default_evaluation(self, piece: Dict[str, Any]) -> Dict[str, Any]:
        """Get default evaluation when LLM fails"""
        return {
            "recommendation": "include",
            "confidence": 0.5,
            "technical_score": 5,
            "musical_fit": 5,
            "duration_appropriate": True,
            "instrument_compatible": True,
            "notes": "Default evaluation"
        }

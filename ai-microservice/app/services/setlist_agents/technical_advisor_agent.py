"""
Technical Advisor Agent - Specializes in technical feasibility and performance considerations
"""
from typing import Dict, List, Any
from .base_agent import BaseSetlistAgent

class TechnicalAdvisorAgent(BaseSetlistAgent):
    """Agent specialized in technical performance considerations"""
    
    def __init__(self):
        super().__init__(
            agent_name="Technical Advisor",
            role="Performance Feasibility Specialist",
            expertise="Technical difficulty assessment, performance logistics, and practical constraints"
        )
    
    async def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements from a technical perspective"""
        analysis = {
            "skill_level": requirements.get("skill_level", "intermediate"),
            "instruments": requirements.get("instruments", []),
            "duration": requirements.get("duration_minutes", 60),
            "technical_constraints": self._assess_technical_constraints(requirements),
            "performance_considerations": self._assess_performance_considerations(requirements)
        }
        
        return analysis
    
    async def suggest_pieces(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest pieces based on technical feasibility"""
        try:
            prompt = self._build_technical_suggestion_prompt(requirements, context)
            response = await self.call_llm(prompt, self._get_technical_system_prompt())
            
            if not response["success"]:
                return self._get_fallback_technical_suggestions(requirements)
            
            pieces = self._parse_technical_suggestions(response["content"], requirements)
            self.add_to_conversation(f"Provided technical analysis for {len(pieces)} pieces")
            
            return pieces
            
        except Exception as e:
            return self._get_fallback_technical_suggestions(requirements)
    
    async def evaluate_piece(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a piece for technical feasibility"""
        try:
            prompt = self._build_technical_evaluation_prompt(piece, requirements)
            response = await self.call_llm(prompt, self._get_evaluation_system_prompt())
            
            if not response["success"]:
                return self._get_default_technical_evaluation(piece, requirements)
            
            evaluation = self._parse_technical_evaluation(response["content"], piece, requirements)
            return evaluation
            
        except Exception as e:
            return self._get_default_technical_evaluation(piece, requirements)
    
    async def refine_suggestions(self, suggestions: List[Dict[str, Any]], feedback: str) -> List[Dict[str, Any]]:
        """Refine suggestions based on technical feedback"""
        try:
            prompt = self._build_technical_refinement_prompt(suggestions, feedback)
            response = await self.call_llm(prompt, self._get_refinement_system_prompt())
            
            if not response["success"]:
                return suggestions
            
            refined = self._parse_technical_refinements(response["content"], suggestions)
            self.add_to_conversation(f"Refined technical recommendations based on: {feedback}")
            
            return refined
            
        except Exception as e:
            return suggestions
    
    def _assess_technical_constraints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess technical constraints for the performance"""
        constraints = {
            "max_difficulty": self._get_max_difficulty(requirements["skill_level"]),
            "instrument_limitations": self._assess_instrument_limitations(requirements["instruments"]),
            "duration_limits": self._assess_duration_limits(requirements["duration_minutes"]),
            "ensemble_considerations": self._assess_ensemble_considerations(requirements)
        }
        
        return constraints
    
    def _assess_performance_considerations(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess performance logistics and considerations"""
        considerations = {
            "warmup_time": self._estimate_warmup_time(requirements["instruments"]),
            "transition_difficulty": self._assess_transition_difficulty(requirements),
            "memory_requirements": self._assess_memory_requirements(requirements["skill_level"]),
            "physical_demands": self._assess_physical_demands(requirements["instruments"])
        }
        
        return considerations
    
    def _get_max_difficulty(self, skill_level: str) -> int:
        """Get maximum difficulty level for the skill level"""
        difficulty_map = {
            "beginner": 3,
            "intermediate": 6,
            "advanced": 9,
            "professional": 10
        }
        return difficulty_map.get(skill_level, 5)
    
    def _assess_instrument_limitations(self, instruments: List[str]) -> Dict[str, Any]:
        """Assess limitations for each instrument"""
        limitations = {}
        
        for instrument in instruments:
            if instrument == "piano":
                limitations[instrument] = {
                    "technical_demands": "High - requires independent hand coordination",
                    "memory_requirements": "High - complex harmonic progressions",
                    "physical_demands": "Moderate - finger dexterity and endurance"
                }
            elif instrument == "violin":
                limitations[instrument] = {
                    "technical_demands": "Very High - intonation and bowing technique",
                    "memory_requirements": "High - melodic lines and phrasing",
                    "physical_demands": "High - sustained playing position"
                }
            elif instrument == "cello":
                limitations[instrument] = {
                    "technical_demands": "High - left hand technique and bowing",
                    "memory_requirements": "Moderate - bass line patterns",
                    "physical_demands": "Moderate - sitting position"
                }
            else:
                limitations[instrument] = {
                    "technical_demands": "Moderate",
                    "memory_requirements": "Moderate",
                    "physical_demands": "Moderate"
                }
        
        return limitations
    
    def _assess_duration_limits(self, duration_minutes: int) -> Dict[str, Any]:
        """Assess duration-related constraints"""
        if duration_minutes < 30:
            return {
                "max_piece_length": 8,
                "recommended_pieces": 4,
                "considerations": "Short program - focus on concise, impactful pieces"
            }
        elif duration_minutes < 60:
            return {
                "max_piece_length": 15,
                "recommended_pieces": 6,
                "considerations": "Medium program - good balance of short and medium pieces"
            }
        else:
            return {
                "max_piece_length": 25,
                "recommended_pieces": 8,
                "considerations": "Long program - can include extended works and intermission"
            }
    
    def _assess_ensemble_considerations(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess ensemble-specific considerations"""
        instruments = requirements.get("instruments", [])
        
        if len(instruments) == 1:
            return {
                "type": "solo",
                "considerations": "Focus on solo repertoire, consider technical variety"
            }
        elif len(instruments) == 2:
            return {
                "type": "duo",
                "considerations": "Balance between instruments, consider dialogue and harmony"
            }
        elif len(instruments) <= 4:
            return {
                "type": "chamber",
                "considerations": "Ensemble balance, individual parts, group dynamics"
            }
        else:
            return {
                "type": "orchestral",
                "considerations": "Section balance, conductor coordination, large-scale works"
            }
    
    def _estimate_warmup_time(self, instruments: List[str]) -> int:
        """Estimate warmup time needed for instruments"""
        total_warmup = 0
        for instrument in instruments:
            if instrument in ["violin", "cello", "viola", "bass"]:
                total_warmup += 10  # String instruments need more warmup
            elif instrument == "piano":
                total_warmup += 5   # Piano needs less warmup
            else:
                total_warmup += 7   # Other instruments moderate warmup
        
        return min(total_warmup, 20)  # Cap at 20 minutes
    
    def _assess_transition_difficulty(self, requirements: Dict[str, Any]) -> str:
        """Assess difficulty of transitions between pieces"""
        skill_level = requirements.get("skill_level", "intermediate")
        
        if skill_level == "beginner":
            return "Easy - simple key relationships, similar tempos"
        elif skill_level == "intermediate":
            return "Moderate - some key changes, tempo variations"
        elif skill_level == "advanced":
            return "Challenging - complex modulations, dramatic tempo changes"
        else:
            return "Professional - any transition possible"
    
    def _assess_memory_requirements(self, skill_level: str) -> str:
        """Assess memory requirements for the skill level"""
        if skill_level == "beginner":
            return "Low - shorter pieces, simpler structures"
        elif skill_level == "intermediate":
            return "Moderate - medium-length pieces, some memorization"
        elif skill_level == "advanced":
            return "High - longer works, complex memorization"
        else:
            return "Professional - extensive memorization expected"
    
    def _assess_physical_demands(self, instruments: List[str]) -> str:
        """Assess physical demands for the instrument combination"""
        if "piano" in instruments and len(instruments) == 1:
            return "Moderate - finger dexterity and endurance"
        elif any(inst in instruments for inst in ["violin", "cello", "viola"]):
            return "High - sustained playing position and bowing"
        else:
            return "Moderate - standard physical demands"
    
    def _build_technical_suggestion_prompt(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for technical suggestions"""
        prompt = f"""As a technical advisor, suggest pieces that are technically appropriate for this performance:

Performance Details:
- Skill Level: {requirements['skill_level']}
- Instruments: {', '.join(requirements['instruments'])}
- Duration: {requirements['duration_minutes']} minutes
- Concert Type: {requirements.get('concert_type', 'general')}

Technical Considerations:
- Maximum difficulty level: {self._get_max_difficulty(requirements['skill_level'])}/10
- Instrument limitations: {self._assess_instrument_limitations(requirements['instruments'])}
- Duration constraints: {self._assess_duration_limits(requirements['duration_minutes'])}

Please suggest pieces that are technically feasible and appropriate for the performer's skill level."""
        
        return prompt
    
    def _build_technical_evaluation_prompt(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Build prompt for technical evaluation"""
        prompt = f"""Evaluate this piece for technical feasibility:

Piece: {piece.get('title', 'Unknown')} by {piece.get('composer', 'Unknown')}
Difficulty: {piece.get('difficulty_level', 'Unknown')}
Duration: {piece.get('duration_minutes', 0)} minutes
Instruments: {', '.join(piece.get('instruments', []))}

Performer Profile:
- Skill Level: {requirements['skill_level']}
- Available Instruments: {', '.join(requirements['instruments'])}

Evaluate:
1. Technical difficulty appropriateness
2. Physical demands vs. performer capability
3. Memory requirements
4. Instrument compatibility
5. Performance logistics
6. Overall technical recommendation

Provide detailed technical analysis."""
        
        return prompt
    
    def _build_technical_refinement_prompt(self, suggestions: List[Dict[str, Any]], feedback: str) -> str:
        """Build prompt for technical refinement"""
        pieces_text = "\n".join([f"- {p.get('title', 'Unknown')} (Difficulty: {p.get('difficulty_level', 'Unknown')})" for p in suggestions])
        
        prompt = f"""Refine these technical recommendations based on feedback:

Current Suggestions:
{pieces_text}

Technical Feedback: {feedback}

Please provide refined technical recommendations that address the feedback while maintaining appropriate difficulty levels and technical feasibility."""
        
        return prompt
    
    def _get_technical_system_prompt(self) -> str:
        """Get system prompt for technical tasks"""
        return """You are an expert technical advisor for musical performances. You understand 
instrument capabilities, technical difficulty levels, performance logistics, and practical 
constraints. Your role is to ensure that suggested pieces are technically appropriate and 
feasible for the given performer and performance context."""
    
    def _get_evaluation_system_prompt(self) -> str:
        """Get system prompt for technical evaluation"""
        return """You are an expert technical evaluator who assesses pieces for performance feasibility. 
You consider technical difficulty, physical demands, memory requirements, instrument compatibility, 
and practical performance considerations. Provide detailed technical analysis with clear recommendations."""
    
    def _get_refinement_system_prompt(self) -> str:
        """Get system prompt for technical refinement"""
        return """You are an expert technical consultant who refines performance recommendations based on 
technical feedback. You maintain appropriate difficulty levels while addressing specific technical 
concerns and ensuring performance feasibility."""
    
    def _parse_technical_suggestions(self, content: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse technical suggestions from LLM response"""
        # Simplified parser - in production, use more sophisticated parsing
        return [
            {
                "title": "Technical Piece 1",
                "composer": "Technical Composer",
                "duration_minutes": 8,
                "difficulty_level": requirements["skill_level"],
                "key_signature": "C major",
                "instruments": requirements["instruments"],
                "genre": "classical",
                "reasoning": "Technically appropriate for skill level",
                "technical_notes": "Moderate technical demands, good for this level"
            }
        ]
    
    def _parse_technical_evaluation(self, content: str, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Parse technical evaluation response"""
        return {
            "recommendation": "include",
            "confidence": 0.8,
            "technical_difficulty_score": 7,
            "physical_demands": "moderate",
            "memory_requirements": "moderate",
            "instrument_compatibility": True,
            "performance_feasible": True,
            "technical_notes": "Appropriate technical level for performer"
        }
    
    def _parse_technical_refinements(self, content: str, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse technical refinements"""
        for piece in suggestions:
            piece["technically_refined"] = True
            piece["technical_refinement_notes"] = "Refined based on technical feedback"
        return suggestions
    
    def _get_fallback_technical_suggestions(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback technical suggestions"""
        return [
            {
                "title": "Technical Fallback Piece",
                "composer": "Technical Composer",
                "duration_minutes": 5,
                "difficulty_level": requirements["skill_level"],
                "key_signature": "C major",
                "instruments": requirements["instruments"],
                "genre": "classical",
                "reasoning": "Technically safe choice",
                "technical_notes": "Fallback suggestion"
            }
        ]
    
    def _get_default_technical_evaluation(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get default technical evaluation"""
        return {
            "recommendation": "include",
            "confidence": 0.5,
            "technical_difficulty_score": 5,
            "physical_demands": "moderate",
            "memory_requirements": "moderate",
            "instrument_compatibility": True,
            "performance_feasible": True,
            "technical_notes": "Default technical evaluation"
        }

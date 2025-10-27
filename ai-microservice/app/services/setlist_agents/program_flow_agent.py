"""
Program Flow Agent - Specializes in concert program structure and flow
"""
from typing import Dict, List, Any
from .base_agent import BaseSetlistAgent

class ProgramFlowAgent(BaseSetlistAgent):
    """Agent specialized in program structure and musical flow"""
    
    def __init__(self):
        super().__init__(
            agent_name="Program Flow Director",
            role="Concert Structure Specialist",
            expertise="Program flow, key relationships, tempo progression, and audience engagement"
        )
    
    async def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements from a program flow perspective"""
        analysis = {
            "concert_type": requirements.get("concert_type", "general"),
            "duration": requirements.get("duration_minutes", 60),
            "instruments": requirements.get("instruments", []),
            "flow_considerations": self._assess_flow_considerations(requirements),
            "audience_engagement": self._assess_audience_engagement(requirements),
            "program_structure": self._design_program_structure(requirements)
        }
        
        return analysis
    
    async def suggest_pieces(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest pieces based on program flow considerations"""
        try:
            prompt = self._build_flow_suggestion_prompt(requirements, context)
            response = await self.call_llm(prompt, self._get_flow_system_prompt())
            
            if not response["success"]:
                return self._get_fallback_flow_suggestions(requirements)
            
            pieces = self._parse_flow_suggestions(response["content"], requirements)
            self.add_to_conversation(f"Designed program flow with {len(pieces)} pieces")
            
            return pieces
            
        except Exception as e:
            return self._get_fallback_flow_suggestions(requirements)
    
    async def evaluate_piece(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a piece for program flow fit"""
        try:
            prompt = self._build_flow_evaluation_prompt(piece, requirements)
            response = await self.call_llm(prompt, self._get_evaluation_system_prompt())
            
            if not response["success"]:
                return self._get_default_flow_evaluation(piece, requirements)
            
            evaluation = self._parse_flow_evaluation(response["content"], piece, requirements)
            return evaluation
            
        except Exception as e:
            return self._get_default_flow_evaluation(piece, requirements)
    
    async def refine_suggestions(self, suggestions: List[Dict[str, Any]], feedback: str) -> List[Dict[str, Any]]:
        """Refine suggestions based on flow feedback"""
        try:
            prompt = self._build_flow_refinement_prompt(suggestions, feedback)
            response = await self.call_llm(prompt, self._get_refinement_system_prompt())
            
            if not response["success"]:
                return suggestions
            
            refined = self._parse_flow_refinements(response["content"], suggestions)
            self.add_to_conversation(f"Refined program flow based on: {feedback}")
            
            return refined
            
        except Exception as e:
            return suggestions
    
    def _assess_flow_considerations(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess program flow considerations"""
        considerations = {
            "opening_strategy": self._get_opening_strategy(requirements),
            "closing_strategy": self._get_closing_strategy(requirements),
            "tempo_progression": self._design_tempo_progression(requirements),
            "key_progression": self._design_key_progression(requirements),
            "contrast_balance": self._assess_contrast_balance(requirements)
        }
        
        return considerations
    
    def _assess_audience_engagement(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess audience engagement strategies"""
        engagement = {
            "attention_span": self._estimate_attention_span(requirements["duration_minutes"]),
            "energy_levels": self._design_energy_progression(requirements),
            "variety_requirements": self._assess_variety_requirements(requirements),
            "climax_placement": self._determine_climax_placement(requirements)
        }
        
        return engagement
    
    def _design_program_structure(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design overall program structure"""
        duration = requirements["duration_minutes"]
        
        if duration < 30:
            return {
                "structure": "single_set",
                "sections": ["opening", "development", "climax", "closing"],
                "intermission": False,
                "recommended_pieces": 4
            }
        elif duration < 60:
            return {
                "structure": "single_set_extended",
                "sections": ["opening", "development", "climax", "resolution", "closing"],
                "intermission": False,
                "recommended_pieces": 6
            }
        else:
            return {
                "structure": "two_sets",
                "sections": ["first_set", "intermission", "second_set"],
                "intermission": True,
                "recommended_pieces": 8
            }
    
    def _get_opening_strategy(self, requirements: Dict[str, Any]) -> str:
        """Determine opening strategy"""
        concert_type = requirements.get("concert_type", "general")
        
        if concert_type == "classical_recital":
            return "Start with accessible, technically sound piece to establish confidence"
        elif concert_type == "chamber_music":
            return "Begin with ensemble piece that showcases group cohesion"
        elif concert_type == "solo_performance":
            return "Open with piece that demonstrates technical prowess"
        else:
            return "Start with engaging, audience-friendly piece"
    
    def _get_closing_strategy(self, requirements: Dict[str, Any]) -> str:
        """Determine closing strategy"""
        concert_type = requirements.get("concert_type", "general")
        
        if concert_type == "classical_recital":
            return "End with impressive, memorable piece that leaves strong impression"
        elif concert_type == "chamber_music":
            return "Close with ensemble piece that showcases group virtuosity"
        elif concert_type == "solo_performance":
            return "Finish with piece that demonstrates full technical and musical range"
        else:
            return "End with uplifting, satisfying piece"
    
    def _design_tempo_progression(self, requirements: Dict[str, Any]) -> List[str]:
        """Design tempo progression for the program"""
        duration = requirements["duration_minutes"]
        
        if duration < 30:
            return ["moderate", "slow", "fast", "moderate"]
        elif duration < 60:
            return ["moderate", "slow", "fast", "moderate", "slow", "fast"]
        else:
            return ["moderate", "slow", "fast", "moderate", "slow", "fast", "moderate", "fast"]
    
    def _design_key_progression(self, requirements: Dict[str, Any]) -> List[str]:
        """Design key progression for the program"""
        # Simple key progression - in production, use more sophisticated music theory
        return ["C major", "G major", "A minor", "F major", "D major", "E minor", "G major", "C major"]
    
    def _assess_contrast_balance(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess contrast and balance requirements"""
        return {
            "tempo_contrast": "Include both fast and slow pieces",
            "mood_contrast": "Balance between lyrical and dramatic pieces",
            "technical_contrast": "Mix technically demanding and accessible pieces",
            "key_contrast": "Use different keys for variety and interest"
        }
    
    def _estimate_attention_span(self, duration_minutes: int) -> int:
        """Estimate audience attention span"""
        if duration_minutes < 30:
            return 15  # Short attention span for short programs
        elif duration_minutes < 60:
            return 20  # Medium attention span
        else:
            return 25  # Longer attention span for extended programs
    
    def _design_energy_progression(self, requirements: Dict[str, Any]) -> List[str]:
        """Design energy level progression"""
        duration = requirements["duration_minutes"]
        
        if duration < 30:
            return ["building", "sustained", "peak", "resolution"]
        elif duration < 60:
            return ["building", "sustained", "peak", "resolution", "building", "peak"]
        else:
            return ["building", "sustained", "peak", "resolution", "building", "sustained", "peak", "resolution"]
    
    def _assess_variety_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess variety requirements for the program"""
        return {
            "genre_variety": "Include different musical styles and periods",
            "technical_variety": "Mix different technical challenges",
            "emotional_variety": "Balance different emotional expressions",
            "instrumental_variety": "Showcase different aspects of instrument(s)"
        }
    
    def _determine_climax_placement(self, requirements: Dict[str, Any]) -> str:
        """Determine where to place the program climax"""
        duration = requirements["duration_minutes"]
        
        if duration < 30:
            return "75% through program"
        elif duration < 60:
            return "70% through program"
        else:
            return "65% through program"
    
    def _build_flow_suggestion_prompt(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for flow suggestions"""
        prompt = f"""As a program flow director, design a concert program with excellent flow:

Concert Details:
- Type: {requirements['concert_type']}
- Duration: {requirements['duration_minutes']} minutes
- Instruments: {', '.join(requirements['instruments'])}

Flow Considerations:
- Opening Strategy: {self._get_opening_strategy(requirements)}
- Closing Strategy: {self._get_closing_strategy(requirements)}
- Tempo Progression: {', '.join(self._design_tempo_progression(requirements))}
- Key Progression: {', '.join(self._design_key_progression(requirements))}

Design a program that flows naturally from piece to piece, building energy and interest throughout."""
        
        return prompt
    
    def _build_flow_evaluation_prompt(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Build prompt for flow evaluation"""
        prompt = f"""Evaluate this piece for program flow:

Piece: {piece.get('title', 'Unknown')} by {piece.get('composer', 'Unknown')}
Key: {piece.get('key_signature', 'Unknown')}
Duration: {piece.get('duration_minutes', 0)} minutes
Genre: {piece.get('genre', 'Unknown')}

Program Context:
- Concert Type: {requirements.get('concert_type', 'general')}
- Desired Flow: {self._assess_flow_considerations(requirements)}

Evaluate:
1. How well it fits the program flow
2. Key relationships with other pieces
3. Tempo appropriateness
4. Emotional/mood contribution
5. Audience engagement potential
6. Overall flow recommendation

Provide detailed flow analysis."""
        
        return prompt
    
    def _build_flow_refinement_prompt(self, suggestions: List[Dict[str, Any]], feedback: str) -> str:
        """Build prompt for flow refinement"""
        pieces_text = "\n".join([f"- {p.get('title', 'Unknown')} ({p.get('key_signature', 'Unknown')})" for p in suggestions])
        
        prompt = f"""Refine this program flow based on feedback:

Current Program:
{pieces_text}

Flow Feedback: {feedback}

Please provide refined program flow that addresses the feedback while maintaining excellent musical progression and audience engagement."""
        
        return prompt
    
    def _get_flow_system_prompt(self) -> str:
        """Get system prompt for flow tasks"""
        return """You are an expert program flow director with deep understanding of concert programming, 
musical flow, key relationships, tempo progression, and audience psychology. Your role is to design 
programs that flow naturally and engage audiences from start to finish."""
    
    def _get_evaluation_system_prompt(self) -> str:
        """Get system prompt for flow evaluation"""
        return """You are an expert program evaluator who assesses pieces for their contribution to 
overall program flow. You understand musical relationships, audience engagement, and how pieces 
work together to create a cohesive concert experience."""
    
    def _get_refinement_system_prompt(self) -> str:
        """Get system prompt for flow refinement"""
        return """You are an expert program consultant who refines concert programs based on flow feedback. 
You maintain excellent musical progression while addressing specific flow concerns and optimizing 
audience engagement."""
    
    def _parse_flow_suggestions(self, content: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse flow suggestions from LLM response"""
        # Simplified parser - in production, use more sophisticated parsing
        return [
            {
                "title": "Flow Piece 1",
                "composer": "Flow Composer",
                "duration_minutes": 6,
                "difficulty_level": requirements.get("skill_level", "intermediate"),
                "key_signature": "C major",
                "instruments": requirements["instruments"],
                "genre": "classical",
                "reasoning": "Perfect opening piece for program flow",
                "flow_notes": "Establishes energy and sets tone"
            }
        ]
    
    def _parse_flow_evaluation(self, content: str, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Parse flow evaluation response"""
        return {
            "recommendation": "include",
            "confidence": 0.8,
            "flow_score": 8,
            "key_compatibility": "good",
            "tempo_appropriateness": "excellent",
            "audience_engagement": "high",
            "flow_notes": "Excellent contribution to program flow"
        }
    
    def _parse_flow_refinements(self, content: str, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse flow refinements"""
        for piece in suggestions:
            piece["flow_refined"] = True
            piece["flow_refinement_notes"] = "Refined based on flow feedback"
        return suggestions
    
    def _get_fallback_flow_suggestions(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback flow suggestions"""
        return [
            {
                "title": "Flow Fallback Piece",
                "composer": "Flow Composer",
                "duration_minutes": 5,
                "difficulty_level": requirements.get("skill_level", "intermediate"),
                "key_signature": "C major",
                "instruments": requirements["instruments"],
                "genre": "classical",
                "reasoning": "Safe choice for program flow",
                "flow_notes": "Fallback suggestion"
            }
        ]
    
    def _get_default_flow_evaluation(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get default flow evaluation"""
        return {
            "recommendation": "include",
            "confidence": 0.5,
            "flow_score": 5,
            "key_compatibility": "moderate",
            "tempo_appropriateness": "moderate",
            "audience_engagement": "moderate",
            "flow_notes": "Default flow evaluation"
        }

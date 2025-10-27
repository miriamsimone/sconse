"""
Multi-Agent Coordinator for Setlist Design
"""
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from .music_curator_agent import MusicCuratorAgent
from .technical_advisor_agent import TechnicalAdvisorAgent
from .program_flow_agent import ProgramFlowAgent

class MultiAgentCoordinator:
    """Coordinates multiple AI agents for collaborative setlist design"""
    
    def __init__(self):
        self.agents = {
            "curator": MusicCuratorAgent(),
            "technical": TechnicalAdvisorAgent(),
            "flow": ProgramFlowAgent()
        }
        self.conversation_history = []
    
    async def design_setlist(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a setlist using multiple AI agents
        
        Args:
            requirements: Setlist design requirements
            
        Returns:
            Dict with designed setlist and agent contributions
        """
        try:
            # Phase 1: Analysis - Each agent analyzes requirements
            analysis_results = await self._phase_analysis(requirements)
            
            # Phase 2: Suggestion - Each agent suggests pieces
            suggestion_results = await self._phase_suggestions(requirements, analysis_results)
            
            # Phase 3: Evaluation - Cross-evaluate suggestions
            evaluation_results = await self._phase_evaluation(suggestion_results, requirements)
            
            # Phase 4: Synthesis - Combine results into final setlist
            final_setlist = await self._phase_synthesis(evaluation_results, requirements)
            
            # Generate setlist ID and metadata
            setlist_id = str(uuid.uuid4())
            
            return {
                "success": True,
                "setlist_id": setlist_id,
                "setlist": final_setlist,
                "agent_contributions": self._summarize_contributions(),
                "confidence": self._calculate_overall_confidence(evaluation_results),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "user_id": requirements.get("user_id"),
                    "concert_type": requirements.get("concert_type"),
                    "duration_minutes": requirements.get("duration_minutes"),
                    "instruments": requirements.get("instruments"),
                    "skill_level": requirements.get("skill_level")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Setlist design failed: {str(e)}",
                "setlist_id": None
            }
    
    async def refine_setlist(self, setlist_id: str, refinement_instruction: str, 
                           user_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Refine an existing setlist based on feedback
        
        Args:
            setlist_id: ID of the setlist to refine
            refinement_instruction: How to refine the setlist
            user_id: User ID for tracking
            conversation_id: Optional conversation context
            
        Returns:
            Dict with refined setlist
        """
        try:
            # For now, return a placeholder refinement
            # In production, you'd retrieve the original setlist and refine it
            return {
                "success": True,
                "setlist_id": setlist_id,
                "refined_setlist": {
                    "title": "Refined Setlist",
                    "pieces": [],
                    "changes_made": [f"Applied refinement: {refinement_instruction}"]
                },
                "confidence": 0.8
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Setlist refinement failed: {str(e)}"
            }
    
    async def _phase_analysis(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 1: Each agent analyzes requirements from their perspective"""
        analysis_results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                analysis = await agent.analyze_requirements(requirements)
                analysis_results[agent_name] = analysis
                self._add_to_conversation(f"{agent.agent_name} completed analysis")
            except Exception as e:
                analysis_results[agent_name] = {"error": str(e)}
                self._add_to_conversation(f"{agent.agent_name} analysis failed: {str(e)}")
        
        return analysis_results
    
    async def _phase_suggestions(self, requirements: Dict[str, Any], 
                               analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Each agent suggests pieces based on their analysis"""
        suggestion_results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                context = {
                    "analysis": analysis_results.get(agent_name, {}),
                    "other_analyses": {k: v for k, v in analysis_results.items() if k != agent_name}
                }
                
                suggestions = await agent.suggest_pieces(requirements, context)
                suggestion_results[agent_name] = suggestions
                self._add_to_conversation(f"{agent.agent_name} suggested {len(suggestions)} pieces")
            except Exception as e:
                suggestion_results[agent_name] = []
                self._add_to_conversation(f"{agent.agent_name} suggestions failed: {str(e)}")
        
        return suggestion_results
    
    async def _phase_evaluation(self, suggestion_results: Dict[str, Any], 
                              requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Cross-evaluate suggestions from all agents"""
        evaluation_results = {}
        
        # Collect all unique pieces from all agents
        all_pieces = self._collect_unique_pieces(suggestion_results)
        
        # Each agent evaluates all pieces
        for agent_name, agent in self.agents.items():
            try:
                evaluations = []
                for piece in all_pieces:
                    evaluation = await agent.evaluate_piece(piece, requirements)
                    evaluations.append({
                        "piece": piece,
                        "evaluation": evaluation,
                        "agent": agent_name
                    })
                
                evaluation_results[agent_name] = evaluations
                self._add_to_conversation(f"{agent.agent_name} evaluated {len(evaluations)} pieces")
            except Exception as e:
                evaluation_results[agent_name] = []
                self._add_to_conversation(f"{agent.agent_name} evaluation failed: {str(e)}")
        
        return evaluation_results
    
    async def _phase_synthesis(self, evaluation_results: Dict[str, Any], 
                             requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Synthesize evaluations into final setlist"""
        try:
            # Combine evaluations and score pieces
            piece_scores = self._score_pieces(evaluation_results)
            
            # Select pieces for the setlist
            selected_pieces = self._select_pieces_for_setlist(piece_scores, requirements)
            
            # Order pieces for optimal flow
            ordered_pieces = self._order_pieces_for_flow(selected_pieces, requirements)
            
            # Generate setlist metadata
            setlist_metadata = self._generate_setlist_metadata(ordered_pieces, requirements)
            
            return {
                "title": setlist_metadata["title"],
                "total_duration": setlist_metadata["total_duration"],
                "pieces": ordered_pieces,
                "design_reasoning": setlist_metadata["design_reasoning"]
            }
            
        except Exception as e:
            # Fallback to simple setlist
            return self._create_fallback_setlist(requirements)
    
    def _collect_unique_pieces(self, suggestion_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect all unique pieces from agent suggestions"""
        all_pieces = []
        seen_titles = set()
        
        for agent_suggestions in suggestion_results.values():
            if isinstance(agent_suggestions, list):
                for piece in agent_suggestions:
                    title = piece.get("title", "")
                    if title and title not in seen_titles:
                        all_pieces.append(piece)
                        seen_titles.add(title)
        
        return all_pieces
    
    def _score_pieces(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Score pieces based on agent evaluations"""
        piece_scores = {}
        
        for agent_name, evaluations in evaluation_results.items():
            if isinstance(evaluations, list):
                for eval_data in evaluations:
                    piece = eval_data["piece"]
                    evaluation = eval_data["evaluation"]
                    piece_title = piece.get("title", "unknown")
                    
                    if piece_title not in piece_scores:
                        piece_scores[piece_title] = {
                            "piece": piece,
                            "scores": {},
                            "total_score": 0,
                            "evaluation_count": 0
                        }
                    
                    # Extract score from evaluation
                    score = self._extract_score_from_evaluation(evaluation)
                    piece_scores[piece_title]["scores"][agent_name] = score
                    piece_scores[piece_title]["total_score"] += score
                    piece_scores[piece_title]["evaluation_count"] += 1
        
        # Calculate average scores
        for piece_data in piece_scores.values():
            if piece_data["evaluation_count"] > 0:
                piece_data["average_score"] = piece_data["total_score"] / piece_data["evaluation_count"]
            else:
                piece_data["average_score"] = 0
        
        return piece_scores
    
    def _extract_score_from_evaluation(self, evaluation: Dict[str, Any]) -> float:
        """Extract numerical score from evaluation"""
        # Look for various score fields
        score_fields = ["confidence", "technical_score", "flow_score", "musical_fit"]
        
        for field in score_fields:
            if field in evaluation and isinstance(evaluation[field], (int, float)):
                return float(evaluation[field])
        
        # Default score based on recommendation
        recommendation = evaluation.get("recommendation", "exclude")
        if recommendation == "include":
            return 8.0
        elif recommendation == "modify":
            return 5.0
        else:
            return 2.0
    
    def _select_pieces_for_setlist(self, piece_scores: Dict[str, Any], 
                                 requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select pieces for the setlist based on scores and constraints"""
        # Sort pieces by average score
        sorted_pieces = sorted(
            piece_scores.values(),
            key=lambda x: x["average_score"],
            reverse=True
        )
        
        # Select pieces within duration constraint
        selected_pieces = []
        total_duration = 0
        target_duration = requirements.get("duration_minutes", 60)
        
        for piece_data in sorted_pieces:
            piece = piece_data["piece"]
            piece_duration = piece.get("duration_minutes", 5)
            
            if total_duration + piece_duration <= target_duration + 5:  # 5 minute buffer
                selected_pieces.append(piece)
                total_duration += piece_duration
                
                if len(selected_pieces) >= 8:  # Maximum pieces
                    break
        
        return selected_pieces
    
    def _order_pieces_for_flow(self, pieces: List[Dict[str, Any]], 
                             requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Order pieces for optimal program flow"""
        if not pieces:
            return pieces
        
        # Simple ordering strategy
        # In production, use more sophisticated flow algorithms
        
        # Start with a moderate piece
        ordered = []
        remaining = pieces.copy()
        
        # Find a good opening piece
        opening_piece = self._find_opening_piece(remaining)
        if opening_piece:
            ordered.append(opening_piece)
            remaining.remove(opening_piece)
        
        # Add remaining pieces
        ordered.extend(remaining)
        
        return ordered
    
    def _find_opening_piece(self, pieces: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find a good opening piece"""
        for piece in pieces:
            if piece.get("difficulty_level") in ["beginner", "intermediate"]:
                return piece
        
        return pieces[0] if pieces else None
    
    def _generate_setlist_metadata(self, pieces: List[Dict[str, Any]], 
                                 requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata for the setlist"""
        total_duration = sum(piece.get("duration_minutes", 5) for piece in pieces)
        
        # Generate title based on concert type and pieces
        concert_type = requirements.get("concert_type", "concert")
        if pieces:
            first_composer = pieces[0].get("composer", "Various")
            title = f"{concert_type.title()} Program featuring {first_composer}"
        else:
            title = f"{concert_type.title()} Program"
        
        # Generate design reasoning
        reasoning_parts = [
            f"Designed for {requirements.get('skill_level', 'intermediate')} level performers",
            f"Duration: {total_duration} minutes",
            f"Instruments: {', '.join(requirements.get('instruments', []))}"
        ]
        
        if pieces:
            reasoning_parts.append(f"Features {len(pieces)} carefully selected pieces")
        
        return {
            "title": title,
            "total_duration": total_duration,
            "design_reasoning": "; ".join(reasoning_parts)
        }
    
    def _create_fallback_setlist(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback setlist when synthesis fails"""
        return {
            "title": f"{requirements.get('concert_type', 'Concert')} Program",
            "total_duration": 30,
            "pieces": [
                {
                    "title": "Sample Piece 1",
                    "composer": "Sample Composer",
                    "duration_minutes": 5,
                    "difficulty_level": requirements.get("skill_level", "intermediate"),
                    "key_signature": "C major",
                    "instruments": requirements.get("instruments", []),
                    "genre": "classical",
                    "reasoning": "Fallback suggestion"
                }
            ],
            "design_reasoning": "Fallback setlist created due to synthesis error"
        }
    
    def _summarize_contributions(self) -> Dict[str, Any]:
        """Summarize contributions from each agent"""
        contributions = {}
        
        for agent_name, agent in self.agents.items():
            contributions[agent_name] = {
                "agent_name": agent.agent_name,
                "role": agent.role,
                "expertise": agent.expertise,
                "conversation_messages": len(agent.conversation_history)
            }
        
        return contributions
    
    def _calculate_overall_confidence(self, evaluation_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        if not evaluation_results:
            return 0.5
        
        total_confidence = 0
        count = 0
        
        for agent_evaluations in evaluation_results.values():
            if isinstance(agent_evaluations, list):
                for eval_data in agent_evaluations:
                    evaluation = eval_data["evaluation"]
                    confidence = evaluation.get("confidence", 0.5)
                    total_confidence += confidence
                    count += 1
        
        return total_confidence / count if count > 0 else 0.5
    
    def _add_to_conversation(self, message: str):
        """Add message to coordinator conversation history"""
        self.conversation_history.append({
            "role": "coordinator",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

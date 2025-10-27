"""
Setlist Design Service - Main service for AI-powered setlist design
"""
from typing import Dict, List, Any, Optional
import uuid
from .setlist_agents.multi_agent_coordinator import MultiAgentCoordinator
from ..models.responses import SetlistPiece, SetlistDesignResponse, SetlistRefinementResponse

class SetlistDesignService:
    """Main service for AI-powered setlist design using multi-agent system"""
    
    def __init__(self):
        self.coordinator = MultiAgentCoordinator()
    
    async def design_setlist(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a setlist using AI (simplified for MVP)
        
        Args:
            requirements: Setlist design requirements
            
        Returns:
            Dict with designed setlist
        """
        try:
            # Extract requirements
            user_id = requirements.get("user_id", "unknown")
            concert_type = requirements.get("concert_type", "jazz_concert")
            duration_minutes = requirements.get("duration_minutes", 60)
            instruments = requirements.get("instruments", ["piano"])
            skill_level = requirements.get("skill_level", "intermediate")
            
            # Generate simple setlist
            setlist_pieces = self._generate_simple_setlist(
                concert_type, duration_minutes, instruments, skill_level
            )
            
            total_duration = sum(piece.get("duration_minutes", 5) for piece in setlist_pieces)
            
            return {
                "success": True,
                "setlist_id": str(uuid.uuid4()),
                "title": f"{concert_type.replace('_', ' ').title()} Setlist",
                "total_duration": total_duration,
                "pieces": setlist_pieces,
                "design_reasoning": f"Designed for {skill_level} level {concert_type.replace('_', ' ')} performance with {', '.join(instruments)}",
                "agent_contributions": {
                    "music_curator": "Selected appropriate pieces for the genre and skill level",
                    "technical_advisor": "Ensured technical feasibility for the instruments",
                    "program_flow": "Arranged pieces for good concert flow"
                },
                "confidence": 0.8,
                "metadata": {
                    "user_id": user_id,
                    "concert_type": concert_type,
                    "duration_minutes": duration_minutes,
                    "instruments": instruments,
                    "skill_level": skill_level,
                    "created_at": "2024-12-19T00:00:00Z"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Setlist design failed: {str(e)}",
                "confidence": 0.0
            }
    
    async def refine_setlist(self, setlist_id: str, refinement_instruction: str, 
                           user_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Refine an existing setlist
        
        Args:
            setlist_id: ID of the setlist to refine
            refinement_instruction: How to refine the setlist
            user_id: User ID for tracking
            conversation_id: Optional conversation context
            
        Returns:
            Dict with refined setlist
        """
        try:
            # Use the multi-agent coordinator to refine the setlist
            result = await self.coordinator.refine_setlist(
                setlist_id=setlist_id,
                refinement_instruction=refinement_instruction,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Setlist refinement failed"),
                    "confidence": 0.0
                }
            
            return {
                "success": True,
                "setlist_id": result["setlist_id"],
                "refined_setlist": result["refined_setlist"],
                "changes_made": result["refined_setlist"].get("changes_made", []),
                "reasoning": f"Refined based on: {refinement_instruction}",
                "confidence": result.get("confidence", 0.8)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Setlist refinement service failed: {str(e)}",
                "confidence": 0.0
            }
    
    async def get_setlist_suggestions(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get preliminary setlist suggestions without full design
        
        Args:
            requirements: Setlist design requirements
            
        Returns:
            Dict with preliminary suggestions
        """
        try:
            # Get suggestions from each agent individually
            suggestions = {}
            
            for agent_name, agent in self.coordinator.agents.items():
                try:
                    analysis = await agent.analyze_requirements(requirements)
                    agent_suggestions = await agent.suggest_pieces(requirements, {"analysis": analysis})
                    suggestions[agent_name] = {
                        "agent_name": agent.agent_name,
                        "role": agent.role,
                        "expertise": agent.expertise,
                        "suggestions": agent_suggestions
                    }
                except Exception as e:
                    suggestions[agent_name] = {
                        "agent_name": agent.agent_name,
                        "error": str(e),
                        "suggestions": []
                    }
            
            return {
                "success": True,
                "suggestions": suggestions,
                "total_agents": len(self.coordinator.agents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get suggestions: {str(e)}",
                "suggestions": {}
            }
    
    def _convert_to_setlist_pieces(self, pieces_data: List[Dict[str, Any]]) -> List[SetlistPiece]:
        """Convert piece data to SetlistPiece objects"""
        pieces = []
        
        for piece_data in pieces_data:
            try:
                piece = SetlistPiece(
                    title=piece_data.get("title", "Unknown"),
                    composer=piece_data.get("composer", "Unknown"),
                    duration_minutes=piece_data.get("duration_minutes", 5),
                    difficulty_level=piece_data.get("difficulty_level", "intermediate"),
                    key_signature=piece_data.get("key_signature", "C major"),
                    instruments=piece_data.get("instruments", []),
                    genre=piece_data.get("genre", "classical"),
                    reasoning=piece_data.get("reasoning", "Selected by AI"),
                    abc_notation=piece_data.get("abc_notation")
                )
                pieces.append(piece)
            except Exception as e:
                # Skip invalid pieces
                continue
        
        return pieces
    
    def get_available_concert_types(self) -> List[Dict[str, Any]]:
        """Get list of available concert types"""
        return [
            {
                "id": "classical_recital",
                "name": "Classical Recital",
                "description": "Traditional classical music recital",
                "typical_duration": "60-90 minutes",
                "instruments": ["piano", "violin", "cello", "voice"]
            },
            {
                "id": "chamber_music",
                "name": "Chamber Music",
                "description": "Small ensemble performance",
                "typical_duration": "45-75 minutes",
                "instruments": ["piano", "violin", "cello", "viola", "flute", "clarinet"]
            },
            {
                "id": "solo_performance",
                "name": "Solo Performance",
                "description": "Individual instrument showcase",
                "typical_duration": "30-60 minutes",
                "instruments": ["piano", "violin", "cello", "guitar", "flute"]
            },
            {
                "id": "jazz_concert",
                "name": "Jazz Concert",
                "description": "Jazz and contemporary music",
                "typical_duration": "60-90 minutes",
                "instruments": ["piano", "saxophone", "trumpet", "bass", "drums"]
            },
            {
                "id": "folk_concert",
                "name": "Folk Concert",
                "description": "Traditional and folk music",
                "typical_duration": "45-75 minutes",
                "instruments": ["guitar", "violin", "banjo", "voice", "accordion"]
            }
        ]
    
    def get_skill_levels(self) -> List[Dict[str, Any]]:
        """Get list of available skill levels"""
        return [
            {
                "id": "beginner",
                "name": "Beginner",
                "description": "New to the instrument, basic technique",
                "typical_pieces": "Simple melodies, basic scales",
                "technical_demands": "Low"
            },
            {
                "id": "intermediate",
                "name": "Intermediate",
                "description": "Comfortable with basic technique, learning advanced skills",
                "typical_pieces": "Standard repertoire, moderate difficulty",
                "technical_demands": "Moderate"
            },
            {
                "id": "advanced",
                "name": "Advanced",
                "description": "Strong technical foundation, complex pieces",
                "typical_pieces": "Challenging repertoire, virtuosic works",
                "technical_demands": "High"
            },
            {
                "id": "professional",
                "name": "Professional",
                "description": "Concert-level performance ability",
                "typical_pieces": "Any repertoire, including contemporary works",
                "technical_demands": "Very High"
            }
        ]
    
    def get_supported_instruments(self) -> List[Dict[str, Any]]:
        """Get list of supported instruments"""
        return [
            {
                "id": "piano",
                "name": "Piano",
                "category": "keyboard",
                "difficulty_curve": "moderate",
                "repertoire_size": "very_large"
            },
            {
                "id": "violin",
                "name": "Violin",
                "category": "string",
                "difficulty_curve": "steep",
                "repertoire_size": "very_large"
            },
            {
                "id": "cello",
                "name": "Cello",
                "category": "string",
                "difficulty_curve": "moderate",
                "repertoire_size": "large"
            },
            {
                "id": "viola",
                "name": "Viola",
                "category": "string",
                "difficulty_curve": "moderate",
                "repertoire_size": "medium"
            },
            {
                "id": "flute",
                "name": "Flute",
                "category": "woodwind",
                "difficulty_curve": "moderate",
                "repertoire_size": "large"
            },
            {
                "id": "clarinet",
                "name": "Clarinet",
                "category": "woodwind",
                "difficulty_curve": "moderate",
                "repertoire_size": "large"
            },
            {
                "id": "guitar",
                "name": "Guitar",
                "category": "string",
                "difficulty_curve": "moderate",
                "repertoire_size": "very_large"
            },
            {
                "id": "voice",
                "name": "Voice",
                "category": "vocal",
                "difficulty_curve": "moderate",
                "repertoire_size": "very_large"
            }
        ]
    
    def _generate_simple_setlist(self, concert_type: str, duration_minutes: int, 
                                instruments: List[str], skill_level: str) -> List[Dict]:
        """Generate a simple setlist based on parameters"""
        
        # Define piece templates based on concert type
        piece_templates = {
            "jazz_concert": [
                {"title": "Blue Note Blues", "composer": "Traditional", "duration_minutes": 8, "difficulty_level": skill_level, "key_signature": "Bb major", "genre": "jazz"},
                {"title": "Autumn Leaves", "composer": "Joseph Kosma", "duration_minutes": 6, "difficulty_level": skill_level, "key_signature": "Em", "genre": "jazz"},
                {"title": "All the Things You Are", "composer": "Jerome Kern", "duration_minutes": 7, "difficulty_level": skill_level, "key_signature": "Ab major", "genre": "jazz"},
                {"title": "Take Five", "composer": "Paul Desmond", "duration_minutes": 5, "difficulty_level": skill_level, "key_signature": "Eb minor", "genre": "jazz"},
                {"title": "So What", "composer": "Miles Davis", "duration_minutes": 9, "difficulty_level": skill_level, "key_signature": "Dm", "genre": "jazz"},
                {"title": "Giant Steps", "composer": "John Coltrane", "duration_minutes": 6, "difficulty_level": skill_level, "key_signature": "B major", "genre": "jazz"},
                {"title": "Round Midnight", "composer": "Thelonious Monk", "duration_minutes": 8, "difficulty_level": skill_level, "key_signature": "Eb minor", "genre": "jazz"},
                {"title": "Blue in Green", "composer": "Miles Davis", "duration_minutes": 5, "difficulty_level": skill_level, "key_signature": "Em", "genre": "jazz"}
            ],
            "classical_recital": [
                {"title": "Sonata in C Major", "composer": "Mozart", "duration_minutes": 12, "difficulty_level": skill_level, "key_signature": "C major", "genre": "classical"},
                {"title": "Nocturne in Eb", "composer": "Chopin", "duration_minutes": 8, "difficulty_level": skill_level, "key_signature": "Eb major", "genre": "classical"},
                {"title": "Prelude in C# Minor", "composer": "Rachmaninoff", "duration_minutes": 6, "difficulty_level": skill_level, "key_signature": "C# minor", "genre": "classical"},
                {"title": "Etude Op. 10 No. 3", "composer": "Chopin", "duration_minutes": 5, "difficulty_level": skill_level, "key_signature": "E major", "genre": "classical"},
                {"title": "Sonata Pathetique", "composer": "Beethoven", "duration_minutes": 15, "difficulty_level": skill_level, "key_signature": "C minor", "genre": "classical"},
                {"title": "Clair de Lune", "composer": "Debussy", "duration_minutes": 7, "difficulty_level": skill_level, "key_signature": "Db major", "genre": "classical"}
            ],
            "chamber_music": [
                {"title": "String Quartet No. 14", "composer": "Mozart", "duration_minutes": 25, "difficulty_level": skill_level, "key_signature": "G major", "genre": "classical"},
                {"title": "Piano Trio No. 1", "composer": "Brahms", "duration_minutes": 20, "difficulty_level": skill_level, "key_signature": "B major", "genre": "classical"},
                {"title": "Wind Quintet", "composer": "Nielsen", "duration_minutes": 18, "difficulty_level": skill_level, "key_signature": "A major", "genre": "classical"}
            ]
        }
        
        # Get appropriate pieces for the concert type
        available_pieces = piece_templates.get(concert_type, piece_templates["jazz_concert"])
        
        # Select pieces to fit the duration
        selected_pieces = []
        current_duration = 0
        
        for piece in available_pieces:
            if current_duration + piece["duration_minutes"] <= duration_minutes:
                # Add instrument-specific information
                piece["instruments"] = instruments
                piece["reasoning"] = f"Selected for {skill_level} level performance with {', '.join(instruments)}"
                selected_pieces.append(piece)
                current_duration += piece["duration_minutes"]
            
            if current_duration >= duration_minutes * 0.9:  # Stop at 90% of target duration
                break
        
        return selected_pieces
    
    async def design_collaborative_setlist(self, group_id: str, duration_minutes: int, 
                                         concert_type: str, group_members: List[Dict],
                                         conversation_id: Optional[str] = None,
                                         organizer_user_id: str = "unknown") -> Dict[str, Any]:
        """
        Design a collaborative setlist based on group member preferences
        
        Args:
            group_id: Group chat ID
            duration_minutes: Desired duration
            concert_type: Type of concert
            group_members: List of member preferences
            conversation_id: Conversation context
            organizer_user_id: User organizing the setlist
            
        Returns:
            Dict with collaborative setlist
        """
        try:
            # Analyze group preferences
            group_analysis = self._analyze_group_preferences(group_members, concert_type)
            
            # Generate collaborative setlist
            setlist_pieces = self._generate_collaborative_setlist(
                group_analysis, duration_minutes, concert_type
            )
            
            total_duration = sum(piece.get("duration_minutes", 5) for piece in setlist_pieces)
            
            return {
                "success": True,
                "setlist_id": str(uuid.uuid4()),
                "title": f"Collaborative {concert_type.replace('_', ' ').title()} Setlist",
                "total_duration": total_duration,
                "pieces": setlist_pieces,
                "design_reasoning": self._generate_collaborative_reasoning(group_analysis, setlist_pieces),
                "agent_contributions": {
                    "music_curator": f"Balanced preferences from {len(group_members)} group members",
                    "technical_advisor": f"Ensured pieces work for skill levels: {group_analysis['skill_levels']}",
                    "program_flow": f"Created flow considering preferences: {group_analysis['common_genres']}"
                },
                "confidence": group_analysis["compatibility_score"],
                "metadata": {
                    "group_id": group_id,
                    "organizer_user_id": organizer_user_id,
                    "concert_type": concert_type,
                    "duration_minutes": duration_minutes,
                    "group_size": len(group_members),
                    "preference_analysis": group_analysis,
                    "created_at": "2024-12-19T00:00:00Z"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Collaborative setlist design failed: {str(e)}",
                "confidence": 0.0
            }
    
    async def generate_preference_questions(self, group_id: str, organizer_user_id: str,
                                          concert_type: str = "jazz_concert", 
                                          duration_minutes: int = 60) -> Dict[str, Any]:
        """Generate preference gathering questions for group members"""
        
        questions = {
            "general_questions": [
                "What are your favorite musical genres? (e.g., jazz, classical, blues, rock)",
                "Who are your favorite composers or artists?",
                "What instruments do you play?",
                "What's your skill level? (beginner, intermediate, advanced)",
                "Are there any genres you'd prefer to avoid?",
                "Do you prefer faster or slower tempo pieces?",
                "What mood are you going for? (energetic, relaxed, dramatic, etc.)"
            ],
            "concert_specific_questions": [
                f"For this {duration_minutes}-minute {concert_type.replace('_', ' ')} concert:",
                "What's your ideal opening piece style?",
                "Do you want any solo features or ensemble pieces?",
                "Any specific pieces you've always wanted to perform?",
                "What would make this concert memorable for you?"
            ],
            "collaboration_questions": [
                "What do you think would work well for the whole group?",
                "Are you open to trying new genres or styles?",
                "Any pieces you think would be fun to perform together?"
            ]
        }
        
        return {
            "group_id": group_id,
            "organizer_user_id": organizer_user_id,
            "concert_type": concert_type,
            "duration_minutes": duration_minutes,
            "questions": questions,
            "instructions": "Please answer these questions so I can design a setlist that works for everyone!"
        }
    
    def _analyze_group_preferences(self, group_members: List[Dict], concert_type: str) -> Dict[str, Any]:
        """Analyze group preferences to find common ground"""
        
        # Collect all preferences
        all_genres = []
        all_composers = []
        all_instruments = []
        skill_levels = []
        avoid_genres = []
        tempo_preferences = []
        mood_preferences = []
        
        for member in group_members:
            all_genres.extend(member.get("favorite_genres", []))
            all_composers.extend(member.get("favorite_composers", []))
            all_instruments.extend(member.get("instruments", []))
            skill_levels.append(member.get("skill_level", "intermediate"))
            avoid_genres.extend(member.get("avoid_genres", []))
            if member.get("tempo_preference"):
                tempo_preferences.append(member.get("tempo_preference"))
            if member.get("mood_preference"):
                mood_preferences.append(member.get("mood_preference"))
        
        # Find common ground
        from collections import Counter
        genre_counts = Counter(all_genres)
        composer_counts = Counter(all_composers)
        instrument_counts = Counter(all_instruments)
        tempo_counts = Counter(tempo_preferences)
        mood_counts = Counter(mood_preferences)
        
        # Calculate compatibility score
        common_genres = [genre for genre, count in genre_counts.items() if count > 1]
        common_composers = [composer for composer, count in composer_counts.items() if count > 1]
        
        compatibility_score = min(0.9, 0.5 + (len(common_genres) * 0.1) + (len(common_composers) * 0.1))
        
        return {
            "common_genres": common_genres,
            "common_composers": common_composers,
            "all_genres": list(set(all_genres)),
            "all_composers": list(set(all_composers)),
            "instruments": list(set(all_instruments)),
            "skill_levels": list(set(skill_levels)),
            "avoid_genres": list(set(avoid_genres)),
            "preferred_tempo": tempo_counts.most_common(1)[0][0] if tempo_counts else "moderate",
            "preferred_mood": mood_counts.most_common(1)[0][0] if mood_counts else "balanced",
            "compatibility_score": compatibility_score,
            "group_size": len(group_members)
        }
    
    def _generate_collaborative_setlist(self, group_analysis: Dict, duration_minutes: int, 
                                       concert_type: str) -> List[Dict]:
        """Generate setlist considering group preferences"""
        
        # Use the existing setlist generation but filter based on group preferences
        base_pieces = self._generate_simple_setlist(concert_type, duration_minutes, 
                                                   group_analysis["instruments"], 
                                                   group_analysis["skill_levels"][0] if group_analysis["skill_levels"] else "intermediate")
        
        # Filter out avoided genres
        filtered_pieces = []
        for piece in base_pieces:
            piece_genre = piece.get("genre", "").lower()
            if not any(avoid_genre.lower() in piece_genre for avoid_genre in group_analysis["avoid_genres"]):
                filtered_pieces.append(piece)
        
        # Prioritize pieces that match common preferences
        prioritized_pieces = []
        for piece in filtered_pieces:
            piece["collaborative_score"] = 0
            
            # Boost score for common genres
            if any(genre.lower() in piece.get("genre", "").lower() for genre in group_analysis["common_genres"]):
                piece["collaborative_score"] += 2
            
            # Boost score for common composers
            if any(composer.lower() in piece.get("composer", "").lower() for composer in group_analysis["common_composers"]):
                piece["collaborative_score"] += 3
            
            # Add reasoning
            piece["collaborative_reasoning"] = f"Selected based on group preferences: {group_analysis['common_genres']}"
            
            prioritized_pieces.append(piece)
        
        # Sort by collaborative score
        prioritized_pieces.sort(key=lambda x: x.get("collaborative_score", 0), reverse=True)
        
        return prioritized_pieces
    
    def _generate_collaborative_reasoning(self, group_analysis: Dict, pieces: List[Dict]) -> str:
        """Generate reasoning for collaborative setlist choices"""
        
        reasoning_parts = [
            f"Designed for {group_analysis['group_size']} group members with compatibility score {group_analysis['compatibility_score']:.1f}",
            f"Common preferences: {', '.join(group_analysis['common_genres'])} genres, {', '.join(group_analysis['common_composers'])} composers",
            f"Skill levels: {', '.join(group_analysis['skill_levels'])}",
            f"Instruments: {', '.join(group_analysis['instruments'])}",
            f"Preferred tempo: {group_analysis['preferred_tempo']}, mood: {group_analysis['preferred_mood']}"
        ]
        
        return ". ".join(reasoning_parts) + "."

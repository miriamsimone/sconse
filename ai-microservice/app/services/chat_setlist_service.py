"""
Chat-based Collaborative Setlist Service

This service handles collaborative setlist design through natural chat interactions.
It manages the flow of asking group members for preferences and generating setlists
based on their responses, all within the chat interface.
"""
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class ChatSetlistService:
    """Service for managing chat-based collaborative setlist design"""
    
    def __init__(self):
        # In-memory storage for active setlist requests (in production, use Redis/DB)
        self.active_requests: Dict[str, Dict] = {}
        self.group_responses: Dict[str, List[Dict]] = {}
    
    async def handle_setlist_request(self, user_input: str, group_id: str, 
                                   conversation_id: str, organizer_user_id: str,
                                   group_member_ids: List[str], organizer_username: str = None) -> Dict[str, Any]:
        """
        Handle initial setlist request and determine next action
        
        Args:
            user_input: User's request for collaborative setlist
            group_id: Group chat ID
            conversation_id: Conversation ID
            organizer_user_id: User making the request
            group_member_ids: List of group member user IDs
            
        Returns:
            Dict with action to take and message to send
        """
        try:
            # Extract setlist parameters from user input
            params = self._extract_setlist_parameters(user_input)
            
            # Create setlist request ID
            setlist_id = str(uuid.uuid4())
            
            # Store active request
            self.active_requests[setlist_id] = {
                "group_id": group_id,
                "conversation_id": conversation_id,
                "organizer_user_id": organizer_user_id,
                "group_member_ids": group_member_ids,
                "duration_minutes": params["duration_minutes"],
                "concert_type": params["concert_type"],
                "created_at": datetime.now().isoformat(),
                "status": "collecting_preferences",
                "responses_received": []
            }
            
            # Initialize group responses
            self.group_responses[setlist_id] = []
            
            # Generate preference questions
            questions = self._generate_preference_questions(
                params["concert_type"], params["duration_minutes"]
            )
            
            # Create message for group chat
            display_name = organizer_username or self._get_display_name(organizer_user_id)
            message = self._create_preference_request_message(
                display_name, params, questions, group_member_ids
            )
            
            return {
                "success": True,
                "action": "ask_preferences",
                "message": message,
                "setlist_id": setlist_id,
                "waiting_for_responses": True,
                "required_responses": group_member_ids,
                "questions": questions,
                "setlist_context": {
                    "duration_minutes": params["duration_minutes"],
                    "concert_type": params["concert_type"],
                    "organizer": organizer_user_id
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": "error",
                "message": f"Sorry, I couldn't process your setlist request: {str(e)}",
                "error": str(e)
            }
    
    async def handle_preference_response(self, setlist_id: str, user_id: str, 
                                       username: str, preference_text: str) -> Dict[str, Any]:
        """
        Handle a group member's preference response
        
        Args:
            setlist_id: ID of the active setlist request
            user_id: User ID of the person responding
            username: Display name of the user
            preference_text: Natural language response with preferences
            
        Returns:
            Dict with next action and message
        """
        try:
            if setlist_id not in self.active_requests:
                return {
                    "success": False,
                    "action": "error",
                    "message": "Setlist request not found or expired"
                }
            
            # Parse natural language preferences
            parsed_preferences = self._parse_preference_text(preference_text)
            
            # Store the response
            response_data = {
                "user_id": user_id,
                "username": username,
                "preference_text": preference_text,
                "preferences": parsed_preferences,
                "response_timestamp": datetime.now().isoformat()
            }
            
            self.group_responses[setlist_id].append(response_data)
            
            # Update active request
            request = self.active_requests[setlist_id]
            request["responses_received"].append(user_id)
            
            # Check if we have all responses
            remaining_users = set(request["group_member_ids"]) - set(request["responses_received"])
            
            if not remaining_users:
                # All responses received, generate setlist
                return await self._generate_collaborative_setlist(setlist_id)
            else:
                # Still waiting for more responses
                remaining_names = [self._get_username_for_id(user_id) for user_id in remaining_users]
                message = f"Thanks {username}! Still waiting for responses from: {', '.join(remaining_names)}"
                
                return {
                    "success": True,
                    "action": "waiting_for_responses",
                    "message": message,
                    "setlist_id": setlist_id,
                    "waiting_for_responses": True,
                    "required_responses": list(remaining_users)
                }
                
        except Exception as e:
            return {
                "success": False,
                "action": "error",
                "message": f"Error processing your preferences: {str(e)}"
            }
    
    async def _generate_collaborative_setlist(self, setlist_id: str) -> Dict[str, Any]:
        """Generate setlist based on all collected preferences"""
        try:
            request = self.active_requests[setlist_id]
            responses = self.group_responses[setlist_id]
            
            # Analyze group preferences
            group_analysis = self._analyze_group_preferences(responses)
            
            # Generate setlist
            setlist_pieces = self._generate_setlist_pieces(
                group_analysis, request["duration_minutes"], request["concert_type"]
            )
            
            total_duration = sum(piece.get("duration_minutes", 5) for piece in setlist_pieces)
            
            # Create success message
            message = self._create_setlist_completion_message(
                request["organizer_user_id"], setlist_pieces, group_analysis
            )
            
            # Update request status
            request["status"] = "completed"
            request["setlist_data"] = {
                "title": f"Collaborative {request['concert_type'].replace('_', ' ').title()} Setlist",
                "total_duration": total_duration,
                "pieces": setlist_pieces,
                "design_reasoning": self._generate_collaborative_reasoning(group_analysis, setlist_pieces)
            }
            
            return {
                "success": True,
                "action": "setlist_complete",
                "message": message,
                "setlist_id": setlist_id,
                "waiting_for_responses": False,
                "setlist_data": request["setlist_data"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": "error",
                "message": f"Error generating setlist: {str(e)}"
            }
    
    def _extract_setlist_parameters(self, user_input: str) -> Dict[str, Any]:
        """Extract setlist parameters from user input"""
        import re
        
        user_lower = user_input.lower()
        
        # Extract duration
        duration_minutes = 60  # default
        duration_match = re.search(r'(\d+)\s*(?:minute|min|hour|hr)', user_lower)
        if duration_match:
            duration_value = int(duration_match.group(1))
            if 'hour' in user_lower or 'hr' in user_lower:
                duration_minutes = duration_value * 60
            else:
                duration_minutes = duration_value
        
        # Extract concert type
        concert_type = "jazz_concert"  # default
        if any(word in user_lower for word in ["jazz", "blues", "swing", "bebop"]):
            concert_type = "jazz_concert"
        elif any(word in user_lower for word in ["classical", "baroque", "romantic", "sonata", "concerto"]):
            concert_type = "classical_recital"
        elif any(word in user_lower for word in ["chamber", "quartet", "trio", "ensemble"]):
            concert_type = "chamber_music"
        
        return {
            "concert_type": concert_type,
            "duration_minutes": duration_minutes
        }
    
    def _generate_preference_questions(self, concert_type: str, duration_minutes: int) -> Dict[str, List[str]]:
        """Generate preference questions for group members"""
        return {
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
    
    def _get_display_name(self, user_id: str) -> str:
        """Get display name for user ID"""
        # In production, this would query the user database
        # For now, return a friendly placeholder
        if len(user_id) > 8:
            return f"User {user_id[-4:]}"  # Last 4 chars
        return f"User {user_id}"
    
    def _parse_preference_text(self, preference_text: str) -> Dict[str, Any]:
        """Parse natural language preference text into structured data"""
        import re
        
        text_lower = preference_text.lower()
        
        # Extract genres
        genres = []
        genre_keywords = {
            "jazz": ["jazz", "swing", "bebop", "fusion"],
            "blues": ["blues", "bluesy"],
            "classical": ["classical", "baroque", "romantic", "chamber"],
            "rock": ["rock", "pop", "alternative"],
            "folk": ["folk", "acoustic", "traditional"],
            "country": ["country", "bluegrass"],
            "electronic": ["electronic", "edm", "techno"],
            "latin": ["latin", "salsa", "bossa nova", "samba"]
        }
        
        for genre, keywords in genre_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                genres.append(genre)
        
        # Extract composers/artists
        composers = []
        composer_patterns = [
            r"(?:favorite|love|like).*?(?:composer|artist|musician).*?([a-zA-Z\s]+)",
            r"(?:composer|artist|musician).*?([a-zA-Z\s]+)",
            r"(?:miles davis|john coltrane|beethoven|mozart|bach|chopin|debussy)",
        ]
        
        for pattern in composer_patterns:
            matches = re.findall(pattern, text_lower)
            composers.extend([match.strip() for match in matches if len(match.strip()) > 2])
        
        # Extract instruments
        instruments = []
        instrument_keywords = {
            "piano": ["piano", "keyboard", "keys"],
            "guitar": ["guitar", "acoustic guitar", "electric guitar"],
            "violin": ["violin", "fiddle"],
            "cello": ["cello"],
            "viola": ["viola"],
            "flute": ["flute"],
            "clarinet": ["clarinet"],
            "saxophone": ["saxophone", "sax", "alto sax", "tenor sax"],
            "trumpet": ["trumpet"],
            "drums": ["drums", "drum set", "percussion"],
            "bass": ["bass", "bass guitar", "upright bass"],
            "voice": ["voice", "vocal", "singer", "singing"]
        }
        
        for instrument, keywords in instrument_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                instruments.append(instrument)
        
        # Extract skill level
        skill_level = "intermediate"  # default
        if any(word in text_lower for word in ["beginner", "starting", "new to", "learning"]):
            skill_level = "beginner"
        elif any(word in text_lower for word in ["advanced", "expert", "professional", "experienced"]):
            skill_level = "advanced"
        elif any(word in text_lower for word in ["expert", "master", "virtuoso"]):
            skill_level = "professional"
        
        # Extract avoid genres
        avoid_genres = []
        avoid_patterns = [
            r"(?:avoid|don't like|hate|dislike).*?(?:genre|music|style).*?([a-zA-Z\s]+)",
            r"(?:not into|not a fan of).*?([a-zA-Z\s]+)",
        ]
        
        for pattern in avoid_patterns:
            matches = re.findall(pattern, text_lower)
            avoid_genres.extend([match.strip() for match in matches if len(match.strip()) > 2])
        
        # Extract avoid composers
        avoid_composers = []
        avoid_composer_patterns = [
            r"(?:avoid|don't like|hate|dislike).*?(?:composer|artist|musician).*?([a-zA-Z\s]+)",
            r"(?:not into|not a fan of).*?(?:composer|artist|musician).*?([a-zA-Z\s]+)",
            r"(?:no|avoid|don't want).*?(?:miles davis|john coltrane|beethoven|mozart|bach|chopin|debussy|herbie hancock|thelonious monk)",
        ]
        
        for pattern in avoid_composer_patterns:
            matches = re.findall(pattern, text_lower)
            avoid_composers.extend([match.strip() for match in matches if len(match.strip()) > 2])
        
        # Also check for direct composer mentions with negative words
        negative_words = ["no", "avoid", "don't", "hate", "dislike", "not"]
        composer_names = ["miles davis", "john coltrane", "beethoven", "mozart", "bach", "chopin", "debussy", "herbie hancock", "thelonious monk"]
        
        for composer in composer_names:
            if composer in text_lower:
                # Check if there's a negative word nearby
                composer_pos = text_lower.find(composer)
                context_start = max(0, composer_pos - 20)
                context_end = min(len(text_lower), composer_pos + len(composer) + 20)
                context = text_lower[context_start:context_end]
                
                if any(neg_word in context for neg_word in negative_words):
                    avoid_composers.append(composer.title())
        
        # Extract tempo preference
        tempo_preference = None
        if any(word in text_lower for word in ["fast", "upbeat", "energetic", "quick"]):
            tempo_preference = "fast"
        elif any(word in text_lower for word in ["slow", "relaxed", "calm", "gentle"]):
            tempo_preference = "slow"
        elif any(word in text_lower for word in ["moderate", "medium", "balanced"]):
            tempo_preference = "moderate"
        
        # Extract mood preference
        mood_preference = None
        if any(word in text_lower for word in ["energetic", "exciting", "dynamic", "powerful"]):
            mood_preference = "energetic"
        elif any(word in text_lower for word in ["relaxed", "calm", "peaceful", "serene"]):
            mood_preference = "relaxed"
        elif any(word in text_lower for word in ["dramatic", "intense", "emotional", "passionate"]):
            mood_preference = "dramatic"
        elif any(word in text_lower for word in ["happy", "cheerful", "uplifting", "joyful"]):
            mood_preference = "happy"
        
        # Extract ordering preferences
        start_preference = None
        end_preference = None
        
        # Look for "start with" patterns
        start_patterns = [
            r"start with\s+([a-zA-Z\s]+)",
            r"begin with\s+([a-zA-Z\s]+)",
            r"open with\s+([a-zA-Z\s]+)",
            r"first.*?([a-zA-Z\s]+)",
        ]
        
        for pattern in start_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                start_preference = matches[0].strip()
                break
        
        # Look for "end with" patterns
        end_patterns = [
            r"end with\s+([a-zA-Z\s]+)",
            r"finish with\s+([a-zA-Z\s]+)",
            r"close with\s+([a-zA-Z\s]+)",
            r"last.*?([a-zA-Z\s]+)",
        ]
        
        for pattern in end_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                end_preference = matches[0].strip()
                break
        
        # Extract specific genre requests (not just favorites)
        specific_genres = []
        genre_keywords = ["bebop", "blues", "ballad", "swing", "fusion", "hard bop", "cool jazz", "free jazz"]
        
        for genre in genre_keywords:
            if genre in text_lower:
                specific_genres.append(genre)
        
        return {
            "favorite_genres": genres,
            "favorite_composers": composers[:5],  # Limit to top 5
            "instruments": instruments,
            "skill_level": skill_level,
            "avoid_genres": avoid_genres[:3],  # Limit to top 3
            "avoid_composers": avoid_composers[:3],  # Limit to top 3
            "tempo_preference": tempo_preference,
            "mood_preference": mood_preference,
            "start_preference": start_preference,
            "end_preference": end_preference,
            "specific_genres": specific_genres
        }
    
    def _create_preference_request_message(self, organizer_name: str, params: Dict[str, Any], 
                                          questions: Dict[str, List[str]], group_member_ids: List[str]) -> str:
        """Create message asking group for preferences"""
        concert_type_display = params["concert_type"].replace("_", " ").title()
        
        message = f"""🎵 **Collaborative {concert_type_display} Setlist Request** 🎵

Hey everyone! {organizer_name} wants to create a {params['duration_minutes']}-minute {concert_type_display} setlist for our group.

To make this work for everyone, I need to know your musical preferences. Please respond with your answers to these questions:

**Your Musical Preferences:**
• What are your favorite genres? (jazz, classical, blues, etc.)
• Who are your favorite composers/artists?
• What instruments do you play?
• What's your skill level? (beginner/intermediate/advanced)
• Any genres you'd prefer to avoid?
• Do you prefer faster or slower tempo pieces?
• What mood are you going for? (energetic, relaxed, dramatic, etc.)

**For This Concert:**
• What's your ideal opening piece style?
• Do you want any solo features or ensemble pieces?
• Any specific pieces you've always wanted to perform?
• What would make this concert memorable for you?

**Collaboration:**
• What do you think would work well for the whole group?
• Are you open to trying new genres or styles?
• Any pieces you think would be fun to perform together?

Once everyone responds, I'll create a setlist that balances all our preferences! 🎶"""
        
        return message
    
    def _create_setlist_completion_message(self, organizer_user_id: str, pieces: List[Dict], 
                                         group_analysis: Dict[str, Any]) -> str:
        """Create message announcing completed setlist"""
        total_duration = sum(piece.get("duration_minutes", 5) for piece in pieces)
        
        message = f"""🎉 **Collaborative Setlist Complete!** 🎉

Great news! I've created a setlist that balances everyone's preferences:

**Setlist Overview:**
• **Total Duration:** {total_duration} minutes
• **Pieces:** {len(pieces)} selections
• **Group Compatibility:** {group_analysis.get('compatibility_score', 0.7):.1f}/1.0

**The Program:**
"""
        
        for i, piece in enumerate(pieces, 1):
            message += f"{i}. **{piece.get('title', 'Untitled')}** - {piece.get('composer', 'Unknown')} ({piece.get('duration_minutes', 5)} min)\n"
            if piece.get('collaborative_reasoning'):
                message += f"   *{piece['collaborative_reasoning']}*\n"
        
        message += f"""
**Design Reasoning:**
{self._generate_collaborative_reasoning(group_analysis, pieces)}

This setlist considers everyone's preferences and skill levels. Ready to rehearse! 🎵"""
        
        return message
    
    def _analyze_group_preferences(self, responses: List[Dict]) -> Dict[str, Any]:
        """Analyze group preferences to find common ground"""
        # Collect all preferences
        all_genres = []
        all_composers = []
        all_instruments = []
        skill_levels = []
        avoid_genres = []
        avoid_composers = []
        start_preferences = []
        end_preferences = []
        specific_genres = []
        
        for response in responses:
            prefs = response.get("preferences", {})
            all_genres.extend(prefs.get("favorite_genres", []))
            all_composers.extend(prefs.get("favorite_composers", []))
            all_instruments.extend(prefs.get("instruments", []))
            skill_levels.append(prefs.get("skill_level", "intermediate"))
            avoid_genres.extend(prefs.get("avoid_genres", []))
            avoid_composers.extend(prefs.get("avoid_composers", []))
            
            # Collect ordering preferences
            if prefs.get("start_preference"):
                start_preferences.append(prefs["start_preference"])
            if prefs.get("end_preference"):
                end_preferences.append(prefs["end_preference"])
            specific_genres.extend(prefs.get("specific_genres", []))
        
        # Find common ground
        from collections import Counter
        genre_counts = Counter(all_genres)
        composer_counts = Counter(all_composers)
        
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
            "avoid_composers": list(set(avoid_composers)),
            "start_preferences": start_preferences,
            "end_preferences": end_preferences,
            "specific_genres": list(set(specific_genres)),
            "compatibility_score": compatibility_score,
            "group_size": len(responses)
        }
    
    def _generate_setlist_pieces(self, group_analysis: Dict[str, Any], duration_minutes: int, 
                                concert_type: str) -> List[Dict]:
        """Generate setlist pieces based on group analysis"""
        
        # Generate pieces based on concert type and group preferences
        pieces = []
        
        if concert_type == "jazz_concert":
            pieces = self._generate_jazz_setlist(group_analysis, duration_minutes)
        elif concert_type == "classical_recital":
            pieces = self._generate_classical_setlist(group_analysis, duration_minutes)
        elif concert_type == "chamber_music":
            pieces = self._generate_chamber_setlist(group_analysis, duration_minutes)
        else:
            pieces = self._generate_jazz_setlist(group_analysis, duration_minutes)  # Default
        
        # Filter based on group preferences
        filtered_pieces = self._filter_pieces_by_preferences(pieces, group_analysis)
        
        # Select pieces to fit duration
        selected_pieces = self._select_pieces_for_duration(filtered_pieces, duration_minutes, group_analysis)
        
        return selected_pieces
    
    def _generate_jazz_setlist(self, group_analysis: Dict[str, Any], duration_minutes: int) -> List[Dict]:
        """Generate jazz setlist pieces"""
        jazz_pieces = [
            # Ballads
            {"title": "Blue in Green", "composer": "Miles Davis", "duration_minutes": 5, "genre": "jazz", "style": "ballad", "difficulty": "intermediate"},
            {"title": "Autumn Leaves", "composer": "Joseph Kosma", "duration_minutes": 4, "genre": "jazz", "style": "ballad", "difficulty": "intermediate"},
            {"title": "All the Things You Are", "composer": "Jerome Kern", "duration_minutes": 6, "genre": "jazz", "style": "ballad", "difficulty": "advanced"},
            {"title": "Body and Soul", "composer": "Johnny Green", "duration_minutes": 5, "genre": "jazz", "style": "ballad", "difficulty": "intermediate"},
            {"title": "Round Midnight", "composer": "Thelonious Monk", "duration_minutes": 6, "genre": "jazz", "style": "ballad", "difficulty": "advanced"},
            
            # Medium tempo
            {"title": "Blue Bossa", "composer": "Kenny Dorham", "duration_minutes": 4, "genre": "jazz", "style": "medium", "difficulty": "intermediate"},
            {"title": "Cantaloupe Island", "composer": "Herbie Hancock", "duration_minutes": 5, "genre": "jazz", "style": "medium", "difficulty": "intermediate"},
            {"title": "Song for My Father", "composer": "Horace Silver", "duration_minutes": 4, "genre": "jazz", "style": "medium", "difficulty": "intermediate"},
            {"title": "Maiden Voyage", "composer": "Herbie Hancock", "duration_minutes": 6, "genre": "jazz", "style": "medium", "difficulty": "advanced"},
            
            # Up-tempo
            {"title": "All Blues", "composer": "Miles Davis", "duration_minutes": 5, "genre": "jazz", "style": "up-tempo", "difficulty": "intermediate"},
            {"title": "So What", "composer": "Miles Davis", "duration_minutes": 6, "genre": "jazz", "style": "up-tempo", "difficulty": "advanced"},
            {"title": "Giant Steps", "composer": "John Coltrane", "duration_minutes": 5, "genre": "jazz", "style": "up-tempo", "difficulty": "advanced"},
            {"title": "Take Five", "composer": "Paul Desmond", "duration_minutes": 5, "genre": "jazz", "style": "up-tempo", "difficulty": "intermediate"},
            
            # Blues
            {"title": "Blue Monk", "composer": "Thelonious Monk", "duration_minutes": 4, "genre": "blues", "style": "medium", "difficulty": "intermediate"},
            {"title": "Straight No Chaser", "composer": "Thelonious Monk", "duration_minutes": 5, "genre": "blues", "style": "up-tempo", "difficulty": "intermediate"},
            {"title": "Blue Train", "composer": "John Coltrane", "duration_minutes": 6, "genre": "blues", "style": "up-tempo", "difficulty": "advanced"},
            
            # Bebop
            {"title": "Confirmation", "composer": "Charlie Parker", "duration_minutes": 4, "genre": "bebop", "style": "up-tempo", "difficulty": "advanced"},
            {"title": "Donna Lee", "composer": "Charlie Parker", "duration_minutes": 5, "genre": "bebop", "style": "up-tempo", "difficulty": "advanced"},
            {"title": "Anthropology", "composer": "Charlie Parker", "duration_minutes": 4, "genre": "bebop", "style": "up-tempo", "difficulty": "advanced"},
            {"title": "Hot House", "composer": "Tadd Dameron", "duration_minutes": 5, "genre": "bebop", "style": "up-tempo", "difficulty": "advanced"},
            {"title": "Ornithology", "composer": "Charlie Parker", "duration_minutes": 4, "genre": "bebop", "style": "up-tempo", "difficulty": "advanced"},
            
            # More Blues
            {"title": "Tenor Madness", "composer": "Sonny Rollins", "duration_minutes": 5, "genre": "blues", "style": "medium", "difficulty": "intermediate"},
            {"title": "Blues Walk", "composer": "Lou Donaldson", "duration_minutes": 4, "genre": "blues", "style": "medium", "difficulty": "intermediate"},
            {"title": "Blues for Alice", "composer": "Charlie Parker", "duration_minutes": 5, "genre": "blues", "style": "medium", "difficulty": "advanced"},
        ]
        
        return jazz_pieces
    
    def _generate_classical_setlist(self, group_analysis: Dict[str, Any], duration_minutes: int) -> List[Dict]:
        """Generate classical setlist pieces"""
        classical_pieces = [
            # Baroque
            {"title": "Prelude and Fugue in C Major", "composer": "J.S. Bach", "duration_minutes": 6, "genre": "classical", "style": "baroque", "difficulty": "advanced"},
            {"title": "Air on the G String", "composer": "J.S. Bach", "duration_minutes": 4, "genre": "classical", "style": "baroque", "difficulty": "intermediate"},
            
            # Classical
            {"title": "Sonata in C Major", "composer": "Mozart", "duration_minutes": 8, "genre": "classical", "style": "classical", "difficulty": "advanced"},
            {"title": "Für Elise", "composer": "Beethoven", "duration_minutes": 3, "genre": "classical", "style": "classical", "difficulty": "intermediate"},
            
            # Romantic
            {"title": "Nocturne in E-flat Major", "composer": "Chopin", "duration_minutes": 5, "genre": "classical", "style": "romantic", "difficulty": "advanced"},
            {"title": "Clair de Lune", "composer": "Debussy", "duration_minutes": 5, "genre": "classical", "style": "romantic", "difficulty": "advanced"},
        ]
        
        return classical_pieces
    
    def _generate_chamber_setlist(self, group_analysis: Dict[str, Any], duration_minutes: int) -> List[Dict]:
        """Generate chamber music setlist pieces"""
        chamber_pieces = [
            {"title": "String Quartet No. 14", "composer": "Mozart", "duration_minutes": 8, "genre": "chamber", "style": "classical", "difficulty": "advanced"},
            {"title": "Piano Trio No. 1", "composer": "Brahms", "duration_minutes": 10, "genre": "chamber", "style": "romantic", "difficulty": "advanced"},
            {"title": "Wind Quintet", "composer": "Nielsen", "duration_minutes": 6, "genre": "chamber", "style": "modern", "difficulty": "advanced"},
        ]
        
        return chamber_pieces
    
    def _filter_pieces_by_preferences(self, pieces: List[Dict], group_analysis: Dict[str, Any]) -> List[Dict]:
        """Filter pieces based on group preferences"""
        filtered_pieces = []
        
        for piece in pieces:
            # Skip pieces in avoided genres
            piece_genre = piece.get("genre", "").lower()
            if any(avoid_genre.lower() in piece_genre for avoid_genre in group_analysis.get("avoid_genres", [])):
                continue
            
            # Skip pieces by avoided composers
            piece_composer = piece.get("composer", "").lower()
            if any(avoid_composer.lower() in piece_composer for avoid_composer in group_analysis.get("avoid_composers", [])):
                continue
            
            # Boost pieces that match common preferences
            piece["collaborative_score"] = 0
            
            # Boost for common genres
            if any(genre.lower() in piece_genre for genre in group_analysis.get("common_genres", [])):
                piece["collaborative_score"] += 3
            
            # Boost for common composers
            piece_composer = piece.get("composer", "").lower()
            if any(composer.lower() in piece_composer for composer in group_analysis.get("common_composers", [])):
                piece["collaborative_score"] += 5
            
            # Boost for skill level match
            piece_difficulty = piece.get("difficulty", "intermediate")
            if piece_difficulty in group_analysis.get("skill_levels", ["intermediate"]):
                piece["collaborative_score"] += 2
            
            # Boost for tempo preference match
            group_tempo = group_analysis.get("preferred_tempo", "moderate")
            piece_style = piece.get("style", "medium")
            if (group_tempo == "fast" and piece_style == "up-tempo") or \
               (group_tempo == "slow" and piece_style == "ballad") or \
               (group_tempo == "moderate" and piece_style == "medium"):
                piece["collaborative_score"] += 1
            
            filtered_pieces.append(piece)
        
        # Sort by collaborative score
        filtered_pieces.sort(key=lambda x: x.get("collaborative_score", 0), reverse=True)
        
        return filtered_pieces
    
    def _select_pieces_for_duration(self, pieces: List[Dict], target_duration: int, group_analysis: Dict[str, Any]) -> List[Dict]:
        """Select pieces to fit the target duration with ordering preferences"""
        selected_pieces = []
        current_duration = 0
        
        # Get ordering preferences
        start_preferences = group_analysis.get("start_preferences", [])
        end_preferences = group_analysis.get("end_preferences", [])
        
        # Find pieces that match start preferences
        start_pieces = []
        if start_preferences:
            for preference in start_preferences:
                for piece in pieces:
                    if preference.lower() in piece.get("genre", "").lower():
                        start_pieces.append(piece)
                        break
        
        # Find pieces that match end preferences
        end_pieces = []
        if end_preferences:
            for preference in end_preferences:
                for piece in pieces:
                    if preference.lower() in piece.get("genre", "").lower():
                        end_pieces.append(piece)
                        break
        
        # Add start piece if found and fits
        if start_pieces:
            start_piece = start_pieces[0]
            if start_piece.get("duration_minutes", 5) <= target_duration * 0.9:
                selected_pieces.append(start_piece)
                current_duration += start_piece.get("duration_minutes", 5)
                pieces.remove(start_piece)  # Remove from available pieces
        
        # Add middle pieces
        for piece in pieces:
            piece_duration = piece.get("duration_minutes", 5)
            
            # Skip if this piece is reserved for the end
            if end_pieces and piece in end_pieces:
                continue
            
            # Add piece if it fits within 90% of target duration
            if current_duration + piece_duration <= target_duration * 0.9:
                selected_pieces.append(piece)
                current_duration += piece_duration
            else:
                break
        
        # Add end piece if found and fits
        if end_pieces and current_duration < target_duration * 0.9:
            end_piece = end_pieces[0]
            if current_duration + end_piece.get("duration_minutes", 5) <= target_duration * 0.9:
                selected_pieces.append(end_piece)
                current_duration += end_piece.get("duration_minutes", 5)
        
        # Add reasoning to each piece
        for i, piece in enumerate(selected_pieces):
            piece["collaborative_reasoning"] = self._generate_piece_reasoning(piece, group_analysis, i, len(selected_pieces))
        
        return selected_pieces
    
    def _generate_piece_reasoning(self, piece: Dict, group_analysis: Dict[str, Any], position: int = 0, total_pieces: int = 0) -> str:
        """Generate reasoning for why this piece was selected"""
        reasons = []
        
        # Check if this piece was selected for ordering preferences
        start_preferences = group_analysis.get("start_preferences", [])
        end_preferences = group_analysis.get("end_preferences", [])
        
        if position == 0 and start_preferences:
            for preference in start_preferences:
                if preference.lower() in piece.get("genre", "").lower():
                    reasons.append(f"opens with {preference} as requested")
                    break
        
        if position == total_pieces - 1 and end_preferences:
            for preference in end_preferences:
                if preference.lower() in piece.get("genre", "").lower():
                    reasons.append(f"closes with {preference} as requested")
                    break
        
        if piece.get("collaborative_score", 0) > 0:
            reasons.append("matches group preferences")
        
        if piece.get("genre") in group_analysis.get("common_genres", []):
            reasons.append(f"popular {piece['genre']} choice")
        
        if piece.get("composer") in group_analysis.get("common_composers", []):
            reasons.append(f"group favorite composer {piece['composer']}")
        
        if piece.get("difficulty") in group_analysis.get("skill_levels", []):
            reasons.append(f"appropriate for {piece['difficulty']} skill level")
        
        if reasons:
            return f"Selected because: {', '.join(reasons)}"
        else:
            return "Classic piece that works well for group performance"
    
    def _generate_collaborative_reasoning(self, group_analysis: Dict[str, Any], pieces: List[Dict]) -> str:
        """Generate reasoning for collaborative setlist choices"""
        reasoning_parts = [
            f"Designed for {group_analysis['group_size']} group members with compatibility score {group_analysis['compatibility_score']:.1f}",
            f"Common preferences: {', '.join(group_analysis['common_genres'])} genres, {', '.join(group_analysis['common_composers'])} composers",
            f"Skill levels: {', '.join(group_analysis['skill_levels'])}",
            f"Instruments: {', '.join(group_analysis['instruments'])}"
        ]
        
        return ". ".join(reasoning_parts) + "."
    
    def _get_username_for_id(self, user_id: str) -> str:
        """Get username for user ID (placeholder implementation)"""
        return f"User {user_id[-4:]}"  # Return last 4 chars as placeholder

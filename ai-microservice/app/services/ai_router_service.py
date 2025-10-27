"""
AI Router Service - Intelligently routes user requests to appropriate AI services
"""
from typing import Dict, List, Any, Optional, Tuple
import re
from ..services.llm_service import LLMService

class AIRouterService:
    """Service that intelligently routes user requests to appropriate AI services"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.classical_keywords = [
            "beethoven", "mozart", "bach", "chopin", "debussy", "rachmaninoff",
            "sonata", "concerto", "symphony", "nocturne", "prelude", "etude",
            "classical", "baroque", "romantic", "impressionist", "imslp",
            "mutopia", "lookup", "find", "search", "sheet music for"
        ]
        
        self.generation_keywords = [
            "create", "generate", "make", "compose", "write", "new music",
            "time signature", "key", "notes", "melody", "chord", "scale",
            "quarter notes", "eighth notes", "major", "minor", "tempo"
        ]
        
        self.editing_keywords = [
            "edit", "change", "modify", "add", "remove", "transpose",
            "key change", "tempo change", "add repeat", "add chord",
            "make it", "adjust", "update", "revise"
        ]
        
        self.setlist_keywords = [
            "setlist", "concert", "program", "repertoire", "performance",
            "recital", "chamber music", "solo performance", "duration",
            "pieces for", "concert program", "music program", "playlist",
            "group", "collaborative", "everyone", "team", "ensemble"
        ]
    
    async def route_request(self, user_input: str, user_id: str, 
                          conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Route user input to appropriate AI service
        
        Args:
            user_input: User's natural language input
            user_id: User ID for tracking
            conversation_id: Optional conversation context
            
        Returns:
            Dict with routing decision and service to call
        """
        try:
            # Analyze the input to determine intent
            intent_analysis = await self._analyze_intent(user_input)
            
            # Determine the appropriate service
            service_decision = self._determine_service(intent_analysis, user_input)
            
            # Prepare the routing response
            routing_response = {
                "success": True,
                "intent": intent_analysis["intent"],
                "confidence": intent_analysis["confidence"],
                "service": service_decision["service"],
                "endpoint": service_decision["endpoint"],
                "parameters": service_decision["parameters"],
                "reasoning": intent_analysis["reasoning"]
            }
            
            return routing_response
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Routing failed: {str(e)}",
                "intent": "unknown",
                "service": "imslp_search",  # Default fallback
                "endpoint": "/api/v1/search-imslp",
                "parameters": {"query": user_input, "user_id": user_id}
            }
    
    async def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine intent using LLM"""
        try:
            # Build intent analysis prompt
            prompt = self._build_intent_analysis_prompt(user_input)
            
            # Call LLM for intent analysis
            response = await self.llm_service.generate_abc_edit(
                current_abc="",  # Not used for text generation
                edit_instruction=prompt,
                context="",
                system_prompt=self._get_intent_system_prompt()
            )
            
            if response["success"]:
                # Parse LLM response
                intent_result = self._parse_intent_response(response["abc_notation"])
                return intent_result
            else:
                # Fallback to keyword-based analysis
                return self._keyword_based_intent_analysis(user_input)
                
        except Exception as e:
            # Fallback to keyword-based analysis
            return self._keyword_based_intent_analysis(user_input)
    
    def _build_intent_analysis_prompt(self, user_input: str) -> str:
        """Build prompt for intent analysis"""
        prompt = f"""Analyze this user input and determine what type of music-related request it is:

User Input: "{user_input}"

Classify the intent as one of these types:

1. CLASSICAL_LOOKUP - User wants to find existing classical music (e.g., "find Beethoven's Moonlight Sonata", "lookup Chopin Nocturne")

2. MUSIC_GENERATION - User wants to generate new music from description (e.g., "create a melody in C major", "generate a waltz", "make a song with quarter notes")

3. MUSIC_EDITING - User wants to edit existing music (e.g., "change the key to G major", "add a repeat", "make it faster")

4. SETLIST_DESIGN - User wants to design a concert program (e.g., "create a setlist", "design a concert program", "suggest pieces for a recital")

5. UNKNOWN - Cannot determine intent

Respond with:
- Intent: [CLASSICAL_LOOKUP|MUSIC_GENERATION|MUSIC_EDITING|SETLIST_DESIGN|UNKNOWN]
- Confidence: [0.0-1.0]
- Reasoning: [Brief explanation of why you chose this intent]"""
        
        return prompt
    
    def _get_intent_system_prompt(self) -> str:
        """Get system prompt for intent analysis"""
        return """You are an expert at analyzing music-related user requests and determining their intent. 
You understand the difference between looking up existing music, generating new music, editing music, 
and designing concert programs. Provide accurate intent classification with clear reasoning."""
    
    def _parse_intent_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response for intent analysis"""
        try:
            # Extract intent from response
            intent_match = re.search(r'Intent:\s*(\w+)', content, re.IGNORECASE)
            intent = intent_match.group(1).lower() if intent_match else "unknown"
            
            # Extract confidence
            confidence_match = re.search(r'Confidence:\s*([0-9.]+)', content)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            # Extract reasoning
            reasoning_match = re.search(r'Reasoning:\s*(.+)', content, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "Intent analysis completed"
            
            return {
                "intent": intent,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            return {
                "intent": "unknown",
                "confidence": 0.3,
                "reasoning": f"Failed to parse intent: {str(e)}"
            }
    
    def _keyword_based_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback keyword-based intent analysis"""
        input_lower = user_input.lower()
        
        # Check for classical lookup keywords
        classical_score = sum(1 for keyword in self.classical_keywords if keyword in input_lower)
        
        # Check for generation keywords
        generation_score = sum(1 for keyword in self.generation_keywords if keyword in input_lower)
        
        # Check for editing keywords
        editing_score = sum(1 for keyword in self.editing_keywords if keyword in input_lower)
        
        # Check for setlist keywords
        setlist_score = sum(1 for keyword in self.setlist_keywords if keyword in input_lower)
        
        # Determine intent based on highest score with priority for setlist
        scores = {
            "classical_lookup": classical_score,
            "music_generation": generation_score,
            "music_editing": editing_score,
            "setlist_design": setlist_score
        }
        
        # Give priority to setlist when both setlist and generation keywords are present
        if setlist_score > 0 and generation_score > 0:
            scores["setlist_design"] += 1  # Boost setlist score
        
        max_score = max(scores.values())
        if max_score == 0:
            intent = "unknown"
            confidence = 0.1
        else:
            intent = max(scores, key=scores.get)
            confidence = min(0.8, max_score * 0.2)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "reasoning": f"Keyword-based analysis: {scores}"
        }
    
    def _determine_service(self, intent_analysis: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Determine which service to call based on intent"""
        intent = intent_analysis["intent"]
        
        if intent == "classical_lookup":
            return {
                "service": "imslp_search",
                "endpoint": "/api/v1/search-imslp",
                "parameters": {
                    "query": user_input,
                    "user_id": "routed_user"
                }
            }
        
        elif intent == "music_generation":
            return {
                "service": "music_generation",
                "endpoint": "/api/v1/music/generate",
                "parameters": {
                    "description": user_input,
                    "user_id": "routed_user"
                }
            }
        
        elif intent == "music_editing":
            return {
                "service": "music_edit",
                "endpoint": "/api/v1/music/edit",
                "parameters": {
                    "music_id": "temp_music_id",
                    "current_abc": "X:1\nT:Sample\nM:4/4\nK:C\nC D E F | G A B c |",
                    "edit_instruction": user_input,
                    "user_id": "routed_user"
                }
            }
        
        elif intent == "setlist_design":
            # Extract parameters from user input first
            params = self._extract_setlist_parameters(user_input)
            
            # Check if this is a collaborative request
            if self._is_collaborative_request(user_input):
                return {
                    "service": "chat_setlist",
                    "endpoint": "/api/v1/setlist/chat-based",
                    "parameters": {
                        "user_input": user_input,
                        "group_id": "temp_group_id",
                        "conversation_id": conversation_id or "temp_conv",
                        "organizer_user_id": user_id,
                        "group_member_ids": ["user1", "user2", "user3"]  # Would be populated from group data
                    }
                }
            else:
                return {
                    "service": "setlist_design",
                    "endpoint": "/api/v1/setlist/design",
                    "parameters": {
                        "user_id": "routed_user",
                        "concert_type": params["concert_type"],
                        "duration_minutes": params["duration_minutes"],
                        "instruments": params["instruments"],
                        "skill_level": params["skill_level"],
                        "preferences": {"description": user_input}
                    }
                }
        
        else:  # unknown intent
            return {
                "service": "imslp_search",
                "endpoint": "/api/v1/search-imslp",
                "parameters": {
                    "query": user_input,
                    "user_id": "routed_user"
                }
            }
    
    def get_supported_intents(self) -> List[Dict[str, Any]]:
        """Get list of supported intents and their descriptions"""
        return [
            {
                "intent": "classical_lookup",
                "name": "Classical Music Lookup",
                "description": "Find existing classical music pieces",
                "keywords": ["beethoven", "mozart", "sonata", "concerto", "lookup", "find"],
                "service": "imslp_search",
                "example": "Find Beethoven's Moonlight Sonata"
            },
            {
                "intent": "music_generation",
                "name": "Music Generation",
                "description": "Generate new music from natural language description",
                "keywords": ["create", "generate", "make", "compose", "time signature", "key"],
                "service": "music_generation",
                "example": "Create a waltz in C major"
            },
            {
                "intent": "music_editing",
                "name": "Music Editing",
                "description": "Edit existing music notation",
                "keywords": ["edit", "change", "modify", "transpose", "add repeat"],
                "service": "music_edit",
                "example": "Change the key to G major"
            },
            {
                "intent": "setlist_design",
                "name": "Setlist Design",
                "description": "Design concert programs and setlists",
                "keywords": ["setlist", "concert", "program", "repertoire", "recital"],
                "service": "setlist_design",
                "example": "Create a 60-minute piano recital program"
            }
        ]
    
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
        elif any(word in user_lower for word in ["folk", "traditional", "acoustic"]):
            concert_type = "folk_concert"
        
        # Extract instruments
        instruments = ["piano"]  # default
        instrument_keywords = {
            "piano": ["piano", "keyboard"],
            "violin": ["violin", "fiddle"],
            "cello": ["cello", "cello"],
            "viola": ["viola"],
            "flute": ["flute"],
            "clarinet": ["clarinet"],
            "guitar": ["guitar", "acoustic guitar", "electric guitar"],
            "bass": ["bass", "bass guitar", "upright bass"],
            "drums": ["drums", "drum set", "percussion"],
            "saxophone": ["saxophone", "sax", "alto sax", "tenor sax"],
            "trumpet": ["trumpet"],
            "voice": ["voice", "vocal", "singer", "singing"]
        }
        
        detected_instruments = []
        for instrument, keywords in instrument_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_instruments.append(instrument)
        
        if detected_instruments:
            instruments = detected_instruments
        
        # Extract skill level
        skill_level = "intermediate"  # default
        if any(word in user_lower for word in ["beginner", "easy", "simple"]):
            skill_level = "beginner"
        elif any(word in user_lower for word in ["advanced", "difficult", "challenging", "professional"]):
            skill_level = "advanced"
        elif any(word in user_lower for word in ["expert", "master", "virtuoso"]):
            skill_level = "professional"
        
        return {
            "concert_type": concert_type,
            "duration_minutes": duration_minutes,
            "instruments": instruments,
            "skill_level": skill_level
        }
    
    def _is_collaborative_request(self, user_input: str) -> bool:
        """Check if the request is asking for collaborative/group setlist design"""
        user_lower = user_input.lower()
        
        collaborative_keywords = [
            "everyone", "group", "team", "collaborative", "together", 
            "all of us", "the group", "our group", "ensemble", "band",
            "ask everyone", "gather preferences", "group preferences",
            "what does everyone", "group input", "team input"
        ]
        
        return any(keyword in user_lower for keyword in collaborative_keywords)

"""
Pydantic models for API requests
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class AudioFormat(str, Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"

class IMSLPSearchRequest(BaseModel):
    """Request model for IMSLP classical music search"""
    query: str = Field(..., description="Search query for classical music", example="Moonlight Sonata Beethoven")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")

class AudioTranscriptionRequest(BaseModel):
    """Request model for audio transcription"""
    audio_file: str = Field(..., description="Base64 encoded audio data")
    audio_format: AudioFormat = Field(..., description="Audio format")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")
    duration_seconds: int = Field(..., ge=1, le=30, description="Duration of audio in seconds")
    use_crepe: bool = Field(False, description="Use CREPE pitch tracker instead of Basic Pitch")

class MelodyEditRequest(BaseModel):
    """Request model for melody editing"""
    abc_notation: str = Field(..., description="ABC notation to edit")
    edit_instruction: str = Field(..., description="Natural language edit instruction", example="change the third note to G")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")

class RecommendationRequest(BaseModel):
    """Request model for music recommendations"""
    chat_id: str = Field(..., description="Chat ID for context", example="chat456")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")
    chat_history: List[dict] = Field(..., description="Previous chat messages for context")

class TranspositionRequest(BaseModel):
    """Request model for transposition"""
    abc_notation: str = Field(..., description="ABC notation to transpose")
    target_instrument: str = Field(..., description="Target instrument", example="Bb clarinet")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")

class MusicGenerationRequest(BaseModel):
    """Request model for natural language to ABC generation"""
    description: str = Field(..., description="Natural language description of music", example="Time signature 3/4, key F minor, eighth notes: A-flat, G, F")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context", example="conv789")
    context: Optional[str] = Field(None, description="Additional context for generation", example="This is for a jazz ensemble")

class MusicEditRequest(BaseModel):
    """Request model for ABC notation editing"""
    music_id: str = Field(..., description="ID of the music to edit", example="music123")
    current_abc: str = Field(..., description="Current ABC notation")
    edit_instruction: str = Field(..., description="Natural language edit instruction", example="Add chord symbols Fm, Cm")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context", example="conv789")
    conversation_history: Optional[List[dict]] = Field(None, description="Previous conversation messages")

class SetlistDesignRequest(BaseModel):
    """Request model for AI setlist design"""
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")
    concert_type: str = Field(..., description="Type of concert", example="classical_recital")
    duration_minutes: int = Field(..., ge=15, le=180, description="Desired concert duration in minutes", example=60)
    instruments: List[str] = Field(..., description="Available instruments", example=["piano", "violin", "cello"])
    skill_level: str = Field(..., description="Performer skill level", example="intermediate")
    preferences: Optional[dict] = Field(None, description="Musical preferences and constraints")
    existing_repertoire: Optional[List[str]] = Field(None, description="Existing pieces in repertoire")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context", example="conv789")

class SetlistRefinementRequest(BaseModel):
    """Request model for refining an existing setlist"""
    setlist_id: str = Field(..., description="ID of the setlist to refine", example="setlist123")
    refinement_instruction: str = Field(..., description="How to refine the setlist", example="Make it more challenging")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context", example="conv789")

class GroupMemberPreference(BaseModel):
    """Individual group member's musical preferences"""
    user_id: str = Field(..., description="User ID", example="user123")
    username: str = Field(..., description="Display name", example="Sarah")
    favorite_genres: List[str] = Field(default_factory=list, description="Preferred genres", example=["jazz", "blues"])
    favorite_composers: List[str] = Field(default_factory=list, description="Preferred composers", example=["Miles Davis", "John Coltrane"])
    skill_level: str = Field(..., description="Skill level", example="intermediate")
    instruments: List[str] = Field(default_factory=list, description="Instruments they play", example=["piano", "voice"])
    avoid_genres: List[str] = Field(default_factory=list, description="Genres to avoid", example=["heavy metal"])
    tempo_preference: Optional[str] = Field(None, description="Preferred tempo", example="moderate")
    mood_preference: Optional[str] = Field(None, description="Preferred mood", example="energetic")

class CollaborativeSetlistRequest(BaseModel):
    """Request model for collaborative setlist design with group preferences"""
    group_id: str = Field(..., description="Group chat ID", example="group456")
    duration_minutes: int = Field(..., ge=15, le=180, description="Desired concert duration in minutes", example=60)
    concert_type: str = Field(..., description="Type of concert", example="jazz_concert")
    group_members: List[GroupMemberPreference] = Field(..., description="Group member preferences")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context", example="conv789")
    organizer_user_id: str = Field(..., description="User ID of the person organizing the setlist", example="organizer123")

class ChatBasedSetlistRequest(BaseModel):
    """Request model for chat-based collaborative setlist design"""
    user_input: str = Field(..., description="User's request for collaborative setlist", example="Create a jazz setlist for our group")
    group_id: str = Field(..., description="Group chat ID", example="group456")
    conversation_id: str = Field(..., description="Conversation ID", example="conv789")
    organizer_user_id: str = Field(..., description="User ID of the person making the request", example="organizer123")
    organizer_username: str = Field(..., description="Display name of the person making the request", example="Sarah")
    group_member_ids: List[str] = Field(..., description="List of group member user IDs", example=["user1", "user2", "user3"])

class GroupPreferenceResponse(BaseModel):
    """Response model for group member preference collection"""
    setlist_id: str = Field(..., description="ID of the setlist request", example="setlist123")
    user_id: str = Field(..., description="User ID", example="user123")
    username: str = Field(..., description="Display name", example="Sarah")
    preference_text: str = Field(..., description="Natural language response with preferences", example="I love jazz and blues, play piano and voice, intermediate level, avoid heavy metal, prefer moderate tempo")
    response_timestamp: str = Field(..., description="When the user responded", example="2024-12-19T10:30:00Z")

class AIRouterRequest(BaseModel):
    """Request model for AI routing"""
    user_input: str = Field(..., description="User's natural language input", example="Find Beethoven's Moonlight Sonata")
    user_id: str = Field(..., description="User ID for tracking", example="teacher123")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context", example="conv789")

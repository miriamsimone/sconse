"""
Pydantic models for API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model"""
    status: str = Field(..., description="Response status", example="success")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class IMSLPResponse(BaseResponse):
    """Response model for IMSLP search"""
    image_url: str = Field(..., description="URL to the sheet music image")
    title: str = Field(..., description="Title of the classical piece")
    composer: str = Field(..., description="Composer name")
    imslp_url: str = Field(..., description="URL to the full score on IMSLP")
    opus: Optional[str] = Field(None, description="Opus number if available")
    description: Optional[str] = Field(None, description="Description of the piece")

class AudioTranscriptionResponse(BaseResponse):
    """Response model for audio transcription"""
    abc_notation: str = Field(..., description="Transcribed ABC notation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    key_detected: str = Field(..., description="Detected key signature")
    time_signature: str = Field(..., description="Detected time signature")
    notes_detected: int = Field(..., description="Number of notes detected")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")

class MelodyEditResponse(BaseResponse):
    """Response model for melody editing"""
    abc_notation: str = Field(..., description="Edited ABC notation")
    changes_made: str = Field(..., description="Description of changes made")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

class RecommendationResponse(BaseResponse):
    """Response model for music recommendations"""
    recommendation: str = Field(..., description="Recommended song name")
    artist: Optional[str] = Field(None, description="Artist name")
    reasoning: str = Field(..., description="Explanation for the recommendation")
    abc_notation: Optional[str] = Field(None, description="ABC notation if available")

class TranspositionResponse(BaseResponse):
    """Response model for transposition"""
    abc_notation: str = Field(..., description="Transposed ABC notation")
    original_key: str = Field(..., description="Original key signature")
    transposed_to: str = Field(..., description="Target instrument")
    changes_made: str = Field(..., description="Description of transposition changes")

class MusicGenerationResponse(BaseResponse):
    """Response model for music generation"""
    music_id: str = Field(..., description="Unique ID for the generated music")
    abc_notation: str = Field(..., description="Generated ABC notation")
    sheet_music_url: str = Field(..., description="URL to the rendered sheet music image")
    title: str = Field(..., description="Title of the generated music")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    validation_status: str = Field(..., description="ABC validation status")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

class MusicEditResponse(BaseResponse):
    """Response model for music editing"""
    music_id: str = Field(..., description="ID of the edited music")
    abc_notation: str = Field(..., description="Edited ABC notation")
    sheet_music_url: str = Field(..., description="URL to the updated sheet music image")
    changes: List[str] = Field(..., description="List of changes made")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    validation_status: str = Field(..., description="ABC validation status")

class SetlistPiece(BaseModel):
    """Model for a piece in a setlist"""
    title: str = Field(..., description="Title of the piece")
    composer: str = Field(..., description="Composer name")
    duration_minutes: int = Field(..., description="Estimated duration in minutes")
    difficulty_level: str = Field(..., description="Difficulty level", example="intermediate")
    key_signature: str = Field(..., description="Key signature", example="C major")
    instruments: List[str] = Field(..., description="Required instruments")
    genre: str = Field(..., description="Musical genre", example="classical")
    reasoning: str = Field(..., description="Why this piece was chosen")
    abc_notation: Optional[str] = Field(None, description="ABC notation if available")

class SetlistDesignResponse(BaseResponse):
    """Response model for setlist design"""
    setlist_id: str = Field(..., description="Unique ID for the setlist")
    title: str = Field(..., description="Setlist title")
    total_duration: int = Field(..., description="Total duration in minutes")
    pieces: List[SetlistPiece] = Field(..., description="List of pieces in the setlist")
    design_reasoning: str = Field(..., description="Overall design reasoning")
    agent_contributions: dict = Field(..., description="Contributions from each AI agent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

class SetlistRefinementResponse(BaseResponse):
    """Response model for setlist refinement"""
    setlist_id: str = Field(..., description="ID of the refined setlist")
    original_setlist: dict = Field(..., description="Original setlist data")
    refined_setlist: dict = Field(..., description="Refined setlist data")
    changes_made: List[str] = Field(..., description="List of changes made")
    reasoning: str = Field(..., description="Reasoning for the refinements")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

class ChatBasedSetlistResponse(BaseResponse):
    """Response model for chat-based collaborative setlist design"""
    action: str = Field(..., description="Action to take", example="ask_preferences")
    message: str = Field(..., description="Message to send to group chat")
    setlist_id: Optional[str] = Field(None, description="Setlist ID if generated")
    waiting_for_responses: bool = Field(False, description="Whether waiting for group responses")
    required_responses: List[str] = Field(default_factory=list, description="User IDs still needed to respond")
    questions: Optional[dict] = Field(None, description="Questions to ask group members")
    setlist_data: Optional[dict] = Field(None, description="Generated setlist data if ready")

class GroupPreferenceMessage(BaseResponse):
    """Response model for group preference collection messages"""
    message_type: str = Field(..., description="Type of message", example="preference_question")
    target_user_id: Optional[str] = Field(None, description="Specific user to ask (if individual)")
    message: str = Field(..., description="Message content")
    questions: List[str] = Field(default_factory=list, description="Questions to ask")
    setlist_context: dict = Field(default_factory=dict, description="Context about the setlist being created")

class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

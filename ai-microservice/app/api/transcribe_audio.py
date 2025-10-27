"""
Audio Transcription API Endpoint
"""
from fastapi import APIRouter, HTTPException
from ..models.requests import AudioTranscriptionRequest
from ..models.responses import AudioTranscriptionResponse, ErrorResponse
from ..services.audio_service_simple import AudioTranscriptionService

router = APIRouter()

@router.post("/transcribe-audio", response_model=AudioTranscriptionResponse)
async def transcribe_audio(request: AudioTranscriptionRequest):
    """
    Transcribe hummed audio to ABC notation
    """
    try:
        # Initialize audio transcription service
        audio_service = AudioTranscriptionService()
        
        # Transcribe audio
        result = await audio_service.transcribe_audio(
            audio_data=request.audio_file,
            audio_format=request.audio_format.value,
            use_crepe=request.use_crepe
        )
        
        # Return success response
        return AudioTranscriptionResponse(
            status="success",
            abc_notation=result['abc_notation'],
            confidence=result['confidence'],
            key_detected=result['key_detected'],
            time_signature=result['time_signature'],
            notes_detected=result['notes_detected'],
            processing_time_ms=result['processing_time_ms']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio transcription failed: {str(e)}"
        )

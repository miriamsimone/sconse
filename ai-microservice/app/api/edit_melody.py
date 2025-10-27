"""
Melody Editing API Endpoint
"""
from fastapi import APIRouter, HTTPException
from ..models.requests import MelodyEditRequest
from ..models.responses import MelodyEditResponse, ErrorResponse
from ..services.melody_editing_service import MelodyEditingService

router = APIRouter()

@router.post("/edit-melody", response_model=MelodyEditResponse)
async def edit_melody(request: MelodyEditRequest):
    """
    Edit melody using natural language commands
    """
    try:
        # Initialize melody editing service
        editing_service = MelodyEditingService()
        
        # Edit the melody
        result = await editing_service.edit_melody(
            abc_notation=request.abc_notation,
            edit_instruction=request.edit_instruction
        )
        
        # Return success response
        return MelodyEditResponse(
            status="success",
            abc_notation=result['abc_notation'],
            changes_made=result['changes_made'],
            confidence=result['confidence']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Melody editing failed: {str(e)}"
        )

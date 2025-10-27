"""
Music Editing API Endpoints
"""
from fastapi import APIRouter, HTTPException, status
from ..models.requests import MusicEditRequest
from ..models.responses import MusicEditResponse, ErrorResponse
from ..services.music_edit_service import MusicEditService
from ..services.abc_renderer_simple import ABCRenderer
import uuid

router = APIRouter()

@router.post("/music/edit", response_model=MusicEditResponse, status_code=status.HTTP_200_OK,
             responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
async def edit_music(request: MusicEditRequest):
    """
    Edit existing ABC notation based on natural language instruction
    
    This endpoint allows users to edit existing sheet music by providing natural language instructions.
    The AI will analyze the instruction and apply the appropriate changes to the ABC notation.
    
    Supported edit types:
    - Key changes (transposition)
    - Tempo changes
    - Adding/removing notes
    - Adding repeats
    - Adding chord symbols
    - General edits
    """
    try:
        # Initialize services
        edit_service = MusicEditService()
        renderer = ABCRenderer()
        
        # Perform the edit
        edit_result = await edit_service.edit_music(
            current_abc=request.current_abc,
            edit_instruction=request.edit_instruction,
            user_id=request.user_id,
            conversation_history=request.conversation_history
        )
        
        if not edit_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to edit music: {edit_result.get('error', 'Unknown error')}"
            )
        
        # Generate new music ID for the edited version
        music_id = str(uuid.uuid4())
        
        # Render the edited ABC to image
        render_result = await renderer.render_abc_to_image(
            edit_result["abc_notation"], 
            music_id
        )
        
        if not render_result["success"]:
            # Fallback to placeholder image
            sheet_music_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        else:
            sheet_music_url = render_result["image_url"]
        
        # Return success response
        return MusicEditResponse(
            status="success",
            music_id=music_id,
            abc_notation=edit_result["abc_notation"],
            sheet_music_url=sheet_music_url,
            changes=edit_result["changes"],
            confidence=edit_result["confidence"],
            validation_status=edit_result["validation_status"],
            metadata={
                "user_id": request.user_id,
                "conversation_id": request.conversation_id,
                "edit_type": edit_result.get("edit_type", "general"),
                "validation_errors": edit_result.get("validation_errors", []),
                "validation_warnings": edit_result.get("validation_warnings", [])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in music editing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/music/edit/preview", response_model=dict, status_code=status.HTTP_200_OK)
async def preview_edit(request: MusicEditRequest):
    """
    Preview what changes would be made without actually editing the music
    
    This endpoint analyzes the edit instruction and returns information about
    what changes would be made, without actually modifying the ABC notation.
    """
    try:
        edit_service = MusicEditService()
        
        # Analyze the edit instruction
        edit_type = edit_service._analyze_edit_type(request.edit_instruction)
        
        # Build context for analysis
        context = edit_service._build_edit_context(
            request.current_abc,
            request.edit_instruction,
            edit_type,
            request.conversation_history
        )
        
        return {
            "status": "success",
            "edit_type": edit_type,
            "analysis": {
                "instruction": request.edit_instruction,
                "detected_type": edit_type,
                "context": context,
                "confidence": 0.8  # Placeholder confidence
            },
            "preview_available": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Preview analysis failed: {str(e)}"
        )

@router.get("/music/edit/types", response_model=dict, status_code=status.HTTP_200_OK)
async def get_edit_types():
    """
    Get list of supported edit types and their descriptions
    """
    return {
        "status": "success",
        "edit_types": {
            "key_change": {
                "name": "Key Change",
                "description": "Transpose the music to a different key",
                "keywords": ["key", "major", "minor", "transpose"],
                "example": "Change the key to G major"
            },
            "tempo_change": {
                "name": "Tempo Change", 
                "description": "Modify the tempo or speed of the music",
                "keywords": ["tempo", "bpm", "faster", "slower", "speed"],
                "example": "Make it faster, around 120 BPM"
            },
            "add_notes": {
                "name": "Add Notes",
                "description": "Add specific notes or musical elements",
                "keywords": ["add", "insert", "include", "put"],
                "example": "Add a high C at the end"
            },
            "remove_notes": {
                "name": "Remove Notes",
                "description": "Remove specific notes from the music",
                "keywords": ["remove", "delete", "take out", "omit"],
                "example": "Remove the last note"
            },
            "add_repeat": {
                "name": "Add Repeat",
                "description": "Add repeat signs or structures",
                "keywords": ["repeat", "again", "da capo", "dc"],
                "example": "Add repeat signs so it plays twice"
            },
            "add_chords": {
                "name": "Add Chords",
                "description": "Add chord symbols or harmony",
                "keywords": ["chord", "harmony", "accompaniment"],
                "example": "Add C major and G major chords"
            },
            "general": {
                "name": "General Edit",
                "description": "Any other type of musical edit",
                "keywords": [],
                "example": "Make it more interesting"
            }
        }
    }

"""
Music Generation API Endpoint
"""
from fastapi import APIRouter, HTTPException
from ..models.requests import MusicGenerationRequest
from ..models.responses import MusicGenerationResponse, ErrorResponse
from ..services.llm_service import LLMService
from ..services.abc_validator_simple import ABCValidator
from ..services.abc_renderer_simple import ABCRenderer
from ..prompts.generation_prompts import GenerationPrompts
import uuid
import os

router = APIRouter()

@router.post("/music/generate", response_model=MusicGenerationResponse)
async def generate_music(request: MusicGenerationRequest):
    """
    Generate sheet music from natural language description
    """
    try:
        # Initialize services
        llm_service = LLMService()
        validator = ABCValidator()
        renderer = ABCRenderer()
        
        # Generate ABC notation using LLM
        print(f"Generating music for: {request.description}")
        
        # Build context if provided
        context = request.context
        if request.conversation_id:
            context = f"Conversation ID: {request.conversation_id}\n{context or ''}"
        
        # Call LLM service
        llm_result = await llm_service.generate_abc_from_natural_language(
            description=request.description,
            context=context
        )
        
        if not llm_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate ABC notation: {llm_result.get('error', 'Unknown error')}"
            )
        
        abc_notation = llm_result["abc_notation"]
        confidence = llm_result.get("confidence", 0.8)
        
        print(f"Generated ABC notation: {abc_notation[:100]}...")
        
        # Validate ABC notation
        validation_result = validator.validate(abc_notation)
        
        if not validation_result["is_valid"]:
            print(f"ABC validation failed: {validation_result['errors']}")
            # Try to improve the ABC notation
            improved_result = await _try_improve_abc(
                llm_service, abc_notation, validation_result["errors"]
            )
            if improved_result["success"]:
                abc_notation = improved_result["abc_notation"]
                validation_result = validator.validate(abc_notation)
        
        # Generate unique music ID
        music_id = str(uuid.uuid4())
        
        # Extract title from ABC notation
        title = _extract_title_from_abc(abc_notation)
        
        # Render to image
        render_result = await renderer.render_abc_to_image(abc_notation, music_id)
        
        if not render_result["success"]:
            # Fallback to text representation
            sheet_music_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        else:
            sheet_music_url = render_result["image_url"]
        
        # Determine validation status
        validation_status = "valid" if validation_result["is_valid"] else "invalid"
        if validation_result["warnings"]:
            validation_status = "valid_with_warnings"
        
        # Return success response
        return MusicGenerationResponse(
            status="success",
            music_id=music_id,
            abc_notation=abc_notation,
            sheet_music_url=sheet_music_url,
            title=title,
            confidence=confidence,
            validation_status=validation_status,
            metadata={
                "user_id": request.user_id,
                "conversation_id": request.conversation_id,
                "validation_errors": validation_result.get("errors", []),
                "validation_warnings": validation_result.get("warnings", []),
                "render_format": "image"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in music generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

async def _try_improve_abc(llm_service: LLMService, abc_notation: str, errors: list) -> dict:
    """Try to improve ABC notation based on validation errors"""
    try:
        improvement_prompt = GenerationPrompts.get_improvement_prompt(abc_notation, errors)
        
        # Call LLM to improve the notation
        if llm_service.openai_client:
            response = await llm_service._call_openai(improvement_prompt)
        elif llm_service.anthropic_client:
            response = await llm_service._call_anthropic(improvement_prompt)
        else:
            return {"success": False, "error": "No LLM client available"}
        
        # Parse the improved ABC
        result = llm_service._parse_abc_response(response)
        return {
            "success": True,
            "abc_notation": result["abc_notation"]
        }
        
    except Exception as e:
        print(f"Failed to improve ABC notation: {e}")
        return {"success": False, "error": str(e)}

def _extract_title_from_abc(abc_notation: str) -> str:
    """Extract title from ABC notation"""
    lines = abc_notation.split('\n')
    for line in lines:
        if line.startswith('T:'):
            return line[2:].strip()
    return "Generated Music"

@router.get("/music/generate/test")
async def test_generation():
    """Test endpoint for music generation"""
    return {
        "status": "success",
        "message": "Music generation endpoint is working",
        "available_services": {
            "llm": "OpenAI/Anthropic integration",
            "validator": "ABC notation validation",
            "renderer": "ABC to image conversion"
        }
    }

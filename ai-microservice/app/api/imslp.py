"""
IMSLP Classical Music Search API Endpoint
"""
from fastapi import APIRouter, HTTPException
from ..models.requests import IMSLPSearchRequest
from ..models.responses import IMSLPResponse, ErrorResponse
from ..services.imslp_service import IMSLPService

router = APIRouter()

@router.post("/search-imslp", response_model=IMSLPResponse)
async def search_imslp(request: IMSLPSearchRequest):
    """
    Search for classical music from IMSLP/Mutopia Project
    """
    try:
        # Initialize IMSLP service
        imslp_service = IMSLPService()
        
        # Search for classical music
        result = await imslp_service.search_classical_music(request.query)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No classical music found for '{request.query}'"
            )
        
        # Return success response
        return IMSLPResponse(
            status="success",
            image_url=result['pdf_url'],  # For now, use PDF URL directly
            title=result['title'],
            composer=result['composer'],
            imslp_url=result['mutopia_url'],
            opus=result.get('opus'),
            description=result.get('description')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching classical music: {str(e)}"
        )

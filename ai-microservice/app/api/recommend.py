"""
Music Recommendations API Endpoint
"""
from fastapi import APIRouter, HTTPException
from ..models.requests import RecommendationRequest
from ..models.responses import RecommendationResponse, ErrorResponse
from ..services.recommendation_service import RecommendationService

router = APIRouter()

@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """
    Get music recommendations based on chat history
    """
    try:
        # Initialize recommendation service
        recommendation_service = RecommendationService()
        
        # Get recommendation
        result = await recommendation_service.get_recommendation(
            chat_history=request.chat_history
        )
        
        # Return success response
        return RecommendationResponse(
            status="success",
            recommendation=result['recommendation'],
            artist=result.get('artist'),
            reasoning=result['reasoning'],
            abc_notation=result.get('abc_notation')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation failed: {str(e)}"
        )

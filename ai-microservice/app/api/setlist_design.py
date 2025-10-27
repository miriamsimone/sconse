"""
Setlist Design API Endpoints
"""
from fastapi import APIRouter, HTTPException, status
from ..models.requests import SetlistDesignRequest, SetlistRefinementRequest, CollaborativeSetlistRequest
from ..models.responses import SetlistDesignResponse, SetlistRefinementResponse, ErrorResponse
from ..services.setlist_design_service import SetlistDesignService
import uuid

router = APIRouter()

@router.post("/setlist/design", response_model=SetlistDesignResponse, status_code=status.HTTP_200_OK,
             responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
async def design_setlist(request: SetlistDesignRequest):
    """
    Design a concert setlist using AI multi-agent system
    
    This endpoint uses multiple specialized AI agents to collaboratively design
    a concert setlist based on your requirements. The agents work together to:
    
    - Music Curator: Selects appropriate pieces from classical repertoire
    - Technical Advisor: Ensures pieces are technically feasible
    - Program Flow Director: Creates optimal program flow and structure
    
    The system considers:
    - Concert type and duration
    - Available instruments and skill level
    - Musical preferences and existing repertoire
    - Program flow and audience engagement
    """
    try:
        # Initialize service
        setlist_service = SetlistDesignService()
        
        # Convert request to requirements dict
        requirements = {
            "user_id": request.user_id,
            "concert_type": request.concert_type,
            "duration_minutes": request.duration_minutes,
            "instruments": request.instruments,
            "skill_level": request.skill_level,
            "preferences": request.preferences or {},
            "existing_repertoire": request.existing_repertoire or [],
            "conversation_id": request.conversation_id
        }
        
        # Design the setlist
        result = await setlist_service.design_setlist(requirements)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to design setlist: {result.get('error', 'Unknown error')}"
            )
        
        # Return success response
        return SetlistDesignResponse(
            status="success",
            setlist_id=result["setlist_id"],
            title=result["title"],
            total_duration=result["total_duration"],
            pieces=result["pieces"],
            design_reasoning=result["design_reasoning"],
            agent_contributions=result["agent_contributions"],
            confidence=result["confidence"],
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in setlist design: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/setlist/refine", response_model=SetlistRefinementResponse, status_code=status.HTTP_200_OK,
             responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
async def refine_setlist(request: SetlistRefinementRequest):
    """
    Refine an existing setlist based on feedback
    
    This endpoint allows you to refine a previously designed setlist by providing
    natural language feedback. The AI agents will work together to modify the
    setlist according to your instructions.
    
    Examples of refinement instructions:
    - "Make it more challenging"
    - "Add more romantic period pieces"
    - "Shorten the program by 15 minutes"
    - "Include more pieces in minor keys"
    """
    try:
        # Initialize service
        setlist_service = SetlistDesignService()
        
        # Refine the setlist
        result = await setlist_service.refine_setlist(
            setlist_id=request.setlist_id,
            refinement_instruction=request.refinement_instruction,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to refine setlist: {result.get('error', 'Unknown error')}"
            )
        
        # Return success response
        return SetlistRefinementResponse(
            status="success",
            setlist_id=result["setlist_id"],
            original_setlist={},  # Would include original setlist data in production
            refined_setlist=result["refined_setlist"],
            changes_made=result["changes_made"],
            reasoning=result["reasoning"],
            confidence=result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in setlist refinement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/setlist/suggestions", response_model=dict, status_code=status.HTTP_200_OK)
async def get_setlist_suggestions(
    concert_type: str = "classical_recital",
    duration_minutes: int = 60,
    instruments: str = "piano",
    skill_level: str = "intermediate"
):
    """
    Get preliminary setlist suggestions from individual agents
    
    This endpoint provides preliminary suggestions from each AI agent without
    the full collaborative design process. Useful for understanding what each
    agent would recommend before committing to a full setlist design.
    """
    try:
        # Initialize service
        setlist_service = SetlistDesignService()
        
        # Parse instruments
        instrument_list = [inst.strip() for inst in instruments.split(",")]
        
        # Create requirements
        requirements = {
            "concert_type": concert_type,
            "duration_minutes": duration_minutes,
            "instruments": instrument_list,
            "skill_level": skill_level
        }
        
        # Get suggestions
        result = await setlist_service.get_setlist_suggestions(requirements)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get suggestions: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "status": "success",
            "suggestions": result["suggestions"],
            "total_agents": result["total_agents"],
            "requirements": requirements
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get suggestions: {str(e)}"
        )

@router.get("/setlist/concert-types", response_model=dict, status_code=status.HTTP_200_OK)
async def get_concert_types():
    """Get available concert types for setlist design"""
    try:
        setlist_service = SetlistDesignService()
        concert_types = setlist_service.get_available_concert_types()
        
        return {
            "status": "success",
            "concert_types": concert_types
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get concert types: {str(e)}"
        )

@router.get("/setlist/skill-levels", response_model=dict, status_code=status.HTTP_200_OK)
async def get_skill_levels():
    """Get available skill levels for setlist design"""
    try:
        setlist_service = SetlistDesignService()
        skill_levels = setlist_service.get_skill_levels()
        
        return {
            "status": "success",
            "skill_levels": skill_levels
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get skill levels: {str(e)}"
        )

@router.get("/setlist/instruments", response_model=dict, status_code=status.HTTP_200_OK)
async def get_supported_instruments():
    """Get supported instruments for setlist design"""
    try:
        setlist_service = SetlistDesignService()
        instruments = setlist_service.get_supported_instruments()
        
        return {
            "status": "success",
            "instruments": instruments
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get instruments: {str(e)}"
        )

@router.get("/setlist/agents", response_model=dict, status_code=status.HTTP_200_OK)
async def get_agent_info():
    """Get information about the AI agents used in setlist design"""
    try:
        agents_info = {
            "music_curator": {
                "name": "Music Curator",
                "role": "Piece Selection Specialist",
                "expertise": "Classical music repertoire, difficulty assessment, and program flow",
                "responsibilities": [
                    "Select appropriate pieces from classical repertoire",
                    "Assess difficulty levels and musical appropriateness",
                    "Ensure pieces fit the concert type and audience"
                ]
            },
            "technical_advisor": {
                "name": "Technical Advisor",
                "role": "Performance Feasibility Specialist",
                "expertise": "Technical difficulty assessment, performance logistics, and practical constraints",
                "responsibilities": [
                    "Evaluate technical feasibility of pieces",
                    "Assess physical demands and memory requirements",
                    "Ensure pieces are appropriate for skill level"
                ]
            },
            "program_flow_director": {
                "name": "Program Flow Director",
                "role": "Concert Structure Specialist",
                "expertise": "Program flow, key relationships, tempo progression, and audience engagement",
                "responsibilities": [
                    "Design optimal program flow and structure",
                    "Ensure smooth transitions between pieces",
                    "Optimize audience engagement and energy levels"
                ]
            }
        }
        
        return {
            "status": "success",
            "agents": agents_info,
            "total_agents": len(agents_info),
            "collaboration": "Agents work together in a 4-phase process: Analysis, Suggestion, Evaluation, and Synthesis"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent info: {str(e)}"
        )

@router.post("/setlist/collaborative", response_model=SetlistDesignResponse, status_code=status.HTTP_200_OK,
             responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
async def design_collaborative_setlist(request: CollaborativeSetlistRequest):
    """
    Design a collaborative setlist based on group member preferences
    
    This endpoint analyzes preferences from all group members and creates
    a setlist that balances everyone's musical tastes and skill levels.
    
    The AI will:
    - Analyze each member's preferences
    - Find common ground and compromises
    - Suggest pieces that work for the group's skill levels
    - Balance different musical tastes
    - Ensure the setlist flows well as a cohesive program
    """
    try:
        # Initialize service
        setlist_service = SetlistDesignService()
        
        # Design collaborative setlist
        result = await setlist_service.design_collaborative_setlist(
            group_id=request.group_id,
            duration_minutes=request.duration_minutes,
            concert_type=request.concert_type,
            group_members=request.group_members,
            conversation_id=request.conversation_id,
            organizer_user_id=request.organizer_user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to design collaborative setlist: {result.get('error', 'Unknown error')}"
            )
        
        # Return success response
        return SetlistDesignResponse(
            status="success",
            setlist_id=result["setlist_id"],
            title=result["title"],
            total_duration=result["total_duration"],
            pieces=result["pieces"],
            design_reasoning=result["design_reasoning"],
            agent_contributions=result["agent_contributions"],
            confidence=result["confidence"],
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/setlist/gather-preferences", response_model=dict, status_code=status.HTTP_200_OK)
async def gather_group_preferences(
    group_id: str,
    organizer_user_id: str,
    concert_type: str = "jazz_concert",
    duration_minutes: int = 60
):
    """
    Generate preference gathering questions for group members
    
    This endpoint creates personalized questions for each group member
    to gather their musical preferences before designing the setlist.
    """
    try:
        setlist_service = SetlistDesignService()
        
        questions = await setlist_service.generate_preference_questions(
            group_id=group_id,
            organizer_user_id=organizer_user_id,
            concert_type=concert_type,
            duration_minutes=duration_minutes
        )
        
        return {
            "status": "success",
            "group_id": group_id,
            "questions": questions,
            "instructions": "Share these questions with your group members to gather their preferences before designing the setlist."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate preference questions: {str(e)}"
        )

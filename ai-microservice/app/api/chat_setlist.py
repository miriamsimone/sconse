"""
Chat-based Setlist Design API Endpoints

This module provides endpoints for collaborative setlist design through natural chat interactions.
It handles the flow of asking group members for preferences and generating setlists based on
their responses, all within the chat interface.
"""
from fastapi import APIRouter, HTTPException, status
from ..models.requests import ChatBasedSetlistRequest, GroupPreferenceResponse
from ..models.responses import ChatBasedSetlistResponse, GroupPreferenceMessage, ErrorResponse
from ..services.chat_setlist_service import ChatSetlistService

router = APIRouter()

# Maintain a single service instance so in-memory state persists between requests.
chat_service = ChatSetlistService()

@router.post("/setlist/chat-based", response_model=ChatBasedSetlistResponse, status_code=status.HTTP_200_OK,
             responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
async def handle_chat_setlist_request(request: ChatBasedSetlistRequest):
    """
    Handle chat-based collaborative setlist request
    
    This endpoint processes a user's request for a collaborative setlist and returns
    a message to send to the group chat asking for preferences.
    
    The flow:
    1. User requests collaborative setlist
    2. AI sends message to group asking for preferences
    3. Group members respond with their preferences
    4. AI generates setlist based on all responses
    5. AI sends completed setlist to group
    
    Args:
        request: Chat-based setlist request with group info
        
    Returns:
        Response with message to send to group chat
    """
    try:
        # Handle the setlist request
        result = await chat_service.handle_setlist_request(
            user_input=request.user_input,
            group_id=request.group_id,
            conversation_id=request.conversation_id,
            organizer_user_id=request.organizer_user_id,
            organizer_username=request.organizer_username,
            group_member_ids=request.group_member_ids
        )
        
        if not result["success"]:
            message = result.get("message") or result.get("error") or "Unknown error"
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process setlist request: {message}"
            )
        
        # Return response
        return ChatBasedSetlistResponse(
            status="success",
            action=result["action"],
            message=result["message"],
            setlist_id=result.get("setlist_id"),
            waiting_for_responses=result.get("waiting_for_responses", False),
            required_responses=result.get("required_responses", []),
            questions=result.get("questions"),
            setlist_data=result.get("setlist_data")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/setlist/preference-response", response_model=ChatBasedSetlistResponse, status_code=status.HTTP_200_OK,
             responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}})
async def handle_preference_response(request: GroupPreferenceResponse):
    """
    Handle a group member's preference response
    
    This endpoint processes a group member's response to the preference questions
    and either waits for more responses or generates the final setlist.
    
    Args:
        request: Group member's preference response
        
    Returns:
        Response with next action (wait for more responses or setlist complete)
    """
    try:
        # Handle the preference response
        result = await chat_service.handle_preference_response(
            setlist_id=request.setlist_id,
            user_id=request.user_id,
            username=request.username,
            preference_text=request.preference_text
        )
        
        if not result["success"]:
            message = result.get("message") or result.get("error") or "Unknown error"
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process preference response: {message}"
            )
        
        # Return response
        return ChatBasedSetlistResponse(
            status="success",
            action=result["action"],
            message=result["message"],
            setlist_id=result.get("setlist_id"),
            waiting_for_responses=result.get("waiting_for_responses", False),
            required_responses=result.get("required_responses", []),
            setlist_data=result.get("setlist_data")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/setlist/status/{setlist_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_setlist_status(setlist_id: str):
    """
    Get the current status of a collaborative setlist request
    
    Args:
        setlist_id: ID of the setlist request
        
    Returns:
        Current status and progress information
    """
    try:
        if setlist_id not in chat_service.active_requests:
            raise HTTPException(
                status_code=404,
                detail="Setlist request not found"
            )
        
        request = chat_service.active_requests[setlist_id]
        responses = chat_service.group_responses.get(setlist_id, [])
        
        return {
            "status": "success",
            "setlist_id": setlist_id,
            "request_status": request["status"],
            "total_members": len(request["group_member_ids"]),
            "responses_received": len(responses),
            "remaining_responses": len(request["group_member_ids"]) - len(request["responses_received"]),
            "created_at": request["created_at"],
            "setlist_data": request.get("setlist_data")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

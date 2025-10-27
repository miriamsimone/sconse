"""
AI Router API Endpoints - Intelligent routing of user requests to appropriate AI services
"""
from fastapi import APIRouter, HTTPException, status
from ..models.requests import IMSLPSearchRequest, MusicGenerationRequest, MusicEditRequest, SetlistDesignRequest, AIRouterRequest
from ..services.ai_router_service import AIRouterService

router = APIRouter()

@router.post("/ai/route", response_model=dict, status_code=status.HTTP_200_OK)
async def route_ai_request(request: AIRouterRequest):
    """
    Intelligently route user input to appropriate AI service
    
    This endpoint analyzes the user's natural language input and determines
    which AI service should handle the request. It supports:
    
    - Classical music lookup (IMSLP search)
    - Music generation from natural language
    - Music editing and modification
    - Concert setlist design
    
    The router uses AI to understand user intent and route accordingly.
    """
    try:
        # Initialize router service
        router_service = AIRouterService()
        
        # Route the request
        routing_result = await router_service.route_request(
            user_input=request.user_input,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        if not routing_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Routing failed: {routing_result.get('error', 'Unknown error')}"
            )
        
        return {
            "status": "success",
            "routing": routing_result,
            "user_input": request.user_input,
            "user_id": request.user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in AI routing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/ai/route-and-execute", response_model=dict, status_code=status.HTTP_200_OK)
async def route_and_execute_ai_request(request: AIRouterRequest):
    """
    Route user input and execute the appropriate AI service
    
    This endpoint not only routes the request but also executes the
    appropriate AI service and returns the actual results. This is
    useful for the iOS app to get the final result in one call.
    """
    try:
        # Initialize router service
        router_service = AIRouterService()
        
        # Route the request
        routing_result = await router_service.route_request(
            user_input=request.user_input,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        if not routing_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Routing failed: {routing_result.get('error', 'Unknown error')}"
            )
        
        # Execute the appropriate service based on routing decision
        service_result = await _execute_routed_service(routing_result, request.user_input, request.user_id)
        
        return {
            "status": "success",
            "routing": routing_result,
            "service_result": service_result,
            "user_input": request.user_input,
            "user_id": request.user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in AI routing and execution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/ai/intents", response_model=dict, status_code=status.HTTP_200_OK)
async def get_supported_intents():
    """Get list of supported intents and their descriptions"""
    try:
        router_service = AIRouterService()
        intents = router_service.get_supported_intents()
        
        return {
            "status": "success",
            "intents": intents,
            "total_intents": len(intents)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get intents: {str(e)}"
        )

async def _execute_routed_service(routing_result: dict, user_input: str, user_id: str) -> dict:
    """Execute the appropriate service based on routing decision"""
    try:
        service = routing_result["service"]
        parameters = routing_result["parameters"]
        
        if service == "imslp_search":
            # Call IMSLP search service
            from ..services.imslp_service import IMSLPService
            imslp_service = IMSLPService()
            result = await imslp_service.search_classical_music(parameters["query"])
            return {
                "service": "imslp_search",
                "result": result
            }
        
        elif service == "music_generation":
            # Call music generation service
            from ..services.llm_service import LLMService
            from ..services.abc_validator_simple import ABCValidator
            from ..services.abc_renderer_simple import ABCRenderer
            import uuid
            
            llm_service = LLMService()
            validator = ABCValidator()
            renderer = ABCRenderer()
            
            # Generate music
            llm_result = await llm_service.generate_abc(parameters["description"])
            
            if llm_result["success"]:
                abc_notation = llm_result["abc_notation"]
                music_id = str(uuid.uuid4())
                
                # Validate and render
                validation_result = validator.validate(abc_notation)
                render_result = await renderer.render_abc_to_image(abc_notation, music_id)
                
                return {
                    "service": "music_generation",
                    "result": {
                        "music_id": music_id,
                        "abc_notation": abc_notation,
                        "sheet_music_url": render_result.get("image_url", ""),
                        "validation_status": "valid" if validation_result["is_valid"] else "invalid",
                        "confidence": llm_result.get("confidence", 0.8)
                    }
                }
            else:
                return {
                    "service": "music_generation",
                    "result": {"error": llm_result.get("error", "Generation failed")}
                }
        
        elif service == "music_edit":
            # Call music editing service
            from ..services.music_edit_service import MusicEditService
            edit_service = MusicEditService()
            
            result = await edit_service.edit_music(
                current_abc=parameters["current_abc"],
                edit_instruction=parameters["edit_instruction"],
                user_id=parameters["user_id"]
            )
            
            return {
                "service": "music_edit",
                "result": result
            }
        
        elif service == "setlist_design":
            # Call setlist design service
            from ..services.setlist_design_service import SetlistDesignService
            setlist_service = SetlistDesignService()
            
            result = await setlist_service.design_setlist(parameters)
            
            return {
                "service": "setlist_design",
                "result": result
            }
        
        else:
            return {
                "service": "unknown",
                "result": {"error": f"Unknown service: {service}"}
            }
            
    except Exception as e:
        return {
            "service": routing_result["service"],
            "result": {"error": f"Service execution failed: {str(e)}"}
        }

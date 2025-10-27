"""
Base Agent Class for Multi-Agent Setlist Design System
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ..llm_service import LLMService

class BaseSetlistAgent(ABC):
    """Base class for all setlist design agents"""
    
    def __init__(self, agent_name: str, role: str, expertise: str):
        self.agent_name = agent_name
        self.role = role
        self.expertise = expertise
        self.llm_service = LLMService()
        self.conversation_history = []
    
    @abstractmethod
    async def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the setlist requirements from the agent's perspective"""
        pass
    
    @abstractmethod
    async def suggest_pieces(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest pieces for the setlist based on expertise"""
        pass
    
    @abstractmethod
    async def evaluate_piece(self, piece: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a specific piece for inclusion in the setlist"""
        pass
    
    @abstractmethod
    async def refine_suggestions(self, suggestions: List[Dict[str, Any]], feedback: str) -> List[Dict[str, Any]]:
        """Refine suggestions based on feedback"""
        pass
    
    def add_to_conversation(self, message: str, role: str = "assistant"):
        """Add a message to the conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": message,
            "agent": self.agent_name
        })
    
    def get_conversation_context(self) -> str:
        """Get the conversation context for this agent"""
        if not self.conversation_history:
            return ""
        
        context_parts = [f"Agent: {self.agent_name} ({self.role})"]
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    async def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Call the LLM with the given prompt"""
        try:
            if system_prompt:
                response = await self.llm_service.generate_abc_edit(
                    current_abc="",  # Not used for text generation
                    edit_instruction=prompt,
                    context=self.get_conversation_context(),
                    system_prompt=system_prompt
                )
            else:
                response = await self.llm_service.generate_abc(
                    natural_language_description=prompt,
                    context=self.get_conversation_context()
                )
            
            if response["success"]:
                return {
                    "success": True,
                    "content": response.get("abc_notation", ""),  # Using abc_notation field for text
                    "confidence": response.get("confidence", 0.8)
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "LLM call failed")
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM call failed: {str(e)}"
            }
    
    def format_agent_response(self, content: str, confidence: float = 0.8) -> Dict[str, Any]:
        """Format a response from this agent"""
        return {
            "agent": self.agent_name,
            "role": self.role,
            "expertise": self.expertise,
            "content": content,
            "confidence": confidence,
            "timestamp": "2024-12-19T00:00:00Z"  # Would use actual timestamp in production
        }

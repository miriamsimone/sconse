"""
Music Editing Service for Conversational Sheet Music Editing
"""
import re
from typing import Dict, List, Optional, Tuple
from ..services.llm_service import LLMService
from ..services.abc_validator_simple import ABCValidator
from ..services.abc_renderer_simple import ABCRenderer
from ..prompts.editing_prompts import EditingPrompts

class MusicEditService:
    """Service for editing ABC notation through natural language"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.validator = ABCValidator()
        self.renderer = ABCRenderer()
        self.prompts = EditingPrompts()
    
    async def edit_music(self, current_abc: str, edit_instruction: str, 
                        user_id: str, conversation_history: Optional[List[dict]] = None) -> Dict:
        """
        Edit ABC notation based on natural language instruction
        
        Args:
            current_abc: Current ABC notation
            edit_instruction: Natural language instruction for editing
            user_id: User ID for tracking
            conversation_history: Previous conversation context
            
        Returns:
            Dict with editing results
        """
        try:
            # Analyze the edit instruction to determine edit type
            edit_type = self._analyze_edit_type(edit_instruction)
            
            # Generate edited ABC notation using LLM
            edit_result = await self._generate_edit(current_abc, edit_instruction, edit_type, conversation_history)
            
            if not edit_result["success"]:
                return {
                    "success": False,
                    "error": edit_result.get("error", "Failed to generate edit"),
                    "confidence": 0.0
                }
            
            edited_abc = edit_result["abc_notation"]
            changes = edit_result.get("changes", [])
            confidence = edit_result.get("confidence", 0.8)
            
            # Validate the edited ABC notation
            validation_result = self.validator.validate(edited_abc)
            
            # If validation fails, try to fix common issues
            if not validation_result["is_valid"]:
                fixed_result = await self._try_fix_abc(edited_abc, validation_result["errors"])
                if fixed_result["success"]:
                    edited_abc = fixed_result["abc_notation"]
                    changes.append("Fixed ABC syntax errors")
                    validation_result = self.validator.validate(edited_abc)
            
            # Determine validation status
            validation_status = "valid" if validation_result["is_valid"] else "invalid"
            if validation_result["warnings"]:
                validation_status = "valid_with_warnings"
            
            return {
                "success": True,
                "abc_notation": edited_abc,
                "changes": changes,
                "confidence": confidence,
                "validation_status": validation_status,
                "validation_errors": validation_result.get("errors", []),
                "validation_warnings": validation_result.get("warnings", []),
                "edit_type": edit_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Music editing failed: {str(e)}",
                "confidence": 0.0
            }
    
    def _analyze_edit_type(self, edit_instruction: str) -> str:
        """Analyze the edit instruction to determine the type of edit"""
        instruction_lower = edit_instruction.lower()
        
        # Key changes
        if any(keyword in instruction_lower for keyword in ["key", "major", "minor", "transpose"]):
            return "key_change"
        
        # Tempo changes
        if any(keyword in instruction_lower for keyword in ["tempo", "bpm", "faster", "slower", "speed"]):
            return "tempo_change"
        
        # Add notes
        if any(keyword in instruction_lower for keyword in ["add", "insert", "include", "put"]):
            return "add_notes"
        
        # Remove notes
        if any(keyword in instruction_lower for keyword in ["remove", "delete", "take out", "omit"]):
            return "remove_notes"
        
        # Add repeats
        if any(keyword in instruction_lower for keyword in ["repeat", "again", "da capo", "dc"]):
            return "add_repeat"
        
        # Add chords
        if any(keyword in instruction_lower for keyword in ["chord", "harmony", "accompaniment"]):
            return "add_chords"
        
        # Group notes (beaming)
        if any(keyword in instruction_lower for keyword in ["group", "beam", "together", "connect"]):
            return "group_notes"
        
        # Note duration changes
        if any(keyword in instruction_lower for keyword in ["half note", "quarter note", "eighth note", "whole note", "duration", "length", "turn into", "make it"]):
            return "note_duration"
        
        # General edit
        return "general"
    
    async def _generate_edit(self, current_abc: str, edit_instruction: str, 
                           edit_type: str, conversation_history: Optional[List[dict]]) -> Dict:
        """Generate edited ABC notation using LLM"""
        try:
            # Prepare context for the LLM
            context = self._build_edit_context(current_abc, edit_instruction, edit_type, conversation_history)
            
            # Get the appropriate prompt based on edit type
            system_prompt = self.prompts.get_edit_system_prompt(edit_type)
            few_shot_examples = self.prompts.get_edit_examples(edit_type)
            
            # Call LLM to generate the edit
            llm_result = await self.llm_service.generate_abc_edit(
                current_abc=current_abc,
                edit_instruction=edit_instruction,
                context=context,
                system_prompt=system_prompt,
                few_shot_examples=few_shot_examples
            )
            
            if not llm_result["success"]:
                return {
                    "success": False,
                    "error": llm_result.get("error", "LLM generation failed")
                }
            
            # Parse the LLM response
            edited_abc = llm_result["abc_notation"]
            changes = llm_result.get("changes", [f"Applied {edit_type} edit"])
            confidence = llm_result.get("confidence", 0.8)
            
            return {
                "success": True,
                "abc_notation": edited_abc,
                "changes": changes,
                "confidence": confidence
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Edit generation failed: {str(e)}"
            }
    
    def _build_edit_context(self, current_abc: str, edit_instruction: str, 
                          edit_type: str, conversation_history: Optional[List[dict]]) -> str:
        """Build context for the edit operation"""
        context_parts = []
        
        # Add current ABC analysis
        context_parts.append(f"Current ABC notation:\n{current_abc}")
        
        # Add conversation history if available
        if conversation_history:
            context_parts.append("Previous conversation:")
            for msg in conversation_history[-3:]:  # Last 3 messages
                context_parts.append(f"- {msg.get('role', 'user')}: {msg.get('content', '')}")
        
        # Add edit type context
        context_parts.append(f"Edit type: {edit_type}")
        context_parts.append(f"Instruction: {edit_instruction}")
        
        return "\n\n".join(context_parts)
    
    async def _try_fix_abc(self, abc_notation: str, errors: List[str]) -> Dict:
        """Try to fix common ABC syntax errors"""
        try:
            # Simple fixes for common errors
            fixed_abc = abc_notation
            
            # Fix missing X: field
            if not re.search(r'^X:\d+', fixed_abc, re.MULTILINE):
                fixed_abc = "X:1\n" + fixed_abc
            
            # Fix missing T: field
            if not re.search(r'^T:', fixed_abc, re.MULTILINE):
                fixed_abc = fixed_abc.replace("X:1\n", "X:1\nT:Edited Music\n")
            
            # Fix missing M: field
            if not re.search(r'^M:', fixed_abc, re.MULTILINE):
                fixed_abc = fixed_abc.replace("T:", "T:Edited Music\nM:4/4\n")
            
            # Fix missing K: field
            if not re.search(r'^K:', fixed_abc, re.MULTILINE):
                fixed_abc = fixed_abc.replace("M:", "M:4/4\nK:C\n")
            
            # Validate the fixed version
            validation_result = self.validator.validate(fixed_abc)
            
            if validation_result["is_valid"]:
                return {
                    "success": True,
                    "abc_notation": fixed_abc,
                    "fixes_applied": ["Added missing required fields"]
                }
            else:
                return {
                    "success": False,
                    "error": "Could not fix ABC syntax errors"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"ABC fix failed: {str(e)}"
            }
    
    def _extract_title_from_abc(self, abc_notation: str) -> str:
        """Extract title from ABC notation"""
        title_match = re.search(r'^T:(.+)$', abc_notation, re.MULTILINE)
        return title_match.group(1).strip() if title_match else "Edited Music"

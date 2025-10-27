"""
LLM Service for AI-powered music generation and editing
"""
import asyncio
import json
from typing import Dict, Optional, List
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from ..config import settings

class LLMService:
    """Service for interfacing with OpenAI and Claude APIs"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize OpenAI client
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize Anthropic client (if API key is available)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.anthropic_client = AsyncAnthropic(api_key=anthropic_key)
    
    async def generate_abc_from_natural_language(self, description: str, context: Optional[str] = None) -> Dict:
        """
        Convert natural language description to ABC notation
        
        Args:
            description: Natural language description of music
            context: Optional context from conversation
            
        Returns:
            Dict with abc_notation, confidence, and metadata
        """
        try:
            # Build the prompt
            prompt = self._build_generation_prompt(description, context)
            
            # Try OpenAI first, fallback to Anthropic
            if self.openai_client:
                response = await self._call_openai(prompt)
            elif self.anthropic_client:
                response = await self._call_anthropic(prompt)
            else:
                raise Exception("No LLM client available")
            
            # Parse the response
            result = self._parse_abc_response(response)
            
            return {
                "success": True,
                "abc_notation": result["abc_notation"],
                "confidence": result.get("confidence", 0.8),
                "metadata": result.get("metadata", {}),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "abc_notation": None
            }
    
    async def generate_abc(self, natural_language_description: str, context: Optional[str] = None) -> Dict:
        """
        Generate ABC notation from natural language description
        
        Args:
            natural_language_description: Natural language description of music
            context: Optional conversation context
            
        Returns:
            Dict with generated abc_notation and metadata
        """
        try:
            # Build the generation prompt
            prompt = self._build_generation_prompt(natural_language_description, context)
            
            # Try OpenAI first, fallback to Anthropic
            if self.openai_client:
                response = await self._call_openai(prompt)
            elif self.anthropic_client:
                response = await self._call_anthropic(prompt)
            else:
                raise Exception("No LLM client available")
            
            # Parse the response
            result = self._parse_abc_response(response)
            
            return {
                "success": True,
                "abc_notation": result["abc_notation"],
                "confidence": result.get("confidence", 0.8),
                "metadata": result.get("metadata", {}),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "abc_notation": None
            }

    async def generate_abc_edit(self, current_abc: str, edit_instruction: str, context: Optional[str] = None, 
                               system_prompt: Optional[str] = None, few_shot_examples: Optional[List[Dict]] = None) -> Dict:
        """
        Generate edited ABC notation with custom prompts and examples
        
        Args:
            current_abc: Current ABC notation
            edit_instruction: Natural language edit instruction
            context: Optional conversation context
            system_prompt: Custom system prompt
            few_shot_examples: Few-shot examples for the edit type
            
        Returns:
            Dict with edited abc_notation and metadata
        """
        try:
            # Build the editing prompt with custom system prompt and examples
            prompt = self._build_custom_editing_prompt(
                current_abc, edit_instruction, context, system_prompt, few_shot_examples
            )
            
            # Try OpenAI first, fallback to Anthropic
            if self.openai_client:
                response = await self._call_openai(prompt, system_prompt)
            elif self.anthropic_client:
                response = await self._call_anthropic(prompt, system_prompt)
            else:
                raise Exception("No LLM client available")
            
            # Parse the response
            result = self._parse_abc_response(response)
            
            return {
                "success": True,
                "abc_notation": result["abc_notation"],
                "confidence": result.get("confidence", 0.8),
                "changes": result.get("changes", [f"Applied edit: {edit_instruction}"]),
                "metadata": result.get("metadata", {}),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "abc_notation": None
            }

    async def edit_abc_notation(self, current_abc: str, edit_instruction: str, context: Optional[str] = None) -> Dict:
        """
        Edit existing ABC notation based on natural language instruction
        
        Args:
            current_abc: Current ABC notation
            edit_instruction: Natural language edit instruction
            context: Optional conversation context
            
        Returns:
            Dict with edited abc_notation and metadata
        """
        try:
            # Build the editing prompt
            prompt = self._build_editing_prompt(current_abc, edit_instruction, context)
            
            # Try OpenAI first, fallback to Anthropic
            if self.openai_client:
                response = await self._call_openai(prompt)
            elif self.anthropic_client:
                response = await self._call_anthropic(prompt)
            else:
                raise Exception("No LLM client available")
            
            # Parse the response
            result = self._parse_abc_response(response)
            
            return {
                "success": True,
                "abc_notation": result["abc_notation"],
                "confidence": result.get("confidence", 0.8),
                "changes": result.get("changes", []),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "abc_notation": current_abc  # Return original on error
            }
    
    def _build_generation_prompt(self, description: str, context: Optional[str] = None) -> str:
        """Build prompt for natural language to ABC conversion"""
        base_prompt = """You are an expert music notation specialist who converts natural language descriptions into ABC notation.

ABC Notation Basics:
- X:1 (reference number)
- T:Title (title)
- M:4/4 (time signature)
- L:1/4 (default note length)
- K:C (key signature)
- Notes: C D E F G A B c d e f g a b (lowercase = higher octave)
- Durations: /2 (half), 2 (double), no modifier (default length)
- Bar lines: |

Examples:
Input: "Time signature 3/4, key F minor, eighth notes: A-flat, G, F"
Output:
X:1
T:Untitled
M:3/4
K:Fm
L:1/8
A2G2F2|

Input: "Quarter notes: C D E F, half note: G"
Output:
X:1
T:Untitled
M:4/4
K:C
L:1/4
C D E F | G2 |

Instructions:
1. Always include proper ABC header (X, T, M, L, K)
2. Use appropriate key signatures
3. Use proper note durations
4. Add bar lines for musical phrases
5. Keep it simple and clean
6. If unsure about key, use C major
7. If unsure about time signature, use 4/4

Now convert this description to ABC notation:
"""
        
        if context:
            base_prompt += f"\nContext: {context}\n"
        
        base_prompt += f"\nDescription: {description}\n\nABC Notation:"
        
        return base_prompt
    
    def _build_editing_prompt(self, current_abc: str, edit_instruction: str, context: Optional[str] = None) -> str:
        """Build prompt for ABC notation editing"""
        base_prompt = """You are an expert music notation editor who modifies ABC notation based on natural language instructions.

Current ABC notation:
```
{current_abc}
```

Edit instruction: {edit_instruction}

Instructions:
1. Make the requested changes to the ABC notation
2. Keep the same structure and format
3. Preserve the header information unless specifically asked to change it
4. Return only the modified ABC notation
5. If the instruction is unclear, make the most reasonable interpretation

Modified ABC notation:
"""
        
        if context:
            base_prompt += f"\nContext: {context}\n"
        
        return base_prompt.format(current_abc=current_abc, edit_instruction=edit_instruction)
    
    def _build_custom_editing_prompt(self, current_abc: str, edit_instruction: str, context: Optional[str] = None,
                                   system_prompt: Optional[str] = None, few_shot_examples: Optional[List[Dict]] = None) -> str:
        """Build custom editing prompt with system prompt and few-shot examples"""
        
        # Use custom system prompt or default
        if system_prompt:
            base_prompt = system_prompt
        else:
            base_prompt = """You are an expert music notation editor who modifies ABC notation based on natural language instructions.

Current ABC notation:
```
{current_abc}
```

Edit instruction: {edit_instruction}

Instructions:
1. Make the requested changes to the ABC notation
2. Keep the same structure and format
3. Preserve the header information unless specifically asked to change it
4. Return only the modified ABC notation
5. If the instruction is unclear, make the most reasonable interpretation

Modified ABC notation:
"""
        
        # Add few-shot examples if provided
        if few_shot_examples:
            examples_text = "\n\nExamples:\n"
            for i, example in enumerate(few_shot_examples[:2]):  # Limit to 2 examples
                examples_text += f"\nExample {i+1}:\n"
                examples_text += f"Input: {example['input']['instruction']}\n"
                examples_text += f"Original ABC:\n{example['input']['current_abc']}\n"
                examples_text += f"Edited ABC:\n{example['output']}\n"
                if 'changes' in example:
                    examples_text += f"Changes: {', '.join(example['changes'])}\n"
            
            base_prompt = examples_text + "\n" + base_prompt
        
        # Add context if provided
        if context:
            base_prompt += f"\nContext: {context}\n"
        
        return base_prompt.format(current_abc=current_abc, edit_instruction=edit_instruction)
    
    async def _call_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call OpenAI API"""
        try:
            system_content = system_prompt or "You are an expert music notation specialist."
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _call_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Anthropic API"""
        try:
            # Anthropic doesn't support system prompts in the same way, so we prepend it to the user message
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
                
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": full_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def _parse_abc_response(self, response: str) -> Dict:
        """Parse LLM response to extract ABC notation"""
        try:
            # Clean up the response
            response = response.strip()
            
            # Look for ABC notation block
            if "```" in response:
                # Extract content between code blocks
                start = response.find("```")
                end = response.find("```", start + 3)
                if end > start:
                    abc_content = response[start + 3:end].strip()
                else:
                    abc_content = response[start + 3:].strip()
            else:
                # Look for ABC notation patterns
                lines = response.split('\n')
                abc_lines = []
                in_abc = False
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('X:') or line.startswith('T:') or line.startswith('M:') or line.startswith('K:'):
                        in_abc = True
                    if in_abc:
                        abc_lines.append(line)
                        if line and not any(line.startswith(prefix) for prefix in ['X:', 'T:', 'M:', 'L:', 'K:', '|', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'c', 'd', 'e', 'f', 'g', 'a', 'b', '^', '=', '_', '/', '(', ')', 'z', 'Z']):
                            break
                
                abc_content = '\n'.join(abc_lines)
            
            # Remove "T:Untitled" lines if present
            abc_lines = abc_content.split('\n')
            filtered_lines = []
            for line in abc_lines:
                if line.strip() != "T:Untitled":
                    filtered_lines.append(line)
            abc_content = '\n'.join(filtered_lines)
            
            # Validate that we have ABC content
            if not abc_content or not any(line.startswith(('X:', 'T:', 'M:', 'K:')) for line in abc_content.split('\n')):
                raise Exception("No valid ABC notation found in response")
            
            return {
                "abc_notation": abc_content,
                "confidence": 0.8,
                "metadata": {
                    "source": "llm",
                    "model": settings.OPENAI_MODEL if self.openai_client else "claude-3-sonnet"
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse ABC response: {str(e)}")

# Import os for environment variables
import os

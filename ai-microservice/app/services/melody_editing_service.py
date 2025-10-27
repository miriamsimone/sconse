"""
Melody Editing Service using GPT-4
"""
import openai
from ..config import settings

class MelodyEditingService:
    """Service for editing melodies using natural language commands"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def edit_melody(self, abc_notation: str, edit_instruction: str) -> dict:
        """
        Edit melody using natural language commands
        
        Args:
            abc_notation: Original ABC notation
            edit_instruction: Natural language edit instruction
            
        Returns:
            Dict with edited ABC notation and changes made
        """
        try:
            prompt = f"""
            Edit this ABC notation based on the instruction:
            
            ABC Notation:
            {abc_notation}
            
            Edit Instruction: {edit_instruction}
            
            Requirements:
            1. Make the requested changes to the ABC notation
            2. Keep the same format and structure
            3. Ensure the ABC notation remains valid
            4. Return ONLY the modified ABC notation
            5. Do not add explanations or comments
            
            Modified ABC Notation:
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a music editing expert. Edit ABC notation based on natural language instructions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=1000
            )
            
            edited_abc = response.choices[0].message.content.strip()
            
            # Clean up the response
            if edited_abc.startswith('```'):
                edited_abc = edited_abc.split('```')[1]
            if edited_abc.startswith('abc'):
                edited_abc = edited_abc[3:]
            
            return {
                'abc_notation': edited_abc.strip(),
                'changes_made': f"Applied edit: {edit_instruction}",
                'confidence': 0.85  # Default confidence
            }
            
        except Exception as e:
            raise Exception(f"Melody editing failed: {str(e)}")

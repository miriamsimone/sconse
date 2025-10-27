"""
Generation prompts for natural language to ABC notation conversion
"""
from typing import Dict, List

class GenerationPrompts:
    """Collection of prompts for music generation"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for ABC notation generation"""
        return """You are an expert music notation specialist who converts natural language descriptions into ABC notation.

Your expertise includes:
- Classical and contemporary music notation
- ABC notation syntax and best practices
- Music theory and harmony
- Instrument-specific considerations
- Proper formatting and structure

IMPORTANT: Do NOT include a T: (title) field unless the user specifically mentions a title or name for the piece. Only include X:, M:, L:, and K: fields by default.

Always provide clean, valid ABC notation that follows standard conventions."""

    @staticmethod
    def get_few_shot_examples() -> List[Dict[str, str]]:
        """Get few-shot examples for better generation"""
        return [
            {
                "input": "Time signature 3/4, key F minor, eighth notes: A-flat, G, F",
                "output": """X:1
M:3/4
K:Fm
L:1/8
A2G2F2| A2G2F2| A2G2F2|"""
            },
            {
                "input": "Quarter notes: C D E F, half note: G",
                "output": """X:1
M:4/4
K:C
L:1/4
C D E F | G2 |"""
            },
            {
                "input": "Simple melody in C major: C C G G A A G F F E E D D C",
                "output": """X:1
M:4/4
K:C
L:1/4
C C G G | A A G2 | F F E E | D D C2 |"""
            },
            {
                "input": "Create a song called 'Jazz Progression' with chords: Cmaj7, Am7, Dm7, G7",
                "output": """X:1
T:Jazz Progression
M:4/4
K:C
L:1/4
"Cmaj7" C E G B | "Am7" A C E G | "Dm7" D F A C | "G7" G B D F |"""
            },
            {
                "input": "Waltz in 3/4 time, key of D major, quarter note quarter note half note pattern",
                "output": """X:1
M:3/4
K:D
L:1/4
D E F# | G A B | c2 B |"""
            }
        ]

    @staticmethod
    def get_generation_prompt(description: str, context: str = None) -> str:
        """Build the complete generation prompt"""
        system_prompt = GenerationPrompts.get_system_prompt()
        examples = GenerationPrompts.get_few_shot_examples()
        
        prompt = f"""{system_prompt}

ABC Notation Reference:
- X:1 (reference number - REQUIRED)
- T:Title (title - ONLY include if user specifies a title)
- M:4/4 (time signature: 2/4, 3/4, 4/4, 6/8, etc. - REQUIRED)
- L:1/4 (default note length - REQUIRED)
- K:C (key signature: C, G, D, A, E, B, F#, C#, F, Bb, Eb, Ab, Db, Gb, Cb - REQUIRED)
- Notes: C D E F G A B c d e f g a b (lowercase = higher octave)
- Durations: /2 (half), 2 (double), no modifier (default length)
- Bar lines: | (end of measure)
- Chords: "Cmaj7" (chord symbols in quotes)
- Rests: z (rest)

Examples:
"""
        
        # Add few-shot examples
        for i, example in enumerate(examples[:3]):  # Use first 3 examples
            prompt += f"""
Example {i+1}:
Input: {example['input']}
Output:
{example['output']}
"""
        
        prompt += f"""
Instructions:
1. Always include proper ABC header (X, M, L, K)
2. Only include T: (title) if the user specifically mentions a title or name for the piece
3. Use appropriate key signatures
4. Use proper note durations
5. Add bar lines for musical phrases
6. Keep it simple and clean
7. If unsure about key, use C major
8. If unsure about time signature, use 4/4
9. For chord progressions, use chord symbols in quotes
10. For melodies, use proper note names and durations

"""
        
        if context:
            prompt += f"Context: {context}\n"
        
        prompt += f"Now convert this description to ABC notation:\n{description}\n\nABC Notation:"
        
        return prompt

    @staticmethod
    def get_validation_prompt(abc_notation: str) -> str:
        """Get prompt for validating ABC notation"""
        return f"""Please validate this ABC notation and suggest improvements if needed:

{abc_notation}

Check for:
1. Proper header fields (X, T, M, L, K)
2. Valid time signatures
3. Valid key signatures
4. Proper note syntax
5. Musical logic and structure

Provide validation result and any suggestions for improvement."""

    @staticmethod
    def get_improvement_prompt(abc_notation: str, issues: List[str]) -> str:
        """Get prompt for improving ABC notation based on issues"""
        return f"""Please improve this ABC notation based on the identified issues:

{abc_notation}

Issues to fix:
{chr(10).join(f"- {issue}" for issue in issues)}

Provide the corrected ABC notation:"""

"""
Prompts for Conversational Sheet Music Editing
"""
from typing import Dict, List

class EditingPrompts:
    """Prompts for different types of music editing operations"""
    
    def __init__(self):
        self.system_prompts = {
            "key_change": self._get_key_change_system_prompt(),
            "tempo_change": self._get_tempo_change_system_prompt(),
            "add_notes": self._get_add_notes_system_prompt(),
            "remove_notes": self._get_remove_notes_system_prompt(),
            "add_repeat": self._get_add_repeat_system_prompt(),
            "add_chords": self._get_add_chords_system_prompt(),
            "group_notes": self._get_group_notes_system_prompt(),
            "note_duration": self._get_note_duration_system_prompt(),
            "general": self._get_general_edit_system_prompt()
        }
        
        self.examples = {
            "key_change": self._get_key_change_examples(),
            "tempo_change": self._get_tempo_change_examples(),
            "add_notes": self._get_add_notes_examples(),
            "remove_notes": self._get_remove_notes_examples(),
            "add_repeat": self._get_add_repeat_examples(),
            "add_chords": self._get_add_chords_examples(),
            "group_notes": self._get_group_notes_examples(),
            "note_duration": self._get_note_duration_examples(),
            "general": self._get_general_edit_examples()
        }
    
    def get_edit_system_prompt(self, edit_type: str) -> str:
        """Get system prompt for specific edit type"""
        return self.system_prompts.get(edit_type, self.system_prompts["general"])
    
    def get_edit_examples(self, edit_type: str) -> List[Dict]:
        """Get few-shot examples for specific edit type"""
        return self.examples.get(edit_type, self.examples["general"])
    
    def _get_general_edit_system_prompt(self) -> str:
        return """You are an expert music editor. Your task is to edit ABC notation based on natural language instructions.

IMPORTANT RULES:
1. Always preserve the original structure and format of the ABC notation
2. Only make the specific changes requested
3. Maintain proper ABC syntax and musical logic
4. Keep the same X: reference number unless specifically asked to change it
5. Preserve the original title unless asked to change it
6. Ensure all required fields (X:, T:, M:, K:) are present
7. Return ONLY the edited ABC notation, no explanations

When editing:
- Maintain the original meter (M:) unless specifically asked to change it
- Preserve the original key signature (K:) unless asked to change it
- Keep the same note length (L:) unless asked to change it
- Ensure proper bar line placement
- Maintain musical coherence and flow

Return the complete edited ABC notation."""
    
    def _get_key_change_system_prompt(self) -> str:
        return """You are an expert music editor specializing in key changes. Your task is to transpose ABC notation to a new key while maintaining the musical structure.

IMPORTANT RULES:
1. Transpose all notes by the correct interval to reach the target key
2. Update the K: field to reflect the new key signature
3. Preserve all other aspects of the music (rhythm, structure, etc.)
4. Maintain proper ABC syntax
5. Return ONLY the transposed ABC notation

Key transposition rules:
- C major to G major: transpose up a perfect 5th (7 semitones)
- C major to F major: transpose up a perfect 4th (5 semitones)
- Major to minor: adjust the 3rd, 6th, and 7th scale degrees
- Use proper ABC accidentals: ^ for sharp, _ for flat

Return the complete transposed ABC notation."""
    
    def _get_tempo_change_system_prompt(self) -> str:
        return """You are an expert music editor specializing in tempo changes. Your task is to modify the tempo of ABC notation while preserving the musical content.

IMPORTANT RULES:
1. Add or modify the Q: field for tempo indication
2. Preserve all notes and rhythms exactly as they are
3. Use standard tempo markings (e.g., Q:1/4=120 for 120 BPM)
4. Maintain proper ABC syntax
5. Return ONLY the modified ABC notation

Common tempo markings:
- Q:1/4=60 (very slow)
- Q:1/4=90 (moderate)
- Q:1/4=120 (allegro)
- Q:1/4=150 (presto)

Return the complete ABC notation with tempo indication."""
    
    def _get_add_notes_system_prompt(self) -> str:
        return """You are an expert music editor specializing in adding notes. Your task is to add specific notes or musical elements to existing ABC notation.

IMPORTANT RULES:
1. Add notes in the correct location within the melody
2. Maintain proper rhythm and timing
3. Use appropriate note lengths and durations
4. Preserve the existing musical structure
5. Ensure proper ABC syntax
6. Return ONLY the modified ABC notation

When adding notes:
- Use proper ABC note notation (A, B, C, D, E, F, G)
- Use appropriate octave indicators (c, d, e, f, g, a, b for higher octave)
- Use proper duration indicators (/, 2, 4, 8, etc.)
- Maintain proper bar line placement

Return the complete ABC notation with added notes."""
    
    def _get_remove_notes_system_prompt(self) -> str:
        return """You are an expert music editor specializing in removing notes. Your task is to remove specific notes from existing ABC notation while maintaining musical coherence.

IMPORTANT RULES:
1. Remove only the specified notes
2. Maintain proper rhythm and timing
3. Preserve the overall musical structure
4. Ensure proper ABC syntax
5. Return ONLY the modified ABC notation

When removing notes:
- Replace removed notes with rests (z) if needed
- Maintain proper bar line placement
- Preserve the meter and key signature
- Keep the musical flow natural

Return the complete ABC notation with notes removed."""
    
    def _get_add_repeat_system_prompt(self) -> str:
        return """You are an expert music editor specializing in adding repeats. Your task is to add repeat signs and structures to existing ABC notation.

IMPORTANT RULES:
1. Add appropriate repeat signs (|: and :|)
2. Maintain proper musical structure
3. Preserve all existing notes and rhythms
4. Ensure proper ABC syntax
5. Return ONLY the modified ABC notation

Common repeat patterns:
- |: ... :| for simple repeat
- |1 ... |2 for first and second endings
- |: ... |: for multiple repeats

Return the complete ABC notation with repeat signs."""
    
    def _get_add_chords_system_prompt(self) -> str:
        return """You are an expert music editor specializing in adding chord symbols. Your task is to add chord symbols above the melody in existing ABC notation.

IMPORTANT RULES:
1. Add chord symbols using "chord" notation (e.g., "Cmaj7"G)
2. Place chords above the appropriate notes
3. Use standard chord symbols (C, F, G, Am, Dm, etc.)
4. Maintain proper ABC syntax
5. Return ONLY the modified ABC notation

Chord notation format:
- "C"G for C major chord above G note
- "Am"E for A minor chord above E note
- "Fmaj7"F for F major 7th chord above F note

Return the complete ABC notation with chord symbols."""
    
    def _get_general_edit_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Make it more interesting by adding some eighth notes"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c | C2 D2 E2 F2 | G A B c2 |",
                "changes": ["Added eighth note variations"]
            },
            {
                "input": {
                    "current_abc": "X:1\nT:Basic Scale\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Add a repeat sign so it plays twice"
                },
                "output": "X:1\nT:Basic Scale\nM:4/4\nK:C\n|: C D E F | G A B c :|",
                "changes": ["Added repeat signs"]
            }
        ]
    
    def _get_key_change_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Change the key to G major"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:G\nG A B c | d e f g |",
                "changes": ["Transposed from C major to G major"]
            },
            {
                "input": {
                    "current_abc": "X:1\nT:Minor Melody\nM:4/4\nK:Am\nA B C D | E F G A |",
                    "instruction": "Change to F major"
                },
                "output": "X:1\nT:Minor Melody\nM:4/4\nK:F\nF G A _B | c d e f |",
                "changes": ["Transposed from A minor to F major"]
            }
        ]
    
    def _get_tempo_change_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Slow Song\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Make it faster, around 120 BPM"
                },
                "output": "X:1\nT:Slow Song\nM:4/4\nK:C\nQ:1/4=120\nC D E F | G A B c |",
                "changes": ["Added tempo marking Q:1/4=120"]
            }
        ]
    
    def _get_add_notes_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Add a high C at the end"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c c |",
                "changes": ["Added high C at the end"]
            }
        ]
    
    def _get_remove_notes_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Remove the last note"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B z |",
                "changes": ["Removed last note, replaced with rest"]
            }
        ]
    
    def _get_add_repeat_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Add repeat signs so it plays twice"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:C\n|: C D E F | G A B c :|",
                "changes": ["Added repeat signs for two times through"]
            }
        ]
    
    def _get_add_chords_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Add C major and G major chords"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:C\n\"C\"C D E F | \"G\"G A B c |",
                "changes": ["Added C major and G major chord symbols"]
            }
        ]
    
    def _get_group_notes_system_prompt(self) -> str:
        return """You are an expert music editor specializing in note grouping and beaming. Your task is to group notes together to create beamed eighth notes or other grouped rhythms.

IMPORTANT RULES:
1. Group notes by placing them together without spaces between them
2. Use proper ABC beaming syntax for eighth notes and smaller values
3. Maintain the same note values and pitches
4. Preserve the overall rhythm and timing
5. Ensure proper ABC syntax
6. Return ONLY the modified ABC notation

ABC beaming rules:
- Eighth notes: group as CDEF (no spaces between notes, NO numbers underneath)
- Sixteenth notes: group as CDEF (no spaces, NO numbers underneath)
- Quarter notes and longer: keep separate with spaces
- DO NOT add numbers like (4CDEF) - that's for tuplets, not regular beaming
- Regular eighth note beaming is just: CDEF

Examples of CORRECT grouping:
- "C D E F" becomes "CDEF" for beamed eighth notes (NOT (4CDEF))
- "G A B c" becomes "GABc" for beamed eighth notes (NOT (4GABc))
- "C2 D2" becomes "C2D2" for beamed quarter notes

Examples of INCORRECT grouping:
- (4CDEF) - This is for tuplets, not regular eighth notes
- CDEF4 - This is wrong syntax

Return the complete ABC notation with properly grouped notes."""
    
    def _get_note_duration_system_prompt(self) -> str:
        return """You are an expert music editor specializing in note duration changes. Your task is to modify note durations while maintaining musical coherence.

IMPORTANT RULES:
1. Understand note duration relationships:
   - Whole note = 4 quarter notes
   - Half note = 2 quarter notes  
   - Quarter note = 1 quarter note
   - Eighth note = 1/2 quarter note
   - Sixteenth note = 1/4 quarter note
2. Use proper ABC duration notation:
   - Whole note: C4
   - Half note: C2
   - Quarter note: C (or C/1)
   - Eighth note: C/2
   - Sixteenth note: C/4
3. Maintain proper rhythm and timing
4. Preserve the overall musical structure
5. Ensure proper ABC syntax
6. Return ONLY the modified ABC notation

Duration conversion examples:
- "Turn C into a half note" → C becomes C2
- "Make D a quarter note" → D becomes D (or D/1)
- "Change E to eighth note" → E becomes E/2
- "Convert F to whole note" → F becomes F4

Return the complete ABC notation with modified note durations."""
    
    def _get_group_notes_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Group notes 567 and eight together"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC DEF | GABc |",
                "changes": ["Grouped notes DEF and ABc to create beamed eighth notes"]
            },
            {
                "input": {
                    "current_abc": "X:1\nT:Scale\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Group the first four notes together"
                },
                "output": "X:1\nT:Scale\nM:4/4\nK:C\nCDEF | G A B c |",
                "changes": ["Grouped first four notes CDEF to create beamed eighth notes"]
            },
            {
                "input": {
                    "current_abc": "X:1\nT:Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Beam the eighth notes together"
                },
                "output": "X:1\nT:Melody\nM:4/4\nK:C\nCDEF | GABc |",
                "changes": ["Beamed eighth notes CDEF and GABc together"]
            }
        ]
    
    def _get_note_duration_examples(self) -> List[Dict]:
        return [
            {
                "input": {
                    "current_abc": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Turn the first note into a half note"
                },
                "output": "X:1\nT:Simple Melody\nM:4/4\nK:C\nC2 D E F | G A B c |",
                "changes": ["Changed first note C to half note C2"]
            },
            {
                "input": {
                    "current_abc": "X:1\nT:Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Make the last note a whole note"
                },
                "output": "X:1\nT:Melody\nM:4/4\nK:C\nC D E F | G A B c4 |",
                "changes": ["Changed last note c to whole note c4"]
            },
            {
                "input": {
                    "current_abc": "X:1\nT:Quick Melody\nM:4/4\nK:C\nC D E F | G A B c |",
                    "instruction": "Turn the middle notes into eighth notes"
                },
                "output": "X:1\nT:Quick Melody\nM:4/4\nK:C\nC D/2 E/2 F | G A/2 B/2 c |",
                "changes": ["Changed middle notes to eighth notes"]
            }
        ]

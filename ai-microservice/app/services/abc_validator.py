"""
ABC Notation Validator Service
"""
import re
from typing import Dict, List, Tuple, Optional

class ABCValidator:
    """Service for validating ABC notation syntax and musical logic"""
    
    def __init__(self):
        self.valid_time_signatures = [
            "2/2", "2/4", "3/4", "4/4", "6/8", "9/8", "12/8",
            "2/8", "3/8", "4/8", "6/4", "9/4", "12/4"
        ]
        
        self.valid_keys = [
            "C", "G", "D", "A", "E", "B", "F#", "C#",
            "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb",
            "Am", "Em", "Bm", "F#m", "C#m", "G#m", "D#m", "A#m",
            "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm", "Abm"
        ]
    
    def validate(self, abc_notation: str) -> Dict:
        """
        Validate ABC notation for syntax and musical logic
        
        Args:
            abc_notation: ABC notation string to validate
            
        Returns:
            Dict with validation results
        """
        try:
            errors = []
            warnings = []
            
            # Basic syntax validation
            syntax_errors = self._validate_syntax(abc_notation)
            errors.extend(syntax_errors)
            
            # Musical logic validation
            if not syntax_errors:  # Only do musical validation if syntax is OK
                music_errors, music_warnings = self._validate_musical_logic(abc_notation)
                errors.extend(music_errors)
                warnings.extend(music_warnings)
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "abc_notation": abc_notation
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "abc_notation": abc_notation
            }
    
    def _validate_syntax(self, abc_notation: str) -> List[str]:
        """Validate basic ABC syntax"""
        errors = []
        lines = abc_notation.strip().split('\n')
        
        # Check for required header fields
        has_x = any(line.startswith('X:') for line in lines)
        has_t = any(line.startswith('T:') for line in lines)
        has_m = any(line.startswith('M:') for line in lines)
        has_k = any(line.startswith('K:') for line in lines)
        
        if not has_x:
            errors.append("Missing required X: field (reference number)")
        if not has_t:
            errors.append("Missing required T: field (title)")
        if not has_m:
            errors.append("Missing required M: field (time signature)")
        if not has_k:
            errors.append("Missing required K: field (key signature)")
        
        # Validate header field formats
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('X:'):
                if not re.match(r'^X:\s*\d+$', line):
                    errors.append(f"Line {i+1}: Invalid X: format (should be 'X:1')")
            
            elif line.startswith('T:'):
                if len(line) < 3:
                    errors.append(f"Line {i+1}: Title cannot be empty")
            
            elif line.startswith('M:'):
                time_sig = line[2:].strip()
                if time_sig not in self.valid_time_signatures:
                    errors.append(f"Line {i+1}: Invalid time signature '{time_sig}'")
            
            elif line.startswith('L:'):
                if not re.match(r'^L:\s*\d+/\d+$', line):
                    errors.append(f"Line {i+1}: Invalid L: format (should be 'L:1/4')")
            
            elif line.startswith('K:'):
                key = line[2:].strip()
                if key not in self.valid_keys:
                    errors.append(f"Line {i+1}: Invalid key signature '{key}'")
        
        return errors
    
    def _validate_musical_logic(self, abc_notation: str) -> Tuple[List[str], List[str]]:
        """Validate musical logic and structure"""
        errors = []
        warnings = []
        lines = abc_notation.strip().split('\n')
        
        # Find the music line (after header)
        music_start = -1
        for i, line in enumerate(lines):
            if line.startswith('K:'):
                music_start = i + 1
                break
        
        if music_start == -1:
            errors.append("No key signature found")
            return errors, warnings
        
        # Extract music content
        music_lines = lines[music_start:]
        music_content = ' '.join(music_lines)
        
        # Validate note syntax
        note_errors = self._validate_notes(music_content)
        errors.extend(note_errors)
        
        # Validate bar structure
        bar_warnings = self._validate_bars(music_content)
        warnings.extend(bar_warnings)
        
        return errors, warnings
    
    def _validate_notes(self, music_content: str) -> List[str]:
        """Validate note syntax"""
        errors = []
        
        # Remove comments and extra whitespace
        music_content = re.sub(r'%.*', '', music_content)  # Remove comments
        music_content = re.sub(r'\s+', ' ', music_content)  # Normalize whitespace
        
        # Split into individual elements
        elements = music_content.split()
        
        for element in elements:
            if not element:
                continue
                
            # Skip bar lines and other non-note elements
            if element in ['|', '||', '[|', '|]', '|:', ':|']:
                continue
            
            # Check for valid note patterns
            if not self._is_valid_note_element(element):
                errors.append(f"Invalid note element: '{element}'")
        
        return errors
    
    def _is_valid_note_element(self, element: str) -> bool:
        """Check if an element is a valid note or rest"""
        # Valid note patterns
        note_patterns = [
            r'^[A-Ga-g][#b]?[0-9]*$',  # Basic notes with accidentals and octaves
            r'^[A-Ga-g][#b]?/[0-9]+$',  # Notes with duration
            r'^[A-Ga-g][#b]?[0-9]*/[0-9]+$',  # Notes with octave and duration
            r'^z[0-9]*$',  # Rests
            r'^z/[0-9]+$',  # Rests with duration
            r'^\([A-Ga-g][#b]?[0-9]*\)$',  # Tied notes
            r'^\[[A-Ga-g][#b]?[0-9]*\]$',  # Chord notes
        ]
        
        for pattern in note_patterns:
            if re.match(pattern, element):
                return True
        
        return False
    
    def _validate_bars(self, music_content: str) -> List[str]:
        """Validate bar structure"""
        warnings = []
        
        # Count bar lines
        bar_count = music_content.count('|')
        
        if bar_count == 0:
            warnings.append("No bar lines found - consider adding | for musical phrases")
        elif bar_count < 2:
            warnings.append("Very few bar lines - consider adding more for better structure")
        
        # Check for balanced repeats
        open_repeats = music_content.count('|:')
        close_repeats = music_content.count(':|')
        
        if open_repeats != close_repeats:
            warnings.append(f"Unbalanced repeat signs: {open_repeats} open, {close_repeats} close")
        
        return warnings
    
    def get_suggestions(self, abc_notation: str) -> List[str]:
        """Get suggestions for improving ABC notation"""
        suggestions = []
        
        # Check for common improvements
        if 'X:1' not in abc_notation:
            suggestions.append("Add X:1 field for reference number")
        
        if 'T:' not in abc_notation:
            suggestions.append("Add T: field for title")
        
        if 'M:4/4' not in abc_notation and 'M:' not in abc_notation:
            suggestions.append("Add M:4/4 for time signature")
        
        if 'K:C' not in abc_notation and 'K:' not in abc_notation:
            suggestions.append("Add K:C for key signature")
        
        # Check for note density
        music_lines = [line for line in abc_notation.split('\n') if not line.startswith(('X:', 'T:', 'M:', 'L:', 'K:'))]
        if music_lines:
            music_content = ' '.join(music_lines)
            note_count = len([elem for elem in music_content.split() if self._is_valid_note_element(elem)])
            if note_count < 4:
                suggestions.append("Consider adding more notes for a complete musical phrase")
        
        return suggestions

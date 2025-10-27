"""
Simple ABC Validator Service (MVP version)
"""
import re
from typing import Dict, List

class ABCValidator:
    """Simple service for validating ABC notation (MVP version)"""
    
    def __init__(self):
        pass
    
    def validate(self, abc_notation: str) -> Dict:
        """
        Validate ABC notation syntax and musical logic
        
        Args:
            abc_notation: ABC notation string to validate
            
        Returns:
            Dict with validation results
        """
        try:
            errors = []
            warnings = []
            
            # Basic syntax validation
            if not abc_notation.strip():
                errors.append("Empty ABC notation")
                return {
                    "is_valid": False,
                    "errors": errors,
                    "warnings": warnings,
                    "confidence": 0.0
                }
            
            # Check for required fields
            required_fields = {
                'X:': 'Reference number',
                'T:': 'Title',
                'M:': 'Meter (time signature)',
                'K:': 'Key signature'
            }
            
            for field, description in required_fields.items():
                if field not in abc_notation:
                    errors.append(f"Missing required field: {description} ({field})")
            
            # Check for basic ABC note syntax
            note_pattern = r'[A-Ga-g][#b]?[0-9]*[/]?[0-9]*'
            notes_found = re.findall(note_pattern, abc_notation)
            
            if not notes_found:
                warnings.append("No musical notes found in ABC notation")
            
            # Check for common syntax issues
            if '||' in abc_notation and '|' not in abc_notation:
                warnings.append("Double bar line found without single bar lines")
            
            # Basic musical logic validation
            lines = abc_notation.split('\n')
            melody_lines = [line for line in lines if line.strip() and not line.startswith(('X:', 'T:', 'M:', 'L:', 'K:', 'C:', 'Q:', 'N:', 'Z:'))]
            
            if melody_lines:
                melody_content = ' '.join(melody_lines)
                if len(melody_content.strip()) < 10:
                    warnings.append("Melody line seems very short")
            
            is_valid = len(errors) == 0
            confidence = 0.9 if is_valid and len(warnings) == 0 else 0.7 if is_valid else 0.3
            
            return {
                "is_valid": is_valid,
                "errors": errors,
                "warnings": warnings,
                "confidence": confidence
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "confidence": 0.0
            }

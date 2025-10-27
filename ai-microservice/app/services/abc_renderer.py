"""
ABC Notation Renderer Service
"""
import os
import uuid
import subprocess
import tempfile
from typing import Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import io

class ABCRenderer:
    """Service for converting ABC notation to visual sheet music"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.output_dir = os.path.join(self.temp_dir, "abc_renderer")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def render_to_image(self, abc_notation: str, title: str = "Generated Music") -> Dict:
        """
        Render ABC notation to PNG image
        
        Args:
            abc_notation: ABC notation string
            title: Title for the image
            
        Returns:
            Dict with image_path, image_url, and metadata
        """
        try:
            # Generate unique filename
            music_id = str(uuid.uuid4())
            abc_file = os.path.join(self.output_dir, f"{music_id}.abc")
            png_file = os.path.join(self.output_dir, f"{music_id}.png")
            
            # Write ABC notation to file
            with open(abc_file, 'w', encoding='utf-8') as f:
                f.write(abc_notation)
            
            # Try to use abcjs via Node.js if available, otherwise create simple visualization
            if self._has_abcjs():
                success = self._render_with_abcjs(abc_file, png_file)
            else:
                success = self._render_simple_visualization(abc_notation, png_file, title)
            
            if success and os.path.exists(png_file):
                return {
                    "success": True,
                    "image_path": png_file,
                    "image_url": f"/static/images/{music_id}.png",  # For serving via web
                    "music_id": music_id,
                    "title": title
                }
            else:
                # Fallback to simple text-based visualization
                return self._create_text_visualization(abc_notation, title)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": None,
                "image_url": None
            }
    
    def _has_abcjs(self) -> bool:
        """Check if abcjs is available via Node.js"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Try to check if abcjs is available
                result = subprocess.run(['node', '-e', 'require("abcjs")'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
        except:
            pass
        return False
    
    def _render_with_abcjs(self, abc_file: str, png_file: str) -> bool:
        """Render using abcjs via Node.js"""
        try:
            # Create a simple Node.js script to render ABC
            script_content = f"""
const abcjs = require('abcjs');
const fs = require('fs');

// Read ABC file
const abc = fs.readFileSync('{abc_file}', 'utf8');

// Render to SVG
const svg = abcjs.renderAbc('output', abc, {{
    responsive: 'resize',
    viewportHorizontal: true,
    scale: 1.5
}});

// For now, we'll create a simple text representation
// In a full implementation, you'd convert SVG to PNG
console.log('ABC rendered successfully');
"""
            
            script_file = os.path.join(self.temp_dir, f"render_{uuid.uuid4()}.js")
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            result = subprocess.run(['node', script_file], 
                                  capture_output=True, text=True, timeout=10)
            
            # Clean up
            os.remove(script_file)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"ABCjs rendering failed: {e}")
            return False
    
    def _render_simple_visualization(self, abc_notation: str, png_file: str, title: str) -> bool:
        """Create a simple text-based visualization of ABC notation"""
        try:
            # Create a simple image with the ABC notation
            img_width = 800
            img_height = 600
            
            # Create image with white background
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a font, fallback to default
            try:
                font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
                font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
            except:
                try:
                    font_large = ImageFont.truetype("arial.ttf", 24)
                    font_medium = ImageFont.truetype("arial.ttf", 18)
                    font_small = ImageFont.truetype("arial.ttf", 14)
                except:
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                    font_small = ImageFont.load_default()
            
            # Draw title
            draw.text((50, 30), title, fill='black', font=font_large)
            
            # Draw ABC notation
            y_pos = 80
            lines = abc_notation.split('\n')
            
            for line in lines:
                if line.strip():
                    # Color code different parts
                    if line.startswith('X:') or line.startswith('T:'):
                        color = 'blue'
                        font = font_medium
                    elif line.startswith('M:') or line.startswith('K:') or line.startswith('L:'):
                        color = 'green'
                        font = font_medium
                    else:
                        color = 'black'
                        font = font_small
                    
                    draw.text((50, y_pos), line, fill=color, font=font)
                    y_pos += 25
            
            # Add a simple staff representation
            staff_y = y_pos + 20
            for i in range(5):
                draw.line([(50, staff_y + i * 15), (750, staff_y + i * 15)], fill='black', width=2)
            
            # Add some note representations
            note_x = 100
            note_y = staff_y + 30
            for i in range(8):
                draw.ellipse([note_x + i * 80 - 10, note_y - 5, note_x + i * 80 + 10, note_y + 5], 
                           fill='black')
                draw.line([note_x + i * 80 + 10, note_y, note_x + i * 80 + 10, note_y - 30], 
                         fill='black', width=2)
            
            # Save image
            img.save(png_file, 'PNG')
            return True
            
        except Exception as e:
            print(f"Simple visualization failed: {e}")
            return False
    
    def _create_text_visualization(self, abc_notation: str, title: str) -> Dict:
        """Create a text-based visualization as fallback"""
        try:
            # Create a simple text representation
            lines = abc_notation.split('\n')
            formatted_lines = []
            
            for line in lines:
                if line.strip():
                    if line.startswith(('X:', 'T:', 'M:', 'K:', 'L:')):
                        formatted_lines.append(f"📝 {line}")
                    else:
                        formatted_lines.append(f"🎵 {line}")
            
            # Create a simple text file
            music_id = str(uuid.uuid4())
            text_file = os.path.join(self.output_dir, f"{music_id}.txt")
            
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"🎼 {title}\n")
                f.write("=" * 50 + "\n\n")
                f.write('\n'.join(formatted_lines))
                f.write("\n\n" + "=" * 50)
                f.write("\nGenerated by AI Music Assistant")
            
            return {
                "success": True,
                "image_path": text_file,
                "image_url": f"/static/text/{music_id}.txt",
                "music_id": music_id,
                "title": title,
                "format": "text"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": None,
                "image_url": None
            }
    
    def render_to_midi(self, abc_notation: str) -> Optional[str]:
        """
        Convert ABC notation to MIDI file
        
        Args:
            abc_notation: ABC notation string
            
        Returns:
            Path to MIDI file or None if failed
        """
        try:
            music_id = str(uuid.uuid4())
            abc_file = os.path.join(self.output_dir, f"{music_id}.abc")
            midi_file = os.path.join(self.output_dir, f"{music_id}.mid")
            
            # Write ABC notation to file
            with open(abc_file, 'w', encoding='utf-8') as f:
                f.write(abc_notation)
            
            # Try to use abc2midi if available
            try:
                result = subprocess.run(['abc2midi', abc_file, '-o', midi_file], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and os.path.exists(midi_file):
                    return midi_file
            except FileNotFoundError:
                pass  # abc2midi not available
            
            return None
            
        except Exception as e:
            print(f"MIDI conversion failed: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old generated files"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        
        except Exception as e:
            print(f"Cleanup failed: {e}")

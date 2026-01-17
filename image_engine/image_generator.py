"""
Simple Image Generator for Roastify Bot
Termux Compatible - No font issues
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple
from pathlib import Path
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager

class SimpleImageGenerator:
    """সিম্পল ইমেজ জেনারেটর - কোনো ফন্ট সমস্যা নেই"""
    
    def __init__(self):
        self.assets_path = Path(Config.ASSETS_PATH)
        self.fonts_path = Path(Config.FONTS_PATH)
        self.fonts_path.mkdir(parents=True, exist_ok=True)
        
        # Default font (always available)
        self.default_font = None
        self._setup_default_font()
        
        logger.info("SimpleImageGenerator initialized")
    
    def _setup_default_font(self):
        """ডিফল্ট ফন্ট সেটআপ করে"""
        try:
            # Try to load any available font
            font_paths = [
                "/system/fonts/Roboto-Regular.ttf",
                "/system/fonts/DroidSans.ttf",
                "/system/fonts/NotoSansBengali-Regular.ttf",
                str(self.fonts_path / "arial.ttf"),
                str(self.fonts_path / "default.ttf"),
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.default_font = ImageFont.truetype(font_path, 40)
                    logger.info(f"Using font: {font_path}")
                    return
            
            # Ultimate fallback
            self.default_font = ImageFont.load_default()
            logger.info("Using default font")
            
        except Exception as e:
            logger.error(f"Font setup error: {e}")
            self.default_font = ImageFont.load_default()
    
    def create_roast_image(self, primary_text: str, secondary_text: str, 
                          user_id: int) -> Image.Image:
        """রোস্ট ইমেজ তৈরি করে - খুব সহজ"""
        try:
            # Create simple background
            width = Config.IMAGE_WIDTH
            height = Config.IMAGE_HEIGHT
            
            image = self._create_simple_background(width, height)
            draw = ImageDraw.Draw(image)
            
            # Add text
            image = self._add_simple_text(image, draw, primary_text, secondary_text)
            
            # Add border
            draw.rectangle([(5, 5), (width-5, height-5)], 
                          outline=(100, 100, 100), 
                          width=3)
            
            return image
            
        except Exception as e:
            logger.error(f"Error in create_roast_image: {e}")
            return self._create_error_image()
    
    def _create_simple_background(self, width: int, height: int) -> Image.Image:
        """সিম্পল ব্যাকগ্রাউন্ড তৈরি করে"""
        # Create gradient based on time
        is_day = TimeManager.is_day_time()
        
        if is_day:
            # Day theme
            colors = [
                (135, 206, 235),  # Light blue
                (176, 224, 230),  # Powder blue
                (240, 248, 255)   # Alice blue
            ]
        else:
            # Night theme
            colors = [
                (25, 25, 35),     # Dark blue
                (40, 40, 50),     # Darker blue
                (60, 60, 70)      # Dark gray
            ]
        
        # Create gradient
        image = Image.new('RGB', (width, height))
        for y in range(height):
            ratio = y / height
            color_idx = int(ratio * (len(colors) - 1))
            next_idx = min(color_idx + 1, len(colors) - 1)
            
            r1, g1, b1 = colors[color_idx]
            r2, g2, b2 = colors[next_idx]
            
            r = int(r1 + (r2 - r1) * (ratio * len(colors) - color_idx))
            g = int(g1 + (g2 - g1) * (ratio * len(colors) - color_idx))
            b = int(b1 + (b2 - b1) * (ratio * len(colors) - color_idx))
            
            for x in range(width):
                image.putpixel((x, y), (r, g, b))
        
        return image
    
    def _add_simple_text(self, image: Image.Image, draw: ImageDraw.Draw,
                        primary_text: str, secondary_text: str) -> Image.Image:
        """সিম্পল টেক্সট যোগ করে"""
        width, height = image.size
        
        # Prepare text
        primary_lines = self._wrap_text(primary_text, 25)
        secondary_lines = self._wrap_text(secondary_text, 35)
        
        # Calculate positions
        primary_height = len(primary_lines) * 50
        secondary_height = len(secondary_lines) * 30
        
        total_height = primary_height + secondary_height + 40
        start_y = (height - total_height) // 2
        
        # Draw primary text
        font_large = self._get_font(48)
        for i, line in enumerate(primary_lines):
            text_width = self._get_text_width(line, font_large)
            x = (width - text_width) // 2
            y = start_y + (i * 50)
            
            # Shadow
            draw.text((x+2, y+2), line, font=font_large, fill=(0, 0, 0, 128))
            # Main text
            draw.text((x, y), line, font=font_large, fill=(255, 255, 255))
        
        # Draw secondary text
        font_small = self._get_font(24)
        text_y = start_y + primary_height + 20
        
        for i, line in enumerate(secondary_lines):
            text_width = self._get_text_width(line, font_small)
            x = (width - text_width) // 2
            y = text_y + (i * 30)
            draw.text((x, y), line, font=font_small, fill=(200, 200, 200))
        
        return image
    
    def _get_font(self, size: int):
        """ফন্ট পায়"""
        try:
            if self.default_font:
                # Try to scale default font
                return ImageFont.truetype(self.default_font.path, size)
        except:
            pass
        
        # Fallback to default
        return ImageFont.load_default()
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """টেক্সট লাইনে ভাগ করে"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _get_text_width(self, text: str, font) -> int:
        """টেক্সট প্রস্থ বের করে"""
        try:
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(text)
                return bbox[2] - bbox[0] if bbox else len(text) * 10
            elif hasattr(font, 'getsize'):
                return font.getsize(text)[0]
            else:
                return len(text) * 10
        except:
            return len(text) * 10
    
    def _create_error_image(self) -> Image.Image:
        """এরর ইমেজ তৈরি করে"""
        image = Image.new('RGB', (400, 200), (255, 200, 200))
        draw = ImageDraw.Draw(image)
        
        # Simple text without font issues
        text = "রোস্ট তৈরি হচ্ছে..."
        draw.text((100, 80), text, fill=(255, 0, 0))
        
        return image
    
    def save_image(self, image: Image.Image) -> str:
        """ইমেজ সেভ করে"""
        try:
            timestamp = TimeManager.get_current_time().strftime("%Y%m%d_%H%M%S")
            filename = f"roast_{timestamp}.png"
            
            output_dir = Path("generated")
            output_dir.mkdir(exist_ok=True)
            
            output_path = output_dir / filename
            image.save(output_path, "PNG", optimize=True)
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            # Save to temp file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, "PNG")
            return temp_file.name

# Global instance
image_generator = SimpleImageGenerator()

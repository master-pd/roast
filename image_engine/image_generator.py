"""
Image Generator for Roastify Bot - Termux Compatible
Fixed for Pillow and Android/Termux issues
"""

import os
import random
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging
from config import Config
from utils.logger import logger
from utils.helpers import Helpers
from utils.time_manager import TimeManager
from image_engine.templates import TemplateManager

class ImageGenerator:
    """ইমেজ জেনারেটর ক্লাস - Termux/Android compatible"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.assets_path = Path(Config.ASSETS_PATH)
        self.fonts_path = Path(Config.FONTS_PATH)
        self.backgrounds_path = Path(Config.BACKGROUNDS_PATH)
        
        # Ensure directories exist
        self.fonts_path.mkdir(parents=True, exist_ok=True)
        self.backgrounds_path.mkdir(parents=True, exist_ok=True)
        
        # Default font cache
        self.default_font = None
        self.font_cache = {}
        
        logger.info("ImageGenerator initialized (Termux compatible)")
    
    def create_roast_image(self, primary_text: str, secondary_text: str, 
                          user_id: int, user_photo_path: str = None) -> Image.Image:
        """রোস্ট ইমেজ তৈরি করে - Termux compatible"""
        try:
            # Get template
            template = self.template_manager.get_template(user_id)
            
            # Create base image
            image = self._create_base_image(template)
            
            # Add user photo if provided and exists
            if user_photo_path and os.path.exists(user_photo_path):
                try:
                    image = self._add_user_photo(image, user_photo_path, template)
                except Exception as e:
                    logger.warning(f"Could not add user photo: {e}")
            
            # Prepare text
            draw = ImageDraw.Draw(image)
            
            # Load fonts with fallback
            primary_font = self._load_font_safe(
                template.get("font", "arial.ttf"),
                template.get("font_size", 50)  # Reduced for Termux
            )
            
            secondary_font = self._load_font_safe(
                template.get("font", "arial.ttf"),
                template.get("sub_font_size", 25)  # Reduced for Termux
            )
            
            # Get positions
            primary_pos = template.get("position", {"x": 540, "y": 400})
            secondary_pos = template.get("sub_position", {"x": 540, "y": 480})
            
            # Split text for display
            primary_lines = Helpers.split_text_for_image(primary_text, 20)  # Reduced chars
            secondary_lines = Helpers.split_text_for_image(secondary_text, 25)
            
            # Draw primary text
            primary_color = tuple(template.get("primary_color", (255, 255, 255)))
            self._draw_text_safe(
                draw, primary_lines, primary_font, 
                primary_pos, primary_color, "primary"
            )
            
            # Draw secondary text
            secondary_color = tuple(template.get("secondary_color", (200, 200, 200)))
            self._draw_text_safe(
                draw, secondary_lines, secondary_font,
                secondary_pos, secondary_color, "secondary"
            )
            
            # Add simple decorative elements
            image = self._add_simple_decoration(image)
            
            return image
            
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            return self._create_error_image_safe()
    
    def _create_base_image(self, template: Dict) -> Image.Image:
        """বেস ইমেজ তৈরি করে - Simple for Termux"""
        # Use simpler method for Termux
        width = min(Config.IMAGE_WIDTH, 720)  # Max 720 for Termux
        height = min(Config.IMAGE_HEIGHT, 720)
        
        # Try to load background if exists
        if "background" in template:
            bg_path = self.backgrounds_path / template["background"]
            if bg_path.exists():
                try:
                    image = Image.open(bg_path).convert("RGBA")
                    return image.resize((width, height))
                except:
                    pass
        
        # Create gradient background
        return self._create_simple_gradient(width, height)
    
    def _create_simple_gradient(self, width: int, height: int) -> Image.Image:
        """সিম্পল গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড তৈরি করে"""
        image = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Time-based colors
        theme = Helpers.get_time_based_theme()
        
        if theme["theme"] == "day":
            # Light gradient
            for y in range(height):
                ratio = y / height
                r = int(135 + (120 * ratio))
                g = int(206 + (49 * ratio))
                b = int(235 + (20 * ratio))
                draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        else:
            # Dark gradient
            for y in range(height):
                ratio = y / height
                r = int(25 + (25 * ratio))
                g = int(25 + (25 * ratio))
                b = int(35 + (35 * ratio))
                draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
        return image
    
    def _load_font_safe(self, font_name: str, size: int):
        """সেফ ফন্ট লোড করে - Termux compatible"""
        cache_key = f"{font_name}_{size}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            from PIL import ImageFont
            
            # Check Android/Termux font paths
            font_paths = [
                # Android system fonts
                "/system/fonts/Roboto-Regular.ttf",
                "/system/fonts/DroidSans.ttf",
                "/system/fonts/NotoSansBengali-Regular.ttf",
                "/system/fonts/NotoSans-Regular.ttf",
                
                # Termux fonts
                "/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/data/data/com.termux/files/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                
                # Local assets
                str(self.fonts_path / font_name),
                str(self.fonts_path / "arial.ttf"),
                str(self.fonts_path / "default.ttf"),
                
                # Fallback to font name
                font_name,
            ]
            
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, size)
                        self.font_cache[cache_key] = font
                        return font
                except Exception as e:
                    continue
            
            # Ultimate fallback - default font
            logger.warning(f"Font {font_name} not found, using default")
            font = ImageFont.load_default()
            
            # Try to scale default font
            try:
                # For default font, we need to handle differently
                font = ImageFont.load_default()
            except:
                # Create a dummy font
                font = ImageFont.load_default()
            
            self.font_cache[cache_key] = font
            return font
            
        except Exception as e:
            logger.error(f"Font loading error: {e}")
            return ImageFont.load_default()
    
    def _draw_text_safe(self, draw: ImageDraw.Draw, lines: List[str], font, 
                       position: Dict, color: Tuple, text_type: str):
        """সেফ টেক্সট ড্র করে - Termux compatible"""
        try:
            # Calculate text dimensions using textbbox (Pillow 8.0+)
            if hasattr(font, 'getbbox'):
                # New method
                bbox = font.getbbox(lines[0] if lines else "Test")
                font_height = bbox[3] - bbox[1] if bbox else 20
            elif hasattr(font, 'getsiz'):
                # Old method
                try:
                    font_height = font.getsize(lines[0] if lines else "Test")[1]
                except:
                    font_height = 20
            else:
                font_height = 20
            
            line_height = font_height + 5
            total_height = len(lines) * line_height
            start_y = position["y"] - (total_height // 2)
            
            for i, line in enumerate(lines):
                y_pos = start_y + (i * line_height)
                
                # Calculate text width
                try:
                    if hasattr(font, 'getlength'):
                        text_width = font.getlength(line)
                    elif hasattr(font, 'getsize'):
                        text_width = font.getsize(line)[0]
                    else:
                        text_width = len(line) * 10  # Approximate
                except:
                    text_width = len(line) * 10
                
                x_pos = position["x"] - (text_width // 2)
                
                # Draw text with simple shadow for primary text
                if text_type == "primary":
                    # Simple shadow
                    shadow_color = (0, 0, 0, 150)
                    draw.text((x_pos + 2, y_pos + 2), line, font=font, fill=shadow_color)
                
                # Draw main text
                draw.text((x_pos, y_pos), line, font=font, fill=color)
                
        except Exception as e:
            logger.error(f"Error drawing text: {e}")
            # Fallback: draw at center
            try:
                draw.text((position["x"], position["y"]), 
                         " ".join(lines), 
                         font=font, 
                         fill=color,
                         anchor="mm")
            except:
                # Last resort
                draw.text((10, 10), " ".join(lines), font=font, fill=color)
    
    def _add_user_photo(self, image: Image.Image, photo_path: str, template: Dict) -> Image.Image:
        """ইউজার ফটো যোগ করে - Simple version"""
        try:
            # Load user image
            user_img = Image.open(photo_path).convert("RGBA")
            
            # Resize
            size = 150  # Smaller for Termux
            user_img = user_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Simple circular crop
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (size, size)], fill=255)
            
            result = Image.new('RGBA', (size, size))
            result.paste(user_img, (0, 0), mask)
            user_img = result
            
            # Position
            x = (image.width - size) // 2
            y = 50
            
            # Paste onto image
            image.paste(user_img, (x, y), user_img)
            
            return image
            
        except Exception as e:
            logger.warning(f"Could not add user photo: {e}")
            return image
    
    def _add_simple_decoration(self, image: Image.Image) -> Image.Image:
        """সিম্পল ডেকোরেশন যোগ করে"""
        try:
            draw = ImageDraw.Draw(image)
            width, height = image.size
            
            # Simple border
            border_color = (100, 100, 100, 200)
            draw.rectangle([(5, 5), (width-5, height-5)], 
                          outline=border_color, 
                          width=2)
            
            # Simple corners
            corner_size = 20
            corners = [
                (5, 5), (width-corner_size-5, 5),
                (5, height-corner_size-5), (width-corner_size-5, height-corner_size-5)
            ]
            
            for x, y in corners:
                draw.rectangle([(x, y), (x+corner_size, y+corner_size)], 
                              outline=border_color, 
                              width=1)
            
            return image
        except:
            return image
    
    def _create_error_image_safe(self) -> Image.Image:
        """এরর ইমেজ তৈরি করে - Termux compatible"""
        try:
            width = 400
            height = 200
            image = Image.new('RGBA', (width, height), (255, 200, 200, 255))
            draw = ImageDraw.Draw(image)
            
            font = self._load_font_safe("arial.ttf", 24)
            text = "ইমেজ তৈরি সমস্যা"
            
            # Simple text at center
            draw.text((width//2, height//2), 
                     text, 
                     font=font, 
                     fill=(255, 0, 0, 255),
                     anchor="mm")
            
            return image
        except:
            # Ultimate fallback
            return Image.new('RGBA', (400, 200), (255, 255, 255, 255))
    
    def save_image(self, image: Image.Image, filename: str = None) -> str:
        """ইমেজ ফাইল হিসেবে সেভ করে - Termux compatible"""
        try:
            if filename is None:
                timestamp = TimeManager.get_current_time().strftime("%Y%m%d_%H%M%S")
                filename = f"roast_{timestamp}.png"
            
            output_path = Path("generated") / filename
            output_path.parent.mkdir(exist_ok=True)
            
            # Save with optimization for Termux
            image.save(
                output_path, 
                "PNG", 
                optimize=True,
                compress_level=6  # Balanced compression
            )
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, "PNG")
            return temp_file.name
    
    def cleanup_temp_files(self):
        """টেম্প ফাইল ক্লিনআপ করে"""
        try:
            import glob
            import time
            
            # Clean old generated images (older than 1 day)
            gen_path = Path("generated")
            if gen_path.exists():
                for img_file in gen_path.glob("*.png"):
                    file_age = time.time() - img_file.stat().st_mtime
                    if file_age > 86400:  # 1 day
                        img_file.unlink()
                        
            # Clean temp files
            temp_dir = Path("temp")
            if temp_dir.exists():
                for temp_file in temp_dir.glob("*"):
                    file_age = time.time() - temp_file.stat().st_mtime
                    if file_age > 3600:  # 1 hour
                        temp_file.unlink()
                        
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")

# Global instance
image_generator = ImageGenerator()

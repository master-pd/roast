"""
Image Generator for Roastify Bot - Termux Compatible
Fully Fixed with Bengali support
"""

import os
import random
import tempfile
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from config import Config
from utils.logger import logger
from utils.helpers import Helpers
from utils.time_manager import TimeManager
from image_engine.templates import TemplateManager

class ImageGenerator:
    """ইমেজ জেনারেটর ক্লাস - সম্পূর্ণ ফিক্সড"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
        self.assets_path = Path(Config.ASSETS_PATH)
        self.fonts_path = Path(Config.FONTS_PATH)
        self.backgrounds_path = Path(Config.BACKGROUNDS_PATH)
        
        # Ensure directories exist
        self.fonts_path.mkdir(parents=True, exist_ok=True)
        self.backgrounds_path.mkdir(parents=True, exist_ok=True)
        
        # Font cache
        self.font_cache = {}
        
        # Create default fonts
        self._setup_default_fonts()
        
        logger.info("ImageGenerator initialized")
    
    def _setup_default_fonts(self):
        """ডিফল্ট ফন্ট সেটআপ করে"""
        try:
            # Try to create symlinks to system fonts
            system_fonts = {
                "arial.ttf": "/system/fonts/Roboto-Regular.ttf",
                "comic.ttf": "/system/fonts/DroidSans.ttf",
                "bengali.ttf": "/system/fonts/NotoSansBengali-Regular.ttf"
            }
            
            for local_name, system_path in system_fonts.items():
                local_path = self.fonts_path / local_name
                if not local_path.exists() and os.path.exists(system_path):
                    try:
                        os.symlink(system_path, local_path)
                        logger.info(f"Created symlink: {local_name} -> {system_path}")
                    except:
                        # Try to copy if symlink fails
                        import shutil
                        shutil.copy2(system_path, local_path)
        except Exception as e:
            logger.warning(f"Could not setup system fonts: {e}")
    
    def create_roast_image(self, primary_text: str, secondary_text: str, 
                          user_id: int, user_photo_path: str = None) -> Image.Image:
        """রোস্ট ইমেজ তৈরি করে"""
        try:
            # Get template
            template = self.template_manager.get_template(user_id)
            
            # Create base image
            image = self._create_base_image(template)
            
            # Add text
            image = self._add_text_to_image(image, primary_text, secondary_text, template)
            
            # Add user photo if available
            if user_photo_path and os.path.exists(user_photo_path):
                try:
                    image = self._add_user_photo_simple(image, user_photo_path)
                except Exception as e:
                    logger.warning(f"Could not add user photo: {e}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            return self._create_error_image()
    
    def _create_base_image(self, template: Dict) -> Image.Image:
        """বেস ইমেজ তৈরি করে"""
        width = Config.IMAGE_WIDTH
        height = Config.IMAGE_HEIGHT
        
        # Try to use template background
        if "background" in template:
            bg_path = self.backgrounds_path / template["background"]
            if bg_path.exists():
                try:
                    image = Image.open(bg_path).convert("RGBA")
                    return image.resize((width, height))
                except:
                    pass
        
        # Create gradient background
        return self._create_gradient_background(width, height)
    
    def _create_gradient_background(self, width: int, height: int) -> Image.Image:
        """গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড তৈরি করে"""
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Time-based colors
        is_day = TimeManager.is_day_time()
        
        if is_day:
            # Day gradient: Light blue to white
            for y in range(height):
                ratio = y / height
                r = int(135 + (120 * ratio))
                g = int(206 + (49 * ratio))
                b = int(235 + (20 * ratio))
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        else:
            # Night gradient: Dark blue to black
            for y in range(height):
                ratio = y / height
                r = int(25 + (30 * ratio))
                g = int(25 + (30 * ratio))
                b = int(35 + (30 * ratio))
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    
    def _add_text_to_image(self, image: Image.Image, primary_text: str, 
                          secondary_text: str, template: Dict) -> Image.Image:
        """টেক্সট ইমেজে যোগ করে"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Load fonts
        primary_font = self._load_font_safe(
            template.get("font", "arial.ttf"),
            template.get("font_size", 48)
        )
        
        secondary_font = self._load_font_safe(
            template.get("font", "arial.ttf"),
            template.get("sub_font_size", 24)
        )
        
        # Get colors
        primary_color = tuple(template.get("primary_color", (255, 255, 255)))
        secondary_color = tuple(template.get("secondary_color", (200, 200, 200)))
        
        # Draw primary text (centered)
        primary_lines = self._wrap_text(primary_text, primary_font, width - 100)
        primary_y = height // 3
        
        for i, line in enumerate(primary_lines):
            text_width = self._get_text_width(line, primary_font)
            x = (width - text_width) // 2
            y = primary_y + (i * (self._get_font_height(primary_font) + 10))
            
            # Add shadow for primary text
            shadow_color = (0, 0, 0, 128)
            draw.text((x + 2, y + 2), line, font=primary_font, fill=shadow_color)
            draw.text((x, y), line, font=primary_font, fill=primary_color)
        
        # Draw secondary text
        secondary_lines = self._wrap_text(secondary_text, secondary_font, width - 100)
        secondary_y = height * 2 // 3
        
        for i, line in enumerate(secondary_lines):
            text_width = self._get_text_width(line, secondary_font)
            x = (width - text_width) // 2
            y = secondary_y + (i * (self._get_font_height(secondary_font) + 5))
            draw.text((x, y), line, font=secondary_font, fill=secondary_color)
        
        return image
    
    def _load_font_safe(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """সেফ ফন্ট লোড করে"""
        cache_key = f"{font_name}_{size}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        try:
            # Try local fonts first
            local_path = self.fonts_path / font_name
            if local_path.exists():
                font = ImageFont.truetype(str(local_path), size)
                self.font_cache[cache_key] = font
                return font
            
            # Try system fonts
            for system_font in Config.FONT_FALLBACKS:
                if os.path.exists(system_font):
                    try:
                        font = ImageFont.truetype(system_font, size)
                        self.font_cache[cache_key] = font
                        return font
                    except:
                        continue
            
            # Fallback to default font
            font = ImageFont.load_default()
            self.font_cache[cache_key] = font
            return font
            
        except Exception as e:
            logger.error(f"Font loading error: {e}")
            return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """টেক্সট লাইনে ভাগ করে"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line_text = ' '.join(current_line)
            
            if self._get_text_width(line_text, font) > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _get_text_width(self, text: str, font) -> int:
        """টেক্সটের প্রস্থ বের করে"""
        try:
            # Try multiple methods
            if hasattr(font, 'getlength'):
                return int(font.getlength(text))
            elif hasattr(font, 'getsize'):
                return font.getsize(text)[0]
            else:
                # Approximate
                return len(text) * font.size // 2
        except:
            return len(text) * 10
    
    def _get_font_height(self, font) -> int:
        """ফন্টের উচ্চতা বের করে"""
        try:
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox("Ag")
                return bbox[3] - bbox[1] if bbox else font.size
            elif hasattr(font, 'getsize'):
                return font.getsize("Ag")[1]
            else:
                return font.size + 5
        except:
            return 20
    
    def _add_user_photo_simple(self, image: Image.Image, photo_path: str) -> Image.Image:
        """ইউজার ফটো যোগ করে (সিম্পল)"""
        try:
            user_img = Image.open(photo_path).convert("RGBA")
            user_img = user_img.resize((150, 150))
            
            # Position at top center
            x = (image.width - 150) // 2
            y = 20
            
            # Create circular mask
            mask = Image.new('L', (150, 150), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (150, 150)], fill=255)
            
            # Apply mask
            user_img.putalpha(mask)
            
            # Paste onto image
            image.paste(user_img, (x, y), user_img)
            
            return image
        except Exception as e:
            logger.warning(f"Could not add user photo: {e}")
            return image
    
    def _create_error_image(self) -> Image.Image:
        """এরর ইমেজ তৈরি করে"""
        width = 400
        height = 200
        
        image = Image.new('RGB', (width, height), (255, 200, 200))
        draw = ImageDraw.Draw(image)
        
        font = self._load_font_safe("arial.ttf", 20)
        text = "ইমেজ তৈরি সমস্যা"
        
        text_width = self._get_text_width(text, font)
        x = (width - text_width) // 2
        y = (height - self._get_font_height(font)) // 2
        
        draw.text((x, y), text, font=font, fill=(255, 0, 0))
        
        return image
    
    def save_image(self, image: Image.Image, filename: str = None) -> str:
        """ইমেজ ফাইল হিসেবে সেভ করে"""
        try:
            if filename is None:
                timestamp = TimeManager.get_current_time().strftime("%Y%m%d_%H%M%S")
                filename = f"roast_{timestamp}.png"
            
            output_path = Path("generated") / filename
            output_path.parent.mkdir(exist_ok=True)
            
            # Save with optimization
            image.save(output_path, "PNG", optimize=True)
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, "PNG")
            return temp_file.name

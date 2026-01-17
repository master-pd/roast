"""
Professional Image Generator for Roastify Bot
Termux Compatible - No PIL Font Issues
Advanced Features with Fallbacks
"""

import os
import random
import base64
from io import BytesIO
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
from config import Config
from utils.logger import logger, log_error, log_info
from utils.time_manager import TimeManager
from utils.helpers import Helpers

class ProfessionalImageGenerator:
    """প্রফেশনাল ইমেজ জেনারেটর - টার্মিনাল কম্প্যাটিবল"""
    
    def __init__(self):
        self.width = min(Config.IMAGE_WIDTH, 720)  # Max 720 for Termux
        self.height = min(Config.IMAGE_HEIGHT, 720)
        self.use_pil = self._check_pil_availability()
        self.font_available = False
        self.templates = self._load_templates()
        
        self._setup_fonts()
        logger.info(f"✅ ProfessionalImageGenerator initialized (PIL: {self.use_pil}, Fonts: {self.font_available})")
    
    def _check_pil_availability(self) -> bool:
        """PIL উপলব্ধ কিনা চেক করে"""
        try:
            import PIL
            from PIL import Image, ImageDraw
            return True
        except ImportError as e:
            logger.warning(f"PIL not available: {e}")
            return False
        except Exception as e:
            logger.error(f"PIL check error: {e}")
            return False
    
    def _setup_fonts(self):
        """ফন্ট সেটআপ করে"""
        if not self.use_pil:
            self.font_available = False
            return
        
        try:
            from PIL import ImageFont
            
            # Check for fonts in Termux/Android
            font_paths = [
                # Android system fonts
                "/system/fonts/Roboto-Regular.ttf",
                "/system/fonts/DroidSans.ttf",
                "/system/fonts/NotoSansBengali-Regular.ttf",
                # Termux fonts
                "/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                # Local assets
                str(Path(Config.FONTS_PATH) / "arial.ttf"),
                str(Path(Config.FONTS_PATH) / "default.ttf"),
            ]
            
            self.font_cache = {}
            
            for size in [24, 32, 40, 48, 56]:
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            self.font_cache[size] = ImageFont.truetype(font_path, size)
                            self.font_available = True
                            logger.info(f"✅ Font loaded: {font_path} (size: {size})")
                            break
                        except Exception as e:
                            continue
            
            if not self.font_available:
                logger.warning("No fonts found, using default")
                self.font_cache = {size: ImageFont.load_default() for size in [24, 32, 40, 48, 56]}
                
        except Exception as e:
            logger.error(f"Font setup error: {e}")
            self.font_available = False
    
    def _load_templates(self) -> Dict:
        """টেমপ্লেট লোড করে"""
        return {
            "day": {
                "bg_color": (240, 248, 255),  # Alice Blue
                "primary_color": (41, 128, 185),  # Peter River
                "secondary_color": (52, 152, 219),  # Belize Hole
                "accent_color": (155, 89, 182),  # Amethyst
                "border_color": (189, 195, 199),  # Silver
            },
            "night": {
                "bg_color": (30, 30, 40),  # Dark Blue
                "primary_color": (255, 105, 180),  # Hot Pink
                "secondary_color": (0, 255, 255),  # Cyan
                "accent_color": (50, 205, 50),  # Lime Green
                "border_color": (100, 100, 120),  # Dark Gray
            },
            "funny": {
                "bg_color": (255, 250, 205),  # Lemon Chiffon
                "primary_color": (255, 69, 0),  # Red Orange
                "secondary_color": (255, 140, 0),  # Dark Orange
                "accent_color": (255, 215, 0),  # Gold
                "border_color": (255, 182, 193),  # Light Pink
            },
            "savage": {
                "bg_color": (20, 20, 20),  # Near Black
                "primary_color": (220, 20, 60),  # Crimson
                "secondary_color": (255, 0, 0),  # Red
                "accent_color": (255, 69, 0),  # Red Orange
                "border_color": (139, 0, 0),  # Dark Red
            }
        }
    
    def create_roast_image(self, primary_text: str, secondary_text: str, 
                          user_id: int, roast_type: str = "general") -> Image.Image:
        """রোস্ট ইমেজ তৈরি করে"""
        try:
            if not self.use_pil:
                return self._create_fallback_image(primary_text, secondary_text)
            
            # Select template based on time and type
            template = self._select_template(roast_type)
            
            # Create image
            image = self._create_base_image(template)
            
            # Add text
            image = self._add_text_to_image(image, primary_text, secondary_text, template)
            
            # Add decorations
            image = self._add_decorations(image, template)
            
            # Add user-specific elements
            image = self._add_user_elements(image, user_id)
            
            return image
            
        except Exception as e:
            log_error(f"Image creation failed: {e}")
            return self._create_error_image(primary_text, secondary_text)
    
    def _select_template(self, roast_type: str) -> Dict:
        """টেমপ্লেট সিলেক্ট করে"""
        time_key = "day" if TimeManager.is_day_time() else "night"
        
        if roast_type in ["savage", "burn", "roast"]:
            return self.templates.get("savage", self.templates[time_key])
        elif roast_type in ["funny", "joke", "comedy"]:
            return self.templates.get("funny", self.templates[time_key])
        else:
            return self.templates.get(time_key, self.templates["day"])
    
    def _create_base_image(self, template: Dict) -> Image.Image:
        """বেস ইমেজ তৈরি করে"""
        from PIL import Image
        
        # Create gradient background
        image = Image.new('RGB', (self.width, self.height))
        
        # Simple gradient effect
        for y in range(self.height):
            ratio = y / self.height
            r = int(template["bg_color"][0] * (1 - ratio) + template["primary_color"][0] * ratio * 0.3)
            g = int(template["bg_color"][1] * (1 - ratio) + template["primary_color"][1] * ratio * 0.3)
            b = int(template["bg_color"][2] * (1 - ratio) + template["primary_color"][2] * ratio * 0.3)
            
            for x in range(self.width):
                image.putpixel((x, y), (r, g, b))
        
        return image
    
    def _add_text_to_image(self, image: Image.Image, primary_text: str, 
                          secondary_text: str, template: Dict) -> Image.Image:
        """টেক্সট ইমেজে যোগ করে"""
        from PIL import ImageDraw
        
        draw = ImageDraw.Draw(image)
        
        # Prepare text
        primary_lines = self._wrap_text(primary_text, 25)
        secondary_lines = self._wrap_text(secondary_text, 35)
        
        # Calculate positions
        primary_font = self._get_font(48 if self.font_available else None)
        secondary_font = self._get_font(32 if self.font_available else None)
        
        # Draw primary text
        primary_y = self.height // 3
        for i, line in enumerate(primary_lines):
            text_width = self._get_text_width(line, primary_font)
            x = (self.width - text_width) // 2
            y = primary_y + (i * 60)
            
            # Text shadow
            if self.font_available:
                draw.text((x + 3, y + 3), line, font=primary_font, fill=(0, 0, 0, 128))
            
            # Main text
            draw.text((x, y), line, fill=template["primary_color"], font=primary_font)
        
        # Draw secondary text
        secondary_y = self.height * 2 // 3
        for i, line in enumerate(secondary_lines):
            text_width = self._get_text_width(line, secondary_font)
            x = (self.width - text_width) // 2
            y = secondary_y + (i * 40)
            
            if self.font_available:
                draw.text((x + 2, y + 2), line, font=secondary_font, fill=(0, 0, 0, 100))
            
            draw.text((x, y), line, fill=template["secondary_color"], font=secondary_font)
        
        return image
    
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
    
    def _get_font(self, size: int):
        """ফন্ট পায়"""
        if not self.use_pil or not self.font_available:
            return None
        
        from PIL import ImageFont
        
        # Get closest size
        closest_size = min(self.font_cache.keys(), key=lambda x: abs(x - size))
        return self.font_cache.get(closest_size, None)
    
    def _get_text_width(self, text: str, font) -> int:
        """টেক্সট প্রস্থ বের করে"""
        if font:
            try:
                if hasattr(font, 'getbbox'):
                    bbox = font.getbbox(text)
                    return bbox[2] - bbox[0] if bbox else len(text) * 10
                elif hasattr(font, 'getsize'):
                    return font.getsize(text)[0]
            except:
                pass
        
        # Fallback approximation
        return len(text) * (12 if len(text) < 20 else 8)
    
    def _add_decorations(self, image: Image.Image, template: Dict) -> Image.Image:
        """ডেকোরেশন যোগ করে"""
        from PIL import ImageDraw
        
        draw = ImageDraw.Draw(image)
        
        # Add border
        border_width = 5
        draw.rectangle(
            [(border_width, border_width), 
             (self.width - border_width, self.height - border_width)],
            outline=template["border_color"],
            width=border_width
        )
        
        # Add corner decorations
        corner_size = 30
        corners = [
            (border_width, border_width),
            (self.width - corner_size - border_width, border_width),
            (border_width, self.height - corner_size - border_width),
            (self.width - corner_size - border_width, self.height - corner_size - border_width)
        ]
        
        for x, y in corners:
            draw.rectangle(
                [(x, y), (x + corner_size, y + corner_size)],
                outline=template["accent_color"],
                width=2
            )
        
        # Add decorative lines
        line_y = self.height // 2
        draw.line(
            [(50, line_y), (self.width - 50, line_y)],
            fill=template["accent_color"],
            width=2
        )
        
        return image
    
    def _add_user_elements(self, image: Image.Image, user_id: int) -> Image.Image:
        """ইউজার এলিমেন্ট যোগ করে"""
        # Add user ID in corner (subtle)
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(image)
        
        # Small font for user ID
        small_font = self._get_font(12)
        if small_font:
            user_text = f"ID: {user_id % 10000:04d}"  # Last 4 digits for privacy
            draw.text(
                (10, self.height - 25),
                user_text,
                fill=(100, 100, 100, 150),
                font=small_font
            )
        
        return image
    
    def _create_fallback_image(self, primary_text: str, secondary_text: str):
        """ফলব্যাক ইমেজ তৈরি করে (যখন PIL না থাকে)"""
        # Create a simple ASCII art style representation
        from PIL import Image
        
        image = Image.new('RGB', (self.width, self.height), (41, 128, 185))
        
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Draw text boxes
        draw.rectangle([(50, 50), (self.width-50, self.height-50)], 
                      fill=(255, 255, 255, 200), 
                      outline=(0, 0, 0))
        
        # Center text
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Primary text
        primary_lines = self._wrap_text(primary_text, 30)
        for i, line in enumerate(primary_lines):
            text_width = len(line) * 10
            x = center_x - (text_width // 2)
            y = center_y - 60 + (i * 30)
            draw.text((x, y), line, fill=(41, 128, 185))
        
        # Secondary text
        secondary_lines = self._wrap_text(secondary_text, 40)
        for i, line in enumerate(secondary_lines):
            text_width = len(line) * 8
            x = center_x - (text_width // 2)
            y = center_y + 20 + (i * 25)
            draw.text((x, y), line, fill=(100, 100, 100))
        
        return image
    
    def _create_error_image(self, primary_text: str, secondary_text: str):
        """এরর ইমেজ তৈরি করে"""
        try:
            from PIL import Image, ImageDraw
            
            image = Image.new('RGB', (400, 200), (255, 200, 200))
            draw = ImageDraw.Draw(image)
            
            # Error message
            error_msg = "রোস্ট তৈরি হচ্ছে..."
            text_width = len(error_msg) * 10
            
            draw.text(
                ((400 - text_width) // 2, 80),
                error_msg,
                fill=(255, 0, 0)
            )
            
            # Original text (truncated)
            short_primary = primary_text[:20] + "..." if len(primary_text) > 20 else primary_text
            draw.text(
                (50, 120),
                f"\"{short_primary}\"",
                fill=(100, 100, 100)
            )
            
            return image
            
        except:
            # Ultimate fallback
            from PIL import Image
            return Image.new('RGB', (400, 200), (255, 255, 255))
    
    def save_image(self, image) -> str:
        """ইমেজ ফাইল হিসেবে সেভ করে"""
        try:
            timestamp = TimeManager.get_current_time().strftime("%Y%m%d_%H%M%S")
            filename = f"roast_{timestamp}.png"
            
            output_dir = Path("generated")
            output_dir.mkdir(exist_ok=True)
            
            output_path = output_dir / filename
            
            # Save with optimization
            image.save(output_path, "PNG", optimize=True, quality=85)
            
            log_info(f"Image saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            log_error(f"Error saving image: {e}")
            
            # Save to temp file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, "PNG")
            return temp_file.name
    
    def image_to_base64(self, image) -> str:
        """ইমেজকে Base64 এ কনভার্ট করে"""
        try:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            log_error(f"Error converting image to base64: {e}")
            return ""
    
    def get_image_stats(self) -> Dict:
        """ইমেজ স্ট্যাটস রিটার্ন করে"""
        return {
            "pil_available": self.use_pil,
            "fonts_available": self.font_available,
            "image_width": self.width,
            "image_height": self.height,
            "templates_loaded": len(self.templates),
            "font_cache_size": len(self.font_cache) if hasattr(self, 'font_cache') else 0
        }

# Global instance
image_generator = ProfessionalImageGenerator()

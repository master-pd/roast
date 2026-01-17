"""
Professional Image Generator for Roastify Bot
Termux Compatible - No PIL Font Issues
Fixed all errors
"""

import os
import random
import base64
from io import BytesIO
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
from config import Config
from utils.logger import logger, log_error, log_info
from utils.time_manager import TimeManager

class ProfessionalImageGenerator:
    """প্রফেশনাল ইমেজ জেনারেটর - কোনো এরর নেই"""
    
    def __init__(self):
        self.width = min(Config.IMAGE_WIDTH, 720)  # Max 720 for Termux
        self.height = min(Config.IMAGE_HEIGHT, 720)
        self.use_pil = self._check_pil_availability()
        self.font_available = False
        
        if self.use_pil:
            self._setup_fonts()
        
        self.templates = self._load_templates()
        
        logger.info(f"✅ ImageGenerator initialized (PIL: {self.use_pil}, Fonts: {self.font_available})")
    
    def _check_pil_availability(self) -> bool:
        """PIL উপলব্ধ কিনা চেক করে"""
        try:
            from PIL import Image
            return True
        except ImportError:
            logger.warning("PIL not available, using text-only mode")
            return False
        except Exception as e:
            logger.error(f"PIL check error: {e}")
            return False
    
    def _setup_fonts(self):
        """ফন্ট সেটআপ করে"""
        if not self.use_pil:
            return
        
        try:
            from PIL import ImageFont
            
            # Check for fonts in Termux/Android
            font_paths = [
                "/system/fonts/Roboto-Regular.ttf",
                "/system/fonts/DroidSans.ttf",
                "/system/fonts/NotoSansBengali-Regular.ttf",
                "/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                str(Path(Config.FONTS_PATH) / "arial.ttf"),
            ]
            
            self.font_cache = {}
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # Load different sizes
                        for size in [24, 32, 40, 48]:
                            self.font_cache[size] = ImageFont.truetype(font_path, size)
                        
                        self.font_available = True
                        logger.info(f"✅ Fonts loaded from: {font_path}")
                        break
                    except Exception as e:
                        continue
            
            if not self.font_available:
                logger.warning("No fonts found, using text-only mode")
                
        except Exception as e:
            logger.error(f"Font setup error: {e}")
            self.font_available = False
    
    def _load_templates(self) -> Dict[str, Dict]:
        """টেমপ্লেট লোড করে"""
        return {
            "day": {
                "bg_color": (240, 248, 255),
                "primary_color": (41, 128, 185),
                "secondary_color": (52, 152, 219),
                "border_color": (189, 195, 199),
            },
            "night": {
                "bg_color": (30, 30, 40),
                "primary_color": (255, 105, 180),
                "secondary_color": (0, 255, 255),
                "border_color": (100, 100, 120),
            },
            "funny": {
                "bg_color": (255, 250, 205),
                "primary_color": (255, 69, 0),
                "secondary_color": (255, 140, 0),
                "border_color": (255, 182, 193),
            },
            "savage": {
                "bg_color": (20, 20, 20),
                "primary_color": (220, 20, 60),
                "secondary_color": (255, 0, 0),
                "border_color": (139, 0, 0),
            },
            "welcome": {
                "bg_color": (135, 206, 235),
                "primary_color": (255, 255, 255),
                "secondary_color": (240, 248, 255),
                "border_color": (70, 130, 180),
            }
        }
    
    def create_roast_image(self, primary_text: str, secondary_text: str, 
                          user_id: int, roast_type: str = "general") -> Any:
        """রোস্ট ইমেজ তৈরি করে - কোনো এরর নেই"""
        try:
            if not self.use_pil:
                return self._create_text_only_image(primary_text, secondary_text)
            
            from PIL import Image, ImageDraw
            
            # Select template
            template = self._select_template(roast_type)
            
            # Create base image
            image = Image.new('RGB', (self.width, self.height))
            
            # Fill with background color
            for y in range(self.height):
                for x in range(self.width):
                    image.putpixel((x, y), template["bg_color"])
            
            draw = ImageDraw.Draw(image)
            
            # Add border
            border_width = 10
            draw.rectangle(
                [(border_width, border_width), 
                 (self.width - border_width, self.height - border_width)],
                outline=template["border_color"],
                width=border_width
            )
            
            # Add text
            self._add_simple_text(draw, primary_text, secondary_text, template)
            
            # Add decorations
            self._add_simple_decorations(draw, template)
            
            return image
            
        except Exception as e:
            log_error(f"Image creation error: {e}")
            return self._create_error_image()
    
    def _select_template(self, roast_type: str) -> Dict:
        """টেমপ্লেট সিলেক্ট করে"""
        is_day = TimeManager.is_day_time()
        base_template = "day" if is_day else "night"
        
        if roast_type in ["savage", "burn", "roast"]:
            return self.templates.get("savage", self.templates[base_template])
        elif roast_type in ["funny", "joke", "comedy", "welcome"]:
            return self.templates.get(roast_type, self.templates["funny"])
        else:
            return self.templates.get(base_template)
    
    def _add_simple_text(self, draw, primary_text: str, secondary_text: str, template: Dict):
        """সিম্পল টেক্সট যোগ করে"""
        try:
            from PIL import ImageFont
            
            # Get fonts
            if self.font_available:
                primary_font = self.font_cache.get(48, ImageFont.load_default())
                secondary_font = self.font_cache.get(32, ImageFont.load_default())
            else:
                primary_font = ImageFont.load_default()
                secondary_font = ImageFont.load_default()
            
            # Wrap text
            primary_lines = self._wrap_text(primary_text, 25)
            secondary_lines = self._wrap_text(secondary_text, 35)
            
            # Draw primary text
            primary_y = self.height // 3
            for i, line in enumerate(primary_lines):
                text_width = self._get_text_width(line, primary_font)
                x = (self.width - text_width) // 2
                y = primary_y + (i * 60)
                
                # Shadow
                draw.text((x + 3, y + 3), line, font=primary_font, fill=(0, 0, 0, 128))
                # Main text
                draw.text((x, y), line, font=primary_font, fill=template["primary_color"])
            
            # Draw secondary text
            secondary_y = self.height * 2 // 3
            for i, line in enumerate(secondary_lines):
                text_width = self._get_text_width(line, secondary_font)
                x = (self.width - text_width) // 2
                y = secondary_y + (i * 40)
                
                draw.text((x, y), line, font=secondary_font, fill=template["secondary_color"])
                
        except Exception as e:
            log_error(f"Text drawing error: {e}")
            # Fallback: draw simple text
            draw.text((50, 50), primary_text, fill=template["primary_color"])
            draw.text((50, 150), secondary_text, fill=template["secondary_color"])
    
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
    
    def _add_simple_decorations(self, draw, template: Dict):
        """সিম্পল ডেকোরেশন যোগ করে"""
        try:
            # Add corner decorations
            corner_size = 20
            corners = [
                (10, 10),
                (self.width - corner_size - 10, 10),
                (10, self.height - corner_size - 10),
                (self.width - corner_size - 10, self.height - corner_size - 10)
            ]
            
            for x, y in corners:
                draw.rectangle(
                    [(x, y), (x + corner_size, y + corner_size)],
                    outline=template["border_color"],
                    width=2
                )
            
            # Add center line
            center_y = self.height // 2
            draw.line(
                [(50, center_y), (self.width - 50, center_y)],
                fill=template["primary_color"],
                width=2
            )
            
        except Exception as e:
            log_error(f"Decoration error: {e}")
    
    def _create_text_only_image(self, primary_text: str, secondary_text: str) -> Any:
        """টেক্সট-ওনলি ইমেজ তৈরি করে"""
        try:
            from PIL import Image, ImageDraw
            
            # Create simple image
            image = Image.new('RGB', (self.width, self.height), (41, 128, 185))
            draw = ImageDraw.Draw(image)
            
            # Draw text boxes
            draw.rectangle([(50, 50), (self.width-50, self.height-50)], 
                          fill=(255, 255, 255, 200), 
                          outline=(0, 0, 0))
            
            # Add text
            font = ImageFont.load_default()
            
            # Primary text
            primary_lines = self._wrap_text(primary_text, 30)
            for i, line in enumerate(primary_lines):
                text_width = len(line) * 10
                x = (self.width - text_width) // 2
                y = (self.height // 2) - 60 + (i * 30)
                draw.text((x, y), line, fill=(41, 128, 185))
            
            # Secondary text
            secondary_lines = self._wrap_text(secondary_text, 40)
            for i, line in enumerate(secondary_lines):
                text_width = len(line) * 8
                x = (self.width - text_width) // 2
                y = (self.height // 2) + 20 + (i * 25)
                draw.text((x, y), line, fill=(100, 100, 100))
            
            return image
            
        except Exception as e:
            log_error(f"Text-only image error: {e}")
            return self._create_error_image()
    
    def _create_error_image(self):
        """এরর ইমেজ তৈরি করে"""
        try:
            from PIL import Image, ImageDraw
            
            image = Image.new('RGB', (400, 200), (255, 200, 200))
            draw = ImageDraw.Draw(image)
            
            # Error message
            error_text = "রোস্ট তৈরি হচ্ছে..."
            draw.text((100, 80), error_text, fill=(255, 0, 0))
            
            return image
            
        except:
            # Ultimate fallback
            try:
                from PIL import Image
                return Image.new('RGB', (400, 200), (255, 255, 255))
            except:
                return None
    
    def save_image(self, image) -> str:
        """ইমেজ ফাইল হিসেবে সেভ করে"""
        try:
            if image is None:
                raise ValueError("Image is None")
            
            timestamp = TimeManager.get_current_time().strftime("%Y%m%d_%H%M%S")
            filename = f"roast_{timestamp}.png"
            
            output_dir = Path("generated")
            output_dir.mkdir(exist_ok=True)
            
            output_path = output_dir / filename
            
            # Save with optimization
            image.save(output_path, "PNG", optimize=True)
            
            log_info(f"✅ Image saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            log_error(f"❌ Error saving image: {e}")
            
            # Save to temp file
            try:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                image.save(temp_file.name, "PNG")
                return temp_file.name
            except:
                return ""
    
    def image_to_base64(self, image) -> str:
        """ইমেজকে Base64 এ কনভার্ট করে"""
        try:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            log_error(f"Base64 conversion error: {e}")
            return ""
    
    def get_image_stats(self) -> Dict[str, Any]:
        """ইমেজ স্ট্যাটস রিটার্ন করে"""
        return {
            "pil_available": self.use_pil,
            "fonts_available": self.font_available,
            "image_width": self.width,
            "image_height": self.height,
            "templates_loaded": len(self.templates)
        }
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """টেম্প ফাইল ক্লিনআপ করে"""
        try:
            import time
            import glob
            
            # Clean generated images
            gen_path = Path("generated")
            if gen_path.exists():
                current_time = time.time()
                
                for img_file in gen_path.glob("*.png"):
                    file_age = current_time - img_file.stat().st_mtime
                    
                    if file_age > (max_age_hours * 3600):
                        img_file.unlink()
                        logger.info(f"Removed old image: {img_file.name}")
            
        except Exception as e:
            log_error(f"Cleanup error: {e}")

# Global instance
image_generator = ProfessionalImageGenerator()

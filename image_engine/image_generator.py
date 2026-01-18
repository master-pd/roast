#!/usr/bin/env python3
"""
Advanced Image Generator for Roastify Bot
HTML Compatible | Border System | Professional
Termux Optimized - No PIL Font Issues
"""

import os
import random
import base64
import textwrap
import hashlib
from io import BytesIO
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
from datetime import datetime

# Fallback imports
try:
    from config import Config
except ImportError:
    class Config:
        IMAGE_WIDTH = 600
        IMAGE_HEIGHT = 450
        FONTS_PATH = "fonts"
        BORDER_STYLES = {
            "fire": "🔥", "star": "✦", "heart": "❤️", "diamond": "💎",
            "arrow": "➤", "wave": "〰️", "music": "♪", "sparkle": "✨",
            "zap": "⚡", "crown": "👑", "smile": "😊", "ghost": "👻",
            "rocket": "🚀"
        }

try:
    from utils.logger import logger, log_error, log_info
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def log_error(msg):
        logger.error(f"❌ {msg}")
    
    def log_info(msg):
        logger.info(f"✅ {msg}")

class AdvancedImageGenerator:
    """এডভান্সড ইমেজ জেনারেটর - HTML & Border Compatible"""
    
    def __init__(self):
        self.width = min(Config.IMAGE_WIDTH, 800)
        self.height = min(Config.IMAGE_HEIGHT, 800)
        self.use_pil = self._check_pil_availability()
        self.font_available = False
        self.border_styles = Config.BORDER_STYLES
        
        if self.use_pil:
            self._setup_fonts()
        
        self.templates = self._load_templates()
        self.colors = self._load_color_palettes()
        
        logger.info(f"✅ ImageGenerator v3.0 initialized (PIL: {self.use_pil})")
    
    def _check_pil_availability(self) -> bool:
        """PIL উপলব্ধ কিনা চেক করে"""
        try:
            import importlib.util
            pil_spec = importlib.util.find_spec("PIL")
            if pil_spec is None:
                logger.warning("PIL not found")
                return False
            
            from PIL import Image
            return True
            
        except Exception as e:
            logger.warning(f"PIL check failed: {e}")
            return False
    
    def _setup_fonts(self):
        """ফন্ট সেটআপ করে - টার্মাক্স কম্পেটিবল"""
        try:
            from PIL import ImageFont
            
            font_paths = [
                # Android/Termux paths
                "/system/fonts/Roboto-Regular.ttf",
                "/system/fonts/DroidSans.ttf",
                "/system/fonts/NotoSansBengali-Regular.ttf",
                "/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/data/data/com.termux/files/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                
                # Project fonts
                "fonts/arial.ttf",
                "fonts/DejaVuSans.ttf",
                "arial.ttf",
                "DejaVuSans.ttf",
            ]
            
            self.font_cache = {}
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # Load multiple sizes
                        self.font_cache['small'] = ImageFont.truetype(font_path, 20)
                        self.font_cache['medium'] = ImageFont.truetype(font_path, 28)
                        self.font_cache['large'] = ImageFont.truetype(font_path, 36)
                        self.font_cache['xlarge'] = ImageFont.truetype(font_path, 44)
                        
                        self.font_available = True
                        logger.info(f"✅ Font loaded: {font_path}")
                        break
                        
                    except Exception as e:
                        continue
            
            if not self.font_available:
                logger.warning("Using default bitmap fonts")
                self.font_cache = {
                    'small': ImageFont.load_default(),
                    'medium': ImageFont.load_default(),
                    'large': ImageFont.load_default(),
                    'xlarge': ImageFont.load_default(),
                }
                
        except Exception as e:
            logger.error(f"Font setup error: {e}")
            self.font_available = False
    
    def _load_templates(self) -> Dict[str, Dict]:
        """টেমপ্লেট লোড করে"""
        return {
            "default": {
                "bg_color": (25, 25, 35),
                "primary_color": (255, 107, 53),   # #FF6B35
                "secondary_color": (0, 180, 216),  # #00B4D8
                "border_color": (255, 209, 102),   # #FFD166
                "accent_color": (239, 71, 111),    # #EF476F
                "text_color": (255, 255, 255),
                "shadow_color": (0, 0, 0, 128)
            },
            "funny": {
                "bg_color": (255, 250, 205),       # LemonChiffon
                "primary_color": (255, 69, 0),     # Red-Orange
                "secondary_color": (255, 140, 0),  # Dark Orange
                "border_color": (50, 205, 50),     # Lime Green
                "accent_color": (138, 43, 226),    # Blue Violet
                "text_color": (0, 0, 0),
                "shadow_color": (100, 100, 100, 128)
            },
            "savage": {
                "bg_color": (15, 15, 15),          # Almost Black
                "primary_color": (220, 20, 60),    # Crimson
                "secondary_color": (255, 0, 0),    # Red
                "border_color": (255, 215, 0),     # Gold
                "accent_color": (255, 20, 147),    # Deep Pink
                "text_color": (255, 255, 255),
                "shadow_color": (50, 0, 0, 128)
            },
            "welcome": {
                "bg_color": (135, 206, 235),       # Sky Blue
                "primary_color": (255, 255, 255),  # White
                "secondary_color": (70, 130, 180), # Steel Blue
                "border_color": (255, 165, 0),     # Orange
                "accent_color": (255, 255, 0),     # Yellow
                "text_color": (0, 0, 0),
                "shadow_color": (0, 0, 139, 128)   # Dark Blue
            },
            "vibrant": {
                "bg_color": (0, 0, 30),            # Deep Blue
                "primary_color": (0, 255, 255),    # Cyan
                "secondary_color": (255, 20, 147), # Deep Pink
                "border_color": (0, 255, 127),     # Spring Green
                "accent_color": (255, 255, 0),     # Yellow
                "text_color": (255, 255, 255),
                "shadow_color": (0, 0, 0, 128)
            },
            "premium": {
                "bg_color": (20, 20, 30),          # Dark Blue-Grey
                "primary_color": (255, 215, 0),    # Gold
                "secondary_color": (192, 192, 192),# Silver
                "border_color": (184, 134, 11),    # Dark Goldenrod
                "accent_color": (218, 165, 32),    # Goldenrod
                "text_color": (255, 255, 255),
                "shadow_color": (0, 0, 0, 128)
            }
        }
    
    def _load_color_palettes(self) -> Dict[str, List[Tuple]]:
        """কালার প্যালেট লোড করে"""
        return {
            "gradient_1": [(255, 107, 53), (0, 180, 216)],  # Orange to Blue
            "gradient_2": [(138, 43, 226), (255, 20, 147)], # Violet to Pink
            "gradient_3": [(0, 255, 127), (0, 255, 255)],   # Green to Cyan
            "gradient_4": [(255, 215, 0), (255, 69, 0)],    # Gold to Red
            "gradient_5": [(25, 25, 35), (70, 130, 180)],   # Dark to Steel Blue
        }
    
    def create_roast_image(self, 
                          primary_text: str, 
                          secondary_text: str = "",
                          user_id: Optional[int] = None,
                          roast_type: str = "default",
                          border_style: str = None,
                          add_decoration: bool = True) -> Any:
        """রোস্ট ইমেজ তৈরি করে - HTML কম্পেটিবল"""
        try:
            if not self.use_pil:
                return self._create_text_based_image(primary_text, secondary_text)
            
            from PIL import Image, ImageDraw, ImageFilter
            
            # Select random border if not specified
            if not border_style:
                border_style = random.choice(list(self.border_styles.keys()))
            
            # Get template
            template = self.templates.get(roast_type, self.templates["default"])
            
            # Create base image with gradient
            image = self._create_gradient_background(template)
            
            draw = ImageDraw.Draw(image)
            
            # Add decorative border
            if add_decoration:
                self._add_decorative_border(draw, template, border_style)
            
            # Add content
            self._add_content(draw, primary_text, secondary_text, template)
            
            # Add user info if available
            if user_id:
                self._add_user_info(draw, user_id, template)
            
            # Add border symbols
            self._add_border_symbols(draw, border_style, template)
            
            # Add final effects
            image = self._apply_effects(image, template)
            
            return image
            
        except Exception as e:
            log_error(f"Image creation error: {e}")
            return self._create_error_image()
    
    def _create_gradient_background(self, template: Dict) -> Any:
        """গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড তৈরি করে"""
        try:
            from PIL import Image
            
            # Select random gradient
            gradient_name = random.choice(list(self.colors.keys()))
            colors = self.colors[gradient_name]
            
            # Create gradient
            base = Image.new('RGB', (self.width, self.height), colors[0])
            
            # Vertical gradient
            for y in range(self.height):
                ratio = y / self.height
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                
                for x in range(self.width):
                    base.putpixel((x, y), (r, g, b))
            
            return base
            
        except Exception as e:
            log_error(f"Gradient error: {e}")
            from PIL import Image
            return Image.new('RGB', (self.width, self.height), template["bg_color"])
    
    def _add_decorative_border(self, draw, template: Dict, border_style: str):
        """ডেকোরেটিভ বর্ডার যোগ করে"""
        try:
            # Outer border
            border_width = 15
            draw.rectangle(
                [(border_width, border_width), 
                 (self.width - border_width, self.height - border_width)],
                outline=template["border_color"],
                width=border_width
            )
            
            # Inner accent border
            inner_border = border_width + 10
            draw.rectangle(
                [(inner_border, inner_border),
                 (self.width - inner_border, self.height - inner_border)],
                outline=template["accent_color"],
                width=3
            )
            
            # Corner decorations
            corner_size = 25
            corners = [
                (border_width, border_width),
                (self.width - border_width - corner_size, border_width),
                (border_width, self.height - border_width - corner_size),
                (self.width - border_width - corner_size, self.height - border_width - corner_size)
            ]
            
            for x, y in corners:
                draw.rectangle(
                    [(x, y), (x + corner_size, y + corner_size)],
                    fill=template["accent_color"],
                    outline=template["primary_color"],
                    width=2
                )
                
        except Exception as e:
            log_error(f"Border decoration error: {e}")
    
    def _add_content(self, draw, primary_text: str, secondary_text: str, template: Dict):
        """কনটেন্ট যোগ করে"""
        try:
            from PIL import ImageFont
            
            # Get fonts
            font_large = self.font_cache.get('large', ImageFont.load_default())
            font_medium = self.font_cache.get('medium', ImageFont.load_default())
            font_small = self.font_cache.get('small', ImageFont.load_default())
            
            # Header area
            header_height = 80
            draw.rectangle(
                [(30, 30), (self.width - 30, header_height)],
                fill=template["primary_color"] + (100,),  # Add alpha
                outline=template["border_color"],
                width=2
            )
            
            # Draw header text
            header_text = "🔥 Roastify Bot 🔥"
            text_width = self._get_text_width(header_text, font_large)
            draw.text(
                ((self.width - text_width) // 2, 45),
                header_text,
                font=font_large,
                fill=template["text_color"]
            )
            
            # Wrap and draw primary text
            primary_lines = self._smart_wrap_text(primary_text, 30, font_large)
            primary_y = header_height + 40
            
            for i, line in enumerate(primary_lines[:3]):  # Max 3 lines
                text_width = self._get_text_width(line, font_large)
                x = (self.width - text_width) // 2
                y = primary_y + (i * 50)
                
                # Text shadow
                draw.text(
                    (x + 2, y + 2),
                    line,
                    font=font_large,
                    fill=template["shadow_color"]
                )
                
                # Main text
                draw.text(
                    (x, y),
                    line,
                    font=font_large,
                    fill=template["primary_color"]
                )
            
            # Separator line
            separator_y = primary_y + len(primary_lines[:3]) * 50 + 20
            draw.line(
                [(self.width // 4, separator_y),
                 (3 * self.width // 4, separator_y)],
                fill=template["border_color"],
                width=3
            )
            
            # Draw secondary text
            if secondary_text:
                secondary_lines = self._smart_wrap_text(secondary_text, 40, font_medium)
                secondary_y = separator_y + 30
                
                for i, line in enumerate(secondary_lines[:2]):  # Max 2 lines
                    text_width = self._get_text_width(line, font_medium)
                    x = (self.width - text_width) // 2
                    y = secondary_y + (i * 40)
                    
                    draw.text(
                        (x, y),
                        line,
                        font=font_medium,
                        fill=template["secondary_color"]
                    )
                    
        except Exception as e:
            log_error(f"Content drawing error: {e}")
            # Fallback
            draw.text((50, 50), primary_text, fill=template["primary_color"])
            if secondary_text:
                draw.text((50, 100), secondary_text, fill=template["secondary_color"])
    
    def _add_user_info(self, draw, user_id: int, template: Dict):
        """ইউজার ইনফো যোগ করে"""
        try:
            from PIL import ImageFont
            
            font_small = self.font_cache.get('small', ImageFont.load_default())
            footer_y = self.height - 50
            
            # User info text
            user_info = f"User ID: {user_id}"
            text_width = self._get_text_width(user_info, font_small)
            
            draw.text(
                ((self.width - text_width) // 2, footer_y),
                user_info,
                font=font_small,
                fill=template["secondary_color"]
            )
            
            # Timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            time_width = self._get_text_width(timestamp, font_small)
            
            draw.text(
                ((self.width - time_width) // 2, footer_y + 25),
                timestamp,
                font=font_small,
                fill=template["border_color"]
            )
            
        except Exception as e:
            log_error(f"User info error: {e}")
    
    def _add_border_symbols(self, draw, border_style: str, template: Dict):
        """বর্ডার সিম্বল যোগ করে"""
        try:
            from PIL import ImageFont
            
            font_medium = self.font_cache.get('medium', ImageFont.load_default())
            symbol = self.border_styles.get(border_style, "🔥")
            
            # Top border symbols
            symbol_count = self.width // 40
            for i in range(symbol_count):
                x = 30 + (i * 40)
                draw.text((x, 15), symbol, font=font_medium, fill=template["border_color"])
            
            # Bottom border symbols
            for i in range(symbol_count):
                x = 30 + (i * 40)
                draw.text((x, self.height - 40), symbol, font=font_medium, fill=template["border_color"])
                
        except Exception as e:
            log_error(f"Border symbols error: {e}")
    
    def _apply_effects(self, image, template: Dict) -> Any:
        """ইফেক্ট প্রয়োগ করে"""
        try:
            from PIL import ImageFilter, ImageEnhance
            
            # Slight blur to background
            blurred = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Enhance colors
            enhancer = ImageEnhance.Color(blurred)
            enhanced = enhancer.enhance(1.1)
            
            # Enhance contrast
            contrast = ImageEnhance.Contrast(enhanced)
            result = contrast.enhance(1.05)
            
            # Add vignette effect
            width, height = result.size
            for y in range(height):
                for x in range(width):
                    dx = (x - width/2) / (width/2)
                    dy = (y - height/2) / (height/2)
                    distance = (dx*dx + dy*dy) * 0.5
                    
                    if distance > 0.3:
                        pixel = result.getpixel((x, y))
                        darken = max(0.8, 1 - distance)
                        new_pixel = tuple(int(c * darken) for c in pixel)
                        result.putpixel((x, y), new_pixel)
            
            return result
            
        except Exception as e:
            log_error(f"Effects error: {e}")
            return image
    
    def _smart_wrap_text(self, text: str, max_chars: int, font) -> List[str]:
        """স্মার্ট টেক্সট র‍্যাপিং"""
        if not text:
            return []
        
        # Simple wrap first
        lines = textwrap.wrap(text, width=max_chars)
        
        # Adjust based on actual width
        if self.font_available and lines:
            adjusted = []
            current_line = ""
            
            words = text.split()
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if self._get_text_width(test_line, font) < (self.width - 100):
                    current_line = test_line
                else:
                    if current_line:
                        adjusted.append(current_line)
                    current_line = word
            
            if current_line:
                adjusted.append(current_line)
            
            return adjusted if adjusted else lines
        
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
    
    def _create_text_based_image(self, primary_text: str, secondary_text: str) -> Any:
        """টেক্সট-বেসড ইমেজ তৈরি করে"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            image = Image.new('RGB', (self.width, self.height), (25, 25, 35))
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            
            # Add decorative elements
            draw.rectangle([(10, 10), (self.width-10, self.height-10)], 
                          outline=(255, 107, 53), width=3)
            
            # Text with border effect
            text_lines = [
                "╔══════════════════════════╗",
                "   🔥 ROASTIFY BOT 🔥   ",
                "╚══════════════════════════╝",
                "",
                primary_text[:100],
                "",
                secondary_text[:80] if secondary_text else "Professional Roast Service",
                "",
                "═" * 30,
                f"📅 {datetime.now().strftime('%Y-%m-%d')}",
                f"⏰ {datetime.now().strftime('%H:%M:%S')}"
            ]
            
            for i, line in enumerate(text_lines):
                y_pos = 30 + (i * 30)
                if i < 3:
                    draw.text((20, y_pos), line, fill=(255, 107, 53))
                elif i == 4:
                    draw.text((20, y_pos), line, fill=(0, 180, 216))
                else:
                    draw.text((20, y_pos), line, fill=(255, 255, 255))
            
            return image
            
        except Exception as e:
            log_error(f"Text image error: {e}")
            return self._create_error_image()
    
    def _create_error_image(self):
        """এরর ইমেজ তৈরি করে"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            image = Image.new('RGB', (500, 300), (220, 20, 60))
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            
            # Error message with style
            draw.rectangle([(50, 50), (450, 250)], 
                          fill=(255, 255, 255, 200), 
                          outline=(0, 0, 0))
            
            error_lines = [
                "╔══════════════════════╗",
                "   ⚠️ ERROR ⚠️   ",
                "╚══════════════════════╝",
                "",
                "Image generation failed!",
                "",
                "Please try again...",
                "",
                "🔥 Roastify Bot 🔥"
            ]
            
            for i, line in enumerate(error_lines):
                y_pos = 80 + (i * 25)
                draw.text((100, y_pos), line, fill=(0, 0, 0))
            
            return image
            
        except Exception as e:
            log_error(f"Error image creation failed: {e}")
            try:
                from PIL import Image
                return Image.new('RGB', (400, 200), (255, 255, 255))
            except:
                return None
    
    def save_image(self, image, filename: str = None) -> str:
        """ইমেজ সেভ করে"""
        try:
            if image is None:
                raise ValueError("Image is None")
            
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
                filename = f"roast_{timestamp}_{random_hash}.png"
            
            # Create directory
            output_dir = Path("generated_images")
            output_dir.mkdir(exist_ok=True)
            
            output_path = output_dir / filename
            
            # Save with optimization
            image.save(output_path, "PNG", optimize=True, compress_level=9)
            
            log_info(f"✅ Image saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            log_error(f"❌ Save error: {e}")
            
            # Fallback save
            try:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                image.save(temp_file.name, "PNG")
                return temp_file.name
            except:
                return ""
    
    def image_to_bytes(self, image) -> BytesIO:
        """ইমেজকে বাইটসে কনভার্ট করে"""
        try:
            buffered = BytesIO()
            image.save(buffered, format="PNG", optimize=True)
            buffered.seek(0)
            return buffered
            
        except Exception as e:
            log_error(f"Bytes conversion error: {e}")
            return self._create_fallback_bytes()
    
    def _create_fallback_bytes(self) -> BytesIO:
        """ফলব্যাক বাইটস তৈরি করে"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (400, 200), (255, 107, 53))
            draw = ImageDraw.Draw(img)
            draw.text((100, 80), "🔥 Roastify Bot 🔥", fill=(255, 255, 255))
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            buffered.seek(0)
            return buffered
            
        except:
            return BytesIO(b'')
    
    def image_to_base64(self, image) -> str:
        """ইমেজকে Base64 এ কনভার্ট করে"""
        try:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
            
        except Exception as e:
            log_error(f"Base64 error: {e}")
            return ""
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """টেম্প ফাইল ক্লিনআপ করে"""
        try:
            import time
            from pathlib import Path
            
            gen_path = Path("generated_images")
            if not gen_path.exists():
                return
            
            current_time = time.time()
            cutoff = current_time - (max_age_hours * 3600)
            
            files_deleted = 0
            for img_file in gen_path.glob("*.png"):
                if img_file.stat().st_mtime < cutoff:
                    try:
                        img_file.unlink()
                        files_deleted += 1
                    except:
                        continue
            
            if files_deleted:
                logger.info(f"Cleaned {files_deleted} old images")
                
        except Exception as e:
            log_error(f"Cleanup error: {e}")
    
    def get_image_stats(self) -> Dict[str, Any]:
        """ইমেজ স্ট্যাটস রিটার্ন করে"""
        return {
            "version": "3.0",
            "pil_available": self.use_pil,
            "font_available": self.font_available,
            "templates": len(self.templates),
            "border_styles": len(self.border_styles),
            "image_size": f"{self.width}x{self.height}",
            "color_palettes": len(self.colors)
        }
    
    def create_html_compatible_image(self, 
                                    primary_html: str, 
                                    secondary_html: str = "",
                                    user_id: Optional[int] = None) -> Any:
        """HTML কম্পেটিবল ইমেজ তৈরি করে"""
        # Remove HTML tags for image text
        import re
        clean_primary = re.sub(r'<[^>]+>', '', primary_html)
        clean_secondary = re.sub(r'<[^>]+>', '', secondary_html)
        
        return self.create_roast_image(
            primary_text=clean_primary[:100],
            secondary_text=clean_secondary[:80],
            user_id=user_id,
            border_style=random.choice(list(self.border_styles.keys()))
        )

# Global instance
image_generator = AdvancedImageGenerator()

def get_image_generator() -> AdvancedImageGenerator:
    """গ্লোবাল ইমেজ জেনারেটর ইনস্ট্যান্স রিটার্ন করে"""
    return image_generator

# Test function
if __name__ == "__main__":
    print("Testing Advanced Image Generator...")
    
    gen = get_image_generator()
    stats = gen.get_image_stats()
    
    print(f"\n📊 Generator Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test image creation
    test_image = gen.create_roast_image(
        primary_text="This is a test roast for HTML compatibility!",
        secondary_text="Roastify Bot Professional Edition",
        user_id=123456,
        roast_type="savage",
        border_style="fire"
    )
    
    if test_image:
        save_path = gen.save_image(test_image, "test_output.png")
        print(f"✅ Test image saved: {save_path}")
        
        # Test bytes conversion
        image_bytes = gen.image_to_bytes(test_image)
        print(f"✅ Bytes conversion successful: {len(image_bytes.getvalue())} bytes")
    
    print("\n✨ Testing completed!")

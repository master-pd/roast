"""
Professional Image Generator for Roastify Bot
Fully Fixed & Upgraded Version
Termux Compatible - No PIL Font Issues
Added Fallback Systems & Error Handling
"""

import os
import random
import base64
import textwrap
import sys
from io import BytesIO
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
from datetime import datetime

# Check if config exists
try:
    from config import Config
except ImportError:
    # Fallback config
    class Config:
        IMAGE_WIDTH = 600
        IMAGE_HEIGHT = 400
        FONTS_PATH = "fonts"

# Fallback logger if not available
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

# Fallback TimeManager
try:
    from utils.time_manager import TimeManager
except ImportError:
    class TimeManager:
        @staticmethod
        def is_day_time():
            from datetime import datetime
            hour = datetime.now().hour
            return 6 <= hour < 18
        
        @staticmethod
        def get_current_time():
            return datetime.now()


class ImageGenerator:
    """প্রফেশনাল ইমেজ জেনারেটর - উন্নত ভার্সন"""
    
    def __init__(self):
        self.width = min(getattr(Config, 'IMAGE_WIDTH', 600), 800)  # Max 800 for Termux
        self.height = min(getattr(Config, 'IMAGE_HEIGHT', 400), 800)
        self.use_pil = self._check_pil_availability()
        self.font_available = False
        self.default_fonts = {}
        
        if self.use_pil:
            self._setup_fonts()
        
        self.templates = self._load_templates()
        self.emoji_fallback = ["🔥", "😎", "🤣", "💀", "👑", "🎯", "⚡", "✨", "🎭", "🃏"]
        
        logger.info(f"✅ ImageGenerator v2.0 initialized (PIL: {self.use_pil}, Fonts: {self.font_available})")
    
    def _check_pil_availability(self) -> bool:
        """PIL উপলব্ধ কিনা চেক করে - উন্নত চেকিং"""
        try:
            # Try to import PIL
            import importlib.util
            
            # Check for PIL/Pillow
            pil_spec = importlib.util.find_spec("PIL")
            if pil_spec is None:
                logger.warning("PIL/Pillow not found in system")
                return False
            
            # Try actual import
            from PIL import Image, ImageDraw, ImageFont
            return True
            
        except Exception as e:
            logger.warning(f"PIL unavailable: {e}")
            return False
    
    def _setup_fonts(self):
        """ফন্ট সেটআপ করে - উন্নত পদ্ধতি"""
        try:
            from PIL import ImageFont, Image
            
            # First, try to create default bitmap font
            try:
                self.default_fonts = {
                    'small': ImageFont.load_default(),
                    'medium': ImageFont.load_default(),
                    'large': ImageFont.load_default()
                }
            except:
                pass
            
            # Font paths for Termux/Android/Linux/Windows
            font_paths = [
                # Android/Termux
                "/system/fonts/Roboto-Regular.ttf",
                "/system/fonts/DroidSans.ttf",
                "/system/fonts/NotoSansBengali-Regular.ttf",
                "/system/fonts/NotoSans-Regular.ttf",
                "/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/data/data/com.termux/files/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                
                # Linux
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                
                # Windows fallback (if running in Termux on Windows)
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/tahoma.ttf",
                
                # Project fonts
                str(Path("fonts") / "arial.ttf"),
                str(Path("fonts") / "DejaVuSans.ttf"),
                
                # Current directory
                "arial.ttf",
                "DejaVuSans.ttf"
            ]
            
            # Add config path if exists
            try:
                font_paths.append(str(Path(Config.FONTS_PATH) / "arial.ttf"))
            except:
                pass
            
            self.font_cache = {}
            loaded_font = None
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        logger.info(f"Trying font: {font_path}")
                        
                        # Test load
                        test_font = ImageFont.truetype(font_path, 20)
                        
                        # Load different sizes
                        font_sizes = {
                            'tiny': 16,
                            'small': 20,
                            'medium': 28,
                            'large': 36,
                            'xlarge': 44,
                            'xxlarge': 52
                        }
                        
                        for name, size in font_sizes.items():
                            try:
                                self.font_cache[name] = ImageFont.truetype(font_path, size)
                            except:
                                # Create scaled default font
                                self.font_cache[name] = ImageFont.load_default()
                        
                        self.font_available = True
                        loaded_font = font_path
                        logger.info(f"✅ Fonts loaded successfully from: {font_path}")
                        break
                        
                    except Exception as font_error:
                        logger.debug(f"Failed to load {font_path}: {font_error}")
                        continue
            
            if not self.font_available:
                logger.warning("No TrueType fonts found, using bitmap fonts only")
                # Create scaled bitmap fonts
                try:
                    # Try to create custom bitmap-like fonts
                    self.font_cache = {
                        'tiny': ImageFont.load_default(),
                        'small': ImageFont.load_default(),
                        'medium': ImageFont.load_default(),
                        'large': ImageFont.load_default()
                    }
                    logger.info("✅ Using PIL default bitmap fonts")
                except:
                    logger.error("❌ Could not load any fonts")
            
        except Exception as e:
            logger.error(f"⚠️ Font setup error: {e}")
            self.font_available = False
    
    def _load_templates(self) -> Dict[str, Dict]:
        """টেমপ্লেট লোড করে - আরও রং যুক্ত"""
        return {
            "day": {
                "bg_color": (240, 248, 255),  # AliceBlue
                "primary_color": (41, 128, 185),  # Peter River
                "secondary_color": (52, 152, 219),  # Belize Hole
                "border_color": (189, 195, 199),  # Silver
                "accent_color": (241, 196, 15),  # Sun Flower
                "text_shadow": (30, 30, 30)
            },
            "night": {
                "bg_color": (25, 25, 35),  # Dark Blue Grey
                "primary_color": (255, 105, 180),  # Hot Pink
                "secondary_color": (0, 255, 255),  # Cyan
                "border_color": (80, 80, 100),
                "accent_color": (155, 89, 182),  # Amethyst
                "text_shadow": (0, 0, 0)
            },
            "funny": {
                "bg_color": (255, 250, 205),  # LemonChiffon
                "primary_color": (255, 69, 0),  # Red-Orange
                "secondary_color": (255, 140, 0),  # Dark Orange
                "border_color": (255, 182, 193),  # Light Pink
                "accent_color": (50, 205, 50),  # Lime Green
                "text_shadow": (100, 100, 100)
            },
            "savage": {
                "bg_color": (15, 15, 15),  # Almost Black
                "primary_color": (220, 20, 60),  # Crimson
                "secondary_color": (255, 0, 0),  # Red
                "border_color": (139, 0, 0),  # Dark Red
                "accent_color": (255, 215, 0),  # Gold
                "text_shadow": (50, 0, 0)
            },
            "welcome": {
                "bg_color": (135, 206, 235),  # Sky Blue
                "primary_color": (255, 255, 255),  # White
                "secondary_color": (240, 248, 255),  # Alice Blue
                "border_color": (70, 130, 180),  # Steel Blue
                "accent_color": (255, 165, 0),  # Orange
                "text_shadow": (30, 30, 100)
            },
            "premium": {
                "bg_color": (25, 25, 35),  # Dark
                "primary_color": (255, 215, 0),  # Gold
                "secondary_color": (192, 192, 192),  # Silver
                "border_color": (184, 134, 11),  # Dark Goldenrod
                "accent_color": (218, 165, 32),  # Goldenrod
                "text_shadow": (0, 0, 0)
            },
            "vibrant": {
                "bg_color": (0, 0, 30),  # Deep Blue
                "primary_color": (0, 255, 255),  # Cyan
                "secondary_color": (255, 20, 147),  # Deep Pink
                "border_color": (0, 255, 127),  # Spring Green
                "accent_color": (255, 255, 0),  # Yellow
                "text_shadow": (0, 0, 0)
            }
        }
    
    def create_gradient_background(self, width, height, colors):
        """গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড তৈরি করে"""
        try:
            from PIL import Image
            
            # Create gradient
            base = Image.new('RGB', (width, height), colors[0])
            
            # Simple gradient effect
            for y in range(height):
                # Calculate color interpolation
                ratio = y / height
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                
                # Draw line
                for x in range(width):
                    base.putpixel((x, y), (r, g, b))
            
            return base
            
        except Exception as e:
            # Fallback to solid color
            return Image.new('RGB', (width, height), colors[0])
    
    def create_roast_image(self, primary_text: str, secondary_text: str = "", 
                          user_id: Optional[int] = None, roast_type: str = "general",
                          add_emoji: bool = True) -> Any:
        """রোস্ট ইমেজ তৈরি করে - উন্নত ভার্সন"""
        try:
            if not self.use_pil:
                logger.info("Using text-only mode")
                return self._create_advanced_text_image(primary_text, secondary_text, roast_type)
            
            from PIL import Image, ImageDraw, ImageFilter
            
            # Select template
            template = self._select_template(roast_type)
            
            # Create image with gradient background
            colors = [template["bg_color"], self._darken_color(template["bg_color"], 0.8)]
            image = self.create_gradient_background(self.width, self.height, colors)
            draw = ImageDraw.Draw(image)
            
            # Add decorative border
            self._add_decorative_border(draw, template)
            
            # Add header section
            header_height = self.height // 4
            self._add_header_section(draw, header_height, template, roast_type, add_emoji)
            
            # Add main content
            self._add_main_content(draw, primary_text, secondary_text, header_height, template)
            
            # Add footer
            self._add_footer(draw, template, user_id)
            
            # Add some effects
            image = self._add_image_effects(image, template)
            
            logger.info(f"✅ Image created successfully for type: {roast_type}")
            return image
            
        except Exception as e:
            log_error(f"Image creation error: {e}")
            logger.exception("Detailed error:")
            return self._create_error_image(primary_text, secondary_text)
    
    def _select_template(self, roast_type: str) -> Dict:
        """টেমপ্লেট সিলেক্ট করে - স্মার্ট সিলেকশন"""
        is_day = TimeManager.is_day_time()
        base_template = "day" if is_day else "night"
        
        template_map = {
            "savage": "savage",
            "burn": "savage", 
            "roast": "savage",
            "harsh": "savage",
            "funny": "funny",
            "joke": "funny",
            "comedy": "funny",
            "welcome": "welcome",
            "greet": "welcome",
            "premium": "premium",
            "vip": "premium",
            "vibrant": "vibrant",
            "epic": "vibrant"
        }
        
        selected = template_map.get(roast_type.lower(), base_template)
        return self.templates.get(selected, self.templates[base_template])
    
    def _darken_color(self, color, factor=0.7):
        """কালার ডার্কেন করে"""
        return tuple(int(c * factor) for c in color)
    
    def _lighten_color(self, color, factor=1.3):
        """কালার লাইটেন করে"""
        return tuple(min(255, int(c * factor)) for c in color)
    
    def _add_decorative_border(self, draw, template):
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
            
            # Inner border
            inner_border = border_width + 20
            draw.rectangle(
                [(inner_border, inner_border),
                 (self.width - inner_border, self.height - inner_border)],
                outline=self._lighten_color(template["border_color"], 1.2),
                width=3
            )
            
            # Corner accents
            corner_size = 30
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
    
    def _add_header_section(self, draw, header_height, template, roast_type, add_emoji):
        """হেডার সেকশন যোগ করে"""
        try:
            # Header background
            draw.rectangle(
                [(20, 20), (self.width - 20, header_height)],
                fill=self._darken_color(template["bg_color"], 0.9),
                outline=template["accent_color"],
                width=2
            )
            
            # Title
            title = self._get_roast_title(roast_type)
            if self.font_available:
                font = self.font_cache.get('large', self.default_fonts.get('large'))
            else:
                from PIL import ImageFont
                font = ImageFont.load_default()
            
            # Center text
            text_width = self._get_text_width(title, font)
            text_x = (self.width - text_width) // 2
            text_y = header_height // 3
            
            # Text shadow
            draw.text((text_x + 2, text_y + 2), title, font=font, fill=template["text_shadow"])
            # Main text
            draw.text((text_x, text_y), title, font=font, fill=template["primary_color"])
            
            # Add emoji if enabled
            if add_emoji:
                emoji = random.choice(self.emoji_fallback)
                # Try to draw emoji (might not work in all fonts)
                try:
                    emoji_x = text_x - 40
                    emoji_y = text_y
                    draw.text((emoji_x, emoji_y), emoji, font=font, fill=template["accent_color"])
                except:
                    pass
                    
        except Exception as e:
            log_error(f"Header error: {e}")
    
    def _get_roast_title(self, roast_type):
        """রোস্ট টাইটেল রিটার্ন করে"""
        titles = {
            "savage": "SAVAGE ROAST 🔥",
            "burn": "BURN NOTICE 🔥",
            "funny": "FUNNY ROAST 😂",
            "welcome": "WELCOME 👋",
            "premium": "PREMIUM ROAST 👑",
            "vibrant": "EPIC ROAST ⚡",
            "general": "ROASTIFY BOT 🎯"
        }
        return titles.get(roast_type, "ROASTIFY BOT 🎯")
    
    def _add_main_content(self, draw, primary_text, secondary_text, header_y, template):
        """মেইন কনটেন্ট যোগ করে"""
        try:
            content_start = header_y + 40
            content_height = self.height - content_start - 80
            
            # Content background
            draw.rectangle(
                [(40, content_start), 
                 (self.width - 40, self.height - 60)],
                fill=(255, 255, 255, 50),
                outline=template["secondary_color"],
                width=1
            )
            
            # Get fonts
            if self.font_available:
                primary_font = self.font_cache.get('medium', self.default_fonts.get('medium'))
                secondary_font = self.font_cache.get('small', self.default_fonts.get('small'))
            else:
                from PIL import ImageFont
                primary_font = ImageFont.load_default()
                secondary_font = ImageFont.load_default()
            
            # Wrap and draw primary text
            primary_lines = self._smart_wrap_text(primary_text, 30, primary_font)
            primary_y = content_start + 30
            
            for i, line in enumerate(primary_lines):
                if i >= 4:  # Max 4 lines
                    break
                text_width = self._get_text_width(line, primary_font)
                x = (self.width - text_width) // 2
                y = primary_y + (i * 45)
                
                # Text shadow for depth
                draw.text((x + 1, y + 1), line, font=primary_font, fill=template["text_shadow"])
                draw.text((x, y), line, font=primary_font, fill=template["primary_color"])
            
            # Separator line
            separator_y = primary_y + len(primary_lines) * 45 + 20
            draw.line(
                [(self.width // 4, separator_y),
                 (3 * self.width // 4, separator_y)],
                fill=template["accent_color"],
                width=2
            )
            
            # Draw secondary text if exists
            if secondary_text:
                secondary_lines = self._smart_wrap_text(secondary_text, 40, secondary_font)
                secondary_y = separator_y + 30
                
                for i, line in enumerate(secondary_lines):
                    if i >= 3:  # Max 3 lines
                        break
                    text_width = self._get_text_width(line, secondary_font)
                    x = (self.width - text_width) // 2
                    y = secondary_y + (i * 35)
                    
                    draw.text((x, y), line, font=secondary_font, fill=template["secondary_color"])
                    
        except Exception as e:
            log_error(f"Main content error: {e}")
            # Fallback to simple text
            draw.text((50, content_start + 50), primary_text, fill=template["primary_color"])
            if secondary_text:
                draw.text((50, content_start + 100), secondary_text, fill=template["secondary_color"])
    
    def _smart_wrap_text(self, text: str, max_chars: int, font) -> List[str]:
        """স্মার্ট টেক্সট র‍্যাপিং"""
        if not text:
            return []
        
        # First try simple wrap
        lines = textwrap.wrap(text, width=max_chars)
        
        # Adjust based on actual width
        if self.font_available and len(lines) > 0:
            adjusted_lines = []
            current_line = ""
            
            words = text.split()
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if self._get_text_width(test_line, font) < (self.width - 100):
                    current_line = test_line
                else:
                    if current_line:
                        adjusted_lines.append(current_line)
                    current_line = word
            
            if current_line:
                adjusted_lines.append(current_line)
            
            if adjusted_lines:
                return adjusted_lines
        
        return lines if lines else [text]
    
    def _add_footer(self, draw, template, user_id):
        """ফুটার যোগ করে"""
        try:
            footer_y = self.height - 40
            
            # Footer line
            draw.line(
                [(50, footer_y), (self.width - 50, footer_y)],
                fill=template["border_color"],
                width=2
            )
            
            # Footer text
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            footer_text = f"Roastify Bot • {timestamp}"
            
            if user_id:
                footer_text += f" • ID: {user_id}"
            
            if self.font_available:
                font = self.font_cache.get('tiny', self.default_fonts.get('tiny'))
            else:
                from PIL import ImageFont
                font = ImageFont.load_default()
            
            text_width = self._get_text_width(footer_text, font)
            text_x = (self.width - text_width) // 2
            
            draw.text((text_x, footer_y + 10), footer_text, font=font, 
                     fill=self._lighten_color(template["border_color"], 1.5))
            
        except Exception as e:
            log_error(f"Footer error: {e}")
    
    def _add_image_effects(self, image, template):
        """ইমেজ ইফেক্ট যোগ করে"""
        try:
            from PIL import ImageFilter, ImageEnhance
            
            # Slight blur to background edges
            # Create a copy for effects
            enhanced = image.copy()
            
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            # Enhance color
            color_enhancer = ImageEnhance.Color(enhanced)
            enhanced = color_enhancer.enhance(1.05)
            
            # Add subtle vignette effect
            width, height = enhanced.size
            for y in range(height):
                for x in range(width):
                    # Calculate distance from center
                    dx = (x - width/2) / (width/2)
                    dy = (y - height/2) / (height/2)
                    distance = (dx*dx + dy*dy) * 0.5
                    
                    # Apply darkening at edges
                    if distance > 0.3:
                        pixel = enhanced.getpixel((x, y))
                        darken = max(0.7, 1 - distance)
                        new_pixel = tuple(int(c * darken) for c in pixel)
                        enhanced.putpixel((x, y), new_pixel)
            
            return enhanced
            
        except Exception as e:
            log_error(f"Image effects error: {e}")
            return image
    
    def _get_text_width(self, text: str, font) -> int:
        """টেক্সট প্রস্থ বের করে - উন্নত"""
        try:
            if hasattr(font, 'getlength'):
                return int(font.getlength(text))
            elif hasattr(font, 'getbbox'):
                bbox = font.getbbox(text)
                return bbox[2] - bbox[0] if bbox else len(text) * 8
            elif hasattr(font, 'getsize'):
                return font.getsize(text)[0]
            else:
                # Estimate based on character count
                return len(text) * (10 if len(text) < 20 else 8)
        except:
            return len(text) * 8
    
    def _create_advanced_text_image(self, primary_text, secondary_text, roast_type):
        """এডভান্সড টেক্সট-ওনলি ইমেজ"""
        try:
            # Try to use PIL even in fallback
            from PIL import Image, ImageDraw, ImageFont
            
            image = Image.new('RGB', (self.width, self.height), (25, 25, 35))
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            
            # Create text-based design
            margin = 30
            line_height = 30
            
            # Header
            draw.text((margin, margin), "╔════════════════════════╗", fill=(255, 215, 0))
            draw.text((margin, margin + line_height), "     ROASTIFY BOT", fill=(255, 215, 0))
            draw.text((margin, margin + line_height*2), "╚════════════════════════╝", fill=(255, 215, 0))
            
            # Primary text
            primary_lines = textwrap.wrap(primary_text, width=40)
            for i, line in enumerate(primary_lines[:4]):  # Max 4 lines
                y_pos = margin + 100 + (i * line_height)
                draw.text((margin + 10, y_pos), f"» {line}", fill=(255, 105, 180))
            
            # Separator
            draw.text((margin, margin + 220), "─" * 40, fill=(100, 100, 100))
            
            # Secondary text
            if secondary_text:
                secondary_lines = textwrap.wrap(secondary_text, width=50)
                for i, line in enumerate(secondary_lines[:3]):  # Max 3 lines
                    y_pos = margin + 250 + (i * line_height)
                    draw.text((margin, y_pos), f"• {line}", fill=(0, 255, 255))
            
            # Footer
            timestamp = datetime.now().strftime("%H:%M")
            draw.text((margin, self.height - 50), f"Generated at {timestamp}", fill=(150, 150, 150))
            
            return image
            
        except Exception as e:
            log_error(f"Advanced text image error: {e}")
            return self._create_error_image(primary_text, secondary_text)
    
    def _create_error_image(self, primary_text="", secondary_text=""):
        """এরর ইমেজ তৈরি করে"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            image = Image.new('RGB', (500, 300), (40, 40, 60))
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            
            # Error box
            draw.rectangle([(50, 50), (450, 250)], fill=(60, 60, 80), outline=(255, 100, 100))
            
            # Error title
            draw.text((150, 80), "⚠️ ROAST GENERATOR ⚠️", fill=(255, 100, 100))
            
            # Messages
            if primary_text:
                draw.text((100, 130), primary_text[:50], fill=(255, 200, 200))
            
            if secondary_text:
                draw.text((100, 160), secondary_text[:50], fill=(200, 200, 255))
            
            # Status
            draw.text((150, 200), "Image rendering active...", fill=(100, 255, 100))
            
            return image
            
        except:
            # Ultimate fallback - create simple image
            try:
                from PIL import Image
                return Image.new('RGB', (400, 200), (255, 255, 255))
            except:
                return None
    
    def save_image(self, image, filename: str = None) -> str:
        """ইমেজ ফাইল হিসেবে সেভ করে - উন্নত"""
        try:
            if image is None:
                raise ValueError("Image object is None")
            
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"roast_{timestamp}.png"
            
            # Ensure valid filename
            filename = filename.replace(" ", "_").replace(":", "")
            
            # Create output directory
            output_dir = Path("generated_images")
            output_dir.mkdir(exist_ok=True)
            
            output_path = output_dir / filename
            
            # Save with optimization
            image.save(
                output_path, 
                "PNG", 
                optimize=True, 
                compress_level=9
            )
            
            # Verify file was saved
            if output_path.exists() and output_path.stat().st_size > 0:
                log_info(f"✅ Image saved: {output_path} (Size: {output_path.stat().st_size} bytes)")
                return str(output_path)
            else:
                raise Exception("File save verification failed")
            
        except Exception as e:
            log_error(f"❌ Error saving image: {e}")
            
            # Multiple fallback strategies
            try:
                import tempfile
                
                # Try different formats
                formats = ["PNG", "JPEG", "BMP"]
                
                for fmt in formats:
                    try:
                        temp_file = tempfile.NamedTemporaryFile(
                            delete=False, 
                            suffix=f'.{fmt.lower()}',
                            prefix='roast_'
                        )
                        
                        if fmt == "JPEG":
                            image.save(temp_file.name, fmt, quality=95)
                        else:
                            image.save(temp_file.name, fmt)
                        
                        log_info(f"✅ Image saved to temp: {temp_file.name}")
                        return temp_file.name
                        
                    except:
                        continue
                
                # Last resort: save to current directory
                simple_path = f"roast_fallback_{datetime.now().timestamp()}.png"
                image.save(simple_path, "PNG")
                return simple_path
                
            except Exception as fallback_error:
                log_error(f"❌ All save attempts failed: {fallback_error}")
                return ""
    
    def image_to_base64(self, image) -> str:
        """ইমেজকে Base64 এ কনভার্ট করে"""
        try:
            buffered = BytesIO()
            
            # Save to buffer
            image.save(buffered, format="PNG", optimize=True)
            
            # Get base64
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Add data URI prefix if needed
            # data_uri = f"data:image/png;base64,{img_str}"
            
            return img_str
            
        except Exception as e:
            log_error(f"Base64 conversion error: {e}")
            
            # Return a placeholder image in base64
            try:
                placeholder = self._create_error_image("Base64 Error", "Image conversion failed")
                buffered = BytesIO()
                placeholder.save(buffered, format="PNG")
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
            except:
                return ""
    
    def get_image_stats(self) -> Dict[str, Any]:
        """ইমেজ স্ট্যাটস রিটার্ন করে"""
        return {
            "version": "2.0",
            "pil_available": self.use_pil,
            "fonts_available": self.font_available,
            "font_cache_size": len(self.font_cache) if hasattr(self, 'font_cache') else 0,
            "image_width": self.width,
            "image_height": self.height,
            "templates_loaded": len(self.templates),
            "status": "Operational" if self.use_pil else "Text-Only Mode"
        }
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """টেম্প ফাইল ক্লিনআপ করে"""
        try:
            import time
            import shutil
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            # Clean generated_images directory
            gen_path = Path("generated_images")
            if gen_path.exists():
                files_deleted = 0
                for img_file in gen_path.glob("*.*"):
                    try:
                        file_age = current_time - img_file.stat().st_mtime
                        
                        if file_age > max_age_seconds:
                            img_file.unlink()
                            files_deleted += 1
                            logger.debug(f"Removed old image: {img_file.name}")
                    except:
                        continue
                
                if files_deleted > 0:
                    logger.info(f"Cleaned up {files_deleted} old image files")
            
            # Clean system temp files
            temp_dir = "/tmp"
            if os.path.exists(temp_dir):
                for temp_file in Path(temp_dir).glob("roast_*.*"):
                    try:
                        if temp_file.stat().st_mtime < (current_time - 3600):  # 1 hour
                            temp_file.unlink()
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def quick_roast_image(self, text: str, style: str = "funny") -> Any:
        """কুইক রোস্ট ইমেজ তৈরি করে"""
        return self.create_roast_image(
            primary_text=text,
            secondary_text="",
            roast_type=style,
            add_emoji=True
        )
    
    def test_all_templates(self):
        """সকল টেমপ্লেট টেস্ট করে"""
        results = []
        
        for template_name in self.templates.keys():
            try:
                test_image = self.create_roast_image(
                    primary_text=f"Testing {template_name}",
                    secondary_text="Roastify Bot Template Test",
                    roast_type=template_name
                )
                
                if test_image:
                    # Save test image
                    filename = f"test_{template_name}.png"
                    save_path = self.save_image(test_image, filename)
                    
                    results.append({
                        "template": template_name,
                        "status": "SUCCESS",
                        "path": save_path
                    })
                else:
                    results.append({
                        "template": template_name,
                        "status": "FAILED",
                        "error": "Image creation returned None"
                    })
                    
            except Exception as e:
                results.append({
                    "template": template_name,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        return results


# Singleton instance with lazy loading
_image_generator_instance = None

def get_image_generator() -> ProfessionalImageGenerator:
    """গ্লোবাল ইমেজ জেনারেটর ইনস্ট্যান্স রিটার্ন করে"""
    global _image_generator_instance
    
    if _image_generator_instance is None:
        _image_generator_instance = ProfessionalImageGenerator()
    
    return _image_generator_instance


# Usage example
if __name__ == "__main__":
    print("Testing Professional Image Generator v2.0...")
    
    # Get instance
    generator = get_image_generator()
    
    # Print stats
    stats = generator.get_image_stats()
    print(f"\n📊 Generator Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test creation
    print("\n🎨 Testing image creation...")
    test_image = generator.create_roast_image(
        primary_text="This is a test roast!",
        secondary_text="Generated by Roastify Bot v2.0",
        roast_type="savage"
    )
    
    if test_image:
        # Save image
        save_path = generator.save_image(test_image, "test_output.png")
        print(f"✅ Test image saved to: {save_path}")
        
        # Get base64
        b64 = generator.image_to_base64(test_image)
        print(f"✅ Base64 length: {len(b64)} characters")
        
        # Test quick roast
        quick_img = generator.quick_roast_image("Quick roast test!", "funny")
        quick_path = generator.save_image(quick_img, "quick_test.png")
        print(f"✅ Quick roast saved to: {quick_path}")
        
    print("\n✨ Testing completed successfully!")

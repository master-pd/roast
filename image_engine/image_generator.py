#!/usr/bin/env python3
"""
🎨 Advanced Image Generator for Roastify Bot
✅ Professional | Multiple Templates | Random Designs | No Errors
"""

import os
import sys
import random
import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from io import BytesIO

# Import PIL
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance, ImageChops
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from utils.logger import logger
from utils.helpers import Helpers

# ==================== ADVANCED TEMPLATE MANAGER ====================

class AdvancedTemplateManager:
    """Advanced template management with random designs"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.user_history = {}
        
    def _load_templates(self):
        """Load all templates from JSON files"""
        templates = {
            "modern": self._create_modern_template(),
            "vintage": self._create_vintage_template(),
            "cyberpunk": self._create_cyberpunk_template(),
            "gradient": self._create_gradient_template(),
            "minimal": self._create_minimal_template(),
            "neon": self._create_neon_template(),
            "elegant": self._create_elegant_template(),
            "funky": self._create_funky_template(),
            "dark": self._create_dark_template(),
            "light": self._create_light_template()
        }
        
        # Load custom templates if available
        templates_path = Path("assets/templates")
        if templates_path.exists():
            for template_file in templates_path.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template_name = template_file.stem
                        templates[template_name] = template_data
                except Exception as e:
                    logger.warning(f"Failed to load template {template_file}: {e}")
        
        return templates
    
    def get_random_template(self, user_id: int = None):
        """Get a random template for user"""
        if user_id and user_id in self.user_history:
            # Try to give a different template than last time
            last_template = self.user_history[user_id]
            available_templates = [t for t in self.templates.keys() if t != last_template]
            if available_templates:
                template_name = random.choice(available_templates)
            else:
                template_name = random.choice(list(self.templates.keys()))
        else:
            template_name = random.choice(list(self.templates.keys()))
        
        template = self.templates[template_name].copy()
        
        # Add some random variations
        template = self._add_random_variations(template)
        
        if user_id:
            self.user_history[user_id] = template_name
        
        return template
    
    def _add_random_variations(self, template: Dict) -> Dict:
        """Add random variations to template"""
        # Random color variations
        if "colors" in template:
            color_variations = [
                {"primary": (255, 107, 53), "secondary": (0, 180, 216)},  # Original
                {"primary": (239, 71, 111), "secondary": (6, 214, 160)},   # Pink/Teal
                {"primary": (255, 209, 102), "secondary": (17, 138, 178)}, # Yellow/Blue
                {"primary": (155, 93, 229), "secondary": (41, 171, 226)},  # Purple/Blue
                {"primary": (255, 94, 87), "secondary": (255, 147, 39)},   # Red/Orange
            ]
            
            variation = random.choice(color_variations)
            template["primary_color"] = variation["primary"]
            template["secondary_color"] = variation["secondary"]
        
        # Random effects
        effects = ["shadow", "glow", "gradient_text", "outline", "blur_background"]
        selected_effects = random.sample(effects, random.randint(1, 3))
        template["effects"] = selected_effects
        
        # Random font size variations
        if "font_size" in template:
            template["font_size"] += random.randint(-5, 5)
        
        return template
    
    # ========== TEMPLATE CREATORS ==========
    
    def _create_modern_template(self):
        return {
            "name": "modern",
            "background": "gradient",
            "primary_color": (255, 107, 53),
            "secondary_color": (0, 180, 216),
            "font": "modern.ttf",
            "font_size": 48,
            "sub_font_size": 24,
            "position": {"x": 300, "y": 200},
            "sub_position": {"x": 300, "y": 300},
            "effects": ["shadow", "gradient_text"],
            "border_style": "rounded",
            "border_color": (255, 255, 255, 50),
            "blur_radius": 0
        }
    
    def _create_vintage_template(self):
        return {
            "name": "vintage",
            "background": "texture",
            "primary_color": (139, 69, 19),
            "secondary_color": (160, 82, 45),
            "font": "serif.ttf",
            "font_size": 42,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 180},
            "sub_position": {"x": 300, "y": 280},
            "effects": ["texture_overlay", "vignette"],
            "border_style": "ornate",
            "border_color": (101, 67, 33, 100),
            "blur_radius": 1
        }
    
    def _create_cyberpunk_template(self):
        return {
            "name": "cyberpunk",
            "background": "grid",
            "primary_color": (0, 255, 255),
            "secondary_color": (255, 0, 255),
            "font": "tech.ttf",
            "font_size": 52,
            "sub_font_size": 26,
            "position": {"x": 300, "y": 190},
            "sub_position": {"x": 300, "y": 290},
            "effects": ["glow", "scan_lines", "noise"],
            "border_style": "neon",
            "border_color": (0, 255, 255, 100),
            "blur_radius": 0
        }
    
    def _create_gradient_template(self):
        return {
            "name": "gradient",
            "background": "gradient_rainbow",
            "primary_color": (255, 255, 255),
            "secondary_color": (200, 200, 200),
            "font": "sans.ttf",
            "font_size": 46,
            "sub_font_size": 23,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "effects": ["gradient_text", "shadow"],
            "border_style": "simple",
            "border_color": (255, 255, 255, 30),
            "blur_radius": 0
        }
    
    def _create_minimal_template(self):
        return {
            "name": "minimal",
            "background": "solid",
            "primary_color": (0, 0, 0),
            "secondary_color": (100, 100, 100),
            "font": "sans.ttf",
            "font_size": 44,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 185},
            "sub_position": {"x": 300, "y": 285},
            "effects": [],
            "border_style": "none",
            "border_color": (0, 0, 0, 0),
            "blur_radius": 0
        }
    
    def _create_neon_template(self):
        return {
            "name": "neon",
            "background": "dark",
            "primary_color": (255, 20, 147),
            "secondary_color": (0, 191, 255),
            "font": "bold.ttf",
            "font_size": 50,
            "sub_font_size": 25,
            "position": {"x": 300, "y": 200},
            "sub_position": {"x": 300, "y": 300},
            "effects": ["neon_glow", "reflection"],
            "border_style": "glowing",
            "border_color": (255, 20, 147, 80),
            "blur_radius": 2
        }
    
    def _create_elegant_template(self):
        return {
            "name": "elegant",
            "background": "marble",
            "primary_color": (75, 0, 130),
            "secondary_color": (138, 43, 226),
            "font": "elegant.ttf",
            "font_size": 45,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 190},
            "sub_position": {"x": 300, "y": 290},
            "effects": ["emboss", "gold_border"],
            "border_style": "decorative",
            "border_color": (255, 215, 0, 100),
            "blur_radius": 1
        }
    
    def _create_funky_template(self):
        return {
            "name": "funky",
            "background": "pattern",
            "primary_color": (255, 165, 0),
            "secondary_color": (0, 128, 0),
            "font": "funky.ttf",
            "font_size": 47,
            "sub_font_size": 24,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "effects": ["dotted", "wavy"],
            "border_style": "dashed",
            "border_color": (255, 69, 0, 100),
            "blur_radius": 0
        }
    
    def _create_dark_template(self):
        return {
            "name": "dark",
            "background": "black",
            "primary_color": (255, 255, 255),
            "secondary_color": (150, 150, 150),
            "font": "sans.ttf",
            "font_size": 46,
            "sub_font_size": 23,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "effects": ["shadow", "gradient"],
            "border_style": "thin",
            "border_color": (50, 50, 50, 100),
            "blur_radius": 0
        }
    
    def _create_light_template(self):
        return {
            "name": "light",
            "background": "white",
            "primary_color": (0, 0, 0),
            "secondary_color": (50, 50, 50),
            "font": "clean.ttf",
            "font_size": 44,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 190},
            "sub_position": {"x": 300, "y": 290},
            "effects": ["soft_shadow", "highlight"],
            "border_style": "simple",
            "border_color": (200, 200, 200, 100),
            "blur_radius": 0
        }

# ==================== ADVANCED IMAGE GENERATOR ====================

class AdvancedImageGenerator:
    """Advanced image generator with multiple templates and effects"""
    
    def __init__(self):
        if not PIL_AVAILABLE:
            logger.error("PIL/Pillow not installed! Please install: pip install pillow")
            self.available = False
            return
        
        self.available = True
        self.width = Config.IMAGE_WIDTH
        self.height = Config.IMAGE_HEIGHT
        
        # Initialize managers
        self.template_manager = AdvancedTemplateManager()
        
        # Setup directories
        self._setup_directories()
        
        # Load assets
        self._load_assets()
        
        logger.info("✅ Advanced Image Generator initialized")
    
    def _setup_directories(self):
        """Create necessary directories"""
        directories = [
            "assets",
            "assets/fonts",
            "assets/backgrounds",
            "assets/templates",
            "generated",
            "temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def _load_assets(self):
        """Load fonts and backgrounds"""
        # Fonts
        self.fonts = {}
        fonts_dir = Path("assets/fonts")
        if fonts_dir.exists():
            for font_file in fonts_dir.glob("*.ttf"):
                try:
                    font_name = font_file.stem
                    self.fonts[font_name] = str(font_file)
                except:
                    continue
        
        # Backgrounds
        self.backgrounds = {}
        bg_dir = Path("assets/backgrounds")
        if bg_dir.exists():
            for bg_file in bg_dir.glob("*.png"):
                try:
                    bg_name = bg_file.stem
                    self.backgrounds[bg_name] = str(bg_file)
                except:
                    continue
    
    def create_roast_image(self, primary_text: str, secondary_text: str = "", 
                          user_id: int = None, category: str = "funny") -> Image.Image:
        """
        Create a roast image with random template
        Returns PIL Image object
        """
        if not self.available:
            return self._create_fallback_image(primary_text, secondary_text)
        
        try:
            # Get random template
            template = self.template_manager.get_random_template(user_id)
            
            # Create base image
            image = self._create_background(template)
            
            # Apply background effects
            image = self._apply_background_effects(image, template)
            
            # Add text
            image = self._add_text(image, primary_text, secondary_text, template)
            
            # Add decorative elements
            image = self._add_decorations(image, template, category)
            
            # Final effects
            image = self._apply_final_effects(image, template)
            
            return image
            
        except Exception as e:
            logger.error(f"Error creating roast image: {e}")
            return self._create_error_image(primary_text)
    
    def _create_background(self, template: Dict) -> Image.Image:
        """Create background based on template"""
        bg_type = template.get("background", "gradient")
        
        # Check if custom background exists
        if bg_type in self.backgrounds:
            try:
                bg_image = Image.open(self.backgrounds[bg_type]).convert("RGBA")
                bg_image = bg_image.resize((self.width, self.height))
                return bg_image
            except:
                pass
        
        # Create background based on type
        if bg_type == "gradient":
            return self._create_gradient_background(template)
        elif bg_type == "gradient_rainbow":
            return self._create_rainbow_gradient()
        elif bg_type == "grid":
            return self._create_grid_background()
        elif bg_type == "texture":
            return self._create_texture_background()
        elif bg_type == "pattern":
            return self._create_pattern_background()
        elif bg_type == "dark":
            return Image.new('RGBA', (self.width, self.height), (20, 20, 30, 255))
        elif bg_type == "light":
            return Image.new('RGBA', (self.width, self.height), (240, 240, 245, 255))
        elif bg_type == "solid":
            color = template.get("primary_color", (25, 25, 35))
            return Image.new('RGBA', (self.width, self.height), color + (255,))
        else:
            # Default gradient
            return self._create_gradient_background(template)
    
    def _create_gradient_background(self, template: Dict) -> Image.Image:
        """Create gradient background"""
        image = Image.new('RGBA', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Get colors from template or generate random
        color1 = template.get("primary_color", (random.randint(0, 100), 
                                                random.randint(0, 100), 
                                                random.randint(100, 200)))
        color2 = template.get("secondary_color", (random.randint(100, 200), 
                                                  random.randint(100, 200), 
                                                  random.randint(0, 100)))
        
        # Create vertical gradient
        for y in range(self.height):
            ratio = y / self.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b, 255))
        
        return image
    
    def _create_rainbow_gradient(self) -> Image.Image:
        """Create rainbow gradient background"""
        image = Image.new('RGBA', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        colors = [
            (255, 0, 0),    # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (148, 0, 211)   # Violet
        ]
        
        segment_height = self.height // len(colors)
        
        for i, color in enumerate(colors):
            y_start = i * segment_height
            y_end = (i + 1) * segment_height if i < len(colors) - 1 else self.height
            
            # Create gradient within segment
            for y in range(y_start, y_end):
                ratio = (y - y_start) / (y_end - y_start)
                next_color = colors[(i + 1) % len(colors)] if i < len(colors) - 1 else colors[0]
                
                r = int(color[0] * (1 - ratio) + next_color[0] * ratio)
                g = int(color[1] * (1 - ratio) + next_color[1] * ratio)
                b = int(color[2] * (1 - ratio) + next_color[2] * ratio)
                
                draw.line([(0, y), (self.width, y)], fill=(r, g, b, 255))
        
        return image
    
    def _create_grid_background(self) -> Image.Image:
        """Create grid background"""
        image = Image.new('RGBA', (self.width, self.height), (10, 10, 20, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw grid lines
        grid_size = 40
        line_color = (30, 30, 50, 150)
        
        for x in range(0, self.width, grid_size):
            draw.line([(x, 0), (x, self.height)], fill=line_color, width=1)
        
        for y in range(0, self.height, grid_size):
            draw.line([(0, y), (self.width, y)], fill=line_color, width=1)
        
        # Add glow points
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(2, 5)
            color = (random.randint(0, 255), random.randint(0, 255), 255, 150)
            draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=color)
        
        return image
    
    def _create_texture_background(self) -> Image.Image:
        """Create textured background"""
        image = Image.new('RGBA', (self.width, self.height), (139, 69, 19, 255))
        draw = ImageDraw.Draw(image)
        
        # Add noise for texture
        for _ in range(5000):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            darkness = random.randint(0, 50)
            draw.point((x, y), fill=(139 - darkness, 69 - darkness//2, 19 - darkness//3, 255))
        
        return image
    
    def _create_pattern_background(self) -> Image.Image:
        """Create patterned background"""
        image = Image.new('RGBA', (self.width, self.height), (255, 245, 230, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw circles pattern
        pattern_size = 80
        colors = [(255, 200, 200, 100), (200, 255, 200, 100), (200, 200, 255, 100)]
        
        for x in range(0, self.width + pattern_size, pattern_size):
            for y in range(0, self.height + pattern_size, pattern_size):
                offset_x = (y // pattern_size) % 2 * pattern_size // 2
                center_x = x + offset_x
                center_y = y
                
                color = random.choice(colors)
                radius = pattern_size // 4
                
                draw.ellipse([(center_x - radius, center_y - radius),
                            (center_x + radius, center_y + radius)], 
                           fill=color)
        
        return image
    
    def _apply_background_effects(self, image: Image.Image, template: Dict) -> Image.Image:
        """Apply background effects"""
        effects = template.get("effects", [])
        
        for effect in effects:
            if effect == "blur_background" and template.get("blur_radius", 0) > 0:
                image = image.filter(ImageFilter.GaussianBlur(template["blur_radius"]))
            elif effect == "vignette":
                image = self._add_vignette(image)
            elif effect == "noise":
                image = self._add_noise(image, intensity=3)
            elif effect == "scan_lines":
                image = self._add_scan_lines(image)
            elif effect == "texture_overlay":
                image = self._add_texture_overlay(image)
        
        return image
    
    def _add_text(self, image: Image.Image, primary_text: str, secondary_text: str, 
                 template: Dict) -> Image.Image:
        """Add text to image with effects"""
        draw = ImageDraw.Draw(image)
        
        # Get font
        font_name = template.get("font", "sans.ttf")
        font_size = template.get("font_size", 48)
        font = self._get_font(font_name, font_size)
        
        # Split text
        primary_lines = Helpers.split_text_for_image(primary_text, 25)
        secondary_lines = Helpers.split_text_for_image(secondary_text, 35) if secondary_text else []
        
        # Get positions
        primary_pos = template.get("position", {"x": self.width//2, "y": self.height//2 - 50})
        secondary_pos = template.get("sub_position", {"x": self.width//2, "y": self.height//2 + 50})
        
        # Draw primary text
        primary_color = template.get("primary_color", (255, 255, 255))
        self._draw_text_with_effects(draw, primary_lines, font, primary_pos, 
                                    primary_color, template, is_primary=True)
        
        # Draw secondary text
        if secondary_lines:
            sub_font_size = template.get("sub_font_size", font_size // 2)
            sub_font = self._get_font(font_name, sub_font_size)
            secondary_color = template.get("secondary_color", (200, 200, 200))
            self._draw_text_with_effects(draw, secondary_lines, sub_font, secondary_pos,
                                        secondary_color, template, is_primary=False)
        
        return image
    
    def _get_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """Get font with fallback"""
        # Try to load from assets
        if font_name in self.fonts:
            try:
                return ImageFont.truetype(self.fonts[font_name], size)
            except:
                pass
        
        # Try system fonts
        font_paths = [
            font_name,
            f"fonts/{font_name}",
            f"assets/fonts/{font_name}",
        ]
        
        for path in font_paths:
            try:
                if Path(path).exists():
                    return ImageFont.truetype(path, size)
            except:
                continue
        
        # Fallback to default
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default(size)
    
    def _draw_text_with_effects(self, draw: ImageDraw, lines: List[str], font: ImageFont.FreeTypeFont,
                               position: Dict, color: Tuple, template: Dict, is_primary: bool = True):
        """Draw text with various effects"""
        effects = template.get("effects", [])
        
        # Calculate text block dimensions
        line_height = font.size + 10
        total_height = len(lines) * line_height
        start_y = position["y"] - (total_height // 2)
        
        for i, line in enumerate(lines):
            y_pos = start_y + (i * line_height)
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_pos = position["x"] - (text_width // 2)
            
            # Apply effects
            if "shadow" in effects and is_primary:
                shadow_color = (0, 0, 0, 150)
                shadow_offset = 5
                draw.text((x_pos + shadow_offset, y_pos + shadow_offset), 
                         line, font=font, fill=shadow_color)
            
            if "outline" in effects and is_primary:
                outline_size = 2
                outline_color = (0, 0, 0, 200)
                for dx in range(-outline_size, outline_size + 1):
                    for dy in range(-outline_size, outline_size + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x_pos + dx, y_pos + dy), 
                                     line, font=font, fill=outline_color)
            
            if "glow" in effects and is_primary:
                glow_color = (color[0], color[1], color[2], 100)
                glow_size = 3
                for dx in range(-glow_size, glow_size + 1):
                    for dy in range(-glow_size, glow_size + 1):
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist <= glow_size:
                            alpha = int(100 * (1 - dist/glow_size))
                            glow_color = (color[0], color[1], color[2], alpha)
                            draw.text((x_pos + dx, y_pos + dy), 
                                     line, font=font, fill=glow_color)
            
            if "gradient_text" in effects and is_primary:
                # Create gradient text
                for j, char in enumerate(line):
                    char_bbox = draw.textbbox((0, 0), char, font=font)
                    char_width = char_bbox[2] - char_bbox[0]
                    
                    # Calculate gradient color
                    ratio = j / max(len(line) - 1, 1)
                    r = int(color[0] * (1 - ratio) + random.randint(0, 255) * ratio)
                    g = int(color[1] * (1 - ratio) + random.randint(0, 255) * ratio)
                    b = int(color[2] * (1 - ratio) + random.randint(0, 255) * ratio)
                    
                    draw.text((x_pos + sum([draw.textbbox((0, 0), line[k], font=font)[2] - 
                                           draw.textbbox((0, 0), line[k], font=font)[0] 
                                           for k in range(j)]), y_pos), 
                             char, font=font, fill=(r, g, b))
            else:
                # Draw normal text
                draw.text((x_pos, y_pos), line, font=font, fill=color)
    
    def _add_decorations(self, image: Image.Image, template: Dict, category: str) -> Image.Image:
        """Add decorative elements"""
        draw = ImageDraw.Draw(image)
        
        border_style = template.get("border_style", "none")
        border_color = template.get("border_color", (255, 255, 255, 100))
        
        if border_style == "rounded":
            # Draw rounded rectangle border
            border_width = 20
            draw.rounded_rectangle(
                [(border_width, border_width), 
                 (self.width - border_width, self.height - border_width)],
                radius=30,
                outline=border_color,
                width=3
            )
        elif border_style == "neon":
            # Draw neon border
            border_width = 10
            for i in range(3):
                alpha = 255 - i * 80
                neon_color = border_color[:3] + (alpha,)
                draw.rectangle(
                    [(border_width + i, border_width + i), 
                     (self.width - border_width - i, self.height - border_width - i)],
                    outline=neon_color,
                    width=1
                )
        elif border_style == "decorative":
            # Add corner decorations
            corner_size = 40
            for corner in [(0, 0), (self.width - corner_size, 0),
                          (0, self.height - corner_size), 
                          (self.width - corner_size, self.height - corner_size)]:
                x, y = corner
                # Draw fancy corner
                draw.line([(x + 10, y), (x + corner_size, y)], fill=border_color, width=3)
                draw.line([(x, y + 10), (x, y + corner_size)], fill=border_color, width=3)
        
        # Add category icon
        icons = {
            "funny": "😂",
            "savage": "🔥",
            "general": "💎"
        }
        
        if category in icons:
            # We'll add emoji as text
            emoji_font = self._get_font("arial.ttf", 60)
            emoji = icons[category]
            bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
            text_width = bbox[2] - bbox[0]
            
            draw.text((self.width - text_width - 20, 20), 
                     emoji, font=emoji_font, fill=border_color)
        
        return image
    
    def _apply_final_effects(self, image: Image.Image, template: Dict) -> Image.Image:
        """Apply final effects to image"""
        effects = template.get("effects", [])
        
        if "emboss" in effects:
            image = image.filter(ImageFilter.EMBOSS)
        
        if "sharpen" in effects:
            image = image.filter(ImageFilter.SHARPEN)
        
        if "smooth" in effects:
            image = image.filter(ImageFilter.SMOOTH)
        
        # Adjust brightness/contrast
        if "highlight" in effects:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
        
        return image
    
    def _add_vignette(self, image: Image.Image) -> Image.Image:
        """Add vignette effect"""
        width, height = image.size
        
        # Create vignette mask
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw white ellipse
        ellipse_bbox = [(-width//2, -height//2), (width*3//2, height*3//2)]
        draw.ellipse(ellipse_bbox, fill=255)
        
        # Apply Gaussian blur
        mask = mask.filter(ImageFilter.GaussianBlur(width//4))
        
        # Create vignette overlay
        vignette = Image.new('RGBA', (width, height), (0, 0, 0, 150))
        
        # Composite with original
        result = Image.composite(image, vignette, mask)
        return result
    
    def _add_noise(self, image: Image.Image, intensity: int = 5) -> Image.Image:
        """Add noise/grain effect"""
        noise = Image.new('RGBA', image.size)
        pixels = noise.load()
        
        for x in range(image.width):
            for y in range(image.height):
                if random.random() < 0.1:  # 10% pixels have noise
                    gray = random.randint(0, intensity)
                    alpha = random.randint(50, 150)
                    pixels[x, y] = (gray, gray, gray, alpha)
        
        return Image.alpha_composite(image, noise)
    
    def _add_scan_lines(self, image: Image.Image) -> Image.Image:
        """Add scan lines effect"""
        draw = ImageDraw.Draw(image)
        
        # Draw horizontal lines
        for y in range(0, image.height, 4):
            draw.line([(0, y), (image.width, y)], fill=(0, 255, 0, 30), width=1)
        
        return image
    
    def _add_texture_overlay(self, image: Image.Image) -> Image.Image:
        """Add texture overlay"""
        # Create a simple texture pattern
        texture = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(texture)
        
        # Add random dots
        for _ in range(1000):
            x = random.randint(0, image.width)
            y = random.randint(0, image.height)
            radius = random.randint(1, 3)
            alpha = random.randint(10, 50)
            draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], 
                        fill=(139, 69, 19, alpha))
        
        return Image.alpha_composite(image, texture)
    
    def image_to_bytes(self, image: Image.Image) -> BytesIO:
        """Convert PIL image to bytes"""
        buffered = BytesIO()
        image.save(buffered, format="PNG", optimize=True, quality=95)
        buffered.seek(0)
        return buffered
    
    def _create_fallback_image(self, primary_text: str, secondary_text: str = "") -> Image.Image:
        """Create simple fallback image when PIL is not available"""
        image = Image.new('RGB', (self.width, self.height), (25, 25, 35))
        draw = ImageDraw.Draw(image)
        
        draw.text((50, 50), "ROASTIFY BOT", fill=(255, 107, 53))
        draw.text((50, 100), primary_text[:100], fill=(255, 255, 255))
        
        if secondary_text:
            draw.text((50, 150), secondary_text[:80], fill=(0, 180, 216))
        
        return image
    
    def _create_error_image(self, text: str) -> Image.Image:
        """Create error image"""
        image = Image.new('RGB', (self.width, self.height), (50, 0, 0))
        draw = ImageDraw.Draw(image)
        
        draw.text((50, 100), "Error creating image", fill=(255, 100, 100))
        draw.text((50, 150), text[:100], fill=(255, 255, 255))
        
        return image

# ==================== SIMPLE HELPER FUNCTIONS ====================

class SimpleHelpers:
    """Simple helper functions"""
    
    @staticmethod
    def split_text_for_image(text: str, max_length: int) -> List[str]:
        """Split text into lines for image"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_length:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text[:max_length]]
    
    @staticmethod
    def get_time_based_theme() -> Dict:
        """Get theme based on time of day"""
        hour = datetime.now().hour
        
        if 6 <= hour < 18:
            return {"theme": "day", "brightness": 1.0}
        else:
            return {"theme": "night", "brightness": 0.7}

# ==================== EXPORT ====================

# Create instances
if 'Helpers' not in globals():
    Helpers = SimpleHelpers

# Create the main image generator
ImageGenerator = AdvancedImageGenerator
#image_generator = AdvancedImageGenerator()

def get_image_generator():
    """Get the image generator instance"""
    return image_generator

# ==================== TEST FUNCTION ====================

def test_image_generator():
    """Test the image generator"""
    if not image_generator.available:
        print("❌ PIL not installed. Install with: pip install pillow")
        return
    
    print("🎨 Testing Image Generator...")
    
    # Create test image
    test_image = image_generator.create_roast_image(
        primary_text="এটি একটি টেস্ট রোস্ট মেসেজ!",
        secondary_text="রোস্টিফাই বট | টেস্ট ইউজার",
        user_id=123456,
        category="funny"
    )
    
    if test_image:
        # Save test image
        test_image.save("test_output.png", "PNG")
        print("✅ Test image saved as 'test_output.png'")
        
        # Show image info
        print(f"📏 Image size: {test_image.size}")
        print(f"🎨 Image mode: {test_image.mode}")
        
        return True
    else:
        print("❌ Failed to create test image")
        return False

if __name__ == "__main__":
    test_image_generator()

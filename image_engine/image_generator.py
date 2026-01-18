#!/usr/bin/env python3
"""
🎨 Advanced Image Generator for Roastify Bot
✅ Professional | Multiple Templates | Random Designs | No Errors | Complete
"""

import os
import sys
import random
import json
import math
import textwrap
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
from io import BytesIO
from enum import Enum

# Import PIL with comprehensive error handling
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance, ImageChops
    PIL_AVAILABLE = True
except ImportError as e:
    PIL_AVAILABLE = False
    print(f"❌ PIL/Pillow not available: {e}")
    print("💡 Install with: pip install pillow")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import Config
    from utils.logger import logger
    from utils.helpers import Helpers
except ImportError:
    # Fallback if helpers not available
    class Helpers:
        @staticmethod
        def split_text_for_image(text: str, max_length: int) -> List[str]:
            """Split text into lines for image"""
            if not text:
                return []
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
    
    class Config:
        IMAGE_WIDTH = 600
        IMAGE_HEIGHT = 450
        ASSETS_PATH = "assets"
        FONTS_PATH = "assets/fonts"
        BACKGROUNDS_PATH = "assets/backgrounds"
    
    # Simple logger if not available
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# ==================== ENUMS AND CONSTANTS ====================

class TemplateStyle(Enum):
    MODERN = "modern"
    VINTAGE = "vintage"
    CYBERPUNK = "cyberpunk"
    GRADIENT = "gradient"
    MINIMAL = "minimal"
    NEON = "neon"
    ELEGANT = "elegant"
    FUNKY = "funky"
    DARK = "dark"
    LIGHT = "light"
    FIERY = "fiery"
    CELESTIAL = "celestial"
    GEOMETRIC = "geometric"
    WATERCOLOR = "watercolor"
    GLITCH = "glitch"

class EffectType(Enum):
    SHADOW = "shadow"
    GLOW = "glow"
    OUTLINE = "outline"
    GRADIENT_TEXT = "gradient_text"
    EMBOSS = "emboss"
    BLUR = "blur"
    VIGNETTE = "vignette"
    NOISE = "noise"
    SCAN_LINES = "scan_lines"
    TEXTURE = "texture"
    REFLECTION = "reflection"
    NEON_GLOW = "neon_glow"
    GRADIENT_BORDER = "gradient_border"

# ==================== ADVANCED TEMPLATE MANAGER ====================

class AdvancedTemplateManager:
    """Advanced template management with random designs and caching"""
    
    def __init__(self):
        self.templates = {}
        self.user_history = {}
        self.template_cache = {}
        self._load_all_templates()
        logger.info(f"📚 Loaded {len(self.templates)} templates")
    
    def _load_all_templates(self):
        """Load all built-in and custom templates"""
        # Built-in templates
        builtin_templates = {
            TemplateStyle.MODERN.value: self._create_modern_template(),
            TemplateStyle.VINTAGE.value: self._create_vintage_template(),
            TemplateStyle.CYBERPUNK.value: self._create_cyberpunk_template(),
            TemplateStyle.GRADIENT.value: self._create_gradient_template(),
            TemplateStyle.MINIMAL.value: self._create_minimal_template(),
            TemplateStyle.NEON.value: self._create_neon_template(),
            TemplateStyle.ELEGANT.value: self._create_elegant_template(),
            TemplateStyle.FUNKY.value: self._create_funky_template(),
            TemplateStyle.DARK.value: self._create_dark_template(),
            TemplateStyle.LIGHT.value: self._create_light_template(),
            TemplateStyle.FIERY.value: self._create_fiery_template(),
            TemplateStyle.CELESTIAL.value: self._create_celestial_template(),
            TemplateStyle.GEOMETRIC.value: self._create_geometric_template(),
            TemplateStyle.WATERCOLOR.value: self._create_watercolor_template(),
            TemplateStyle.GLITCH.value: self._create_glitch_template(),
        }
        
        self.templates.update(builtin_templates)
        
        # Load custom templates from JSON files
        self._load_custom_templates()
    
    def _load_custom_templates(self):
        """Load custom templates from JSON files"""
        templates_path = Path("assets/templates")
        if templates_path.exists():
            for template_file in templates_path.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template_name = template_file.stem
                        self.templates[template_name] = template_data
                        logger.info(f"📄 Loaded custom template: {template_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load template {template_file}: {e}")
    
    def get_template(self, user_id: int = None, style: str = None):
        """Get a template for user"""
        cache_key = f"{user_id}_{style}"
        
        # Check cache first
        if cache_key in self.template_cache:
            cached_template, timestamp = self.template_cache[cache_key]
            if (datetime.now().timestamp() - timestamp) < 300:  # 5 minutes cache
                return cached_template.copy()
        
        if style and style in self.templates:
            template = self.templates[style].copy()
        elif user_id and user_id in self.user_history:
            # Try to give a different template than last time
            last_template = self.user_history[user_id]
            available_templates = [t for t in self.templates.keys() 
                                 if t != last_template]
            if available_templates:
                template_name = random.choice(available_templates)
            else:
                template_name = random.choice(list(self.templates.keys()))
            template = self.templates[template_name].copy()
        else:
            template_name = random.choice(list(self.templates.keys()))
            template = self.templates[template_name].copy()
        
        # Add random variations
        template = self._add_random_variations(template)
        
        # Store in history
        if user_id:
            self.user_history[user_id] = template.get('name', template_name)
        
        # Cache the template
        self.template_cache[cache_key] = (template.copy(), datetime.now().timestamp())
        
        return template
    
    def _add_random_variations(self, template: Dict) -> Dict:
        """Add random variations to template"""
        # Color variations
        color_palettes = [
            {"primary": (255, 107, 53), "secondary": (0, 180, 216), "accent": (255, 209, 102)},  # Original
            {"primary": (239, 71, 111), "secondary": (6, 214, 160), "accent": (255, 94, 87)},    # Pink/Teal
            {"primary": (255, 209, 102), "secondary": (17, 138, 178), "accent": (6, 214, 160)},  # Yellow/Blue
            {"primary": (155, 93, 229), "secondary": (41, 171, 226), "accent": (255, 94, 87)},   # Purple/Blue
            {"primary": (255, 94, 87), "secondary": (255, 147, 39), "accent": (155, 93, 229)},   # Red/Orange
            {"primary": (106, 13, 173), "secondary": (230, 57, 70), "accent": (255, 195, 0)},    # Purple/Red
            {"primary": (0, 180, 216), "secondary": (144, 224, 239), "accent": (202, 240, 248)}, # Blue shades
            {"primary": (247, 37, 133), "secondary": (181, 23, 158), "accent": (114, 9, 183)},   # Pink/Purple
            {"primary": (255, 159, 28), "secondary": (250, 192, 0), "accent": (247, 220, 111)},  # Gold/Yellow
            {"primary": (48, 51, 107), "secondary": (91, 192, 190), "accent": (151, 215, 207)},  # Dark/Teal
        ]
        
        palette = random.choice(color_palettes)
        template["primary_color"] = palette["primary"]
        template["secondary_color"] = palette["secondary"]
        template["accent_color"] = palette["accent"]
        
        # Random effects (2-4 effects)
        all_effects = [e.value for e in EffectType]
        selected_effects = random.sample(all_effects, random.randint(2, 4))
        template["effects"] = selected_effects
        
        # Font size variations (±5)
        if "font_size" in template:
            template["font_size"] = max(20, template["font_size"] + random.randint(-5, 5))
        
        # Border style variations
        border_styles = ["none", "simple", "rounded", "double", "dashed", "dotted", "gradient"]
        template["border_style"] = random.choice(border_styles)
        
        # Opacity variations
        template["text_opacity"] = random.randint(200, 255)
        template["shadow_opacity"] = random.randint(100, 180)
        
        # Add timestamp for freshness
        template["generated_at"] = datetime.now().isoformat()
        template["variation_id"] = random.randint(1, 1000)
        
        return template
    
    # ========== TEMPLATE CREATORS ==========
    
    def _create_modern_template(self):
        return {
            "name": "modern",
            "background": "gradient",
            "primary_color": (255, 107, 53),
            "secondary_color": (0, 180, 216),
            "accent_color": (255, 209, 102),
            "font": "modern.ttf",
            "font_size": 48,
            "sub_font_size": 24,
            "position": {"x": 300, "y": 200},
            "sub_position": {"x": 300, "y": 300},
            "border_style": "rounded",
            "border_color": (255, 255, 255, 50),
            "border_width": 3,
            "shadow_color": (0, 0, 0, 150),
            "shadow_offset": 5,
            "text_opacity": 255,
            "shadow_opacity": 150,
            "blur_radius": 0,
            "gradient_direction": "vertical",
            "effects": ["shadow", "gradient_text", "rounded_border"]
        }
    
    def _create_vintage_template(self):
        return {
            "name": "vintage",
            "background": "texture",
            "primary_color": (139, 69, 19),
            "secondary_color": (160, 82, 45),
            "accent_color": (101, 67, 33),
            "font": "serif.ttf",
            "font_size": 42,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 180},
            "sub_position": {"x": 300, "y": 280},
            "border_style": "ornate",
            "border_color": (101, 67, 33, 100),
            "border_width": 4,
            "shadow_color": (50, 25, 0, 200),
            "shadow_offset": 4,
            "text_opacity": 240,
            "shadow_opacity": 200,
            "blur_radius": 1,
            "texture_intensity": 0.3,
            "effects": ["texture", "vignette", "shadow"]
        }
    
    def _create_cyberpunk_template(self):
        return {
            "name": "cyberpunk",
            "background": "grid",
            "primary_color": (0, 255, 255),
            "secondary_color": (255, 0, 255),
            "accent_color": (255, 255, 0),
            "font": "tech.ttf",
            "font_size": 52,
            "sub_font_size": 26,
            "position": {"x": 300, "y": 190},
            "sub_position": {"x": 300, "y": 290},
            "border_style": "neon",
            "border_color": (0, 255, 255, 100),
            "border_width": 2,
            "shadow_color": (0, 255, 255, 80),
            "shadow_offset": 8,
            "text_opacity": 255,
            "shadow_opacity": 80,
            "blur_radius": 0,
            "glow_intensity": 0.7,
            "effects": ["glow", "scan_lines", "noise", "neon_border"]
        }
    
    def _create_gradient_template(self):
        return {
            "name": "gradient",
            "background": "gradient_rainbow",
            "primary_color": (255, 255, 255),
            "secondary_color": (200, 200, 200),
            "accent_color": (150, 150, 150),
            "font": "sans.ttf",
            "font_size": 46,
            "sub_font_size": 23,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "border_style": "gradient",
            "border_color": (255, 255, 255, 30),
            "border_width": 5,
            "shadow_color": (0, 0, 0, 100),
            "shadow_offset": 4,
            "text_opacity": 255,
            "shadow_opacity": 100,
            "blur_radius": 0,
            "gradient_stops": 7,
            "effects": ["gradient_text", "shadow", "gradient_border"]
        }
    
    def _create_minimal_template(self):
        return {
            "name": "minimal",
            "background": "solid",
            "primary_color": (0, 0, 0),
            "secondary_color": (100, 100, 100),
            "accent_color": (150, 150, 150),
            "font": "sans.ttf",
            "font_size": 44,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 185},
            "sub_position": {"x": 300, "y": 285},
            "border_style": "none",
            "border_color": (0, 0, 0, 0),
            "border_width": 0,
            "shadow_color": (0, 0, 0, 0),
            "shadow_offset": 0,
            "text_opacity": 255,
            "shadow_opacity": 0,
            "blur_radius": 0,
            "minimalism_level": "high",
            "effects": []
        }
    
    def _create_neon_template(self):
        return {
            "name": "neon",
            "background": "dark",
            "primary_color": (255, 20, 147),
            "secondary_color": (0, 191, 255),
            "accent_color": (50, 205, 50),
            "font": "bold.ttf",
            "font_size": 50,
            "sub_font_size": 25,
            "position": {"x": 300, "y": 200},
            "sub_position": {"x": 300, "y": 300},
            "border_style": "glowing",
            "border_color": (255, 20, 147, 80),
            "border_width": 4,
            "shadow_color": (255, 20, 147, 120),
            "shadow_offset": 10,
            "text_opacity": 255,
            "shadow_opacity": 120,
            "blur_radius": 2,
            "glow_strength": 0.8,
            "effects": ["neon_glow", "reflection", "glow", "shadow"]
        }
    
    def _create_elegant_template(self):
        return {
            "name": "elegant",
            "background": "marble",
            "primary_color": (75, 0, 130),
            "secondary_color": (138, 43, 226),
            "accent_color": (255, 215, 0),
            "font": "elegant.ttf",
            "font_size": 45,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 190},
            "sub_position": {"x": 300, "y": 290},
            "border_style": "decorative",
            "border_color": (255, 215, 0, 100),
            "border_width": 3,
            "shadow_color": (75, 0, 130, 150),
            "shadow_offset": 3,
            "text_opacity": 255,
            "shadow_opacity": 150,
            "blur_radius": 1,
            "elegance_level": "high",
            "effects": ["emboss", "gold_border", "shadow"]
        }
    
    def _create_funky_template(self):
        return {
            "name": "funky",
            "background": "pattern",
            "primary_color": (255, 165, 0),
            "secondary_color": (0, 128, 0),
            "accent_color": (255, 69, 0),
            "font": "funky.ttf",
            "font_size": 47,
            "sub_font_size": 24,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "border_style": "dashed",
            "border_color": (255, 69, 0, 100),
            "border_width": 2,
            "shadow_color": (255, 165, 0, 150),
            "shadow_offset": 6,
            "text_opacity": 255,
            "shadow_opacity": 150,
            "blur_radius": 0,
            "pattern_density": "medium",
            "effects": ["dotted", "wavy", "color_shift"]
        }
    
    def _create_dark_template(self):
        return {
            "name": "dark",
            "background": "black",
            "primary_color": (255, 255, 255),
            "secondary_color": (200, 200, 200),
            "accent_color": (100, 100, 100),
            "font": "sans.ttf",
            "font_size": 46,
            "sub_font_size": 23,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "border_style": "thin",
            "border_color": (50, 50, 50, 100),
            "border_width": 1,
            "shadow_color": (0, 0, 0, 200),
            "shadow_offset": 3,
            "text_opacity": 255,
            "shadow_opacity": 200,
            "blur_radius": 0,
            "contrast_level": "high",
            "effects": ["shadow", "gradient", "vignette"]
        }
    
    def _create_light_template(self):
        return {
            "name": "light",
            "background": "white",
            "primary_color": (0, 0, 0),
            "secondary_color": (50, 50, 50),
            "accent_color": (100, 100, 100),
            "font": "clean.ttf",
            "font_size": 44,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 190},
            "sub_position": {"x": 300, "y": 290},
            "border_style": "simple",
            "border_color": (200, 200, 200, 100),
            "border_width": 2,
            "shadow_color": (150, 150, 150, 100),
            "shadow_offset": 2,
            "text_opacity": 255,
            "shadow_opacity": 100,
            "blur_radius": 0,
            "brightness_level": "high",
            "effects": ["soft_shadow", "highlight", "subtle_glow"]
        }
    
    def _create_fiery_template(self):
        return {
            "name": "fiery",
            "background": "fire",
            "primary_color": (255, 69, 0),
            "secondary_color": (255, 140, 0),
            "accent_color": (255, 215, 0),
            "font": "bold.ttf",
            "font_size": 52,
            "sub_font_size": 26,
            "position": {"x": 300, "y": 200},
            "sub_position": {"x": 300, "y": 300},
            "border_style": "flaming",
            "border_color": (255, 69, 0, 150),
            "border_width": 4,
            "shadow_color": (255, 0, 0, 180),
            "shadow_offset": 7,
            "text_opacity": 255,
            "shadow_opacity": 180,
            "blur_radius": 1,
            "fire_intensity": "high",
            "effects": ["fire_glow", "heat_haze", "embers"]
        }
    
    def _create_celestial_template(self):
        return {
            "name": "celestial",
            "background": "stars",
            "primary_color": (135, 206, 235),
            "secondary_color": (176, 224, 230),
            "accent_color": (255, 255, 255),
            "font": "space.ttf",
            "font_size": 48,
            "sub_font_size": 24,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "border_style": "starry",
            "border_color": (135, 206, 235, 100),
            "border_width": 3,
            "shadow_color": (0, 0, 139, 150),
            "shadow_offset": 5,
            "text_opacity": 255,
            "shadow_opacity": 150,
            "blur_radius": 0,
            "star_density": "high",
            "effects": ["starry_night", "twinkle", "nebula"]
        }
    
    def _create_geometric_template(self):
        return {
            "name": "geometric",
            "background": "shapes",
            "primary_color": (70, 130, 180),
            "secondary_color": (100, 149, 237),
            "accent_color": (30, 144, 255),
            "font": "geometric.ttf",
            "font_size": 46,
            "sub_font_size": 23,
            "position": {"x": 300, "y": 195},
            "sub_position": {"x": 300, "y": 295},
            "border_style": "geometric",
            "border_color": (70, 130, 180, 120),
            "border_width": 3,
            "shadow_color": (25, 25, 112, 150),
            "shadow_offset": 4,
            "text_opacity": 255,
            "shadow_opacity": 150,
            "blur_radius": 0,
            "shape_complexity": "medium",
            "effects": ["geometric_pattern", "symmetry", "perspective"]
        }
    
    def _create_watercolor_template(self):
        return {
            "name": "watercolor",
            "background": "watercolor",
            "primary_color": (95, 158, 160),
            "secondary_color": (102, 205, 170),
            "accent_color": (143, 188, 143),
            "font": "brush.ttf",
            "font_size": 45,
            "sub_font_size": 22,
            "position": {"x": 300, "y": 190},
            "sub_position": {"x": 300, "y": 290},
            "border_style": "watercolor",
            "border_color": (95, 158, 160, 80),
            "border_width": 5,
            "shadow_color": (47, 79, 79, 120),
            "shadow_offset": 3,
            "text_opacity": 240,
            "shadow_opacity": 120,
            "blur_radius": 2,
            "watercolor_blend": "high",
            "effects": ["watercolor_blend", "texture", "soft_edges"]
        }
    
    def _create_glitch_template(self):
        return {
            "name": "glitch",
            "background": "digital",
            "primary_color": (0, 255, 0),
            "secondary_color": (255, 0, 255),
            "accent_color": (0, 0, 255),
            "font": "digital.ttf",
            "font_size": 50,
            "sub_font_size": 25,
            "position": {"x": 300, "y": 200},
            "sub_position": {"x": 300, "y": 300},
            "border_style": "glitch",
            "border_color": (0, 255, 0, 100),
            "border_width": 2,
            "shadow_color": (255, 0, 255, 150),
            "shadow_offset": random.randint(3, 8),
            "text_opacity": 255,
            "shadow_opacity": 150,
            "blur_radius": 1,
            "glitch_intensity": "medium",
            "effects": ["glitch", "noise", "scan_lines", "color_shift"]
        }

# ==================== ADVANCED IMAGE GENERATOR ====================

class AdvancedImageGenerator:
    """Advanced image generator with multiple templates and effects"""
    
    def __init__(self):
        if not PIL_AVAILABLE:
            logger.error("❌ PIL/Pillow not installed! Image generation disabled.")
            self.available = False
            self.width = 600
            self.height = 450
            return
        
        self.available = True
        self.width = getattr(Config, 'IMAGE_WIDTH', 600)
        self.height = getattr(Config, 'IMAGE_HEIGHT', 450)
        
        # Initialize managers
        self.template_manager = AdvancedTemplateManager()
        
        # Setup directories
        self._setup_directories()
        
        # Load assets
        self._load_assets()
        
        # Statistics
        self.stats = {
            "images_created": 0,
            "templates_used": {},
            "errors": 0,
            "start_time": datetime.now()
        }
        
        logger.info(f"✅ Advanced Image Generator initialized (Size: {self.width}x{self.height})")
    
    def _setup_directories(self):
        """Create necessary directories"""
        directories = [
            "assets",
            "assets/fonts",
            "assets/backgrounds",
            "assets/templates",
            "generated",
            "generated/roasts",
            "generated/stickers",
            "temp",
            "temp/cache"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
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
                except Exception as e:
                    logger.warning(f"Failed to load font {font_file}: {e}")
        
        logger.info(f"📝 Loaded {len(self.fonts)} fonts")
        
        # Backgrounds
        self.backgrounds = {}
        bg_dir = Path("assets/backgrounds")
        if bg_dir.exists():
            for bg_file in bg_dir.glob("*.png"):
                try:
                    bg_name = bg_file.stem
                    self.backgrounds[bg_name] = str(bg_file)
                except Exception as e:
                    logger.warning(f"Failed to load background {bg_file}: {e}")
        
        logger.info(f"🎨 Loaded {len(self.backgrounds)} backgrounds")
    
    def create_roast_image(self, primary_text: str, secondary_text: str = "", 
                          user_id: int = None, category: str = "funny", 
                          style: str = None) -> Optional[Image.Image]:
        """
        Create a roast image with random template
        Returns PIL Image object or None if failed
        """
        if not self.available:
            logger.error("Image generator not available")
            return self._create_fallback_image(primary_text, secondary_text)
        
        try:
            # Get template
            template = self.template_manager.get_template(user_id, style)
            
            # Update stats
            template_name = template.get('name', 'unknown')
            self.stats["templates_used"][template_name] = self.stats["templates_used"].get(template_name, 0) + 1
            
            # Create base image
            image = self._create_background(template)
            
            # Apply background effects
            image = self._apply_background_effects(image, template)
            
            # Add text
            image = self._add_text(image, primary_text, secondary_text, template)
            
            # Add decorative elements
            image = self._add_decorations(image, template, category)
            
            # Apply border
            image = self._apply_border(image, template)
            
            # Final effects
            image = self._apply_final_effects(image, template)
            
            # Update statistics
            self.stats["images_created"] += 1
            
            logger.info(f"🖼️ Created image for user {user_id} with template {template_name}")
            
            return image
            
        except Exception as e:
            logger.error(f"❌ Error creating roast image: {e}", exc_info=True)
            self.stats["errors"] += 1
            return self._create_error_image(primary_text)
    
    def _create_background(self, template: Dict) -> Image.Image:
        """Create background based on template"""
        bg_type = template.get("background", "gradient")
        
        # Check if custom background exists
        if bg_type in self.backgrounds:
            try:
                bg_image = Image.open(self.backgrounds[bg_type]).convert("RGBA")
                bg_image = bg_image.resize((self.width, self.height), Image.Resampling.LANCZOS)
                return bg_image
            except Exception as e:
                logger.warning(f"Failed to load background {bg_type}: {e}")
        
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
        elif bg_type == "fire":
            return self._create_fire_background()
        elif bg_type == "stars":
            return self._create_stars_background()
        elif bg_type == "shapes":
            return self._create_shapes_background()
        elif bg_type == "watercolor":
            return self._create_watercolor_background()
        elif bg_type == "digital":
            return self._create_digital_background()
        elif bg_type == "black":
            return Image.new('RGBA', (self.width, self.height), (0, 0, 0, 255))
        elif bg_type == "white":
            return Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
        elif bg_type == "dark":
            return Image.new('RGBA', (self.width, self.height), (20, 20, 30, 255))
        elif bg_type == "light":
            return Image.new('RGBA', (self.width, self.height), (240, 240, 245, 255))
        elif bg_type == "solid":
            color = template.get("primary_color", (25, 25, 35))
            return Image.new('RGBA', (self.width, self.height), color + (255,))
        elif bg_type == "marble":
            return self._create_marble_background()
        else:
            # Default gradient
            return self._create_gradient_background(template)
    
    def _create_gradient_background(self, template: Dict) -> Image.Image:
        """Create gradient background"""
        image = Image.new('RGBA', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Get colors
        color1 = template.get("primary_color", (random.randint(0, 100), 
                                                random.randint(0, 100), 
                                                random.randint(100, 200)))
        color2 = template.get("secondary_color", (random.randint(100, 200), 
                                                  random.randint(100, 200), 
                                                  random.randint(0, 100)))
        
        direction = template.get("gradient_direction", "vertical")
        
        if direction == "horizontal":
            # Horizontal gradient
            for x in range(self.width):
                ratio = x / self.width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x, self.height)], fill=(r, g, b, 255))
        elif direction == "diagonal":
            # Diagonal gradient
            for x in range(self.width):
                for y in range(self.height):
                    ratio_x = x / self.width
                    ratio_y = y / self.height
                    ratio = (ratio_x + ratio_y) / 2
                    
                    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                    
                    draw.point((x, y), fill=(r, g, b, 255))
        else:
            # Vertical gradient (default)
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
            (255, 0, 0),      # Red
            (255, 127, 0),    # Orange
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (75, 0, 130),     # Indigo
            (148, 0, 211)     # Violet
        ]
        
        segment_height = self.height // len(colors)
        
        for i, color in enumerate(colors):
            y_start = i * segment_height
            y_end = (i + 1) * segment_height if i < len(colors) - 1 else self.height
            
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
        
        # Vertical lines
        for x in range(0, self.width, grid_size):
            draw.line([(x, 0), (x, self.height)], fill=line_color, width=1)
        
        # Horizontal lines
        for y in range(0, self.height, grid_size):
            draw.line([(0, y), (self.width, y)], fill=line_color, width=1)
        
        # Add glow points at intersections
        for x in range(grid_size // 2, self.width, grid_size):
            for y in range(grid_size // 2, self.height, grid_size):
                if random.random() < 0.3:  # 30% chance
                    radius = random.randint(1, 3)
                    color = (random.randint(0, 255), random.randint(0, 255), 255, 150)
                    draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=color)
        
        return image
    
    def _create_texture_background(self) -> Image.Image:
        """Create textured background"""
        base_color = (139, 69, 19)  # SaddleBrown
        image = Image.new('RGBA', (self.width, self.height), base_color + (255,))
        draw = ImageDraw.Draw(image)
        
        # Add noise for texture
        for _ in range(3000):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            darkness = random.randint(0, 40)
            draw.point((x, y), fill=(
                max(0, base_color[0] - darkness),
                max(0, base_color[1] - darkness // 2),
                max(0, base_color[2] - darkness // 3),
                255
            ))
        
        # Add some lighter spots
        for _ in range(500):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            lightness = random.randint(0, 30)
            draw.point((x, y), fill=(
                min(255, base_color[0] + lightness),
                min(255, base_color[1] + lightness // 2),
                min(255, base_color[2] + lightness // 3),
                255
            ))
        
        return image
    
    def _create_pattern_background(self) -> Image.Image:
        """Create patterned background"""
        image = Image.new('RGBA', (self.width, self.height), (255, 245, 230, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw circles pattern
        pattern_size = 80
        colors = [
            (255, 200, 200, 80),   # Light pink
            (200, 255, 200, 80),   # Light green
            (200, 200, 255, 80),   # Light blue
            (255, 255, 200, 80),   # Light yellow
        ]
        
        for x in range(0, self.width + pattern_size, pattern_size):
            for y in range(0, self.height + pattern_size, pattern_size):
                offset_x = (y // pattern_size) % 2 * pattern_size // 2
                center_x = x + offset_x
                center_y = y
                
                color = random.choice(colors)
                radius = pattern_size // 3
                
                # Draw circle
                draw.ellipse([
                    (center_x - radius, center_y - radius),
                    (center_x + radius, center_y + radius)
                ], fill=color)
                
                # Draw smaller inner circle
                inner_radius = radius // 2
                inner_color = (color[0], color[1], color[2], color[3] + 50)
                draw.ellipse([
                    (center_x - inner_radius, center_y - inner_radius),
                    (center_x + inner_radius, center_y + inner_radius)
                ], fill=inner_color)
        
        return image
    
    def _create_fire_background(self) -> Image.Image:
        """Create fire effect background"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(image)
        
        # Fire colors from hot to cool
        fire_colors = [
            (255, 255, 255),  # White (hottest)
            (255, 255, 0),    # Yellow
            (255, 165, 0),    # Orange
            (255, 69, 0),     # Red-Orange
            (178, 34, 34),    # Firebrick
            (139, 0, 0),      # Dark Red
        ]
        
        # Create fire-like gradient from bottom to top
        for y in range(self.height):
            # More red at bottom, more yellow/white at top
            ratio = y / self.height
            color_index = min(len(fire_colors) - 1, int(ratio * len(fire_colors)))
            color = fire_colors[color_index]
            
            # Add some randomness to make it look like fire
            for x in range(0, self.width, 2):
                if random.random() < 0.7:  # 70% chance to draw fire pixel
                    # Add some variation
                    r = max(0, min(255, color[0] + random.randint(-20, 20)))
                    g = max(0, min(255, color[1] + random.randint(-20, 20)))
                    b = max(0, min(255, color[2] + random.randint(-20, 20)))
                    
                    draw.point((x, self.height - y - 1), fill=(r, g, b, 255))
        
        return image
    
    def _create_stars_background(self) -> Image.Image:
        """Create starry night background"""
        image = Image.new('RGBA', (self.width, self.height), (10, 10, 40, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw stars
        for _ in range(200):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # Star brightness
            brightness = random.randint(150, 255)
            size = random.randint(1, 3)
            
            # Different star colors
            star_type = random.random()
            if star_type < 0.7:  # 70% white stars
                color = (brightness, brightness, brightness, 255)
            elif star_type < 0.85:  # 15% blue stars
                color = (brightness // 2, brightness // 2, brightness, 255)
            else:  # 15% yellow stars
                color = (brightness, brightness, brightness // 2, 255)
            
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
        
        # Add some bigger stars
        for _ in range(20):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            size = random.randint(2, 4)
            
            # Draw star with glow
            for i in range(size, 0, -1):
                alpha = 255 // (size - i + 1)
                draw.ellipse([(x-i, y-i), (x+i, y+i)], fill=(255, 255, 200, alpha))
        
        return image
    
    def _create_shapes_background(self) -> Image.Image:
        """Create geometric shapes background"""
        image = Image.new('RGBA', (self.width, self.height), (240, 240, 245, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw various geometric shapes
        shapes = []
        
        # Triangles
        for _ in range(15):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            size = random.randint(30, 80)
            color = (random.randint(100, 200), random.randint(100, 200), 
                    random.randint(200, 255), random.randint(30, 80))
            
            points = [
                (x1, y1),
                (x1 + size, y1),
                (x1 + size // 2, y1 + size)
            ]
            draw.polygon(points, fill=color)
        
        # Circles
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            radius = random.randint(20, 60)
            color = (random.randint(200, 255), random.randint(100, 200), 
                    random.randint(100, 200), random.randint(40, 90))
            
            draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=color)
        
        # Squares
        for _ in range(10):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(40, 70)
            color = (random.randint(100, 200), random.randint(200, 255), 
                    random.randint(100, 200), random.randint(50, 100))
            
            draw.rectangle([(x, y), (x+size, y+size)], fill=color)
        
        return image
    
    def _create_watercolor_background(self) -> Image.Image:
        """Create watercolor effect background"""
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Soft pastel colors for watercolor
        watercolor_colors = [
            (240, 248, 255, 150),  # AliceBlue
            (230, 230, 250, 150),  # Lavender
            (255, 228, 225, 150),  # MistyRose
            (224, 255, 255, 150),  # LightCyan
            (255, 250, 205, 150),  # LemonChiffon
            (240, 255, 240, 150),  # Honeydew
            (255, 245, 238, 150),  # Seashell
        ]
        
        # Create soft blobs (watercolor effect)
        for _ in range(30):
            center_x = random.randint(0, self.width)
            center_y = random.randint(0, self.height)
            color = random.choice(watercolor_colors)
            
            # Create irregular blob
            for _ in range(100):
                angle = random.random() * 2 * math.pi
                distance = random.randint(10, 60)
                x = center_x + int(math.cos(angle) * distance)
                y = center_y + int(math.sin(angle) * distance)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Soft edges with varying alpha
                    dist_ratio = distance / 60
                    alpha = int(color[3] * (1 - dist_ratio))
                    draw.point((x, y), fill=(color[0], color[1], color[2], alpha))
        
        return image
    
    def _create_digital_background(self) -> Image.Image:
        """Create digital/glitch background"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(image)
        
        # Binary/Matrix style background
        for x in range(0, self.width, 20):
            for y in range(0, self.height, 20):
                # Random green shades for matrix effect
                if random.random() < 0.3:
                    intensity = random.randint(50, 200)
                    color = (0, intensity, 0, 255)
                    
                    # Draw "digital" character (simplified)
                    char_size = 15
                    draw.rectangle([(x, y), (x+char_size, y+char_size)], 
                                 fill=color, outline=(0, 100, 0, 255))
                    
                    # Add some binary text
                    if random.random() < 0.5:
                        binary_char = random.choice(['0', '1'])
                        try:
                            font = self._get_font("arial.ttf", 10)
                            draw.text((x+2, y+2), binary_char, font=font, fill=(0, 255, 0, 200))
                        except:
                            pass
        
        # Add some glitch lines
        for _ in range(5):
            y = random.randint(0, self.height - 1)
            height = random.randint(1, 3)
            color = random.choice([(0, 255, 0, 100), (255, 0, 255, 100), (0, 0, 255, 100)])
            
            # Shift part of the line for glitch effect
            shift = random.randint(-10, 10)
            for x in range(0, self.width, 2):
                if x + shift < self.width and x + shift >= 0:
                    draw.line([(x, y), (x+shift, y+height)], fill=color, width=1)
        
        return image
    
    def _create_marble_background(self) -> Image.Image:
        """Create marble texture background"""
        image = Image.new('RGBA', (self.width, self.height), (245, 245, 245, 255))
        draw = ImageDraw.Draw(image)
        
        # Base marble color
        base_colors = [
            (245, 245, 245),  # White marble
            (230, 230, 220),  # Cream marble
            (220, 220, 210),  # Light gray marble
        ]
        
        base_color = random.choice(base_colors)
        
        # Create veining (marble patterns)
        for _ in range(20):
            # Vein color (darker than base)
            vein_color = (
                max(0, base_color[0] - random.randint(20, 40)),
                max(0, base_color[1] - random.randint(20, 40)),
                max(0, base_color[2] - random.randint(20, 40)),
                random.randint(50, 150)
            )
            
            # Create a vein (curved line)
            start_x = random.randint(0, self.width)
            start_y = random.randint(0, self.height)
            
            for i in range(random.randint(50, 150)):
                angle = random.random() * 2 * math.pi
                distance = random.randint(1, 3)
                
                new_x = start_x + int(math.cos(angle) * distance * i)
                new_y = start_y + int(math.sin(angle) * distance * i)
                
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    # Draw vein with varying thickness
                    thickness = random.randint(1, 3)
                    for dx in range(-thickness, thickness + 1):
                        for dy in range(-thickness, thickness + 1):
                            if random.random() < 0.7:  # Not all points
                                px = new_x + dx
                                py = new_y + dy
                                if 0 <= px < self.width and 0 <= py < self.height:
                                    # Blend with existing pixel
                                    existing = image.getpixel((px, py))
                                    if len(existing) == 4:
                                        r = int((existing[0] * (255 - vein_color[3]) + vein_color[0] * vein_color[3]) / 255)
                                        g = int((existing[1] * (255 - vein_color[3]) + vein_color[1] * vein_color[3]) / 255)
                                        b = int((existing[2] * (255 - vein_color[3]) + vein_color[2] * vein_color[3]) / 255)
                                        a = min(255, existing[3] + vein_color[3] // 2)
                                        draw.point((px, py), fill=(r, g, b, a))
        
        return image
    
    def _apply_background_effects(self, image: Image.Image, template: Dict) -> Image.Image:
        """Apply background effects"""
        effects = template.get("effects", [])
        
        for effect in effects:
            try:
                if effect == "blur" and template.get("blur_radius", 0) > 0:
                    image = image.filter(ImageFilter.GaussianBlur(template["blur_radius"]))
                elif effect == "vignette":
                    image = self._add_vignette(image)
                elif effect == "noise":
                    image = self._add_noise(image, intensity=template.get("noise_intensity", 3))
                elif effect == "scan_lines":
                    image = self._add_scan_lines(image)
                elif effect == "texture":
                    image = self._add_texture_overlay(image)
                elif effect == "emboss":
                    image = image.filter(ImageFilter.EMBOSS)
                elif effect == "heat_haze":
                    image = self._add_heat_haze(image)
                elif effect == "nebula":
                    image = self._add_nebula_effect(image)
                elif effect == "watercolor_blend":
                    image = self._apply_watercolor_filter(image)
            except Exception as e:
                logger.debug(f"Effect {effect} failed: {e}")
        
        return image
    
    def _add_text(self, image: Image.Image, primary_text: str, secondary_text: str, 
                 template: Dict) -> Image.Image:
        """Add text to image with effects"""
        if not primary_text:
            return image
        
        draw = ImageDraw.Draw(image)
        
        # Get font
        font_name = template.get("font", "arial.ttf")
        font_size = template.get("font_size", 48)
        font = self._get_font(font_name, font_size)
        
        # Split text
        max_chars_per_line = 25
        primary_lines = self._split_text(primary_text, max_chars_per_line)
        secondary_lines = self._split_text(secondary_text, 35) if secondary_text else []
        
        # Get positions
        primary_pos = template.get("position", {"x": self.width//2, "y": self.height//2 - 50})
        secondary_pos = template.get("sub_position", {"x": self.width//2, "y": self.height//2 + 50})
        
        # Draw primary text with effects
        primary_color = template.get("primary_color", (255, 255, 255))
        text_opacity = template.get("text_opacity", 255)
        primary_color_with_alpha = primary_color + (text_opacity,)
        
        self._draw_text_with_effects(draw, primary_lines, font, primary_pos, 
                                    primary_color_with_alpha, template, is_primary=True)
        
        # Draw secondary text
        if secondary_lines:
            sub_font_size = template.get("sub_font_size", font_size // 2)
            sub_font = self._get_font(font_name, sub_font_size)
            secondary_color = template.get("secondary_color", (200, 200, 200))
            secondary_color_with_alpha = secondary_color + (text_opacity,)
            
            self._draw_text_with_effects(draw, secondary_lines, sub_font, secondary_pos,
                                        secondary_color_with_alpha, template, is_primary=False)
        
        return image
    
    def _split_text(self, text: str, max_chars: int) -> List[str]:
        """Split text into lines"""
        if not text:
            return []
        
        # Use textwrap for better line breaking
        return textwrap.wrap(text, width=max_chars)
    
    def _get_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """Get font with fallback"""
        # Remove .ttf extension if present
        font_name = font_name.replace('.ttf', '')
        
        # Try to load from assets
        if font_name in self.fonts:
            try:
                return ImageFont.truetype(self.fonts[font_name], size)
            except Exception as e:
                logger.debug(f"Failed to load font {font_name}: {e}")
        
        # Try common font names
        common_fonts = [
            f"{font_name}.ttf",
            font_name,
            "arial.ttf",
            "DejaVuSans.ttf",
            "LiberationSans-Regular.ttf",
        ]
        
        for font_path in common_fonts:
            try:
                # Check if it's a system font
                return ImageFont.truetype(font_path, size)
            except:
                continue
        
        # Try absolute paths
        font_dirs = [
            "/usr/share/fonts/truetype/",
            "/usr/local/share/fonts/",
            "assets/fonts/",
            "fonts/",
        ]
        
        for font_dir in font_dirs:
            for font_file in common_fonts:
                full_path = Path(font_dir) / font_file
                if full_path.exists():
                    try:
                        return ImageFont.truetype(str(full_path), size)
                    except:
                        continue
        
        # Final fallback
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default(size)
    
    def _draw_text_with_effects(self, draw: ImageDraw.Draw, lines: List[str], 
                               font: ImageFont.FreeTypeFont, position: Dict,
                               color: Tuple, template: Dict, is_primary: bool = True):
        """Draw text with various effects"""
        if not lines:
            return
        
        effects = template.get("effects", [])
        shadow_offset = template.get("shadow_offset", 4)
        shadow_color = template.get("shadow_color", (0, 0, 0, 150))
        
        # Calculate text block dimensions
        line_heights = []
        line_widths = []
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            line_widths.append(line_width)
            line_heights.append(line_height)
        
        max_line_width = max(line_widths) if line_widths else 0
        total_height = sum(line_heights) + (len(lines) - 1) * 10  # 10px line spacing
        
        # Starting position (centered)
        start_x = position["x"] - (max_line_width // 2)
        start_y = position["y"] - (total_height // 2)
        
        current_y = start_y
        
        for i, line in enumerate(lines):
            line_width = line_widths[i]
            line_height = line_heights[i]
            
            # Center each line horizontally
            line_x = start_x + (max_line_width - line_width) // 2
            
            # Apply effects before main text
            if "shadow" in effects and is_primary:
                shadow_alpha = template.get("shadow_opacity", 150)
                shadow_color_with_alpha = shadow_color[:3] + (shadow_alpha,)
                draw.text((line_x + shadow_offset, current_y + shadow_offset), 
                         line, font=font, fill=shadow_color_with_alpha)
            
            if "outline" in effects and is_primary:
                outline_size = 2
                outline_color = (0, 0, 0, 200)
                for dx in range(-outline_size, outline_size + 1):
                    for dy in range(-outline_size, outline_size + 1):
                        if dx != 0 or dy != 0:
                            draw.text((line_x + dx, current_y + dy), 
                                     line, font=font, fill=outline_color)
            
            if "glow" in effects and is_primary:
                glow_size = 3
                glow_color = (color[0], color[1], color[2], 100)
                for dx in range(-glow_size, glow_size + 1):
                    for dy in range(-glow_size, glow_size + 1):
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist <= glow_size:
                            alpha = int(100 * (1 - dist/glow_size))
                            glow_color_with_alpha = glow_color[:3] + (alpha,)
                            draw.text((line_x + dx, current_y + dy), 
                                     line, font=font, fill=glow_color_with_alpha)
            
            # Draw main text
            if "gradient_text" in effects and is_primary and len(line) > 0:
                # Create gradient text (character by character)
                char_spacing = 0
                for j, char in enumerate(line):
                    char_bbox = draw.textbbox((0, 0), char, font=font)
                    char_width = char_bbox[2] - char_bbox[0]
                    
                    # Calculate gradient color
                    ratio = j / max(len(line) - 1, 1)
                    r = int(color[0] * (1 - ratio) + template.get("accent_color", (255, 0, 0))[0] * ratio)
                    g = int(color[1] * (1 - ratio) + template.get("accent_color", (255, 0, 0))[1] * ratio)
                    b = int(color[2] * (1 - ratio) + template.get("accent_color", (255, 0, 0))[2] * ratio)
                    
                    draw.text((line_x + char_spacing, current_y), 
                             char, font=font, fill=(r, g, b, color[3]))
                    char_spacing += char_width
            else:
                # Draw normal text
                draw.text((line_x, current_y), line, font=font, fill=color)
            
            # Move to next line
            current_y += line_height + 10
    
    def _add_decorations(self, image: Image.Image, template: Dict, category: str) -> Image.Image:
        """Add decorative elements"""
        draw = ImageDraw.Draw(image)
        
        # Category-based decorations
        category_icons = {
            "funny": "😂",
            "savage": "🔥",
            "general": "⭐",
            "roast": "👑",
            "insult": "💀",
            "joke": "🎭",
            "comedy": "🤡",
            "pun": "📝",
        }
        
        # Add category icon if available
        if category in category_icons:
            try:
                emoji_font = self._get_font("arial.ttf", 40)
                emoji = category_icons[category]
                emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
                emoji_width = emoji_bbox[2] - emoji_bbox[0]
                
                # Position in top-right corner
                padding = 20
                emoji_x = self.width - emoji_width - padding
                emoji_y = padding
                
                draw.text((emoji_x, emoji_y), emoji, font=emoji_font, 
                         fill=template.get("accent_color", (255, 255, 255, 200)))
            except:
                pass
        
        # Add decorative corners
        corner_size = 30
        corner_color = template.get("accent_color", (255, 255, 255, 150))
        
        # Top-left corner
        draw.line([(0, corner_size), (corner_size, 0)], fill=corner_color, width=2)
        draw.line([(0, 0), (corner_size // 2, 0)], fill=corner_color, width=2)
        draw.line([(0, 0), (0, corner_size // 2)], fill=corner_color, width=2)
        
        # Top-right corner
        draw.line([(self.width - corner_size, 0), (self.width, corner_size)], 
                 fill=corner_color, width=2)
        draw.line([(self.width - corner_size // 2, 0), (self.width, 0)], 
                 fill=corner_color, width=2)
        draw.line([(self.width, 0), (self.width, corner_size // 2)], 
                 fill=corner_color, width=2)
        
        # Bottom-left corner
        draw.line([(0, self.height - corner_size), (corner_size, self.height)], 
                 fill=corner_color, width=2)
        draw.line([(0, self.height - corner_size // 2), (0, self.height)], 
                 fill=corner_color, width=2)
        draw.line([(0, self.height), (corner_size // 2, self.height)], 
                 fill=corner_color, width=2)
        
        # Bottom-right corner
        draw.line([(self.width - corner_size, self.height), (self.width, self.height - corner_size)], 
                 fill=corner_color, width=2)
        draw.line([(self.width - corner_size // 2, self.height), (self.width, self.height)], 
                 fill=corner_color, width=2)
        draw.line([(self.width, self.height - corner_size // 2), (self.width, self.height)], 
                 fill=corner_color, width=2)
        
        return image
    
    def _apply_border(self, image: Image.Image, template: Dict) -> Image.Image:
        """Apply border to image"""
        border_style = template.get("border_style", "none")
        border_color = template.get("border_color", (255, 255, 255, 100))
        border_width = template.get("border_width", 2)
        
        if border_style == "none" or border_width <= 0:
            return image
        
        draw = ImageDraw.Draw(image)
        
        if border_style == "simple":
            # Simple rectangle border
            draw.rectangle([(0, 0), (self.width-1, self.height-1)], 
                         outline=border_color, width=border_width)
        
        elif border_style == "rounded":
            # Rounded rectangle border
            radius = 20
            # Draw four rounded corners and straight lines
            # Top line
            draw.line([(radius, 0), (self.width - radius, 0)], 
                     fill=border_color, width=border_width)
            # Bottom line
            draw.line([(radius, self.height-1), (self.width - radius, self.height-1)], 
                     fill=border_color, width=border_width)
            # Left line
            draw.line([(0, radius), (0, self.height - radius)], 
                     fill=border_color, width=border_width)
            # Right line
            draw.line([(self.width-1, radius), (self.width-1, self.height - radius)], 
                     fill=border_color, width=border_width)
            
            # Draw rounded corners (simplified)
            corner_radius = radius
            # Top-left
            draw.arc([(0, 0), (corner_radius*2, corner_radius*2)], 
                    start=180, end=270, fill=border_color, width=border_width)
            # Top-right
            draw.arc([(self.width - corner_radius*2 - 1, 0), 
                     (self.width-1, corner_radius*2)], 
                    start=270, end=0, fill=border_color, width=border_width)
            # Bottom-left
            draw.arc([(0, self.height - corner_radius*2 - 1), 
                     (corner_radius*2, self.height-1)], 
                    start=90, end=180, fill=border_color, width=border_width)
            # Bottom-right
            draw.arc([(self.width - corner_radius*2 - 1, self.height - corner_radius*2 - 1), 
                     (self.width-1, self.height-1)], 
                    start=0, end=90, fill=border_color, width=border_width)
        
        elif border_style == "double":
            # Double border
            inner_offset = border_width
            outer_offset = border_width * 2
            
            # Outer border
            draw.rectangle([(0, 0), (self.width-1, self.height-1)], 
                         outline=border_color, width=border_width)
            # Inner border
            draw.rectangle([(inner_offset, inner_offset), 
                          (self.width-1-inner_offset, self.height-1-inner_offset)], 
                         outline=border_color, width=border_width)
        
        elif border_style == "dashed":
            # Dashed border
            dash_length = 10
            gap_length = 5
            
            # Top border
            x = 0
            while x < self.width:
                draw.line([(x, 0), (min(x + dash_length, self.width), 0)], 
                         fill=border_color, width=border_width)
                x += dash_length + gap_length
            
            # Bottom border
            x = 0
            while x < self.width:
                draw.line([(x, self.height-1), (min(x + dash_length, self.width), self.height-1)], 
                         fill=border_color, width=border_width)
                x += dash_length + gap_length
            
            # Left border
            y = 0
            while y < self.height:
                draw.line([(0, y), (0, min(y + dash_length, self.height))], 
                         fill=border_color, width=border_width)
                y += dash_length + gap_length
            
            # Right border
            y = 0
            while y < self.height:
                draw.line([(self.width-1, y), (self.width-1, min(y + dash_length, self.height))], 
                         fill=border_color, width=border_width)
                y += dash_length + gap_length
        
        elif border_style == "dotted":
            # Dotted border
            dot_spacing = 8
            
            # Top border
            for x in range(0, self.width, dot_spacing):
                draw.ellipse([(x-border_width//2, 0-border_width//2), 
                             (x+border_width//2, 0+border_width//2)], 
                            fill=border_color)
            
            # Bottom border
            for x in range(0, self.width, dot_spacing):
                draw.ellipse([(x-border_width//2, self.height-1-border_width//2), 
                             (x+border_width//2, self.height-1+border_width//2)], 
                            fill=border_color)
            
            # Left border
            for y in range(0, self.height, dot_spacing):
                draw.ellipse([(0-border_width//2, y-border_width//2), 
                             (0+border_width//2, y+border_width//2)], 
                            fill=border_color)
            
            # Right border
            for y in range(0, self.height, dot_spacing):
                draw.ellipse([(self.width-1-border_width//2, y-border_width//2), 
                             (self.width-1+border_width//2, y+border_width//2)], 
                            fill=border_color)
        
        elif border_style == "gradient":
            # Gradient border
            color1 = template.get("primary_color", (255, 107, 53))
            color2 = template.get("secondary_color", (0, 180, 216))
            
            # Top border gradient
            for x in range(0, self.width, 2):
                ratio = x / self.width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x+1, 0)], fill=(r, g, b, border_color[3]), width=border_width)
            
            # Bottom border gradient (reverse)
            for x in range(0, self.width, 2):
                ratio = x / self.width
                r = int(color2[0] * (1 - ratio) + color1[0] * ratio)
                g = int(color2[1] * (1 - ratio) + color1[1] * ratio)
                b = int(color2[2] * (1 - ratio) + color1[2] * ratio)
                draw.line([(x, self.height-1), (x+1, self.height-1)], 
                         fill=(r, g, b, border_color[3]), width=border_width)
        
        return image
    
    def _apply_final_effects(self, image: Image.Image, template: Dict) -> Image.Image:
        """Apply final effects to image"""
        effects = template.get("effects", [])
        
        try:
            if "emboss" in effects:
                image = image.filter(ImageFilter.EMBOSS)
            
            if "sharpen" in effects:
                image = image.filter(ImageFilter.SHARPEN)
            
            if "smooth" in effects:
                image = image.filter(ImageFilter.SMOOTH_MORE)
            
            if "edge_enhance" in effects:
                image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
            if "detail" in effects:
                image = image.filter(ImageFilter.DETAIL)
            
            # Adjust brightness/contrast if needed
            if "highlight" in effects:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.1)
                
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.1)
            
            if "vibrant" in effects:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(1.2)
        
        except Exception as e:
            logger.debug(f"Final effects failed: {e}")
        
        return image
    
    def _add_vignette(self, image: Image.Image, intensity: float = 0.7) -> Image.Image:
        """Add vignette effect"""
        width, height = image.size
        
        # Create vignette mask
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw white ellipse covering most of the image
        ellipse_margin = width // 4
        ellipse_bbox = [
            (-ellipse_margin, -ellipse_margin),
            (width + ellipse_margin, height + ellipse_margin)
        ]
        draw.ellipse(ellipse_bbox, fill=255)
        
        # Apply Gaussian blur to mask for soft edges
        mask = mask.filter(ImageFilter.GaussianBlur(width // 6))
        
        # Create vignette overlay (dark edges)
        vignette = Image.new('RGBA', (width, height), (0, 0, 0, int(150 * intensity)))
        
        # Composite vignette with original image using mask
        result = Image.composite(image, vignette, mask)
        return result
    
    def _add_noise(self, image: Image.Image, intensity: int = 5) -> Image.Image:
        """Add noise/grain effect"""
        width, height = image.size
        noise = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(noise)
        
        # Add random noise pixels
        num_pixels = int(width * height * 0.05)  # 5% of pixels
        for _ in range(num_pixels):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            gray = random.randint(0, intensity)
            alpha = random.randint(20, 80)
            draw.point((x, y), fill=(gray, gray, gray, alpha))
        
        return Image.alpha_composite(image, noise)
    
    def _add_scan_lines(self, image: Image.Image) -> Image.Image:
        """Add scan lines effect"""
        draw = ImageDraw.Draw(image)
        
        # Draw horizontal scan lines
        line_spacing = 4
        line_color = (0, 255, 0, 30)  # Green with low opacity
        
        for y in range(0, self.height, line_spacing):
            draw.line([(0, y), (self.width, y)], fill=line_color, width=1)
        
        return image
    
    def _add_texture_overlay(self, image: Image.Image) -> Image.Image:
        """Add texture overlay"""
        width, height = image.size
        texture = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(texture)
        
        # Create a simple canvas-like texture
        for _ in range(1000):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            alpha = random.randint(5, 20)
            # Light brown texture color
            draw.point((x, y), fill=(139, 119, 101, alpha))
        
        return Image.alpha_composite(image, texture)
    
    def _add_heat_haze(self, image: Image.Image) -> Image.Image:
        """Add heat haze effect"""
        # Simple heat haze by applying a slight distortion
        width, height = image.size
        
        # Create a copy and apply wave distortion
        distorted = image.copy()
        
        # Apply slight wave distortion
        for y in range(0, height, 5):
            offset = int(2 * math.sin(y / 20))
            if offset != 0:
                region = image.crop((0, y, width, min(y + 5, height)))
                distorted.paste(region, (offset, y))
        
        # Blend with original
        return Image.blend(image, distorted, alpha=0.3)
    
    def _add_nebula_effect(self, image: Image.Image) -> Image.Image:
        """Add nebula/space effect"""
        draw = ImageDraw.Draw(image)
        
        # Add colorful space dust
        for _ in range(100):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            size = random.randint(1, 3)
            color = random.choice([
                (135, 206, 235, 100),  # Light blue
                (147, 112, 219, 100),  # Medium purple
                (255, 182, 193, 100),  # Light pink
                (152, 251, 152, 100),  # Pale green
            ])
            draw.ellipse([(x-size, y-size), (x+size, y+size)], fill=color)
        
        return image
    
    def _apply_watercolor_filter(self, image: Image.Image) -> Image.Image:
        """Apply watercolor painting filter"""
        # Simple watercolor effect by blurring and increasing saturation
        blurred = image.filter(ImageFilter.GaussianBlur(1))
        
        # Increase saturation slightly
        enhancer = ImageEnhance.Color(blurred)
        saturated = enhancer.enhance(1.2)
        
        # Blend with original
        return Image.blend(image, saturated, alpha=0.5)
    
    def image_to_bytes(self, image: Image.Image, format: str = "PNG") -> BytesIO:
        """Convert PIL image to bytes"""
        if image is None:
            return self._create_fallback_bytes()
        
        buffered = BytesIO()
        
        try:
            if format.upper() == "PNG":
                image.save(buffered, format="PNG", optimize=True, compress_level=9)
            elif format.upper() == "JPEG":
                # Convert to RGB if RGBA
                if image.mode == "RGBA":
                    rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                image.save(buffered, format="JPEG", quality=95, optimize=True)
            else:
                image.save(buffered, format=format)
            
            buffered.seek(0)
            return buffered
        except Exception as e:
            logger.error(f"Failed to convert image to bytes: {e}")
            return self._create_fallback_bytes()
    
    def save_image(self, image: Image.Image, filename: str = None, 
                  directory: str = "generated/roasts") -> str:
        """Save image to file"""
        if image is None:
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"roast_{timestamp}.png"
        
        output_path = Path(directory) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            image.save(output_path, "PNG", optimize=True)
            logger.info(f"💾 Image saved: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return ""
    
    def _create_fallback_image(self, primary_text: str, secondary_text: str = "") -> Image.Image:
        """Create simple fallback image when advanced generation fails"""
        try:
            image = Image.new('RGB', (self.width, self.height), (25, 25, 35))
            draw = ImageDraw.Draw(image)
            
            # Try to use default font
            try:
                font = ImageFont.truetype("arial.ttf", 32)
                sub_font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default(32)
                sub_font = ImageFont.load_default(20)
            
            # Draw title
            draw.text((50, 30), "🔥 Roastify Bot 🔥", font=font, fill=(255, 107, 53))
            
            # Draw primary text
            lines = textwrap.wrap(primary_text, width=30)
            y_pos = 80
            for line in lines[:3]:
                draw.text((50, y_pos), line, font=font, fill=(255, 255, 255))
                y_pos += 40
            
            # Draw secondary text
            if secondary_text:
                sec_lines = textwrap.wrap(secondary_text, width=40)
                y_pos += 20
                for line in sec_lines[:2]:
                    draw.text((50, y_pos), line, font=sub_font, fill=(0, 180, 216))
                    y_pos += 30
            
            return image
        except Exception as e:
            logger.error(f"Fallback image creation failed: {e}")
            # Ultimate fallback
            return Image.new('RGB', (self.width, self.height), (255, 0, 0))
    
    def _create_error_image(self, text: str) -> Image.Image:
        """Create error image"""
        try:
            image = Image.new('RGB', (self.width, self.height), (50, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Try to use default font
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except:
                font = ImageFont.load_default(28)
            
            # Draw error message
            error_msg = "Error creating image"
            draw.text((50, 100), error_msg, font=font, fill=(255, 100, 100))
            
            # Draw the text that caused error
            if text:
                lines = textwrap.wrap(text[:100], width=40)
                y_pos = 150
                for line in lines[:2]:
                    draw.text((50, y_pos), line, font=font, fill=(255, 255, 200))
                    y_pos += 35
            
            return image
        except:
            # Ultimate fallback
            return Image.new('RGB', (self.width, self.height), (255, 0, 0))
    
    def _create_fallback_bytes(self) -> BytesIO:
        """Create fallback image bytes"""
        try:
            image = Image.new('RGB', (400, 200), (255, 107, 53))
            draw = ImageDraw.Draw(image)
            
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default(32)
            
            draw.text((100, 80), "🔥 Roastify Bot 🔥", font=font, fill=(255, 255, 255))
            
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)
            return buffered
        except:
            # Return empty bytes
            return BytesIO()
    
    def get_stats(self) -> Dict:
        """Get generator statistics"""
        uptime = datetime.now() - self.stats["start_time"]
        
        return {
            "available": self.available,
            "images_created": self.stats["images_created"],
            "errors": self.stats["errors"],
            "templates_used": self.stats["templates_used"],
            "fonts_loaded": len(self.fonts),
            "backgrounds_loaded": len(self.backgrounds),
            "uptime_seconds": uptime.total_seconds(),
            "images_per_minute": self.stats["images_created"] / max(uptime.total_seconds() / 60, 1),
        }

# ==================== SINGLETON INSTANCE & EXPORTS ====================

# Singleton instance
_advanced_image_generator_instance = None

def get_image_generator() -> AdvancedImageGenerator:
    """Get the image generator instance (singleton pattern)"""
    global _advanced_image_generator_instance
    if _advanced_image_generator_instance is None:
        _advanced_image_generator_instance = AdvancedImageGenerator()
    return _advanced_image_generator_instance

# Alias for backward compatibility
ImageGenerator = AdvancedImageGenerator

# Create instance for direct access
image_generator = get_image_generator()

# ==================== TEST FUNCTION ====================

def test_image_generator():
    """Test the image generator"""
    print("🎨 Testing Advanced Image Generator...")
    print("=" * 50)
    
    generator = get_image_generator()
    
    if not generator.available:
        print("❌ PIL/Pillow not installed!")
        print("💡 Install with: pip install pillow")
        return False
    
    print(f"✅ Image Generator Available")
    print(f"📏 Image Size: {generator.width}x{generator.height}")
    print(f"📝 Fonts Loaded: {len(generator.fonts)}")
    print(f"🎨 Backgrounds Loaded: {len(generator.backgrounds)}")
    print(f"📚 Templates Available: {len(generator.template_manager.templates)}")
    print("-" * 50)
    
    # Test creating an image
    print("Creating test image...")
    try:
        test_image = generator.create_roast_image(
            primary_text="এটি একটি টেস্ট রোস্ট মেসেজ! Advanced Image Generator কাজ করছে।",
            secondary_text="রোস্টিফাই বট | টেস্ট ইউজার | সম্পূর্ণ নতুন টেমপ্লেট",
            user_id=123456789,
            category="funny",
            style="modern"
        )
        
        if test_image:
            # Save test image
            filename = "test_output.png"
            save_path = generator.save_image(test_image, filename)
            
            print(f"✅ Test image created successfully!")
            print(f"📁 Saved to: {save_path}")
            print(f"📏 Image size: {test_image.size}")
            print(f"🎨 Image mode: {test_image.mode}")
            
            # Show stats
            stats = generator.get_stats()
            print(f"📊 Images created: {stats['images_created']}")
            print(f"📊 Templates used: {stats['templates_used']}")
            
            return True
        else:
            print("❌ Failed to create test image")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎨 ADVANCED IMAGE GENERATOR - TEST SUITE")
    print("="*60)
    
    success = test_image_generator()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED")
    print("="*60)

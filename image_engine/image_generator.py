from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import random
from config import Config
from utils.logger import logger
from utils.helpers import Helpers
from utils.time_manager import TimeManager
from .templates import TemplateManager

class ImageGenerator:
    def __init__(self):
        self.template_manager = TemplateManager()
        self.assets_path = Path(Config.ASSETS_PATH)
        self.fonts_path = Path(Config.FONTS_PATH)
        self.backgrounds_path = Path(Config.BACKGROUNDS_PATH)
        
        # Ensure directories exist
        self.fonts_path.mkdir(parents=True, exist_ok=True)
        self.backgrounds_path.mkdir(parents=True, exist_ok=True)
    
    def create_roast_image(self, primary_text: str, secondary_text: str, 
                          user_id: int, user_photo_path: str = None) -> Image.Image:
        """রোস্ট ইমেজ তৈরি করে"""
        try:
            # Get template
            template = self.template_manager.get_template(user_id)
            
            # Create base image
            if "background" in template:
                bg_path = self.backgrounds_path / template["background"]
                if bg_path.exists():
                    image = Image.open(bg_path).convert("RGBA")
                    image = image.resize((Config.IMAGE_WIDTH, Config.IMAGE_HEIGHT))
                else:
                    image = self._create_gradient_background(template)
            else:
                image = self._create_gradient_background(template)
            
            # Apply effects
            image = self._apply_background_effects(image, template)
            
            # Add user photo if provided
            if user_photo_path and Path(user_photo_path).exists():
                image = self._add_user_photo(image, user_photo_path, template)
            
            # Prepare text
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            primary_font = self._load_font(
                template.get("font", "arial.ttf"),
                template.get("font_size", 60)
            )
            
            secondary_font = self._load_font(
                template.get("font", "arial.ttf"),
                template.get("sub_font_size", 30)
            )
            
            # Get positions
            primary_pos = template.get("position", {"x": 540, "y": 400})
            secondary_pos = template.get("sub_position", {"x": 540, "y": 500})
            
            # Split text if too long
            primary_lines = Helpers.split_text_for_image(primary_text, 25)
            secondary_lines = Helpers.split_text_for_image(secondary_text, 35)
            
            # Draw primary text with effects
            primary_color = tuple(template.get("primary_color", (255, 255, 255)))
            self._draw_text_with_effects(
                draw, primary_lines, primary_font, 
                primary_pos, primary_color, template
            )
            
            # Draw secondary text
            secondary_color = tuple(template.get("secondary_color", (200, 200, 200)))
            self._draw_text_with_effects(
                draw, secondary_lines, secondary_font,
                secondary_pos, secondary_color, template, is_secondary=True
            )
            
            # Add decorative elements
            image = self._add_decorative_elements(image, template)
            
            return image
            
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            # Return a simple error image
            return self._create_error_image()
    
    def _create_gradient_background(self, template: Dict) -> Image.Image:
        """গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড তৈরি করে"""
        image = Image.new('RGBA', (Config.IMAGE_WIDTH, Config.IMAGE_HEIGHT))
        draw = ImageDraw.Draw(image)
        
        # Get theme-based colors
        theme = Helpers.get_time_based_theme()
        
        if theme["theme"] == "day":
            color1 = (135, 206, 235)  # Light blue
            color2 = (255, 255, 255)  # White
        else:
            color1 = (25, 25, 35)     # Dark blue
            color2 = (50, 50, 70)     # Darker blue
        
        # Draw gradient
        for y in range(Config.IMAGE_HEIGHT):
            ratio = y / Config.IMAGE_HEIGHT
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (Config.IMAGE_WIDTH, y)], fill=(r, g, b, 255))
        
        return image
    
    def _apply_background_effects(self, image: Image.Image, template: Dict) -> Image.Image:
        """ব্যাকগ্রাউন্ডে ইফেক্ট অ্যাপ্লাই করে"""
        effects = template.get("effects", [])
        
        if "blur" in effects:
            image = image.filter(ImageFilter.GaussianBlur(radius=2))
        
        if "vignette" in effects:
            image = self._apply_vignette(image)
        
        if "noise" in effects:
            image = self._add_noise(image, intensity=5)
        
        return image
    
    def _add_user_photo(self, image: Image.Image, photo_path: str, template: Dict) -> Image.Image:
        """ইউজারের ফটো অ্যাড করে"""
        try:
            user_img = Image.open(photo_path).convert("RGBA")
            
            # Crop to circle
            user_img = self._crop_to_circle(user_img)
            
            # Resize
            size = 200
            user_img = user_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Apply effects
            if "glass_effect" in template.get("photo_effects", []):
                user_img = self._apply_glass_effect(user_img)
            
            # Position
            x = (Config.IMAGE_WIDTH - size) // 2
            y = 100
            
            # Create a shadow
            shadow = Image.new('RGBA', (size + 10, size + 10), (0, 0, 0, 100))
            shadow = self._crop_to_circle(shadow)
            image.paste(shadow, (x - 5, y - 5), shadow)
            
            # Paste user image
            image.paste(user_img, (x, y), user_img)
            
            return image
            
        except Exception as e:
            logger.error(f"Error adding user photo: {e}")
            return image
    
    def _crop_to_circle(self, image: Image.Image) -> Image.Image:
        """ইমেজকে বৃত্তাকারে ক্রপ করে"""
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), image.size], fill=255)
        
        result = Image.new('RGBA', image.size)
        result.paste(image, (0, 0), mask)
        return result
    
    def _load_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """ফন্ট লোড করে"""
        font_paths = [
            self.fonts_path / font_name,
            Path(font_name),
            Path("fonts") / font_name
        ]
        
        for font_path in font_paths:
            if font_path.exists():
                try:
                    return ImageFont.truetype(str(font_path), size)
                except:
                    continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def _draw_text_with_effects(self, draw: ImageDraw.Draw, lines: List[str], 
                               font: ImageFont.FreeTypeFont, position: Dict,
                               color: Tuple, template: Dict, is_secondary: bool = False):
        """টেক্সট ইফেক্ট সহ ড্র করে"""
        effects = template.get("effects", [])
        
        # Calculate total height
        line_height = font.size + 10
        total_height = len(lines) * line_height
        start_y = position["y"] - (total_height // 2)
        
        for i, line in enumerate(lines):
            y_pos = start_y + (i * line_height)
            
            # Calculate text width for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_pos = position["x"] - (text_width // 2)
            
            # Apply effects
            if "shadow" in effects and not is_secondary:
                # Draw shadow
                shadow_offset = 4
                draw.text(
                    (x_pos + shadow_offset, y_pos + shadow_offset),
                    line, font=font, fill=(0, 0, 0, 150)
                )
            
            if "outline" in effects and not is_secondary:
                # Draw outline
                outline_size = 2
                for ox in range(-outline_size, outline_size + 1):
                    for oy in range(-outline_size, outline_size + 1):
                        if ox != 0 or oy != 0:
                            draw.text(
                                (x_pos + ox, y_pos + oy),
                                line, font=font, fill=(0, 0, 0, 200)
                            )
            
            # Draw main text
            draw.text((x_pos, y_pos), line, font=font, fill=color)
    
    def _apply_vignette(self, image: Image.Image) -> Image.Image:
        """ভিগনেট ইফেক্ট অ্যাপ্লাই করে"""
        width, height = image.size
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw white ellipse
        ellipse_bbox = [(-width//2, -height//2), (width*3//2, height*3//2)]
        draw.ellipse(ellipse_bbox, fill=255)
        
        # Apply Gaussian blur to mask
        mask = mask.filter(ImageFilter.GaussianBlur(radius=width//4))
        
        # Create vignette
        vignette = Image.new('RGBA', (width, height), (0, 0, 0, 150))
        image.paste(vignette, (0, 0), mask)
        
        return image
    
    def _add_noise(self, image: Image.Image, intensity: int = 5) -> Image.Image:
        """নয়েজ/গ্রেইন অ্যাড করে"""
        from PIL import ImageMath
        
        noise = Image.new('RGBA', image.size)
        pixels = noise.load()
        
        for x in range(image.width):
            for y in range(image.height):
                if random.random() < 0.1:  # 10% pixels
                    alpha = random.randint(200, 255)
                    gray = random.randint(0, intensity)
                    pixels[x, y] = (gray, gray, gray, alpha)
        
        return Image.alpha_composite(image, noise)
    
    def _apply_glass_effect(self, image: Image.Image) -> Image.Image:
        """গ্লাস ইফেক্ট অ্যাপ্লাই করে"""
        # Apply slight blur
        blurred = image.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Create glass effect with transparency
        glass = Image.new('RGBA', image.size, (255, 255, 255, 30))
        
        # Composite images
        result = Image.alpha_composite(blurred, glass)
        return result
    
    def _add_decorative_elements(self, image: Image.Image, template: Dict) -> Image.Image:
        """ডেকোরেটিভ এলিমেন্ট অ্যাড করে"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Add border if needed
        border_color = template.get("border_color", (100, 100, 100, 150))
        border_width = 10
        draw.rectangle(
            [(border_width, border_width), 
             (width - border_width, height - border_width)],
            outline=border_color, width=2
        )
        
        # Add corner decorations
        corner_size = 30
        for x, y in [(0, 0), (width - corner_size, 0), 
                     (0, height - corner_size), (width - corner_size, height - corner_size)]:
            draw.rectangle(
                [(x, y), (x + corner_size, y + corner_size)],
                outline=border_color, width=2
            )
        
        return image
    
    def _create_error_image(self) -> Image.Image:
        """এরর ইমেজ তৈরি করে"""
        image = Image.new('RGBA', (Config.IMAGE_WIDTH, Config.IMAGE_HEIGHT), 
                         (255, 200, 200, 255))
        draw = ImageDraw.Draw(image)
        
        font = self._load_font("arial.ttf", 40)
        text = "ইমেজ তৈরি করতে সমস্যা!"
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (Config.IMAGE_WIDTH - text_width) // 2
        y = Config.IMAGE_HEIGHT // 2
        
        draw.text((x, y), text, font=font, fill=(255, 0, 0, 255))
        
        return image
    
    def save_image(self, image: Image.Image, filename: str = None) -> str:
        """ইমেজ ফাইল হিসেবে সেভ করে"""
        if filename is None:
            timestamp = TimeManager.get_current_time().strftime("%Y%m%d_%H%M%S")
            filename = f"roast_{timestamp}.png"
        
        output_path = Path("generated") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        image.save(output_path, "PNG", optimize=True)
        return str(output_path)
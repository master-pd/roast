#!/usr/bin/env python3
"""
Assets Setup Script for Roastify Bot
Downloads and organizes required assets
"""

import os
import requests
from pathlib import Path
from zipfile import ZipFile
import shutil

class AssetSetup:
    def __init__(self):
        self.base_path = Path("assets")
        self.fonts_path = self.base_path / "fonts"
        self.backgrounds_path = self.base_path / "backgrounds"
        self.templates_path = self.base_path / "templates"
        
    def setup_directories(self):
        """সকল ডিরেক্টরি তৈরি করে"""
        print("📁 Creating directories...")
        
        directories = [
            self.base_path,
            self.fonts_path,
            self.backgrounds_path,
            self.templates_path,
            Path("generated"),
            Path("logs"),
            Path("temp")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {directory}")
        
        print("✅ Directories created\n")
    
    def download_default_fonts(self):
        """ডিফল্ট ফন্ট ডাউনলোড করে"""
        print("🔤 Downloading default fonts...")
        
        fonts = {
            "arial.ttf": "https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/Arial/Regular/complete/Arial%20Regular.ttf",
            "comic.ttf": "https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/ComicShanns/Regular/complete/Comic%20Shanns%20Regular%20Nerd%20Font%20Complete.ttf",
        }
        
        for font_name, url in fonts.items():
            font_path = self.fonts_path / font_name
            
            if not font_path.exists():
                try:
                    print(f"  Downloading {font_name}...")
                    response = requests.get(url, stream=True)
                    response.raise_for_status()
                    
                    with open(font_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"  ✓ {font_name}")
                except Exception as e:
                    print(f"  ✗ Failed to download {font_name}: {e}")
            else:
                print(f"  ✓ {font_name} (already exists)")
        
        print("✅ Fonts downloaded\n")
    
    def create_default_backgrounds(self):
        """ডিফল্ট ব্যাকগ্রাউন্ড তৈরি করে"""
        print("🎨 Creating default backgrounds...")
        
        from PIL import Image, ImageDraw
        import random
        
        backgrounds = [
            ("gradient_day.png", self._create_gradient_bg, {"theme": "day"}),
            ("gradient_night.png", self._create_gradient_bg, {"theme": "night"}),
            ("simple_white.png", self._create_simple_bg, {"color": (255, 255, 255)}),
            ("simple_black.png", self._create_simple_bg, {"color": (0, 0, 0)}),
        ]
        
        for bg_name, creator_func, kwargs in backgrounds:
            bg_path = self.backgrounds_path / bg_name
            
            if not bg_path.exists():
                try:
                    print(f"  Creating {bg_name}...")
                    image = creator_func(**kwargs)
                    image.save(bg_path, "PNG")
                    print(f"  ✓ {bg_name}")
                except Exception as e:
                    print(f"  ✗ Failed to create {bg_name}: {e}")
            else:
                print(f"  ✓ {bg_name} (already exists)")
        
        print("✅ Backgrounds created\n")
    
    def _create_gradient_bg(self, theme="day"):
        """গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড তৈরি করে"""
        from PIL import Image, ImageDraw
        
        width, height = 1080, 1080
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        if theme == "day":
            color1 = (135, 206, 235)  # Light blue
            color2 = (255, 255, 255)  # White
        else:
            color1 = (25, 25, 35)     # Dark blue
            color2 = (50, 50, 70)     # Darker blue
        
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    
    def _create_simple_bg(self, color=(255, 255, 255)):
        """সিম্পল ব্যাকগ্রাউন্ড তৈরি করে"""
        from PIL import Image
        
        width, height = 1080, 1080
        image = Image.new('RGB', (width, height), color)
        return image
    
    def create_template_config(self):
        """টেমপ্লেট কনফিগ তৈরি করে"""
        print("📝 Creating template configuration...")
        
        template_file = self.templates_path / "templates.json"
        
        if not template_file.exists():
            default_templates = {
                "templates": {
                    "cartoon_roast": [
                        {
                            "id": "cartoon_1",
                            "name": "Cartoon Funny",
                            "background": "gradient_day.png",
                            "font": "arial.ttf",
                            "primary_color": [255, 105, 180],
                            "secondary_color": [0, 0, 0],
                            "font_size": 60,
                            "sub_font_size": 30,
                            "position": {"x": 540, "y": 400},
                            "sub_position": {"x": 540, "y": 500},
                            "effects": ["shadow", "outline"]
                        }
                    ],
                    "neon_savage": [
                        {
                            "id": "neon_1",
                            "name": "Neon Red",
                            "background": "gradient_night.png",
                            "font": "arial.ttf",
                            "primary_color": [255, 0, 100],
                            "secondary_color": [0, 255, 255],
                            "font_size": 65,
                            "sub_font_size": 32,
                            "position": {"x": 540, "y": 420},
                            "sub_position": {"x": 540, "y": 520},
                            "effects": ["glow", "blur"]
                        }
                    ]
                },
                "total_templates": 50,
                "unlocked_templates": ["cartoon_1", "neon_1"]
            }
            
            import json
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(default_templates, f, indent=2, ensure_ascii=False)
            
            print("✓ templates.json created")
        else:
            print("✓ templates.json (already exists)")
        
        print("\n✅ Template config created")
    
    def setup_complete(self):
        """সেটআপ কমপ্লিট মেসেজ"""
        print("\n" + "="*50)
        print("🎉 Asset Setup Complete!")
        print("="*50)
        print("\nNext steps:")
        print("1. Add your bot token to .env file")
        print("2. Add more fonts to assets/fonts/")
        print("3. Add background images to assets/backgrounds/")
        print("4. Customize templates in assets/templates/templates.json")
        print("5. Run: python main.py")
        print("\nHappy roasting! 😈")

def main():
    """মেইন ফাংশন"""
    print("🤖 Roastify Bot Asset Setup")
    print("="*50)
    
    setup = AssetSetup()
    setup.setup_directories()
    setup.download_default_fonts()
    setup.create_default_backgrounds()
    setup.create_template_config()
    setup.setup_complete()

if __name__ == "__main__":
    main()
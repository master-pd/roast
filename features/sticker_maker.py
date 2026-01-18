#!/usr/bin/env python3
"""
🎨 Advanced Sticker Maker for Roastify Bot
✅ Smart Enhancement | Error Fixed | Professional Quality
"""

import os
import io
import random
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, Union
from datetime import datetime

try:
    from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL not installed. Sticker features disabled.")

# Telegram imports
from telegram import Update, Message, File
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# Config imports
from config import Config
from utils.logger import logger, log_error, log_info
from utils.time_manager import TimeManager
from utils.helpers import Helpers

class AdvancedStickerMaker:
    """অ্যাডভান্সড স্টিকার তৈরি করার ক্লাস"""
    
    def __init__(self):
        self.stickers_dir = Path("generated/stickers")
        self.stickers_dir.mkdir(parents=True, exist_ok=True)
        
        # Telegram limits
        self.MAX_STICKER_SIZE = 512 * 1024  # 512KB
        self.MAX_DIMENSION = 512  # pixels
        self.MIN_DIMENSION = 100  # pixels
        
        # Supported formats
        self.SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
        
        # Sticker styles
        self.STICKER_STYLES = {
            "regular": {"size": (512, 512), "format": "webp", "quality": 90},
            "circle": {"size": (512, 512), "format": "webp", "quality": 90, "crop": "circle"},
            "rounded": {"size": (512, 512), "format": "webp", "quality": 90, "radius": 50},
            "bordered": {"size": (512, 512), "format": "webp", "quality": 90, "border": 10},
            "shadow": {"size": (512, 512), "format": "webp", "quality": 90, "shadow": True},
            "transparent": {"size": (512, 512), "format": "webp", "quality": 90, "bg": "transparent"},
            "white_bg": {"size": (512, 512), "format": "webp", "quality": 90, "bg": "white"},
            "black_bg": {"size": (512, 512), "format": "webp", "quality": 90, "bg": "black"},
            "vibrant": {"size": (512, 512), "format": "webp", "quality": 90, "enhance": True},
            "cartoon": {"size": (512, 512), "format": "webp", "quality": 90, "cartoon": True},
        }
        
        # Statistics
        self.stats = {
            "stickers_created": 0,
            "errors": 0,
            "total_size": 0,
            "start_time": datetime.now()
        }
        
        logger.info("✅ Advanced StickerMaker initialized")
        logger.info(f"📁 Sticker directory: {self.stickers_dir}")
    
    async def create_sticker_from_message(self, message: Message) -> Optional[str]:
        """
        টেলিগ্রাম মেসেজ থেকে স্টিকার তৈরি করে
        
        Args:
            message: টেলিগ্রাম মেসেজ অবজেক্ট
        
        Returns:
            str: স্টিকার ফাইল পাথ অথবা None
        """
        try:
            if not PIL_AVAILABLE:
                logger.error("PIL not available for sticker creation")
                return None
            
            # Check if message has photo
            if not message.photo:
                logger.warning("Message doesn't contain a photo")
                return None
            
            # Get the largest photo
            photo = max(message.photo, key=lambda p: p.file_size)
            
            # Download the photo
            photo_file = await photo.get_file()
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
                await photo_file.download_to_drive(temp_path)
            
            try:
                # Create sticker
                sticker_path = await self._create_sticker_from_image(temp_path)
                return sticker_path
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            log_error(f"Error creating sticker from message: {e}")
            self.stats["errors"] += 1
            return None
    
    async def create_sticker_from_image(self, image_path: str, style: str = "random") -> Optional[str]:
        """
        ইমেজ ফাইল থেকে স্টিকার তৈরি করে
        
        Args:
            image_path: ইমেজ ফাইল পাথ
            style: স্টিকার স্টাইল
        
        Returns:
            str: স্টিকার ফাইল পাথ
        """
        try:
            if not PIL_AVAILABLE:
                return None
            
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Validate image
            if not self._validate_image(image_path):
                logger.error(f"Invalid image file: {image_path}")
                return None
            
            # Create sticker
            sticker_path = await self._create_sticker_from_image(image_path, style)
            return sticker_path
            
        except Exception as e:
            log_error(f"Error creating sticker from image: {e}")
            self.stats["errors"] += 1
            return None
    
    async def _create_sticker_from_image(self, image_path: str, style: str = "random") -> Optional[str]:
        """ইমেজ থেকে স্টিকার তৈরি করে (ইন্টারনাল মেথড)"""
        try:
            # Select random style if not specified
            if style == "random":
                style = random.choice(list(self.STICKER_STYLES.keys()))
            
            style_config = self.STICKER_STYLES.get(style, self.STICKER_STYLES["regular"])
            
            # Open image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Apply enhancements based on style
                img = self._apply_style_enhancements(img, style_config)
                
                # Resize to sticker dimensions
                img = self._resize_for_sticker(img, style_config)
                
                # Apply effects based on style
                img = self._apply_style_effects(img, style_config)
                
                # Create output path
                timestamp = TimeManager.get_current_time().strftime("%Y%m%d_%H%M%S_%f")
                sticker_filename = f"sticker_{timestamp}_{style}.webp"
                sticker_path = self.stickers_dir / sticker_filename
                
                # Save as WebP (Telegram sticker format)
                save_kwargs = {
                    'format': 'WEBP',
                    'quality': style_config.get('quality', 90),
                    'method': 6,  # Best quality
                    'lossless': False
                }
                
                # Add transparency if needed
                if style_config.get('bg') == 'transparent' and img.mode == 'RGB':
                    img = img.convert('RGBA')
                    data = img.getdata()
                    new_data = []
                    for item in data:
                        # Make white pixels transparent
                        if item[0] > 200 and item[1] > 200 and item[2] > 200:
                            new_data.append((255, 255, 255, 0))
                        else:
                            new_data.append(item)
                    img.putdata(new_data)
                
                img.save(sticker_path, **save_kwargs)
                
                # Check file size
                file_size = os.path.getsize(sticker_path)
                if file_size > self.MAX_STICKER_SIZE:
                    logger.warning(f"Sticker too large ({file_size} bytes), compressing...")
                    sticker_path = await self._compress_sticker(sticker_path)
                
                # Update statistics
                self.stats["stickers_created"] += 1
                self.stats["total_size"] += os.path.getsize(sticker_path)
                
                logger.info(f"✅ Sticker created: {sticker_path} ({style} style)")
                return str(sticker_path)
                
        except Exception as e:
            log_error(f"Error in _create_sticker_from_image: {e}")
            self.stats["errors"] += 1
            return None
    
    def _validate_image(self, image_path: str) -> bool:
        """ইমেজ ভ্যালিডেট করে"""
        try:
            with Image.open(image_path) as img:
                # Check dimensions
                width, height = img.size
                if width < self.MIN_DIMENSION or height < self.MIN_DIMENSION:
                    logger.warning(f"Image too small: {width}x{height}")
                    return False
                
                # Check file size (rough estimate)
                file_size = os.path.getsize(image_path)
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    logger.warning(f"Image too large: {file_size} bytes")
                    return False
                
                return True
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False
    
    def _apply_style_enhancements(self, img: Image.Image, style_config: Dict) -> Image.Image:
        """স্টাইল অনুযায়ী ইমেজ এনহ্যান্সমেন্ট অ্যাপ্লাই করে"""
        try:
            enhancements = []
            
            # Vibrant style
            if style_config.get('enhance'):
                # Increase saturation
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.3)
                
                # Increase contrast
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
            
            # Cartoon style
            if style_config.get('cartoon'):
                # Apply edge enhancement and posterize
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                img = img.filter(ImageFilter.SMOOTH_MORE)
                # Simple color reduction
                img = img.convert('P', palette=Image.ADAPTIVE, colors=64)
                img = img.convert('RGB')
            
            return img
        except Exception as e:
            log_error(f"Style enhancement error: {e}")
            return img
    
    def _resize_for_sticker(self, img: Image.Image, style_config: Dict) -> Image.Image:
        """স্টিকার সাইজে রিসাইজ করে"""
        try:
            target_size = style_config.get('size', (512, 512))
            
            # Maintain aspect ratio
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Create new image with target size
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            
            # Calculate position to center the image
            img_width, img_height = img.size
            target_width, target_height = target_size
            
            left = (target_width - img_width) // 2
            top = (target_height - img_height) // 2
            
            # Paste image centered
            new_img.paste(img, (left, top))
            
            return new_img
        except Exception as e:
            log_error(f"Resize error: {e}")
            return img
    
    def _apply_style_effects(self, img: Image.Image, style_config: Dict) -> Image.Image:
        """স্টাইল ইফেক্ট অ্যাপ্লাই করে"""
        try:
            # Circle crop
            if style_config.get('crop') == 'circle':
                mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse([(0, 0), img.size], fill=255)
                
                result = Image.new('RGBA', img.size, (255, 255, 255, 0))
                result.paste(img, (0, 0), mask)
                img = result
            
            # Rounded corners
            elif style_config.get('radius'):
                radius = style_config['radius']
                img = self._add_rounded_corners(img, radius)
            
            # Border
            elif style_config.get('border'):
                border_size = style_config['border']
                img = ImageOps.expand(img, border=border_size, fill='black')
                img = ImageOps.expand(img, border=2, fill='white')
            
            # Shadow effect
            elif style_config.get('shadow'):
                img = self._add_shadow_effect(img)
            
            # Background color
            elif style_config.get('bg'):
                bg_color = style_config['bg']
                if bg_color in ['white', 'black']:
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, bg_color)
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = Image.new('RGB', img.size, bg_color)
            
            return img
        except Exception as e:
            log_error(f"Style effects error: {e}")
            return img
    
    def _add_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """রাউন্ডেড কর্নার অ্যাড করে"""
        try:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            
            # Draw rounded rectangle
            draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
            
            result = Image.new('RGBA', img.size, (255, 255, 255, 0))
            result.paste(img, (0, 0), mask)
            
            return result
        except Exception as e:
            log_error(f"Rounded corners error: {e}")
            return img
    
    def _add_shadow_effect(self, img: Image.Image) -> Image.Image:
        """শ্যাডো ইফেক্ট অ্যাড করে"""
        try:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create shadow
            shadow = Image.new('RGBA', (img.width + 20, img.height + 20), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            
            # Draw shadow (semi-transparent black)
            shadow_draw.rounded_rectangle(
                [(10, 10), (img.width + 10, img.height + 10)],
                radius=20,
                fill=(0, 0, 0, 100)
            )
            
            # Paste original image on top of shadow
            shadow.paste(img, (0, 0), img if img.mode == 'RGBA' else None)
            
            return shadow
        except Exception as e:
            log_error(f"Shadow effect error: {e}")
            return img
    
    async def _compress_sticker(self, sticker_path: str) -> str:
        """স্টিকার কম্প্রেস করে"""
        try:
            with Image.open(sticker_path) as img:
                # Convert to WebP with lower quality
                compressed_path = sticker_path.replace('.webp', '_compressed.webp')
                
                save_kwargs = {
                    'format': 'WEBP',
                    'quality': 75,  # Lower quality
                    'method': 4,    # Faster compression
                    'lossless': False
                }
                
                img.save(compressed_path, **save_kwargs)
                
                # Remove original if compression successful
                if os.path.getsize(compressed_path) <= self.MAX_STICKER_SIZE:
                    os.remove(sticker_path)
                    return compressed_path
                else:
                    # If still too large, reduce dimensions
                    os.remove(compressed_path)
                    return await self._reduce_dimensions(sticker_path)
                    
        except Exception as e:
            log_error(f"Compression error: {e}")
            return sticker_path
    
    async def _reduce_dimensions(self, sticker_path: str) -> str:
        """ডাইমেনশন রিডিউস করে"""
        try:
            with Image.open(sticker_path) as img:
                # Reduce size by 10%
                new_width = int(img.width * 0.9)
                new_height = int(img.height * 0.9)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                reduced_path = sticker_path.replace('.webp', '_reduced.webp')
                img.save(reduced_path, format='WEBP', quality=80)
                
                # Remove original
                os.remove(sticker_path)
                
                return reduced_path
        except Exception as e:
            log_error(f"Dimension reduction error: {e}")
            return sticker_path
    
    async def create_sticker_from_text(self, text: str, user_id: int = None, style: str = "regular") -> Optional[str]:
        """
        টেক্সট থেকে স্টিকার তৈরি করে
        
        Args:
            text: টেক্সট
            user_id: ইউজার আইডি
            style: স্টাইল
        
        Returns:
            str: স্টিকার ফাইল পাথ
        """
        try:
            if not PIL_AVAILABLE:
                return None
            
            # Create text image
            text_img = self._create_text_image(text, user_id)
            if not text_img:
                return None
            
            # Save temp image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                text_img.save(temp_path, 'PNG')
            
            try:
                # Create sticker from temp image
                sticker_path = await self._create_sticker_from_image(temp_path, style)
                return sticker_path
            finally:
                # Cleanup
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            log_error(f"Error creating sticker from text: {e}")
            self.stats["errors"] += 1
            return None
    
    def _create_text_image(self, text: str, user_id: int = None) -> Optional[Image.Image]:
        """টেক্সট ইমেজ তৈরি করে"""
        try:
            # Create image
            img = Image.new('RGB', (400, 200), color=(255, 107, 53))
            draw = ImageDraw.Draw(img)
            
            # Try to load font
            try:
                from PIL import ImageFont
                font_path = Path("assets/fonts/arial.ttf")
                if font_path.exists():
                    font = ImageFont.truetype(str(font_path), 30)
                else:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Draw text
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (400 - text_width) // 2
            y = (200 - text_height) // 2
            
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
            
            # Add user info if available
            if user_id:
                user_text = f"User: {user_id}"
                draw.text((10, 170), user_text, font=font, fill=(200, 200, 200))
            
            return img
        except Exception as e:
            log_error(f"Text image creation error: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """স্ট্যাটিস্টিক্স রিটার্ন করে"""
        uptime = datetime.now() - self.stats["start_time"]
        
        return {
            "stickers_created": self.stats["stickers_created"],
            "errors": self.stats["errors"],
            "total_size_mb": self.stats["total_size"] / (1024 * 1024),
            "uptime_seconds": uptime.total_seconds(),
            "stickers_per_minute": self.stats["stickers_created"] / max(uptime.total_seconds() / 60, 1),
            "success_rate": (self.stats["stickers_created"] / max(self.stats["stickers_created"] + self.stats["errors"], 1)) * 100,
            "available_styles": list(self.STICKER_STYLES.keys())
        }
    
    async def cleanup_old_stickers(self, days_old: int = 7):
        """পুরানো স্টিকার ডিলিট করে"""
        try:
            current_time = TimeManager.get_current_time()
            deleted_count = 0
            
            for sticker_file in self.stickers_dir.glob("*.webp"):
                file_time = datetime.fromtimestamp(sticker_file.stat().st_mtime)
                age_days = (current_time - file_time).days
                
                if age_days > days_old:
                    try:
                        sticker_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete {sticker_file}: {e}")
            
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} old stickers")
                
        except Exception as e:
            log_error(f"Cleanup error: {e}")

# ==================== MAIN INSTANCE ====================

# Create global instance
sticker_maker = AdvancedStickerMaker()

# Alias for backward compatibility
StickerMaker = AdvancedStickerMaker

# ==================== HELPER FUNCTIONS ====================

async def handle_sticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """স্টিকার কমান্ড হ্যান্ডলার"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        # Check if replying to an image
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "📸 একটি ইমেজে রিপ্লাই দিয়ে /sticker কমান্ড ব্যবহার করুন!",
                parse_mode=ParseMode.HTML
            )
            return
        
        reply_message = update.message.reply_to_message
        
        # Check if message has photo
        if not reply_message.photo:
            await update.message.reply_text(
                "❌ শুধুমাত্র ইমেজ থেকে স্টিকার তৈরি করা যায়!",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔄 স্টিকার তৈরি হচ্ছে...",
            parse_mode=ParseMode.HTML
        )
        
        # Create sticker
        sticker_path = await sticker_maker.create_sticker_from_message(reply_message)
        
        if sticker_path:
            # Send sticker
            with open(sticker_path, 'rb') as sticker_file:
                await context.bot.send_sticker(
                    chat_id=chat.id,
                    sticker=sticker_file,
                    reply_to_message_id=reply_message.message_id
                )
            
            # Update processing message
            await processing_msg.edit_text(
                "✅ স্টিকার তৈরি সম্পূর্ণ!",
                parse_mode=ParseMode.HTML
            )
            
            logger.info(f"Sticker sent to user {user.id} in chat {chat.id}")
        else:
            await processing_msg.edit_text(
                "❌ স্টিকার তৈরি করতে সমস্যা হয়েছে!",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        log_error(f"Sticker command error: {e}")
        try:
            await update.message.reply_text(
                "❌ স্টিকার তৈরি করতে সমস্যা হয়েছে! দয়া করে আবার চেষ্টা করুন।",
                parse_mode=ParseMode.HTML
            )
        except:
            pass

async def handle_text_sticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """টেক্সট থেকে স্টিকার কমান্ড হ্যান্ডলার"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        # Get text from command arguments
        if not context.args:
            await update.message.reply_text(
                "📝 ব্যবহার: /textsticker <your_text_here>",
                parse_mode=ParseMode.HTML
            )
            return
        
        text = ' '.join(context.args)
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            f"🔄 টেক্সট স্টিকার তৈরি হচ্ছে...\n\n\"{text[:50]}...\"",
            parse_mode=ParseMode.HTML
        )
        
        # Create sticker from text
        sticker_path = await sticker_maker.create_sticker_from_text(text, user.id)
        
        if sticker_path:
            # Send sticker
            with open(sticker_path, 'rb') as sticker_file:
                await context.bot.send_sticker(
                    chat_id=chat.id,
                    sticker=sticker_file,
                    reply_to_message_id=update.message.message_id
                )
            
            # Update processing message
            await processing_msg.edit_text(
                "✅ টেক্সট স্টিকার তৈরি সম্পূর্ণ!",
                parse_mode=ParseMode.HTML
            )
        else:
            await processing_msg.edit_text(
                "❌ টেক্সট স্টিকার তৈরি করতে সমস্যা হয়েছে!",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        log_error(f"Text sticker command error: {e}")
        try:
            await update.message.reply_text(
                "❌ স্টিকার তৈরি করতে সমস্যা হয়েছে!",
                parse_mode=ParseMode.HTML
            )
        except:
            pass

# ==================== TEST FUNCTION ====================

async def test_sticker_maker():
    """স্টিকার মেকার টেস্ট করে"""
    print("\n🎨 Testing Advanced Sticker Maker...")
    print("=" * 50)
    
    if not PIL_AVAILABLE:
        print("❌ PIL/Pillow not installed!")
        print("💡 Install with: pip install pillow")
        return False
    
    # Test creating a sample sticker
    try:
        # Create a simple test image
        test_img = Image.new('RGB', (400, 400), color=(255, 107, 53))
        draw = ImageDraw.Draw(test_img)
        
        # Draw test text
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((100, 180), "TEST STICKER", font=font, fill=(255, 255, 255))
        draw.text((120, 220), "Roastify Bot", font=font, fill=(200, 200, 200))
        
        # Save test image
        test_path = "test_sticker_image.png"
        test_img.save(test_path)
        
        print(f"📸 Created test image: {test_path}")
        
        # Create sticker
        sticker_path = await sticker_maker.create_sticker_from_image(test_path, "vibrant")
        
        if sticker_path and os.path.exists(sticker_path):
            print(f"✅ Sticker created successfully!")
            print(f"📁 Path: {sticker_path}")
            print(f"📏 Size: {os.path.getsize(sticker_path)} bytes")
            
            # Show stats
            stats = sticker_maker.get_stats()
            print(f"📊 Stats: {stats['stickers_created']} stickers created")
            print(f"📊 Success rate: {stats['success_rate']:.1f}%")
            
            # Cleanup
            os.remove(test_path)
            print("🧹 Test files cleaned up")
            
            return True
        else:
            print("❌ Failed to create sticker")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎨 ADVANCED STICKER MAKER - TEST SUITE")
    print("="*60)
    
    import asyncio
    
    success = asyncio.run(test_sticker_maker())
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED")
    print("="*60)

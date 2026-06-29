import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import asyncio

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import handlers
from handlers.convert import ConvertHandler
from handlers.resize import ResizeHandler
from handlers.background import BackgroundHandler
from handlers.watermark import WatermarkHandler

class PixfliptBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("BOT_TOKEN not found in environment variables")
        
        self.application = Application.builder().token(self.token).build()
        self.convert_handler = ConvertHandler()
        self.resize_handler = ResizeHandler()
        self.background_handler = BackgroundHandler()
        self.watermark_handler = WatermarkHandler()
        
    def setup_handlers(self):
        """Set up all command and callback handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback query handlers for main menu
        self.application.add_handler(CallbackQueryHandler(self.main_menu_callback, pattern="^main_menu$"))
        self.application.add_handler(CallbackQueryHandler(self.convert_callback, pattern="^convert$"))
        self.application.add_handler(CallbackQueryHandler(self.resize_callback, pattern="^resize$"))
        self.application.add_handler(CallbackQueryHandler(self.background_callback, pattern="^background$"))
        self.application.add_handler(CallbackQueryHandler(self.watermark_callback, pattern="^watermark$"))
        
        # Register conversion handlers
        self.convert_handler.register_handlers(self.application)
        self.resize_handler.register_handlers(self.application)
        self.background_handler.register_handlers(self.application)
        self.watermark_handler.register_handlers(self.application)
        
        # Message handler for images
        self.application.add_handler(MessageHandler(
            filters.PHOTO | filters.Document.IMAGE, 
            self.handle_image
        ))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        welcome_text = f"""
👋 Welcome to Pixflipt Bot, {user.first_name}!

I'm your all-in-one image processing assistant. Here's what I can do:

🔄 **Convert Images**: JPG ↔ PNG ↔ WEBP ↔ PDF
📏 **Resize & Compress**: Adjust dimensions and reduce file size
📦 **Bulk Processing**: Convert multiple images at once
🎨 **Remove Background**: AI-powered background removal
💧 **Add Watermark**: Protect your images with custom watermarks

**How to use:**
1. Send me any image
2. Choose an option from the menu
3. Follow the instructions

Click the button below to get started!
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Get Started", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_text = """
📚 **Help & Commands**

**Available Commands:**
/start - Start the bot
/help - Show this help message

**Features:**

🔄 **Conversion**
- Supported formats: JPG, PNG, WEBP, PDF
- Bulk conversion supported

📏 **Resize**
- Custom dimensions
- Preserve aspect ratio
- Compress images

🎨 **Background Removal**
- AI-powered removal
- Transparent background

💧 **Watermark**
- Add text watermarks
- Adjust opacity and position

**Tips:**
- Send multiple images for bulk processing
- Use high-quality images for best results
- Supported image formats: JPG, PNG, WEBP

Need more help? Just ask!
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        query = update.callback_query
        await query.answer()
        
        menu_text = """
🎯 **Choose an option:**

Select what you'd like to do with your images.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Convert Images", callback_data="convert")],
            [InlineKeyboardButton("📏 Resize & Compress", callback_data="resize")],
            [InlineKeyboardButton("🎨 Remove Background", callback_data="background")],
            [InlineKeyboardButton("💧 Add Watermark", callback_data="watermark")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def convert_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle convert callback"""
        query = update.callback_query
        await query.answer()
        context.user_data['action'] = 'convert'
        
        keyboard = [
            [
                InlineKeyboardButton("JPG → PNG", callback_data="convert_jpg_png"),
                InlineKeyboardButton("PNG → JPG", callback_data="convert_png_jpg"),
            ],
            [
                InlineKeyboardButton("PNG → WEBP", callback_data="convert_png_webp"),
                InlineKeyboardButton("WEBP → PNG", callback_data="convert_webp_png"),
            ],
            [
                InlineKeyboardButton("JPG → WEBP", callback_data="convert_jpg_webp"),
                InlineKeyboardButton("WEBP → JPG", callback_data="convert_webp_jpg"),
            ],
            [
                InlineKeyboardButton("Image → PDF", callback_data="convert_image_pdf"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔄 **Select conversion format:**\n\nChoose the format you want to convert to:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def resize_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle resize callback"""
        query = update.callback_query
        await query.answer()
        context.user_data['action'] = 'resize'
        
        keyboard = [
            [
                InlineKeyboardButton("📐 Custom Size", callback_data="resize_custom"),
                InlineKeyboardButton("📏 Preset Sizes", callback_data="resize_preset"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📏 **Resize Options:**\n\nChoose how you want to resize your image:\n\n"
            "• Custom Size: Enter your own dimensions\n"
            "• Preset Sizes: Choose from common sizes\n\n"
            "Quality will be preserved while reducing file size.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def background_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle background removal callback"""
        query = update.callback_query
        await query.answer()
        context.user_data['action'] = 'background'
        
        keyboard = [
            [
                InlineKeyboardButton("🎨 Remove Background", callback_data="bg_remove"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎨 **Background Removal:**\n\n"
            "I'll remove the background from your image using AI.\n\n"
            "• Works best with clear subject images\n"
            "• Creates transparent PNG\n"
            "• High accuracy with AI processing\n\n"
            "Click the button below and send me an image!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def watermark_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle watermark callback"""
        query = update.callback_query
        await query.answer()
        context.user_data['action'] = 'watermark'
        
        keyboard = [
            [
                InlineKeyboardButton("📝 Add Text Watermark", callback_data="watermark_text"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💧 **Add Watermark:**\n\n"
            "Add a text watermark to your image:\n\n"
            "• Custom text message\n"
            "• Adjustable opacity\n"
            "• Choose position\n"
            "• Professional look\n\n"
            "Click the button below and follow the instructions!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming images"""
        if 'action' not in context.user_data:
            keyboard = [
                [InlineKeyboardButton("📋 Show Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📸 **Image received!**\n\n"
                "Please select an action from the menu first, "
                "or click the button below to see available options.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        action = context.user_data['action']
        
        if action == 'convert':
            await self.convert_handler.handle_conversion(update, context)
        elif action == 'resize':
            await self.resize_handler.handle_resize(update, context)
        elif action == 'background':
            await self.background_handler.handle_background_removal(update, context)
        elif action == 'watermark':
            await self.watermark_handler.handle_watermark(update, context)
        else:
            await update.message.reply_text(
                "⚠️ Please select an action from the menu first."
            )
    
    def run(self):
        """Run the bot"""
        self.setup_handlers()
        
        # Start the Bot
        port = int(os.environ.get('PORT', 10000))
        
        # For webhook (Render deployment)
        if os.environ.get('RENDER'):
            webhook_url = os.environ.get('RENDER_EXTERNAL_URL')
            if webhook_url:
                self.application.run_webhook(
                    listen="0.0.0.0",
                    port=port,
                    url_path=self.token,
                    webhook_url=f"{webhook_url}/{self.token}"
                )
        else:
            # For polling (local development)
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        bot = PixfliptBot()
        bot.run()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

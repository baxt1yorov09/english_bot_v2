import asyncio
import logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, func
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from config import Config
from database import get_db, init_db, User, MandatoryChannel, BroadcastMessage

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class EnglishLearningBot:
    def __init__(self):
        self.bot_token = Config.BOT_TOKEN
        self.admin_ids = Config.ADMIN_IDS
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        db = get_db()
        
        try:
            # Check if user exists
            db_user = db.query(User).filter(User.telegram_id == user.id).first()
            
            if not db_user:
                # Register new user
                db_user = User(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_admin=(user.id in self.admin_ids)
                )
                db.add(db_user)
                db.commit()
                
                # Check if there are mandatory channels
                if Config.MANDATORY_CHANNELS:
                    welcome_text = f"""
🎉 *Welcome to English Learning Bot!*

👋 Hello, {user.first_name}!

I'm your personal English learning assistant. To get started, you need to join our mandatory channels:

📚 *Mandatory Channels:*
"""
                    
                    # Add mandatory channels
                    for channel in Config.MANDATORY_CHANNELS:
                        welcome_text += f"• @{channel}\n"
                    
                    welcome_text += """
🔗 *Please join all channels above and then click:*
                
✅ *I've joined all channels*

After verification, you'll get access to all learning materials! 🚀
"""
                    
                    keyboard = [[InlineKeyboardButton("✅ I've joined all channels", callback_data="check_subscription")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
                else:
                    # No mandatory channels, directly show main menu
                    db_user.is_verified = True
                    db.commit()
                    await self.show_main_menu(update)
                    
            else:
                # User exists, check verification status
                db_user.last_activity = datetime.utcnow()
                db.commit()
                
                if Config.MANDATORY_CHANNELS and not db_user.is_verified:
                    await self.show_subscription_reminder(update)
                else:
                    await self.show_main_menu(update)
                    
        except Exception as e:
            logger.error(f"Error in start handler: {e}")
            await update.message.reply_text("❌ An error occurred. Please try again.")
        finally:
            db.close()
    
    async def show_subscription_reminder(self, update: Update):
        """Show subscription reminder"""
        reminder_text = """
📋 *Subscription Required*

🔔 *You need to join these mandatory channels:*
"""
        
        for channel in Config.MANDATORY_CHANNELS:
            reminder_text += f"• @{channel}\n"
        
        reminder_text += """
👆 Join all channels above and click the button below to verify!

✅ *Once verified, you'll access:*
• Speaking Partner Practice
• Reading Materials  
• Mock Test Database
• Listening Resources
• And much more! 🎯
"""
        
        keyboard = [[InlineKeyboardButton("✅ Check Subscription", callback_data="check_subscription")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(reminder_text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.edit_text(reminder_text, reply_markup=reply_markup)
    
    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if user is subscribed to mandatory channels"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Get bot from context or create new bot instance
        if context and hasattr(context, 'bot'):
            bot = context.bot
        else:
            # Create bot instance if context is None
            bot = Bot(token=self.bot_token)
        
        db = get_db()
        
        try:
            # Check subscription for each mandatory channel
            all_subscribed = True
            not_subscribed_channels = []
            
            for channel_username in Config.MANDATORY_CHANNELS:
                try:
                    member = await bot.get_chat_member(f"@{channel_username}", user.id)
                    if member.status in ['left', 'kicked']:
                        all_subscribed = False
                        not_subscribed_channels.append(channel_username)
                except TelegramError:
                    all_subscribed = False
                    not_subscribed_channels.append(channel_username)
            
            if all_subscribed:
                # Update user verification status
                db_user = db.query(User).filter(User.telegram_id == user.id).first()
                db_user.is_verified = True
                db_user.last_activity = datetime.utcnow()
                db.commit()
                
                success_text = """
✅ *Verification Successful!*

🎉 Congratulations! You now have full access to all features!

🚀 *What's Available:*
• 🗣️ Speaking Partner Practice
• 📖 Reading Materials
• 📝 Mock Test Database  
• 🎧 Listening Resources
• 📊 Progress Tracking

Let's start learning! 📚
"""
                
                await self.show_main_menu(update, success_text)
                
            else:
                # Show which channels are missing
                error_text = f"""
❌ *Subscription Incomplete*

🔔 *You still need to join:*
"""
                for channel in not_subscribed_channels:
                    error_text += f"• @{channel}\n"
                
                error_text += """
👆 Please join the missing channels and try again!

*Note:* It might take a few minutes for the system to detect your subscription.
"""
                
                keyboard = [[InlineKeyboardButton("🔄 Check Again", callback_data="check_subscription")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.edit_text(error_text, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            await query.message.edit_text("❌ Error checking subscription. Please try again later.")
        finally:
            db.close()
    
    async def check_user_subscription(self, update: Update, context):
        """Check if user is still subscribed to mandatory channels"""
        if not Config.MANDATORY_CHANNELS:
            return True
            
        user = update.effective_user
        
        # Get bot from context or create new bot instance
        if context and hasattr(context, 'bot'):
            bot = context.bot
        else:
            # Create bot instance if context is None
            bot = Bot(token=self.bot_token)
        
        try:
            # Check subscription for each mandatory channel
            for channel_username in Config.MANDATORY_CHANNELS:
                try:
                    member = await bot.get_chat_member(f"@{channel_username}", user.id)
                    if member.status in ['left', 'kicked']:
                        return False
                except TelegramError:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            return False
    
    async def show_main_menu(self, update: Update, custom_text: str = None):
        """Show main menu for verified users"""
        # First check if user is still subscribed to mandatory channels
        if Config.MANDATORY_CHANNELS:
            is_subscribed = await self.check_user_subscription(update, None)
            if not is_subscribed:
                # Update user verification status
                db = get_db()
                try:
                    db_user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
                    if db_user:
                        db_user.is_verified = False
                        db.commit()
                    db.close()
                except Exception as e:
                    logger.error(f"Error updating user verification: {e}")
                    db.close()
                
                await self.show_subscription_reminder(update)
                return
        
        # Ensure custom_text is a string, not an object
        if custom_text and not isinstance(custom_text, str):
            custom_text = str(custom_text)
        
        menu_text = custom_text if custom_text else """
🎯 *English Learning Hub*

👋 Welcome back! Choose what you want to practice today:

📚 *Select Learning Area:*
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🗣️ Speaking Partner", callback_data="speaking_partner"),
                InlineKeyboardButton("📖 Reading", callback_data="reading")
            ],
            [
                InlineKeyboardButton("📝 Mock Test Baza", callback_data="mock_test"),
                InlineKeyboardButton("🎧 Listening", callback_data="listening")
            ],
            [
                InlineKeyboardButton("📊 My Progress", callback_data="my_progress"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(menu_text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.edit_text(menu_text, reply_markup=reply_markup)
    
    async def handle_speaking_partner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle speaking partner"""
        query = update.callback_query
        await query.answer()
        
        # Check subscription first
        if Config.MANDATORY_CHANNELS:
            is_subscribed = await self.check_user_subscription(update, context)
            if not is_subscribed:
                # Update user verification status
                db = get_db()
                try:
                    db_user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
                    if db_user:
                        db_user.is_verified = False
                        db.commit()
                    db.close()
                except Exception as e:
                    logger.error(f"Error updating user verification: {e}")
                    db.close()
                
                await self.show_subscription_reminder(update)
                return
        
        text = f"""
🗣️ *Speaking Partner Practice*

🎯 *Improve your English speaking skills with AI-powered practice!*

🔗 *Practice Platform:*
{Config.SPEAKING_PARTNER_LINK}

📝 *How to use:*
1. Click the link above
2. Start speaking with AI
3. Get instant feedback
4. Track your progress

💡 *Tips for better practice:*
• Speak clearly and slowly
• Use complete sentences
• Practice daily for 15-20 minutes
• Don't worry about mistakes

🔙 *Back to Main Menu*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    
    async def handle_reading(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle reading button"""
        query = update.callback_query
        await query.answer()
        
        # Check subscription first
        if Config.MANDATORY_CHANNELS:
            is_subscribed = await self.check_user_subscription(update, context)
            if not is_subscribed:
                # Update user verification status
                db = get_db()
                try:
                    db_user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
                    if db_user:
                        db_user.is_verified = False
                        db.commit()
                    db.close()
                except Exception as e:
                    logger.error(f"Error updating user verification: {e}")
                    db.close()
                
                await self.show_subscription_reminder(update)
                return
        
        text = f"""
📖 *Reading Practice*

🎯 *Enhance your reading skills with quality articles!*

🔗 *Reading Platform:*
{Config.READING_LINK}

📝 *How to use:*
1. Click the link above
2. Choose articles by level
3. Read and understand
4. Track your progress

💡 *Reading Tips:*
• Start with easier articles
• Look up new words
• Read daily for 20-30 minutes
• Take notes of important points

🔙 *Back to Main Menu*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    
    async def handle_mock_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle mock test button"""
        query = update.callback_query
        await query.answer()
        
        # Check subscription first
        if Config.MANDATORY_CHANNELS:
            is_subscribed = await self.check_user_subscription(update, context)
            if not is_subscribed:
                # Update user verification status
                db = get_db()
                try:
                    db_user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
                    if db_user:
                        db_user.is_verified = False
                        db.commit()
                    db.close()
                except Exception as e:
                    logger.error(f"Error updating user verification: {e}")
                    db.close()
                
                await self.show_subscription_reminder(update)
                return
        
        text = """
📝 *Mock Test Database*

🎯 *Test your knowledge with our comprehensive test collection!*

📚 *Available Test Channels:*
"""
        
        # Add mock test channels
        for name, link in Config.MOCK_TEST_CHANNELS:
            text += f"• [{name}]({link})\n"
        
        text += """
📝 *Test Categories:*
• Speaking Tests
• Writing Tests  
• Reading Comprehension
• Listening Tests
• Grammar & Vocabulary

💡 *Test Tips:*
• Take tests regularly
• Review your mistakes
• Track your progress
• Challenge yourself!

🔙 *Back to Menu*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    
    async def handle_listening(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle listening button"""
        query = update.callback_query
        await query.answer()
        
        # Check subscription first
        if Config.MANDATORY_CHANNELS:
            is_subscribed = await self.check_user_subscription(update, context)
            if not is_subscribed:
                # Update user verification status
                db = get_db()
                try:
                    db_user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
                    if db_user:
                        db_user.is_verified = False
                        db.commit()
                    db.close()
                except Exception as e:
                    logger.error(f"Error updating user verification: {e}")
                    db.close()
                
                await self.show_subscription_reminder(update)
                return
        
        text = f"""
🎧 *Listening Practice*

🎵 *Improve your listening skills with podcasts and audio content!*

🔗 *Listen here:* [Start Listening]({Config.LISTENING_LINK})

📝 *Features:*
• Various difficulty levels
• Different accents
• Interactive exercises
• Transcripts available

💡 *Listening Tips:*
• Start with easier content
• Listen multiple times
• Take notes while listening
• Practice daily

🔙 *Back to Menu*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    
    async def handle_my_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle my progress button"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        db = get_db()
        
        try:
            db_user = db.query(User).filter(User.telegram_id == user.id).first()
            
            # Calculate days since registration
            days_registered = (datetime.utcnow() - db_user.registered_at).days
            
            progress_text = f"""
📊 *Your Learning Progress*

👤 *Profile:*
• Name: {db_user.first_name or 'N/A'}
• Username: @{db_user.username or 'N/A'}
• Member Since: {db_user.registered_at.strftime('%d %B %Y')}
• Active Days: {days_registered}

📈 *Status:*
• Account: ✅ Verified
• Last Activity: {db_user.last_activity.strftime('%d %B %Y %H:%M')}

🎯 *Keep up the great work!*
Consistent practice leads to fluency! 💪

🔙 *Back to Menu*
"""
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(progress_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error showing progress: {e}")
            await query.message.edit_text("❌ Error loading progress data.")
        finally:
            db.close()
    
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings button"""
        query = update.callback_query
        await query.answer()
        
        text = """
⚙️ *Settings*

🔧 *Bot Settings:*
• Language: English
• Notifications: Enabled
• Progress Tracking: On

📱 *About:*
• Version: 1.0.0
• Purpose: English Learning
• Admin Support: Available

💡 *Need Help?*
Contact admin for support!

🔙 *Back to Menu*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle back to main menu"""
        query = update.callback_query
        await query.answer()
        await self.show_main_menu(update)
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin panel"""
        user = update.effective_user
        db = get_db()
        
        # Check if user is admin
        if user.id not in self.admin_ids:
            await update.message.reply_text("❌ You don't have access to admin panel.")
            db.close()
            return
        
        try:
            # Get statistics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            verified_users = db.query(User).filter(User.is_verified == True).count()
            
            admin_text = f"""
👑 *Admin Panel*

📊 *Statistics:*
• Total Users: {total_users}
• Active Users: {active_users}
• Verified Users: {verified_users}
• Registration Rate: {((verified_users/total_users*100) if total_users > 0 else 0):.1f}%

🛠️ *Admin Functions:*
• 📢 Broadcast Message
• 👥 User Management
• � Admin Management
• � Channel Management
• 📈 View Statistics

Choose an action below:
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                    InlineKeyboardButton("👥 Users", callback_data="admin_users")
                ],
                [
                    InlineKeyboardButton("� Admins", callback_data="admin_admins"),
                    InlineKeyboardButton("� Channels", callback_data="admin_channels")
                ],
                [
                    InlineKeyboardButton("📈 Statistics", callback_data="admin_stats")
                ],
                [
                    InlineKeyboardButton("🔙 Exit Admin", callback_data="main_menu")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            if update.message:
                await update.message.reply_text(admin_text, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await update.callback_query.message.edit_text(admin_text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in admin panel: {e}")
            if update.message:
                await update.message.reply_text("❌ Error loading admin panel.")
            else:
                await update.callback_query.message.edit_text("❌ Error loading admin panel.")
        finally:
            db.close()
    
    async def handle_admin_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin broadcast"""
        query = update.callback_query
        await query.answer()
        
        if update.effective_user.id not in self.admin_ids:
            await query.message.edit_text("❌ Access denied.")
            return
        
        text = """
📢 *Broadcast Message*

📝 *Send message to all users:*

Please send the message you want to broadcast to all users.

📋 *Format:*
• Text message
• Markdown supported
• No limits on length

⚠️ *Note:* This will send to all verified users.

🔙 *Cancel*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
        
        # Set state for broadcast
        context.user_data['broadcast_mode'] = True
    
    async def handle_admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin user management"""
        query = update.callback_query
        await query.answer()
        
        if update.effective_user.id not in self.admin_ids:
            await query.message.edit_text("❌ Access denied.")
            return
        
        db = get_db()
        
        try:
            # Get recent users
            recent_users = db.query(User).order_by(User.registered_at.desc()).limit(10).all()
            
            text = """
👥 *User Management*

📋 *Recent Users:*
"""
            
            for user in recent_users:
                status = "✅" if user.is_verified else "❌"
                text += f"{status} {user.first_name or 'N/A'} (@{user.username or 'N/A'}) - {user.registered_at.strftime('%d/%m/%Y')}\n"
            
            text += f"""
📊 *Total Users:* {db.query(User).count()}
✅ *Verified:* {db.query(User).filter(User.is_verified == True).count()}
🔙 *Back to Admin Panel*
"""
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in admin users: {e}")
            await query.message.edit_text("❌ Error loading user data.")
        finally:
            db.close()
    
    async def handle_admin_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin management"""
        query = update.callback_query
        await query.answer()
        
        if update.effective_user.id not in self.admin_ids:
            await query.message.edit_text("❌ Access denied.")
            return
        
        text = """
👑 *Admin Management*

🔧 *Current Admins:*
"""
        
        for admin_id in self.admin_ids:
            text += f"• Admin ID: {admin_id}\n"
        
        text += """
📝 *Quick Management:*
• /add_admin user_id - Add new admin
• /remove_admin user_id - Remove admin
• /list_admins - Show all admins

📝 *Usage Examples:*
• /add_admin 123456789
• /remove_admin 123456789

⚠️ *Note:* Be careful when adding/removing admins!

🔙 *Back to Admin Panel*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    async def handle_admin_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin channel management"""
        query = update.callback_query
        await query.answer()
        
        if update.effective_user.id not in self.admin_ids:
            await query.message.edit_text("❌ Access denied.")
            return
        
        text = """
📋 *Channel Management*

🔧 *Current Mandatory Channels:*
"""
        
        if Config.MANDATORY_CHANNELS:
            for channel in Config.MANDATORY_CHANNELS:
                text += f"• @{channel}\n"
        else:
            text += "❌ No mandatory channels set yet\n"
        
        text += """
🛠️ *Management Options:*
• Add new channel
• Remove channel
• Update channel list

📝 *Quick Management:*
• /add_channel channel_name - Add mandatory channel
• /remove_channel channel_name - Remove mandatory channel
• /list_channels - Show all mandatory channels
• /clear_channels - Remove all mandatory channels

📊 *Mock Test Channels (separate):*
• Speaking Mock Tests: https://t.me/SpeakingMockss
• Multilevel Mock Baza: https://t.me/MultilevelMockBaza

🔙 *Back to Admin Panel*
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    async def handle_admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin statistics"""
        query = update.callback_query
        await query.answer()
        
        if update.effective_user.id not in self.admin_ids:
            await query.message.edit_text("❌ Access denied.")
            return
        
        db = get_db()
        
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            verified_users = db.query(User).filter(User.is_verified == True).count()
            admin_users = db.query(User).filter(User.is_admin == True).count()
            
            # Get today's registrations
            from datetime import date
            today = date.today()
            today_users = db.query(User).filter(func.date(User.registered_at) == today).count()
            
            text = f"""
📈 *Bot Statistics*

👥 *User Statistics:*
• Total Users: {total_users}
• Active Users: {active_users}
• Verified Users: {verified_users}
• Admin Users: {admin_users}
• Today's Registrations: {today_users}

📊 *Conversion Rates:*
• Verification Rate: {((verified_users/total_users*100) if total_users > 0 else 0):.1f}%
• Activity Rate: {((active_users/total_users*100) if total_users > 0 else 0):.1f}%

🔗 *Channel Configuration:*
• Mandatory Channels: {len(Config.MANDATORY_CHANNELS)}
• Mock Test Channels: 2 (fixed)

📅 *Generated:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

🔙 *Back to Admin Panel*
"""
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in admin stats: {e}")
            await query.message.edit_text("❌ Error loading statistics.")
        finally:
            db.close()
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user = update.effective_user
        
        # Check if in broadcast mode
        if context.user_data.get('broadcast_mode') and user.id in self.admin_ids:
            await self.send_broadcast(update, context)
            return
        
        # Handle regular messages
        await update.message.reply_text("👋 Please use the menu buttons to navigate. Use /start to begin!")
    
    async def send_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send broadcast message to all verified users"""
        message_text = update.message.text
        db = get_db()
        
        try:
            # Get all verified users
            verified_users = db.query(User).filter(User.is_verified == True).all()
            
            successful_sends = 0
            failed_sends = 0
            
            for user in verified_users:
                try:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message_text,
                        parse_mode='Markdown'
                    )
                    successful_sends += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    logger.error(f"Failed to send to {user.telegram_id}: {e}")
                    failed_sends += 1
            
            # Save broadcast record
            broadcast = BroadcastMessage(
                message_text=message_text,
                sent_by=user.id,
                total_recipients=len(verified_users),
                successful_sends=successful_sends
            )
            db.add(broadcast)
            db.commit()
            
            # Send confirmation to admin
            confirmation_text = f"""
✅ *Broadcast Sent Successfully!*

📊 *Results:*
• Total Recipients: {len(verified_users)}
• Successful Sends: {successful_sends}
• Failed Sends: {failed_sends}
• Success Rate: {(successful_sends/len(verified_users)*100):.1f}%

📝 *Message Preview:*
{message_text[:100]}{'...' if len(message_text) > 100 else ''}

🔙 *Back to Admin Panel*
"""
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(confirmation_text, reply_markup=reply_markup)
            
            # Clear broadcast mode
            context.user_data['broadcast_mode'] = False
            
        except Exception as e:
            logger.error(f"Error in broadcast: {e}")
            await update.message.reply_text("❌ Error sending broadcast. Please try again.")
        finally:
            db.close()
    
    async def add_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add mandatory channel"""
        if update.effective_user.id not in self.admin_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /add_channel channel_name")
            return
        
        channel_name = context.args[0].lstrip('@')
        
        # Update .env file
        try:
            import os
            from dotenv import load_dotenv, set_key
            
            load_dotenv()
            current_channels = os.getenv('MANDATORY_CHANNELS', '').split(',')
            current_channels = [ch.strip() for ch in current_channels if ch.strip()]
            
            if channel_name in current_channels:
                await update.message.reply_text(f"⚠️ Channel @{channel_name} already exists.")
                return
            
            current_channels.append(channel_name)
            new_channels = ','.join(current_channels)
            
            set_key('.env', 'MANDATORY_CHANNELS', new_channels)
            
            # Update config
            Config.MANDATORY_CHANNELS = current_channels
            
            await update.message.reply_text(f"✅ Channel @{channel_name} added successfully!\n\n📋 Current channels: {', '.join([f'@{ch}' for ch in current_channels])}")
            
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            await update.message.reply_text("❌ Error adding channel.")
    
    async def remove_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove mandatory channel"""
        if update.effective_user.id not in self.admin_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /remove_channel channel_name")
            return
        
        channel_name = context.args[0].lstrip('@')
        
        try:
            import os
            from dotenv import load_dotenv, set_key
            
            load_dotenv()
            current_channels = os.getenv('MANDATORY_CHANNELS', '').split(',')
            current_channels = [ch.strip() for ch in current_channels if ch.strip()]
            
            if channel_name not in current_channels:
                await update.message.reply_text(f"⚠️ Channel @{channel_name} not found.")
                return
            
            current_channels.remove(channel_name)
            new_channels = ','.join(current_channels)
            
            set_key('.env', 'MANDATORY_CHANNELS', new_channels)
            
            # Update config
            Config.MANDATORY_CHANNELS = current_channels
            
            await update.message.reply_text(f"✅ Channel @{channel_name} removed successfully!\n\n📋 Current channels: {', '.join([f'@{ch}' for ch in current_channels]) if current_channels else 'No channels set'}")
            
        except Exception as e:
            logger.error(f"Error removing channel: {e}")
            await update.message.reply_text("❌ Error removing channel.")
    
    async def list_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all mandatory channels"""
        if update.effective_user.id not in self.admin_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        if Config.MANDATORY_CHANNELS:
            channels_text = '\n'.join([f"• @{channel}" for channel in Config.MANDATORY_CHANNELS])
            await update.message.reply_text(f"📋 *Mandatory Channels:*\n\n{channels_text}")
        else:
            await update.message.reply_text("📋 No mandatory channels set.")
    
    async def clear_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear all mandatory channels"""
        if update.effective_user.id not in self.admin_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        try:
            from dotenv import set_key
            set_key('.env', 'MANDATORY_CHANNELS', '')
            
            # Update config
            Config.MANDATORY_CHANNELS = []
            
            await update.message.reply_text("✅ All mandatory channels cleared successfully!")
            
        except Exception as e:
            logger.error(f"Error clearing channels: {e}")
            await update.message.reply_text("❌ Error clearing channels.")
    
    async def add_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add admin"""
        if update.effective_user.id not in self.admin_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /add_admin user_id")
            return
        
        try:
            admin_id = int(context.args[0])
            if admin_id in self.admin_ids:
                await update.message.reply_text(f"⚠️ User {admin_id} is already an admin.")
                return
            
            # Update .env file
            import os
            from dotenv import load_dotenv, set_key
            
            load_dotenv()
            self.admin_ids.append(admin_id)
            new_admin_ids = ','.join(map(str, self.admin_ids))
            
            set_key('.env', 'ADMIN_ID', new_admin_ids)
            
            # Update database
            db = get_db()
            try:
                db_user = db.query(User).filter(User.telegram_id == admin_id).first()
                if db_user:
                    db_user.is_admin = True
                    db.commit()
                db.close()
            except Exception as e:
                logger.error(f"Error updating database: {e}")
            
            await update.message.reply_text(f"✅ Admin {admin_id} added successfully!\n\n👑 Current admins: {', '.join(map(str, self.admin_ids))}")
            
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric ID.")
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            await update.message.reply_text("❌ Error adding admin.")
    
    async def remove_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove admin"""
        if update.effective_user.id not in self.admin_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /remove_admin user_id")
            return
        
        try:
            admin_id = int(context.args[0])
            if admin_id not in self.admin_ids:
                await update.message.reply_text(f"⚠️ User {admin_id} is not an admin.")
                return
            
            # Don't allow removing yourself
            if admin_id == update.effective_user.id:
                await update.message.reply_text("❌ You cannot remove yourself from admin.")
                return
            
            # Update .env file
            import os
            from dotenv import load_dotenv, set_key
            
            load_dotenv()
            self.admin_ids.remove(admin_id)
            new_admin_ids = ','.join(map(str, self.admin_ids))
            
            set_key('.env', 'ADMIN_ID', new_admin_ids)
            
            # Update database
            db = get_db()
            try:
                db_user = db.query(User).filter(User.telegram_id == admin_id).first()
                if db_user:
                    db_user.is_admin = False
                    db.commit()
                db.close()
            except Exception as e:
                logger.error(f"Error updating database: {e}")
            
            await update.message.reply_text(f"✅ Admin {admin_id} removed successfully!\n\n👑 Current admins: {', '.join(map(str, self.admin_ids))}")
            
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric ID.")
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
            await update.message.reply_text("❌ Error removing admin.")
    
    async def list_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all admins"""
        if update.effective_user.id not in self.admin_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        if self.admin_ids:
            admins_text = '\n'.join([f"• Admin ID: {admin_id}" for admin_id in self.admin_ids])
            await update.message.reply_text(f"👑 *Current Admins:*\n\n{admins_text}")
        else:
            await update.message.reply_text("👑 No admins set.")
    
    def run(self):
        """Start the bot"""
        # Initialize database
        init_db()
        
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("admin", self.admin_panel))
        application.add_handler(CommandHandler("add_channel", self.add_channel))
        application.add_handler(CommandHandler("remove_channel", self.remove_channel))
        application.add_handler(CommandHandler("list_channels", self.list_channels))
        application.add_handler(CommandHandler("clear_channels", self.clear_channels))
        application.add_handler(CommandHandler("add_admin", self.add_admin))
        application.add_handler(CommandHandler("remove_admin", self.remove_admin))
        application.add_handler(CommandHandler("list_admins", self.list_admins))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(self.check_subscription, pattern="^check_subscription$"))
        application.add_handler(CallbackQueryHandler(self.handle_main_menu, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(self.handle_speaking_partner, pattern="^speaking_partner$"))
        application.add_handler(CallbackQueryHandler(self.handle_reading, pattern="^reading$"))
        application.add_handler(CallbackQueryHandler(self.handle_mock_test, pattern="^mock_test$"))
        application.add_handler(CallbackQueryHandler(self.handle_listening, pattern="^listening$"))
        application.add_handler(CallbackQueryHandler(self.handle_my_progress, pattern="^my_progress$"))
        application.add_handler(CallbackQueryHandler(self.handle_settings, pattern="^settings$"))
        
        # Admin handlers
        application.add_handler(CallbackQueryHandler(self.admin_panel, pattern="^admin_panel$"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_broadcast, pattern="^admin_broadcast$"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_users, pattern="^admin_users$"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_admins, pattern="^admin_admins$"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_channels, pattern="^admin_channels$"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_stats, pattern="^admin_stats$"))
        
        # Message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start bot with webhook for production
        print("🚀 Bot is starting...")
        
        # Set webhook for production
        import os
        webhook_url = os.getenv('RENDER_EXTERNAL_URL') or os.getenv('WEBHOOK_URL')
        if webhook_url:
            webhook_path = f"{webhook_url}/webhook"
            print(f"📡 Setting webhook to: {webhook_path}")
            try:
                application.run_webhook(
                    port=int(os.getenv('PORT', 10000)),
                    drop_pending_updates=True
                )
            except Exception as e:
                print(f"❌ Webhook error: {e}")
                print("📡 Falling back to polling mode...")
                application.run_polling(allowed_updates=Update.ALL_TYPES)
        else:
            # Fallback to polling for development
            print("📡 Running in polling mode (development)")
            application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = EnglishLearningBot()
    bot.run()

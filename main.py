"""
Swedish Learning Bot - Main Application
Powered by SALDO dictionary with 315,000+ Swedish words.
"""

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from services.dictionary_service import SwedishDictionary

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize dictionary service
dictionary = SwedishDictionary()
stats = dictionary.get_stats()
logger.info(f"Dictionary loaded: {stats['total_entries']} entries ({stats['base_words']} base words, {stats['word_forms']} forms)")


class SwedishBot:
    """Main bot class handling all interactions."""

    def __init__(self, token: str):
        """Initialize the Swedish Learning Bot."""
        self.token = token
        self.application = None

    async def post_init(self, application: Application) -> None:
        """Post-initialization hook to set up bot commands."""
        await self.set_commands(application)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        stats = dictionary.get_stats()

        welcome_message = (
            "🇸🇪 *Swedish Learning Bot*\n"
            "*Powered by SALDO Language Database*\n\n"
            
            "🆕 *What's New (Oct 2025):*\n"
            "• Report button on every word card\n"
            "• Improved strong verb forms\n"
            "• Report missing words feature\n\n"
            
            f"📚 *{stats['total_entries']:,}* Swedish words available\n"
            f"• {stats['base_words']:,} base words\n"
            f"• {stats['word_forms']:,} inflected forms\n\n"
            "*Features:*\n"
            "✅ Complete grammatical forms\n"
            "✅ Word groups (verb groups, noun declensions)\n"
            "✅ Recognizes all word forms\n"
            "✅ Ordinal numbers\n\n"
            "*How to use:*\n"
            "Simply send me any Swedish word!\n\n"
            "*Try these examples:*\n"
            "• `stora` → adjective form\n"
            "• `är` → verb form\n"
            "• `huset` → noun form\n"
            "• `fem` → numeral with ordinal\n\n"
            "*Commands:*\n"
            "/help - Get detailed help\n"
            "/stats - Dictionary statistics\n"
            "/examples - More examples\n"
            "/feedback - How to send feedback"
        )

        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = (
            "📚 *How to Use Swedish Learning Bot*\n\n"
            "*Basic Usage:*\n"
            "Type any Swedish word to see:\n"
            "• Word type and grammatical group\n"
            "• Complete forms (conjugation/declension)\n"
            "• Base form if it's an inflected word\n\n"
            "*Understanding Groups:*\n\n"
            "*Noun Groups (Deklinationer):*\n"
            "• Group 1: en-words ending in -a (flicka→flickor)\n"
            "• Group 2: en-words with -ar plural (bil→bilar)\n"  
            "• Group 3: en-words with -er plural (park→parker)\n"
            "• Group 4: ett-words with -n plural (äpple→äpplen)\n"
            "• Group 5: ett-words no change (hus→hus)\n\n"
            "*Verb Groups:*\n"
            "• Group 1: -ar verbs (talar, talade, talat)\n"
            "• Group 2: -er verbs (läser, läste, läst)\n"
            "• Irregular: Special patterns (vara→är)\n\n"
            "*Tips:*\n"
            "• Try inflected forms like 'större' or 'barnen'\n"
            "• All lookups are case-insensitive\n"
            "• The bot recognizes 315,000+ words"
        )

        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        stats = dictionary.get_stats()

        stats_text = (
            "📊 *Dictionary Statistics*\n\n"
            f"*Total entries:* {stats['total_entries']:,}\n"
            f"*Base words:* {stats['base_words']:,}\n"
            f"*Word forms:* {stats['word_forms']:,}\n\n"
            "*By type:*\n"
            f"• Nouns: {stats['nouns']:,}\n"
            f"• Verbs: {stats['verbs']:,}\n"
            f"• Adjectives: {stats['adjectives']:,}\n\n"
            "*Data source:* SALDO\n"
            "Swedish Language Bank (Språkbanken)"
        )

        await update.message.reply_text(
            stats_text,
            parse_mode='Markdown'
        )

    async def examples_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /examples command."""
        examples_text = (
            "📝 *Example Lookups*\n\n"
            "*Inflected Forms:*\n"
            "• `stora` → plural of 'stor' (big)\n"
            "• `större` → comparative of 'stor'\n"
            "• `störst` → superlative of 'stor'\n\n"
            "• `hundar` → plural of 'hund' (dog)\n"
            "• `hundarna` → definite plural of 'hund'\n"
            "• `hunden` → definite singular of 'hund'\n\n"
            "• `är` → present of 'vara' (to be)\n"
            "• `var` → past of 'vara'\n"
            "• `varit` → supine of 'vara'\n\n"
            "*Numbers:*\n"
            "• `tre` → shows ordinal 'tredje'\n"
            "• `fem` → shows ordinal 'femte'\n"
            "• `tio` → shows ordinal 'tionde'\n\n"
            "*Ambiguous Words:*\n"
            "• `får` → verb or noun (sheep)?\n"
            "• `var` → verb, adverb, or pronoun?\n"
            "• `spring` → verb or noun?\n\n"
            "*Try any Swedish word!*\n"
            "The dictionary contains modern Swedish\n"
            "including slang and technical terms."
        )

        await update.message.reply_text(
            examples_text,
            parse_mode='Markdown'
        )

    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /feedback command."""
        feedback_text = (
            "💬 *Feedback & Support*\n\n"
            "Your feedback helps improve this bot!\n\n"
            "*How to send feedback:*\n\n"
            "📱 *Telegram:* @oleksii\\_shcherbak33\n"
            "📧 *Email:* oleksii\\_shcherbak@icloud.com\n\n"
            "*What to report:*\n"
            "• Incorrect word forms\n"
            "• Missing words\n"
            "• Feature suggestions\n"
            "• Bug reports\n"
            "• General feedback\n\n"
            "*Found a word error?*\n"
            "Please include:\n"
            "1. The word you searched\n"
            "2. What you expected\n"
            "3. What the bot showed\n\n"
            "Thank you for helping make this bot better! 🙏"
        )

        await update.message.reply_text(
            feedback_text,
            parse_mode='Markdown'
        )

    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command - shows only users who reported issues."""
        ADMIN_USER_ID = 266049422
        
        if update.effective_user.id != ADMIN_USER_ID:
            await update.message.reply_text("❌ This command is only available to the bot administrator.")
            return
        
        reported_path = os.path.join(os.path.dirname(__file__), 'data', 'reported_words.json')
        
        try:
            if os.path.exists(reported_path):
                with open(reported_path, 'r', encoding='utf-8') as f:
                    reports = json.load(f)
            else:
                reports = []
            
            if not reports:
                await update.message.reply_text("No issues reported yet.")
                return
            
            users_map = {}
            for report in reports:
                user_id = report['user_id']
                if user_id not in users_map:
                    users_map[user_id] = {
                        'username': report['username'],
                        'first_name': report['first_name'],
                        'reports': []
                    }
                users_map[user_id]['reports'].append(report['word'])
            
            # Format without Markdown to avoid parsing errors
            user_list = f"👥 Users Who Reported Issues ({len(users_map)} total)\n\n"
            for user_id, data in users_map.items():
                username = f"@{data['username']}" if data['username'] else "no username"
                user_list += (
                    f"• {data['first_name']} ({username})\n"
                    f"  Reports: {len(data['reports'])} words\n"
                    f"  Words: {', '.join(data['reports'][:5])}\n\n"
                )
            
            # Send as plain text (no Markdown)
            await update.message.reply_text(user_list)
            
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (word lookups)."""
        word = update.message.text.strip()

        # Log the query
        logger.info(f"User {update.effective_user.id} queried: {word}")

        # Look up word
        result = dictionary.lookup(word)

        if result is None:
            # Word not found
            suggestions = dictionary.get_suggestions(word, limit=5)

            not_found_msg = f"❌ Word '*{word}*' not found.\n\n"

            if suggestions:
                not_found_msg += "*Did you mean:*\n"
                for suggestion in suggestions:
                    not_found_msg += f"• `{suggestion}`\n"
            else:
                not_found_msg += (
                    "The dictionary contains 315,000+ Swedish words.\n"
                    "Please check spelling and try again.\n\n"
                    "Note: Some very rare or archaic words\n"
                    "might not be included."
                )

            # Add report button for missing words too
            keyboard = [[
                InlineKeyboardButton("🚩 Report Missing Word", callback_data=f"report:{word}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                not_found_msg,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return

        # Check if word is ambiguous
        if result.get('ambiguous'):
            await self.show_meaning_options(update, result)
            return

        # Format word card
        card = dictionary.format_word_card(result['data'], result['word'])
        
        # Add report button
        keyboard = [[
            InlineKeyboardButton("🚩 Report Issue", callback_data=f"report:{word}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send with button
        await update.message.reply_text(
            card, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def show_meaning_options(self, update: Update, result: Dict[str, Any]):
        """Show interactive buttons for ambiguous words."""
        word = result['word']
        meanings = result['meanings']

        message = f"📘 *{word.upper()}*\n\n"
        message += "This word has multiple meanings. Please choose:\n\n"

        # Create inline keyboard with meaning options
        keyboard = []
        for idx, meaning in enumerate(meanings):
            type_emoji = dictionary._get_type_emoji(meaning['type'])
            description = meaning.get('description', meaning['type'])
            button_text = f"{type_emoji} {description}"
            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"meaning:{word}:{idx}"
                )
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_meaning_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle selection of meaning for ambiguous words."""
        query = update.callback_query
        await query.answer()

        # Parse callback data
        _, word, meaning_idx = query.data.split(':')
        meaning_idx = int(meaning_idx)

        # Get the selected meaning
        result = dictionary.lookup(word)
        if not result or not result.get('ambiguous'):
            await query.edit_message_text("Error: Word data not found.")
            return

        selected_meaning = result['meanings'][meaning_idx]

        # Format and display the selected meaning
        card = dictionary.format_word_card(selected_meaning, word)
        
        # Add report button to ambiguous words too
        keyboard = [[
            InlineKeyboardButton("🚩 Report Issue", callback_data=f"report:{word}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            card, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def handle_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle word issue reports."""
        query = update.callback_query
        await query.answer("Thank you for reporting!")

        # Parse callback data
        _, word = query.data.split(':', 1)
        
        # Log the report
        user = update.effective_user
        user_info = {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'word': word,
            'timestamp': update.callback_query.message.date.isoformat()
        }
        
        # Save to reported_words.json
        reported_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'reported_words.json'
        )
        
        try:
            # Load existing reports
            if os.path.exists(reported_path):
                with open(reported_path, 'r', encoding='utf-8') as f:
                    reports = json.load(f)
            else:
                reports = []
            
            # Add new report
            reports.append(user_info)
            
            # Save updated reports
            with open(reported_path, 'w', encoding='utf-8') as f:
                json.dump(reports, f, ensure_ascii=False, indent=2)
            
            logger.info(f"User {user.id} reported word: {word}")
            
            # Update message to show report was received
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Reported", callback_data="noop")
                ]])
            )
            
            # Send confirmation
            confirmation = (
                f"✅ Thank you for reporting '*{word}*'!\n\n"
                "Your feedback helps improve the bot.\n"
                "I'll review this word and update it if needed."
            )
            await query.message.reply_text(confirmation, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            await query.message.reply_text(
                "Sorry, there was an error saving your report. "
                "Please contact @oleksii_shcherbak33 directly."
            )

    def _track_user(self, user):
        """Track user for analytics."""
        users_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'users.json'
        )
        
        try:
            # Load existing users
            if os.path.exists(users_path):
                with open(users_path, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            else:
                users = []
            
            # Check if user already tracked
            user_ids = [u['user_id'] for u in users]
            if user.id not in user_ids:
                from datetime import datetime
                users.append({
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'first_seen': datetime.now().isoformat()
                })
                
                # Save
                with open(users_path, 'w', encoding='utf-8') as f:
                    json.dump(users, f, ensure_ascii=False, indent=2)
                    
                logger.info(f"New user tracked: {user.id} (@{user.username})")
        except Exception as e:
            logger.error(f"Error tracking user: {e}")

    async def set_commands(self, application: Application):
        """Set bot commands for the menu."""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help on using the bot"),
            BotCommand("examples", "Show example lookups"),
            BotCommand("stats", "Dictionary statistics"),
            BotCommand("feedback", "How to send feedback")
        ]

        await application.bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")

    def run(self):
        """Run the bot."""
        # Create application
        self.application = Application.builder().token(self.token).build()

        # Add post-init handler
        self.application.post_init = self.post_init

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("examples", self.examples_command))
        self.application.add_handler(CommandHandler("feedback", self.feedback_command))
        self.application.add_handler(CommandHandler("users", self.users_command))

        # Callback handlers
        self.application.add_handler(
            CallbackQueryHandler(self.handle_meaning_selection, pattern=r"^meaning:")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handle_report, pattern=r"^report:")
        )

        # Message handler for word lookups
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        # Start polling
        logger.info("Bot starting...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token")
        logger.error("Example: TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return

    # Create and run bot
    bot = SwedishBot(token)

    try:
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise


if __name__ == '__main__':
    main()

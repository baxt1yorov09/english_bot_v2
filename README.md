# 🤖 English Learning Telegram Bot

A comprehensive Telegram bot for English learning with user authentication, mandatory channel subscriptions, and admin management features.

## 🌟 Features

### User Features:
- ✅ **User Registration** - Simple onboarding process
- 🔒 **Mandatory Channel Verification** - Ensures users join required channels
- 🗣️ **Speaking Partner** - Direct link to AI speaking practice platform
- 📖 **Reading Materials** - Access to quality English articles
- 📝 **Mock Test Database** - Links to test channels for practice
- 🎧 **Listening Resources** - Podcast and audio content
- 📊 **Progress Tracking** - Personal learning statistics
- ⚙️ **Settings** - User preferences and information

### Admin Features:
- 👑 **Admin Panel** - Complete admin dashboard
- 📢 **Broadcast Messages** - Send messages to all verified users
- 👥 **User Management** - View and manage user base
- 📋 **Channel Management** - Manage mandatory channels
- 📈 **Statistics** - Detailed bot usage analytics
- 🔐 **Admin Authentication** - Secure admin access

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Telegram Bot Token
- Admin Telegram ID

### 2. Installation

```bash
# Clone or download the project
cd Bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your settings:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_telegram_id_here
DATABASE_URL=sqlite:///./bot.db
MANDATORY_CHANNELS=SpeakingMockss,MultilevelMockBaza
```

### 4. Run the Bot

```bash
python bot.py
```

## 📋 Configuration Options

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token from @BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `ADMIN_ID` | Your Telegram user ID for admin access | `123456789` |
| `DATABASE_URL` | Database connection string | `sqlite:///./bot.db` |
| `MANDATORY_CHANNELS` | Comma-separated channel usernames | `SpeakingMockss,MultilevelMockBaza` |

### External Links Configuration

The bot includes configurable links for learning resources:

- **Speaking Partner**: AI-powered speaking practice platform
- **Reading**: Quality English articles and materials  
- **Listening**: Podcast and audio content

These can be customized in the `.env` file.

## 🎯 User Flow

1. **Start Bot** - User sends `/start`
2. **Registration** - Bot registers the user in database
3. **Channel Verification** - User must join mandatory channels
4. **Access Granted** - Full access to learning features
5. **Learning** - User accesses various learning materials

## 👑 Admin Features

### Access Admin Panel
Send `/admin` to access the admin panel (only works for configured admin ID).

### Admin Functions

1. **Broadcast Messages**
   - Send messages to all verified users
   - Support for Markdown formatting
   - Delivery statistics and confirmation

2. **User Management**
   - View recent user registrations
   - Monitor verification status
   - Track user activity

3. **Channel Management**
   - View current mandatory channels
   - Instructions for adding/removing channels
   - Channel configuration guidance

4. **Statistics**
   - Total user count
   - Active users
   - Verification rates
   - Daily registrations

## 📊 Database Schema

### Users Table
- `telegram_id` - Unique Telegram user ID
- `username` - Telegram username
- `first_name`, `last_name` - User names
- `is_admin` - Admin status
- `is_active` - Account status
- `is_verified` - Channel verification status
- `registered_at` - Registration timestamp
- `last_activity` - Last activity timestamp

### Broadcast Messages Table
- `message_text` - Broadcast content
- `sent_at` - Send timestamp
- `sent_by` - Admin ID
- `total_recipients` - Total users targeted
- `successful_sends` - Successful deliveries

## 🔧 Technical Details

### Dependencies
- `python-telegram-bot` - Telegram bot framework
- `sqlalchemy` - Database ORM
- `python-dotenv` - Environment configuration
- `asyncpg`/`aiosqlite` - Database drivers

### Architecture
- **Asynchronous** - Built with async/await for performance
- **Modular** - Separated configuration, database, and bot logic
- **Scalable** - Database-driven architecture supports growth
- **Secure** - Admin authentication and input validation

## 📝 Bot Commands

### User Commands
- `/start` - Start the bot and begin registration
- `/help` - Show help information (if implemented)

### Admin Commands
- `/admin` - Access admin panel (admin only)

## 🎨 UI Features

- **Inline Keyboards** - Interactive button navigation
- **Markdown Formatting** - Rich text display
- **Status Indicators** - Visual feedback for user actions
- **Progress Tracking** - User statistics display
- **Responsive Design** - Works on all Telegram clients

## 🛠️ Customization

### Adding New Learning Resources

1. Add link to `.env` file:
```env
NEW_RESOURCE_LINK=https://example.com
```

2. Update `config.py` to include the new link
3. Add handler in `bot.py` for the new resource
4. Update keyboard layouts

### Modifying Mandatory Channels

Edit the `MANDATORY_CHANNELS` variable in `.env`:
```env
MANDATORY_CHANNELS=channel1,channel2,channel3
```

## 📈 Monitoring & Analytics

The bot automatically tracks:
- User registrations
- Channel verification status
- User activity
- Broadcast message delivery
- Daily statistics

## 🔒 Security Features

- **Admin Authentication** - Only configured admin can access admin features
- **Input Validation** - All user inputs are validated
- **Rate Limiting** - Built-in delays for broadcast messages
- **Error Handling** - Comprehensive error handling and logging

## 🚀 Deployment

### Local Development
```bash
python bot.py
```

### Production Deployment
1. Set up a server (VPS, cloud, etc.)
2. Install dependencies
3. Configure environment variables
4. Run with process manager (systemd, supervisor, etc.)
5. Set up reverse proxy (optional)

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

## 🤝 Support

For support and questions:
- Contact the bot admin
- Check the bot documentation
- Review error logs for troubleshooting

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

---

**Happy Learning! 🎓**

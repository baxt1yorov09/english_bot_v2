import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_IDS = [int(admin_id.strip()) for admin_id in os.getenv('ADMIN_ID', '').split(',') if admin_id.strip()]
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./bot.db')
    
    # Mandatory channels
    MANDATORY_CHANNELS = [
        channel.strip() for channel in 
        os.getenv('MANDATORY_CHANNELS', '').split(',') if channel.strip()
    ]
    
    # External links
    SPEAKING_PARTNER_LINK = os.getenv('SPEAKING_PARTNER_LINK', 
        'https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice#demo')
    READING_LINK = os.getenv('READING_LINK', 'https://jamesclear.com/articles')
    LISTENING_LINK = os.getenv('LISTENING_LINK', 'https://www.podcastsinenglish.com/')
    
    # Mock test channels
    MOCK_TEST_CHANNELS = [
        ('Speaking Mock Tests', 'https://t.me/SpeakingMockss'),
        ('Multilevel Mock Baza', 'https://t.me/MultilevelMockBaza')
    ]

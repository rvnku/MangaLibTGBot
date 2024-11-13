import dotenv
import os


dotenv.load_dotenv('.env')


class Settings:
    bot_token = os.getenv('BOT_TOKEN')
    mode = os.getenv('MODE')
    author_id = os.getenv('AUTHOR_ID')
    forum_id = os.getenv('FORUM_ID')
    flood_topic_id = os.getenv('FLOOD_TOPIC_ID')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')


config = Settings()

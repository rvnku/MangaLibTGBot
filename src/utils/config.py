import dotenv
import os


dotenv.load_dotenv('.env')


class Settings:
    bot_token = os.getenv('BOT_TOKEN')
    bot_username = os.getenv('BOT_USERNAME')
    mode = os.getenv('MODE')
    author_id = os.getenv('AUTHOR_ID')
    develop_id = os.getenv('DEVELOP_ID')
    forum_id = os.getenv('FORUM_ID')
    flood_topic_id = os.getenv('FLOOD_TOPIC_ID')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')


config = Settings()

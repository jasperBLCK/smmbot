import os

from dotenv import load_dotenv

import database

load_dotenv()

TOKEN = os.getenv('TOKEN', '')
SMMPANEL_API_KEY = os.getenv('SMMPANEL_API_KEY', '')
SMOSERVICE_USER_ID = os.getenv('SMOSERVICE_USER_ID', '')
SMOSERVICE_API_KEY = os.getenv('SMOSERVICE_API_KEY', '')
TEGRO_API_KEY = os.getenv('TEGRO_API_KEY', '')
ADMIN_ID = database.ADMIN_ID
ADMIN_DEFAULT_BALANCE = database.ADMIN_DEFAULT_BALANCE
DB_PATH = database.DB_PATH

BASE_URL = os.getenv('BOT_URL', '').rstrip('/')
WEB_SERVER_HOST = os.getenv('WEB_SERVER_HOST', '0.0.0.0')
WEB_SERVER_PORT = int(os.getenv('WEB_SERVER_PORT') or 8001)
MAIN_BOT_PATH = '/webhook/main'
OTHER_BOTS_PATH = '/webhook/bot/{bot_token}'
MAIN_BOT_URL = f'{BASE_URL}{MAIN_BOT_PATH}'
OTHER_BOTS_URL = f'{BASE_URL}{OTHER_BOTS_PATH}'

Service = 'All'

database.sql_start()

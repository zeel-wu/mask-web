import os

PROJECT_APP_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = os.path.join(PROJECT_APP_DIR, "../static")
UPLOAD_FOLDER = '/static'
LOG_PATH = os.path.join(PROJECT_APP_DIR, "../log")
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'txt', 'sql', 'json', 'log', 'py'}
AES_KEY_PATH = os.path.join(PROJECT_APP_DIR, "../conf")
AES_IV = "password"
SECRET_KEY = 'password'
JSON_FILE_NAME = 'find_data.json'
# --redis-config---
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 16379
REDIS_PASS = ''

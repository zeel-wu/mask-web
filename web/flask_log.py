import logging
from logging.handlers import RotatingFileHandler

from web.config import LOG_PATH
from web.create_app import app

handler = RotatingFileHandler(f'{LOG_PATH}/app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)

app.logger.addHandler(handler)
print('aaaaaaaa')
if not app.debug:
    # 如果不处于调试模式，将日志输出到 stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

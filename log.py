#-*- coding: utf-8 -*-

import os
import logging
from datetime import datetime
from logging.config import dictConfig

# 로그 설정
logging_config = dict(
    version = 1,
    formatters = {
        'formatter': {'format':
              '[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s'}
    },
    handlers = {
        'stream_handler': {'class': 'logging.StreamHandler',
              'formatter': 'formatter',
              'level': logging.INFO},
        'file_handler': {'class': 'logging.handlers.RotatingFileHandler',
              'formatter': 'formatter',
              'level': logging.INFO,
              'filename': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log/print' + datetime.now().strftime('print_%Y_%m_%d.log')),
              'encoding': 'utf-8',
              'maxBytes': 1048576}
              #'backupCount': 0}
    },
    root = {
        'handlers': ['stream_handler', 'file_handler'],
        'level': logging.INFO,
    },
)

# 로그 설정 삽입
dictConfig(logging_config)

# 로그 생성
logger = logging.getLogger()

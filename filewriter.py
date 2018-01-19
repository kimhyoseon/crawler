#-*- coding: utf-8 -*-

import os
import json

LOG_PATH = os.path.join(os.path.dirname(__file__), 'log')

# 디렉토리 생성
def make_path(path):
    if path:
        if not os.path.exists(path):
            os.makedirs(path)

# 로그 저장
def save_log_file(filename, data):
    if isinstance(filename, str) and isinstance(data, list):
        make_path(LOG_PATH)
        with open(os.path.join(LOG_PATH, filename + '.json'), 'w', encoding='UTF-8') as file:
            json.dump(data, file)

# 로그 가져오기
def get_log_file(filename):
    if isinstance(filename, str):

            make_path(LOG_PATH)
            log_path = os.path.join(LOG_PATH, filename + '.json')
            if os.path.exists(log_path):
                try:
                    with open(log_path, encoding='UTF-8') as f:
                        return json.load(f)
                except Exception as errorMessage:
                    remove_log_file(filename)
                    return []
            else:
                return []

# 로그 저장
def remove_log_file(filename):
    if isinstance(filename, str):
        os.remove(os.path.join(LOG_PATH, filename + '.json'))

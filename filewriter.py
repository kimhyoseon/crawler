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
    if isinstance(filename, str) and (isinstance(data, list) or isinstance(data, dict)):
        make_path(LOG_PATH)
        with open(os.path.join(LOG_PATH, filename + '.json'), 'w') as file:
            json.dump(data, file)

# 로그 가져오기
def get_log_file(filename, is_json=False):
    if isinstance(filename, str):

            make_path(LOG_PATH)
            log_path = os.path.join(LOG_PATH, filename + '.json')
            if os.path.exists(log_path):
                try:
                    with open(log_path) as f:
                        return json.load(f)
                except Exception as errorMessage:
                    remove_log_file(filename)
                    if is_json is False:
                        return []
                    else:
                        return {}
            else:
                if is_json is False:
                    return []
                else:
                    return {}

# 로그 저장
def remove_log_file(filename):
    if isinstance(filename, str):
        os.remove(os.path.join(LOG_PATH, filename + '.json'))

# json 데이터 갯수 관리
def slice_json_by_max_len(data, max_len=100):
    if isinstance(data, list) or isinstance(data, dict):
        for i in range(len(data)):
            if len(data) < max_len: break
            del data[0]

    return data
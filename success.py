#-*- coding: utf-8 -*-

import log
import filewriter
import telegrambot
from crawler2 import Crawler
from datetime import datetime, timedelta

class Success(Crawler):

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)
            today = datetime.today().strftime('%Y_%m_%d')
            yesterday = (datetime.today() - timedelta(1)).strftime('%Y_%m_%d')

            log_yesterday = self.log[yesterday]
            log_today = self.log[today]

            for key in log_today.keys():
                if key in log_yesterday:
                    del log_yesterday[key]

            if log_yesterday and len(log_yesterday) > 0:
                text = ', '.join(map(str, log_yesterday.keys()))
                text = '발송실패 모듈: %s\n확인해주세요.' % text

                if text:
                    telegrambot.send_message(text, 'dev')

        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    success = Success()
    success.start()

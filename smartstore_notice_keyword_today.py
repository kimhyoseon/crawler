#-*- coding: utf-8 -*-

import log
import pymysql
import filewriter
import telegrambot
from pytz import timezone
from datetime import datetime, timedelta
from crawler2 import Crawler

class SmartstoreNoticeKeywordToday(Crawler):

    SHOPPING_URL = 'https://msearch.shopping.naver.com/search/all?frm=NVSHSRC&cat_id=&pb=true&mall=&query='

    def start(self):
        try:
            self.mysql = filewriter.get_log_file('mysql')
            message = ''

            # 날짜
            today = datetime.now(timezone('Asia/Seoul'))
            today = today + timedelta(days=-1)
            today = today.strftime('%Y-%m-%d')
            # print(today)
            # exit()

            # MySQL Connection 연결
            conn = pymysql.connect(host=self.mysql[0], db=self.mysql[1], user=self.mysql[2], password=self.mysql[3], charset='utf8')

            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()

            # SQL문 실행
            sql = "SELECT keyword, raceIndex FROM keywords WHERE regDate > '" + today + "' AND raceIndex > 0 AND raceIndex < 0.2 AND hasMainShoppingSearch=1 ORDER BY raceIndex ASC"
            # sql = "SELECT keyword, raceIndex FROM keywords WHERE raceIndex > 0 AND raceIndex < 1 AND hasMainShoppingSearch=1 ORDER BY raceIndex ASC LIMIT 10"
            curs.execute(sql)

            # 데이타 Fetch
            rows = curs.fetchall()

            if rows:
                for row in rows:
                    print(row)
                    message += '%s (%.5f)' % (row[0], row[1])
                    message += '\n'
                    message += '%s%s' % (self.SHOPPING_URL, row[0])
                    message += '\n'

            log.logger.info('SmartstoreNoticeKeywordToday completed!')

            if message:
                telegrambot.send_message(message, 'keyword')

            conn.close()
            exit()

        except Exception as e:
            conn.close()
            log.logger.error(e, exc_info=True)
            exit()

if __name__ == "__main__":
    jshk = SmartstoreNoticeKeywordToday()
    jshk.utf_8_reload()
    jshk.start()

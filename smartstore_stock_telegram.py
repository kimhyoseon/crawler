#-*- coding: utf-8 -*-

import log
import pymysql
import filewriter
import telegrambot
from pytz import timezone
from datetime import datetime, timedelta

class SmartstoreStockTelegram():

    def start(self):
        try:
            # 날짜
            week_ago = datetime.now(timezone('Asia/Seoul'))
            week_ago = week_ago + timedelta(days=-7)
            week_ago = week_ago.strftime('%Y%m%d')
            week_ago = str(week_ago)
            
            self.mysql = filewriter.get_log_file('mysql')

            # MySQL Connection 연결
            conn = pymysql.connect(host=self.mysql[0], port=3306, db=self.mysql[1], user=self.mysql[2], password=self.mysql[3], charset='utf8')

            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()

            # 연관키워드 정보 가져오기
            sql = "SELECT smartstore_stock.*, smartstore_order.sale_cnt, ROUND((smartstore_stock.amount / smartstore_order.sale_cnt) - smartstore_stock.period) AS remain FROM smartstore_stock LEFT JOIN (SELECT id, ROUND(SUM(sale_cnt) / 7, 1) AS sale_cnt FROM smartstore_order WHERE date >=%s GROUP BY smartstore_order.id) AS smartstore_order ON smartstore_order.id = smartstore_stock.id ORDER BY title ASC" % week_ago
            curs.execute(sql)

            # 데이타 Fetch
            rows = curs.fetchall()

            notice = '[쿠힛 재고 알림]\n\n'

            if rows:
                for row in rows:
                    if row[7] and row[7] < 15:
                        print(row)
                        # if row[3]:
                        #     notice += '%s[%s] %d일\n' % (row[2], row[3], int(row[7]))
                        # else:
                        #     notice += '%s %d일\n' % (row[2], int(row[7]))

            # print(notice)
            telegrambot.send_message(notice, 'kuhit')

            conn.close()
            exit()

        except Exception as e:
            conn.close()
            log.logger.error(e, exc_info=True)
            exit()

if __name__ == "__main__":
    jshk = SmartstoreStockTelegram()
    jshk.start()

#-*- coding: utf-8 -*-

import re
from crawler import Crawler
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone

class Ppomppu(Crawler):

    # 크롤링 할 사이트 주소를 입력
    SITE_URL = ['http://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu', 'http://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu4']
    DETAIL_URL = 'http://www.ppomppu.co.kr/zboard/'

    BASE_GOOD = 5

    IS_PROXY = True
    IS_SELENIUM = True

    # 내용 추출 정의
    def extract(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        element = soup.find('table', id='revolution_main_table')

        # 1+1 영화 리스트
        if element:
            for list in element.find_all('tr', class_=re.compile('list[0-9]')):
                try:
                    tds = list.find_all('td', recursive=False)
                    id = tds[0].getText().strip()
                    good = int(tds[5].getText().strip().split('-')[0].strip())

                    if id and id not in self.log and good and good >= self.BASE_GOOD:
                        link = self.DETAIL_URL + tds[3].find('a')['href'].strip()
                        title = tds[3].getText().strip()
                        s1 = datetime.now(timezone('Asia/Seoul')).strftime('%H:%M:%S')
                        try:
                            s2 = tds[4].getText().strip()
                            tdelta = datetime.strptime(s1, '%H:%M:%S') - datetime.strptime(s2, '%H:%M:%S')
                            hours, remainder = divmod(tdelta.seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            timelap = '등록시간: %d시간 %d분 전' % (hours, minutes)
                        except Exception as errorMessage:
                            timelap = '등록시간: 하루 전'
                        good = '추천수: %d' % good
                        text = title + '\n' + good + '\n' + timelap + '\n' + link
                        self.save(id, text)

                except Exception as errorMessage:
                    #print(errorMessage)
                    continue



if __name__ == "__main__":
    ppomppu = Ppomppu()
    ppomppu.start()
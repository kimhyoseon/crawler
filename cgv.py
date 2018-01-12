#-*- coding: utf-8 -*-

import os
import re
import argparse
import filewriter
import telegrambot
from bs4 import BeautifulSoup
from selenium import webdriver

class Cgv:

    # 사이트 주소
    SITE_URL = 'http://www.cgv.co.kr/culture-event/event/?menu=2'
    DETAIL_URL = 'http://www.cgv.co.kr/culture-event/event/'

    # 파일명
    FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

    # 핫딜 카운트
    count = 0

    def __init__(self, args):
        # 기존 로그 가져오기
        self.log = filewriter.get_log_file(self.FILE_NAME)

        if args.chrome is True:
            self.driver = webdriver.Chrome('./driver/chromedriver')
        else:
            self.driver = webdriver.PhantomJS('./driver/phantomjs')

    def start(self):
        # Connect to site.
        self.driver.get(self.SITE_URL)

        # DOM parse
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 1+1 영화 리스트
        for list in soup.find('div', class_='evt-item-lst').children:
            if not list == -1:
                linkObj = list.find('a')
                imgObj = list.find('img')
                if not linkObj == -1:
                    title = imgObj['alt']

                    if "1+1" not in title:
                        continue

                    link = linkObj['href']
                    img = imgObj['src']
                    m = re.search('idx=(.*?)\&', link)
                    id = m.group(1)
                    link = self.DETAIL_URL + link.replace('./', '')

                    if id and id not in self.log:
                        text = title + '\n' + link
                        telegrambot.send_message(text)
                        self.log.append(id)
                        self.count = self.count + 1
                        # print(link)
                        # print(title)
                        # print(img)
                        # print(id)

        # 결과
        if self.count > 0:
            filewriter.save_log_file(self.FILE_NAME, self.log)
            print('%s: 새로운 핫딜 %d개가 등록 되었습니다.'%(self.FILE_NAME,self.count))
        else:
            print('%s: 새로운 핫딜이 없습니다.'%self.FILE_NAME)

if __name__ == "__main__":
    # argparse를 사용하여 파라미터 정의
    parser = argparse.ArgumentParser()

    # 크롬으로 실행
    parser.add_argument(
        '--chrome',
        default=False,
        help='If true, uses Chrome driver',
        action='store_true'
    )

    FLAGS, unparsed = parser.parse_known_args()

    cgv = Cgv(FLAGS)
    cgv.start()

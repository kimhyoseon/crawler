#-*- coding: utf-8 -*-

import re
from crawler import Crawler
from bs4 import BeautifulSoup

class Cgv(Crawler):

    # 크롤링 할 사이트 주소를 입력
    SITE_URL = 'http://www.cgv.co.kr/culture-event/event/?menu=2'
    DETAIL_URL = 'http://www.cgv.co.kr/culture-event/event/'

    # javascript로 리스트를 가져오기 때문에 셀레니움 사용
    IS_SELENIUM = True
    SELENIUM_WAIT_TAG = {'tag': 'div', 'attr': 'class', 'name': 'evt-item-lst'}

    # 내용 추출 정의
    def extract(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        element = soup.find('div', class_="evt-item-lst")

        print(element)

        # 1+1 영화 리스트
        if element:
            for list in element.children:
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
                            self.save(id, text)

if __name__ == "__main__":
    cgv = Cgv()
    cgv.start()

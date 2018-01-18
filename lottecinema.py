#-*- coding: utf-8 -*-

from crawler import Crawler
from bs4 import BeautifulSoup

class Lottecinema(Crawler):

    # 크롤링 할 사이트 주소를 입력
    SITE_URL = 'http://www.lottecinema.co.kr/LCHS/Contents/Cinema-Mall/gift-shop.aspx'

    # 롯데시네마는 국내IP만 허용하기 때문에 국내 프록시 서버를 이용
    IS_PROXY = True

    # javascript로 리스트를 가져오기 때문에 셀레니움 사용
    IS_SELENIUM = True
    SELENIUM_WAIT_TAG = {'tag': 'ul', 'attr': 'class', 'name': 'product_slist p10'}

    # 내용 추출 정의
    def extract(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        element = soup.find('ul', class_='product_slist p10')

        # 1+1 영화 리스트
        if element:
            for list in element.find_all('li'):
                id = list.get('id')
                if id and id not in self.log:
                    title = list.find('dt', class_='product_tit').getText()
                    date = list.find('dd', class_='date').getText()
                    price = list.find('span', class_='price').getText()
                    img = list.find('img')['src']
                    text = title + '\n' + date + '\n' + price + '\n' + img
                    self.save(id, text)

if __name__ == "__main__":
    lottecinema = Lottecinema()
    lottecinema.start()
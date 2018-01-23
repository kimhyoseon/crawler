#-*- coding: utf-8 -*-

import re
import time
from crawler import Crawler
from bs4 import BeautifulSoup
from decimal import Decimal

class Jejuair(Crawler):

    # 크롤링 할 사이트 주소를 입력
    SITE_URL = ['http://www.jejuair.net/jejuair/kr/main.do']

    IS_CHROME = True
    IS_REPORT = False

    # javascript로 리스트를 가져오기 때문에 셀레니움 사용
    IS_SELENIUM = True
    SELENIUM_WAIT_TAG = {'tag': 'div', 'attr': 'id', 'name': 'divDepStn1'}

    price_depature = 999999999999
    price_return = 999999999999
    date_depature = []
    date_return = []

    # 내용 추출 정의
    def extract(self, html):
        print('jejuair searching start.')

        self.selenium_click_event([
            {'tag': 'div', 'attr': 'id', 'name': 'divDepStn1'},
            {'tag': 'button', 'attr': 'aircode', 'name': 'ICN'},
            {'tag': 'button', 'attr': 'aircode', 'name': 'NRT'},
            {'tag': 'button', 'attr': 'id', 'name': 'btnDoubleOk'},
            {'tag': 'button', 'attr': 'id', 'name': 'btnReservation'},
            {'tag': 'div', 'attr': 'id', 'name': 'btnSearch'},
        ])

        self.is_searching = True

        while self.is_searching == True:
            self.extract_price()

        print('jejuair searching end.')
        exit()

    def extract_price(self):
        try:
            html = self.selenium_extract_with_xpath({'tag': 'div', 'attr': 'id', 'name': 'divDepDateRoll'})

            soup = BeautifulSoup(html, 'html.parser')

            depature_element = soup.find('div', id='divDepDateRoll').find('ul', class_='dataList').find_all('li', recursive=False)
            return_element = soup.find('div', id='divRetDateRoll').find('ul', class_='dataList').find_all('li', recursive=False)

            for depature in depature_element:
                try:
                    price = depature.find('strong', class_='price0').getText()
                    price = Decimal(re.sub(r'[^\d.]', '', price))

                    if self.price_depature is None or price <= self.price_depature:
                        if price < self.price_depature:
                            self.date_depature = []
                        self.price_depature = price
                        self.date_depature.append(depature.find('span').getText())

                except Exception as errorMessage:
                    #print(errorMessage)
                    pass

            for returns in return_element:
                try:
                    price = returns.find('strong', class_='price0').getText()
                    price = Decimal(re.sub(r'[^\d.]', '', price))

                    if self.price_return is None or price <= self.price_return:
                        if price < self.price_return:
                            self.date_return = []
                        self.price_return = price
                        self.date_return.append(returns.find('span').getText())

                except Exception as errorMessage:
                    #print(errorMessage)
                    pass

            print(self.price_depature)
            print(self.date_depature)
            print(self.price_return)
            print(self.date_return)

            self.selenium_click_event([{'tag': 'button', 'attr': 'id', 'name': 'btnNextDep'}])

            if self.selenium_get_alert_text() == '일정을 조회하실 수 없습니다.':
                self.send_message()
                self.is_searching = False

        except Exception as errorMessage:
            #print(errorMessage)
            pass

    def send_message(self):
        print(self.price_depature)
        print(self.date_depature)
        print(self.price_return)
        print(self.date_return)

        self.price_depature = 999999999999
        self.price_return = 999999999999
        self.date_depature = []
        self.date_return = []

if __name__ == "__main__":
    jejuair = Jejuair()
    jejuair.start()

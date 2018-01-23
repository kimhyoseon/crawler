#-*- coding: utf-8 -*-

import re
import time
from crawler import Crawler
from bs4 import BeautifulSoup
from decimal import Decimal

class Jejuair(Crawler):

    # 크롤링 할 사이트 주소를 입력
    SITE_URL = ['http://www.jejuair.net/jejuair/kr/main.do']

    # IS_CHROME = True
    IS_REPORT = False

    # javascript로 리스트를 가져오기 때문에 셀레니움 사용
    IS_SELENIUM = True
    SELENIUM_WAIT_TAG = {'tag': 'div', 'attr': 'id', 'name': 'divDepStn1'}

    MAX_WHILE_COUNT = 5
    while_count = 0
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
            self.while_count = self.while_count + 1

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

            if self.while_count > self.MAX_WHILE_COUNT:
                self.send_message()

            if self.selenium_is_alert_exist() == True:
                self.send_message()


        except Exception as errorMessage:
            if self.while_count > self.MAX_WHILE_COUNT:
                self.send_message()
            pass

    def send_message(self):
        self.is_searching = False
        price_depature = 'depature price: {:0,.0f} won'.format(self.price_depature)
        price_return = 'return price: {:0,.0f} won'.format(self.price_return)
        date_depature = 'depature date: %s'%",".join(self.date_depature)
        date_return = 'return date: %s'%",".join(self.date_return)

        text = price_depature + '\n' + date_depature + '\n' + price_return + '\n' + date_return

        self.save('20180123-NRT', text)

        self.while_count  = 0
        self.price_depature = 999999999999
        self.price_return = 999999999999
        self.date_depature = []
        self.date_return = []

if __name__ == "__main__":
    jejuair = Jejuair()
    jejuair.start()

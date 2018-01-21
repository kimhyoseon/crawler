#-*- coding: utf-8 -*-

import re
from crawler import Crawler
from bs4 import BeautifulSoup

class Jejuair(Crawler):

    # 크롤링 할 사이트 주소를 입력
    SITE_URL = ['http://www.jejuair.net/jejuair/kr/main.do']

    IS_CHROME = True
    IS_REPORT = False

    # javascript로 리스트를 가져오기 때문에 셀레니움 사용
    IS_SELENIUM = True
    SELENIUM_WAIT_TAG = {'tag': 'div', 'attr': 'id', 'name': 'divDepStn1'}

    # 내용 추출 정의

    def extract(self, html):
        self.selenium_click_event([
            {'tag': 'div', 'attr': 'id', 'name': 'divDepStn1'},
            {'tag': 'button', 'attr': 'aircode', 'name': 'ICN'},
            {'tag': 'button', 'attr': 'aircode', 'name': 'NRT'},
            {'tag': 'button', 'attr': 'id', 'name': 'btnDoubleOk'},
            {'tag': 'button', 'attr': 'id', 'name': 'btnReservation'},
        ])

        #self.driver.find_element_by_xpath('//div[@id="divDepStn1"]').click()
        #WebDriverWait(self.driver, self.SITE_CONNECT_TIMEOUT).until(element_present)
        #self.driver.find_element_by_xpath('//button[@aircode="ICN"]').click()
        exit()


if __name__ == "__main__":
    jejuair = Jejuair()
    jejuair.start()

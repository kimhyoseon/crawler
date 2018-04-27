#-*- coding: utf-8 -*-

import re
import log
import filewriter
import telegrambot
from crawler2 import Crawler
from bs4 import BeautifulSoup

class Naver(Crawler):

    DETECT_URLS = [
        # 에어컨
        'https://search.shopping.naver.com/detail/detail.nhn?nv_mid=13799551012',
        'https://search.shopping.naver.com/detail/detail.nhn?nv_mid=11452498768',
        'https://search.shopping.naver.com/detail/detail.nhn?nv_mid=13745706053',
        'https://search.shopping.naver.com/detail/detail.nhn?nv_mid=11399379411',
        'https://search.shopping.naver.com/detail/detail.nhn?nv_mid=11169795789'
    ]

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name, is_json=True)

            for url in self.DETECT_URLS:
                if self.connect(site_url=url, is_proxy=False, default_driver='selenium', is_chrome=False) is False:
                    raise Exception('site connect fail')

                self.scan_page(url)

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def scan_page(self, url):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'table', 'attr': 'class', 'name': 'tbl_lst'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('table', class_="tbl_lst").find('tr', class_="_itemSection").find_all('td', recursive=False)

            if element:
                price_str = element[1].find('a').getText().strip()
                price = re.sub("\D", "", price_str)

                try:
                    if self.log[url] > price:
                        title = soup.find('div', class_="h_area").find('h2').getText().strip()
                        service = element[0].find('img')['alt']
                        price_before = format(self.log[url], ',')
                        price_new = format(price, ',')
                        message = '[네이버쇼핑] 최저가가 갱신되었습니다.\n[%s]\n%s\n이전 가격: %s원\n최저 가격: %s원\n%s' % (service, title, price_before, price_new, url)
                        telegrambot.send_message(message)
                        self.log[url] = price;
                except Exception as e:
                    self.log[url] = price;

            #print(self.log)
            filewriter.save_log_file(self.name, self.log)

        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    naver = Naver()
    naver.utf_8_reload()
    naver.start()

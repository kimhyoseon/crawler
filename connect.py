#-*- coding: utf-8 -*-

import log
from crawler2 import Crawler
from bs4 import BeautifulSoup

class Connect(Crawler):
    def start(self):
        try:
            if self.connect(site_url='http://naver.com') is False:
                raise Exception('site connect fail')

            # if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'evt-item-lst'}) is False:
            #     raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            print(self.driver.title)

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    connect = Connect()
    connect.utf_8_reload()
    connect.start()

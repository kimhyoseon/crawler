#-*- coding: utf-8 -*-

import re
import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup
from ppomppu_link_generator import PpomppuLinkGenerator

class Cgv(Crawler):

    DETAIL_URL = 'http://www.cgv.co.kr/culture-event/event/'

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

            if self.connect(site_url='http://www.cgv.co.kr/culture-event/event/', is_proxy=False,
                            default_driver='selenium',
                            is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'evt-item-lst'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('div', class_="evt-item-lst")

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
                                shop = '핫딜사이트: CGV'
                                title = '상품명: %s' % title
                                ppomppuLinkGenerator = PpomppuLinkGenerator()
                                link = ppomppuLinkGenerator.getShortener(url=link)
                                link = '구매 바로가기: %s' % link
                                text = shop + '\n' + title + '\n' + link

                                # print(text)
                                # self.destroy()
                                # exit()

                                self.log = filewriter.slice_json_by_max_len(self.log, max_len=100)

                                self.send_messge_and_save(id, text, 'hotdeal')

        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    cgv = Cgv()
    cgv.utf_8_reload()
    cgv.start()

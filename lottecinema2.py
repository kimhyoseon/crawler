#-*- coding: utf-8 -*-

import re
import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup
from ppomppu_link_generator import PpomppuLinkGenerator

class Cgv(Crawler):

    DETAIL_URL = 'http://event.lottecinema.co.kr/LCHS/Contents/Event/infomation-delivery-event.aspx?EventID='

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

            if self.connect(site_url='http://event.lottecinema.co.kr/LCHS/Contents/Event/movie-booking-list.aspx', is_proxy=True, default_driver='selenium',
                        is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'ul', 'attr': 'class', 'name': 'emovie_list'}) is False:
                self.remove_proxy_server_ip_list()
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('ul', class_='emovie_list')

            # 1+1 영화 리스트
            if element:
                for list in element.find_all('li'):
                    link_tag = list.find('dt', class_='event').find('a')
                    attr_click = link_tag['onclick'].strip()
                    id = re.search(r'ilsMove\(\"(.*?)\",', attr_click).group(1)

                    if id and id not in self.log:
                        title = link_tag.getText().strip()

                        if "1+1" not in title:
                            continue

                        shop = '핫딜사이트: 롯데시네마'
                        date = list.find('dd', class_='eventdate').getText().strip()
                        #price = list.find('span', class_='price').getText()
                        title = '상품명: %s (%s)' % (title, date)
                        ppomppuLinkGenerator = PpomppuLinkGenerator()
                        img = list.find('img')['src']
                        link = self.DETAIL_URL + id
                        link = ppomppuLinkGenerator.getShortener(url=link)
                        link = '구매 바로가기: %s' % link
                        text = shop + '\n' + title + '\n' + link + '\n' + img

                        # print(text)
                        # self.destroy()
                        # exit()

                        self.send_messge_and_save(id, text)

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    cgv = Cgv()
    cgv.utf_8_reload()
    cgv.start()

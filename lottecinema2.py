#-*- coding: utf-8 -*-

import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup
from ppomppu_link_generator import PpomppuLinkGenerator

class Cgv(Crawler):

    DETAIL_URL = 'http://www.lottecinema.co.kr/LCHS/Contents/Cinema-Mall/gift-shop-detail.aspx?displayMiddleClassification=10&displayItemID='

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

            if self.connect(site_url='http://www.lottecinema.co.kr/LCHS/Contents/Cinema-Mall/gift-shop.aspx', is_proxy=True, default_driver='selenium',
                        is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'ul', 'attr': 'class', 'name': 'product_slist p10'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('ul', class_='product_slist p10')

            # 1+1 영화 리스트
            if element:
                for list in element.find_all('li'):
                    id = list.get('id')
                    if id and id not in self.log:
                        title = list.find('dt', class_='product_tit').getText()

                        if "1+1" not in title:
                            continue

                        shop = '핫딜사이트: 롯데시네마'
                        date = list.find('dd', class_='date').getText()
                        price = list.find('span', class_='price').getText()
                        title = '상품명: %s %s (%s)' % (title, price, date)
                        ppomppuLinkGenerator = PpomppuLinkGenerator()
                        idnum = id.replace('ic', '')
                        img = list.find('img')['src']
                        link = self.DETAIL_URL + idnum
                        link = ppomppuLinkGenerator.getShortener(url=link)
                        link = '구매 바로가기: %s' % link
                        text = shop + '\n' + title + '\n' + link + '\n' + img

                        # print(text)
                        # self.destroy()
                        # exit()

                        self.send_messge_and_save(id, text)

        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    cgv = Cgv()
    cgv.utf_8_reload()
    cgv.start()

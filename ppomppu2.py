#-*- coding: utf-8 -*-

import re
import log
import filewriter
from datetime import datetime
from crawler2 import Crawler
from pytz import timezone
from bs4 import BeautifulSoup
from ppomppu_link_generator import PpomppuLinkGenerator

class Ppomppu(Crawler):

    DETAIL_URL = 'http://www.ppomppu.co.kr/zboard/'
    BASE_GOOD = 10

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

            if self.connect(site_url='http://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu', is_proxy=False, default_driver='selenium',
                        is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            if self.connect(site_url='http://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu4', is_proxy=False, default_driver='selenium',
                        is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'table', 'attr': 'id', 'name': 'revolution_main_table'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('table', id='revolution_main_table')

            # 핫딜리스트
            if element:
                for list in element.find_all('tr', class_=re.compile('list[0-9]')):
                    try:
                        tds = list.find_all('td', recursive=False)

                        title = tds[3].find('font').getText().strip()
                        good = int(tds[5].getText().strip().split('-')[0].strip())
                        regdate = tds[4]['title'].strip()

                        if regdate and regdate not in self.log and good and good >= self.BASE_GOOD:
                            link = self.DETAIL_URL + tds[3].find('a')['href'].strip()
                            s1 = datetime.now(timezone('Asia/Seoul')).strftime('%H:%M:%S')
                            status = '★☆☆☆☆'

                            try:
                                s2 = tds[4].getText().strip()
                                tdelta = datetime.strptime(s1, '%H:%M:%S') - datetime.strptime(s2, '%H:%M:%S')
                                hours, remainder = divmod(tdelta.seconds, 3600)
                                minutes, seconds = divmod(remainder, 60)

                                if hours < 4:
                                    status = '★★☆☆☆'
                                if hours < 2:
                                    status = '★★★☆☆'
                                if hours < 1:
                                    status = '★★★★☆'
                                    if minutes < 20:
                                        status = '★★★★★'

                                #timelap = 'time lap: %d hour %d minutes before' % (hours, minutes)
                                #timelap = '등록시간: %d시간 %d분 전' % (hours, minutes)
                                timelap = '핫딜점수: %s' % status
                            except Exception as errorMessage:
                                status = '★★☆☆☆'

                            try:
                                indexShop = title.index(']')
                                shop = '핫딜사이트: %s' % title[1:indexShop].strip()
                                title = '상품명: %s' % title[indexShop + 1:].strip()
                                title = shop + '\n' + title
                            except Exception as errorMessage:
                                title = '상품명: %s' % title

                            ppomppuLinkGenerator = PpomppuLinkGenerator()
                            boardLink = ppomppuLinkGenerator.getShortener(url=link)
                            boardLink = '게시글 바로가기: %s' % boardLink

                            text = title + '\n' + timelap + '\n' + boardLink

                            # 어필리에이트 링크 생성
                            ailliateLink = self.get_item_link(link)

                            if ailliateLink is not False and len(ailliateLink) > 0:
                                text += '\n상품 바로가기: ' + ailliateLink

                            text = text + '\n\n * 이미지를 클릭해 상세내용을 확인하세요.'

                            # print(text)
                            # self.destroy()
                            # exit()

                            self.send_messge_and_save(regdate, text)
                    except Exception as e:
                        continue

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def get_item_link(self, url=None):
        try:
            if self.connect(site_url=url, is_proxy=False, default_driver='selenium',
                        is_chrome=False) is False:
                raise Exception('site connect fail')

            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'wordfix'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('div', class_='wordfix')

            # 핫딜리스트
            if element:
                try:
                    if not element.find('a', recursive=False):
                        raise Exception('link is not founded.')

                    link = element.find('a', recursive=False).getText()

                    if link is None:
                        raise Exception('link is not founded.')

                    ppomppuLinkGenerator = PpomppuLinkGenerator()
                    apiliateLink = ppomppuLinkGenerator.genLink(url=link)

                    if apiliateLink is None:
                        raise Exception('apiliateLink is not generated.')

                    return apiliateLink

                except Exception as e:
                    log.logger.error(e, exc_info=True)
                    return False
            else:
                return False

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return false

if __name__ == "__main__":
    ppomppu = Ppomppu()
    ppomppu.utf_8_reload()
    ppomppu.start()

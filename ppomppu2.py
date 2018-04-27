#-*- coding: utf-8 -*-

import re
import log
import filewriter
from datetime import datetime
from crawler2 import Crawler
from pytz import timezone
from bs4 import BeautifulSoup

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

                            try:
                                s2 = tds[4].getText().strip()
                                tdelta = datetime.strptime(s1, '%H:%M:%S') - datetime.strptime(s2, '%H:%M:%S')
                                hours, remainder = divmod(tdelta.seconds, 3600)
                                minutes, seconds = divmod(remainder, 60)
                                #timelap = 'time lap: %d hour %d minutes before' % (hours, minutes)
                                timelap = '등록시간: %d시간 %d분 전' % (hours, minutes)
                            except Exception as errorMessage:
                                timelap = '등록시간: 1일전'

                            good = 'Good count: %d' % good
                            text = title + '\n' + good + '\n' + timelap + '\n' + link

                            self.send_messge_and_save(regdate, text)
                    except Exception as e:
                        continue

        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    ppomppu = Ppomppu()
    ppomppu.utf_8_reload()
    ppomppu.start()

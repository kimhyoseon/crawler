#-*- coding: utf-8 -*-

import re
import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup
from ppomppu_link_generator import PpomppuLinkGenerator

class Aptrent(Crawler):

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

            self.kind = 'rent';
            self.tab = '임대';
            self.DETAIL_URL = 'https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId='

            if self.connect(site_url='https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcView.do', is_proxy=False,
                            default_driver='selenium',
                            is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            self.kind = 'buy';
            self.tab = '공공분양';
            self.DETAIL_URL = 'https://www.myhome.go.kr/hws/portal/sch/selectLttotHouseDetailView.do?pblancId='

            if self.connect(site_url='https://www.myhome.go.kr/hws/portal/sch/selectLttotHouseView.do',
                            is_proxy=False,
                            default_driver='selenium',
                            is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'td', 'attr': 'class', 'name': 'al'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('tbody', id="schTbody")

            if element:
                for list in element.find_all('tr'):
                    try:
                        #print(list)
                        tds = list.find_all('td', recursive=False)
                        link_tag = tds[3].find('a')
                        href_attr = link_tag['href'].strip()
                        id = re.search(r'Detail\(\'(.*?)\'', href_attr).group(1)
                        log_id = self.kind + id

                        # 수집 성공로그
                        self.record_success_log()

                        if log_id and log_id not in self.log:
                            tab = '분류: %s' % self.tab
                            type = '공급유형: %s' % tds[0].getText().strip()
                            region = '지역: %s' % tds[2].getText().strip()
                            title = '공고명: %s' % link_tag.getText().strip()
                            link = self.DETAIL_URL + id
                            ppomppuLinkGenerator = PpomppuLinkGenerator()
                            link = ppomppuLinkGenerator.getShortener(url=link)
                            link = '상세보기: %s' % link

                            text = tab + '\n' + type + '\n' + region + '\n' + title + '\n' + link

                            # print(text)
                            # self.destroy()
                            # exit()

                            self.send_messge_and_save(log_id, text, 'aptrent')

                    except Exception as e:
                        print(e)
                        continue


        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    aptrent = Aptrent()
    aptrent.utf_8_reload()
    aptrent.start()

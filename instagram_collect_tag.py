#-*- coding: utf-8 -*-

import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup

class InstagramCollectTag (Crawler):

    DETAIL_URL = 'http://startag.io/search.php?mode=0&q='
    KEYWORD = '필라테스'
    ADD_COUNT = 0;

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

            if self.connect(site_url=self.DETAIL_URL + self.KEYWORD, is_proxy=False,
                            default_driver='selenium',
                            is_chrome=True) is False:
                raise Exception('site connect fail')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('table', id="table_result")

            if self.selenium_extract_by_xpath(xpath='//*[@id="table_result"]') is False:
                raise Exception('selenium_extract_by_xpath fail.')

            if element:
                for list in element.find_all('tr'):
                    try:
                        tag = list.find('td', class_='result_td01').getText().strip()
                        tag = tag.replace("#", "")

                        if tag:
                            if tag not in self.log:
                                print(tag)
                                self.log.append(tag)
                                self.ADD_COUNT = self.ADD_COUNT + 1;
                    except Exception:
                        continue

            filewriter.save_log_file(self.name, self.log)
            log.logger.info('(%d/%d) tags has just updated.' % (self.ADD_COUNT, len(self.log)))

            self.destroy()

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    cgv = InstagramCollectTag()
    cgv.utf_8_reload()
    cgv.start()

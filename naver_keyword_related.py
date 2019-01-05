#-*- coding: utf-8 -*-

import re
import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup

class Naverkeywordrelated(Crawler):

    NAVER_SHOPPING = 'https://shopping.naver.com/'
    
    def start(self):
        try:
            self.bestKeyword = filewriter.get_log_file('naverkeyword')

            for ke in self.bestKeyword:
                print(ke)
            
            exit()

            
            if self.connect(site_url=self.NAVER_SHOPPING, is_proxy=False, default_driver='selenium',
                        is_chrome=True) is False:
                raise Exception('site connect fail')

            self.keywords = []

            self.collect_Naverkeywordrelated()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def collect_Naverkeywordrelated(self):
        try:
            print(len(self.bestKeyword))

            if len(self.bestKeyword) == 0:
                self.end_collect_keyword()
                return False

            if self.selenium_input_text_by_xpath(text='', tag={'tag': 'input', 'attr': 'name', 'name': 'query'}) is False:
                raise Exception('selenium_input_text_by_xpath fail.')
            if self.selenium_input_text_by_xpath(text=self.bestKeyword[0], tag={'tag': 'input', 'attr': 'name', 'name': 'query'}) is False:
                raise Exception('selenium_input_text_by_xpath fail.')
            if self.selenium_click_by_xpath(tag={'tag': 'div', 'attr': 'id', 'name': 'autocompleteWrapper'}, etc='/a[2]') is False:
                raise Exception('selenium_click_by_xpath fail.')            
            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'co_relation_srh'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('div', class_='co_relation_srh')

            if element:
                for list in element.find_all('li'):
                    link_tag = list.find('a')                    
                    keyword = link_tag.getText().strip()
            
                    if keyword:      
                        print(keyword)                      
                        self.keywords.append(keyword)

            
            self.bestKeyword.pop(0)
            self.collect_Naverkeywordrelated()                    
                        
        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)
    
    def end_collect_keyword(self):
        # for keyword in self.keywords:
        #     print(keyword)
        print(len(self.keywords))
        filewriter.save_log_file(self.name, self.keywords)
        log.logger.info('(%d) related keywords has just updated.' % (len(self.keywords)))
        self.destroy()
        exit()

if __name__ == "__main__":
    Naverkeywordrelated = Naverkeywordrelated()
    Naverkeywordrelated.utf_8_reload()
    Naverkeywordrelated.start()

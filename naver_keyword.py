#-*- coding: utf-8 -*-

import re
import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup

class NaverKeyword(Crawler):

    NAVER_DATALAB_URL = 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
    # CATEGORIES = ['50000001','50000002','50000003','50000004','50000005','50000006','50000007','50000008','50000009','50000010']
    CATEGORIES = ['50000010']
    MONTHS = ['01','02','03','04','05','06','07','08','09','10','11','12']

    def start(self):
        try:
            if self.connect(site_url=self.NAVER_DATALAB_URL, is_proxy=False, default_driver='selenium',
                        is_chrome=True) is False:
                raise Exception('site connect fail')

            self.keywords = filewriter.get_log_file(self.name)

            self.click_next_category()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)
    
    def click_next_month(self):
        try:       
            if self.selenium_click_by_xpath(xpath='(//span[@class="select_btn"])[3]') is False:
                raise Exception('selenium_click_by_xpath fail.')
            if self.selenium_click_by_xpath(xpath='(//a[text()="월간"])[1]') is False:
                raise Exception('selenium_click_by_xpath fail.')    
            
            if self.MONTHS[0] == '01':
                if self.selenium_click_by_xpath(xpath='(//span[@class="select_btn"])[5]') is False:
                    raise Exception('selenium_click_by_xpath fail.')
                if self.selenium_click_by_xpath(xpath='(//a[text()="'+self.MONTHS[0]+'"])[1]') is False:
                    raise Exception('selenium_click_by_xpath fail.')
                if self.selenium_click_by_xpath(xpath='(//span[@class="select_btn"])[8]') is False:
                    raise Exception('selenium_click_by_xpath fail.')
                if self.selenium_click_by_xpath(xpath='(//a[text()="'+self.MONTHS[0]+'"])[3]') is False:
                    raise Exception('selenium_click_by_xpath fail.')
            else:
                if self.selenium_click_by_xpath(xpath='(//span[@class="select_btn"])[8]') is False:
                    raise Exception('selenium_click_by_xpath fail.')
                if self.selenium_click_by_xpath(xpath='(//a[text()="'+self.MONTHS[0]+'"])[2]') is False:
                    raise Exception('selenium_click_by_xpath fail.')
                if self.selenium_click_by_xpath(xpath='(//span[@class="select_btn"])[5]') is False:
                    raise Exception('selenium_click_by_xpath fail.')
                if self.selenium_click_by_xpath(xpath='(//a[text()="'+self.MONTHS[0]+'"])[1]') is False:
                    raise Exception('selenium_click_by_xpath fail.')                

            self.click_search()
            self.MONTHS.pop(0)

            self.collect_NaverKeyword()   

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)    

    def collect_NaverKeyword(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'ul', 'attr': 'class', 'name': 'rank_top1000_list'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('ul', class_='rank_top1000_list')

            if element:
                for list in element.find_all('li'):
                    link_tag = list.find('a')
                    link_tag.find('span').extract()
                    keyword = link_tag.getText().strip()

                    if keyword: 
                        if keyword not in self.keywords:                          
                            self.keywords.append(keyword)

                if soup.find('span', class_='page_info').find('em').getText().strip() == '25':
                    if len(self.MONTHS) > 0:
                        self.click_next_month()
                    else:
                        self.click_next_category() 
                else:
                    self.click_next_rank()        
                        
        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def click_next_rank(self):
        try:
            if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'class', 'name': 'btn_page_next'}) is False:
                raise Exception('selenium_click_by_xpath fail.')

            self.collect_NaverKeyword()                                
                        
        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def click_next_category(self):
        try:
            if len(self.CATEGORIES) == 0:
                self.end_collect_keyword()
                return False

            if self.selenium_click_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'select'}) is False:
                raise Exception('selenium_click_by_xpath fail.')
            if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-cid', 'name': self.CATEGORIES[0]}) is False:
                raise Exception('selenium_click_by_xpath fail.')

            self.click_search()     
                      
            self.CATEGORIES.pop(0)

            self.MONTHS = ['01','02','03','04','05','06','07','08','09','10','11','12']

            self.click_next_month()                                
                        
        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def click_search(self):
        try:
            textBefore = self.selenium_wait_change_start_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'section_insite_sub'}, etc='//h4[@class="insite_title"]')
            
            if textBefore is False:
                raise Exception('selenium_wait_change_start_by_xpath fail.')

            if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'class', 'name': 'btn_submit'}) is False:
                raise Exception('selenium_click_by_xpath fail.')
            
            if self.selenium_wait_change_end_by_xpath(text=textBefore, tag={'tag': 'div', 'attr': 'class', 'name': 'section_insite_sub'}, etc='//h4[@class="insite_title"]') is False:
                raise Exception('selenium_wait_change_end_by_xpath fail.')   

            return True                                      
                        
        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def end_collect_keyword(self):
        # for keyword in self.keywords:
        #     print(keyword)
        # print(len(self.keywords))
        filewriter.save_log_file(self.name, self.keywords)
        log.logger.info('(%d) keywords has just updated.' % (len(self.keywords)))
        self.destroy()
        exit()

if __name__ == "__main__":
    NaverKeyword = NaverKeyword()
    NaverKeyword.utf_8_reload()
    NaverKeyword.start()

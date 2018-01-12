#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select


SITE_URL = 'https://www.courtauction.go.kr/index.jsp';

# Chrome
driver = webdriver.Chrome('/Users/khs75/dev/crawler/driver/chromedriver')

# PhantomJS
#driver = webdriver.PhantomJS('/Users/khs75/dev/crawler/driver/phantomjs');

# Connect to site.
driver.get(SITE_URL)

# 법원 선택
select = Select(driver.find_element_by_xpath('//select[@id="idJiwonNm1"]'))
select.select_by_index(0)

# 검색버튼 클릭
driver.find_element_by_xpath('//div[@id="main_btn"]/a').click()

# 경매 리스트
for tr in driver.find_elements_by_xpath('//table[@class="Ltbl_list"]/tbody/tr'):
    for td in tr.find_elements_by_tag_name('td'):
        print(td.text)

# DOM parse
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

print(soup)

#print('법원 : ', select.options)
#print('법원 수 : ', len(select.options))
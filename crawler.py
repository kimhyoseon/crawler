#-*- coding: utf-8 -*-

import filewriter
import telegrambot
import requests
from datetime import datetime
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Crawler:

    # 필수값
    SITE_URL = None

    PROXY_IP = '13.124.253.238:3128'
    IS_PROXY = False
    IS_SELENIUM = False
    SELENIUM_WAIT_TAG = None
    IS_CHROME = False
    # PATH_CHROME_DRIVER = './driver/chromedriver'
    # PATH_PHANTOMJS_DRIVER = './driver/phantomjs'
    PATH_CHROME_DRIVER = '/home/dev/crawler/driver/chromedriver'
    PATH_PHANTOMJS_DRIVER = '/home/dev/crawler/driver/phantomjs'
    SITE_CONNECT_TIMEOUT = 5

    def __init__(self):
        # 기존 로그 가져오기
        self.name = self.__class__.__name__.lower()
        self.log = filewriter.get_log_file(self.name)

    # 사이트 연결
    def connect_with_requests(self):
        if self.IS_PROXY is True:
            proxy_dict = {
                'http': self.PROXY_IP,
                'https': self.PROXY_IP
            }
        else:
            proxy_dict = None
        response = requests.get(self.SITE_URL, proxies=proxy_dict)

        if response.status_code != 200:
            raise Exception('Site connect error (status_code:%d)'%response.status_code)

        return response.text

    # 사이트 연결
    def connect_with_selenium(self):
        if self.IS_CHROME is True:
            options = webdriver.ChromeOptions()
            if self.IS_PROXY is True:
                options.add_argument('--proxy-server=' + self.PROXY_IP)
            self.driver = webdriver.Chrome(executable_path=self.PATH_CHROME_DRIVER, chrome_options=options)
        else:
            if self.IS_PROXY is True:
                args = ['--proxy=' + self.PROXY_IP]
            else:
                args = []
            self.driver = webdriver.PhantomJS(executable_path=self.PATH_PHANTOMJS_DRIVER,
                                              service_args=args)
        self.driver.get(self.SITE_URL)
        # 요소를 찾을 때까지 대기
        if self.SELENIUM_WAIT_TAG is None:
            element_present = EC.presence_of_element_located((By.TAG_NAME, 'body'))
        else:
            xpath = '//%s[@%s="%s"]'%(self.SELENIUM_WAIT_TAG['tag'], self.SELENIUM_WAIT_TAG['attr'], self.SELENIUM_WAIT_TAG['name'])
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
        WebDriverWait(self.driver, self.SITE_CONNECT_TIMEOUT).until(element_present)
        html = self.driver.page_source
        self.driver.quit()
        return html

    def start(self):
        try:
            self.count = 0

            if self.SITE_URL is None:
                raise Exception('Site url is not defined.')

            if self.IS_SELENIUM:
                html = self.connect_with_selenium()
            else:
                html = self.connect_with_requests()

            self.extract(html)
            self.report()
        except Exception as errorMessage:
            text = str('[%s] %s: %s'%(self.get_time(),self.name,errorMessage))
            print(text)
            #telegrambot.send_message(text)

            if self.IS_SELENIUM and self.driver:
                self.driver.quit()
                #self.driver.save_screenshot('screenshot.png')

    def save(self, id, text):
        if text and id:
            self.count = self.count + 1
            telegrambot.send_message(text)
            self.log.append(id)
            filewriter.save_log_file(self.name, self.log)

    def get_time(self):
        return datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    def report(self):
        if self.count > 0:
            print('[%s] %s: 새로운 핫딜 %d개가 등록 되었습니다.' %(self.get_time(), self.name, self.count))
        else:
            print('[%s] %s: 새로운 핫딜이 없습니다.' %(self.get_time(), self.name))

    def extract(self, html):
        pass


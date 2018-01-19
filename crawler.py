#-*- coding: utf-8 -*-

import os
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

    IS_REPORT = True
    IS_PROXY = False
    IS_SELENIUM = False
    SELENIUM_WAIT_TAG = None
    IS_CHROME = False
    PATH_NAME = os.path.dirname(os.path.realpath(__file__))
    PATH_CHROME_DRIVER = os.path.join(PATH_NAME, 'driver/chromedriver')
    PATH_PHANTOMJS_DRIVER = os.path.join(PATH_NAME, 'driver/phantomjs')
    SITE_CONNECT_TIMEOUT = 60

    def __init__(self):
        # 기존 로그 가져오기
        self.name = self.__class__.__name__.lower()
        self.log = filewriter.get_log_file(self.name)
        self.driver = None

    # 사이트 연결
    def connect_with_requests(self):
        if self.IS_PROXY is True:
            proxy_dict = {
                'http': self.proxy_ip,
                'https': self.proxy_ip
            }
        else:
            proxy_dict = None

        response = requests.get(self.url, proxies=proxy_dict)

        if response.status_code != 200:
            raise Exception('Site connect error (status_code:%d)'%response.status_code)

        return response.text

    # 사이트 연결 (셀레니움)
    def connect_with_selenium(self):
        if self.IS_CHROME is True:
            options = webdriver.ChromeOptions()
            if self.IS_PROXY is True:
                options.add_argument('--proxy-server=' + self.proxy_ip)
            self.driver = webdriver.Chrome(executable_path=self.PATH_CHROME_DRIVER, chrome_options=options)
        else:
            if self.IS_PROXY is True:
                args = ['--proxy=' + self.proxy_ip]
            else:
                args = []
            self.driver = webdriver.PhantomJS(executable_path=self.PATH_PHANTOMJS_DRIVER,
                                              service_args=args)

        self.driver.set_page_load_timeout(self.SITE_CONNECT_TIMEOUT)
        self.driver.get(self.url)

        # 요소를 찾을 때까지 대기
        if self.SELENIUM_WAIT_TAG is None:
            element_present = EC.presence_of_element_located((By.TAG_NAME, 'body'))
        else:
            xpath = '//%s[@%s="%s"]'%(self.SELENIUM_WAIT_TAG['tag'], self.SELENIUM_WAIT_TAG['attr'], self.SELENIUM_WAIT_TAG['name'])
            element_present = EC.presence_of_element_located((By.XPATH, xpath))

        WebDriverWait(self.driver, self.SITE_CONNECT_TIMEOUT).until(element_present)
        html = self.driver.page_source
        return html

    def start(self):
        try:
            self.count = 0

            if self.SITE_URL is None:
                raise Exception('Site url is not defined.')

            if self.IS_PROXY is True:
                self.proxy_ip = self.get_proxy_server_ip_list()

            for url in self.SITE_URL:
                self.url = url
                if self.IS_SELENIUM:
                    html = self.connect_with_selenium()
                else:
                    html = self.connect_with_requests()

                self.extract(html)

                if self.IS_REPORT is True:
                    self.report()

            if self.IS_SELENIUM:
                self.driver.quit()

        except Exception as errorMessage:
            text = str('[%s] %s: %s'%(self.get_time(),self.name,errorMessage))
            print(text)
            #telegrambot.send_message(text)

            if self.IS_PROXY is True:
                self.remove_proxy_server_ip_list()

            if self.IS_SELENIUM and self.driver:
                self.driver.quit()

    def save(self, id, text):
        if text and id:
            self.count = self.count + 1
            telegrambot.send_message(text)
            if id not in self.log:
                self.log.append(id)
                filewriter.save_log_file(self.name, self.log)

    def save_file(self, log):
        filewriter.save_log_file(self.name, log)

    def get_time(self):
        return datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

    def report(self):
        if self.count > 0:
            print('[%s] %s: 새로운 핫딜 %d개가 등록 되었습니다.' %(self.get_time(), self.name, self.count))
        else:
            print('[%s] %s: 새로운 핫딜이 없습니다.' %(self.get_time(), self.name))

    def get_proxy_server_ip_list(self):
        self.proxy_list_from_file = filewriter.get_log_file('proxy')

        if len(self.proxy_list_from_file) > 0:
            return self.proxy_list_from_file[0]
        else:
            from proxy import Proxy
            proxy = Proxy()
            proxy.start()
            raise Exception('Proxy server ip is not found.')

    def remove_proxy_server_ip_list(self):
        if self.proxy_list_from_file:
            del self.proxy_list_from_file[0]
            if len(self.proxy_list_from_file) == 0:
                filewriter.save_log_file('proxy', self.proxy_list_from_file)
            else:
                filewriter.save_log_file('proxy', self.proxy_list_from_file)

    def extract(self, html):
        pass
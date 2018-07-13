#-*- coding: utf-8 -*-

import os
import log
import requests
import filewriter

import telegrambot
#from datetime import datetime
#from pytz import timezone
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert

class Crawler:
    PATH_NAME = os.path.dirname(os.path.realpath(__file__))
    PATH_CHROME_DRIVER = os.path.join(PATH_NAME, 'driver/chromedriver')
    PATH_PHANTOMJS_DRIVER = os.path.join(PATH_NAME, 'driver/phantomjs')
    SITE_CONNECT_TIMEOUT = 30

    def __init__(self):
        # 자식 클래스명
        self.name = self.__class__.__name__.lower()
        #self.log = filewriter.get_log_file(self.name)
        self.log = None
        self.driver = None

    def connect(self, site_url=None, is_proxy=False, default_driver='selenium', is_chrome=False):
        try:
            # 사이트 url 체크
            if site_url is None:
                raise Exception('Site url is not defined.')

            # 셀레니움 or 리퀘스츠 연결
            if default_driver == 'selenium':
                if self.connect_with_selenium(site_url=site_url, is_chrome=is_chrome, is_proxy=is_proxy) is False:
                    raise Exception('Site connect fail with selenium.')
                return True
            elif default_driver == 'requests':
                if self.connect_with_requests(site_url=site_url, is_proxy=is_proxy) is False:
                    raise Exception('Site connect fail with requests.')
                return True
            else:
                raise Exception('Wrong default driver.')
        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)
            return False

    # 사이트 연결 (리퀘스츠)
    def connect_with_requests(self, site_url=None, is_proxy=False):
        try:
            proxy_ip = None

            if self.driver is None:
                if is_proxy:
                    proxy_ip = self.get_proxy_server_ip_list()
                    if proxy_ip is False:
                        raise Exception('Proxy server list error.')

                    proxy_dict = {
                        'http': proxy_ip,
                        'https': proxy_ip
                    }
                else:
                    proxy_dict = None

            response = requests.get(site_url, proxies=proxy_dict)

            if response.status_code != 200:
                raise Exception('Site connect error (status_code:%d)' % response.status_code)

            log.logger.info('Connecting site with requests, url:%s, proxy:%s' % (site_url, proxy_ip))

            self.drive = response

            return True
        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)
            return False

    # 사이트 연결 (셀레니움)
    def connect_with_selenium(self, site_url=None, is_chrome=False, is_proxy=False):
        try:
            proxy_ip = None

            if self.driver is not None:
                log.logger.info('Connecting site with selenium, url:%s' % (site_url))
                self.driver.get(site_url)
                return True

            if is_proxy:
                proxy_ip = self.get_proxy_server_ip_list()
                if proxy_ip is False:
                    raise Exception('Proxy server list error.')

            if is_chrome is True:
                options = webdriver.ChromeOptions()
                if is_proxy is True:
                    options.add_argument('--proxy-server=' + proxy_ip)
                self.driver = webdriver.Chrome(executable_path=self.PATH_CHROME_DRIVER, chrome_options=options)
            else:
                if is_proxy is True:
                    args = ['--proxy=' + proxy_ip]
                else:
                    args = []
                self.driver = webdriver.PhantomJS(executable_path=self.PATH_PHANTOMJS_DRIVER,
                                                  service_args=args)

            log.logger.info('Connecting site with selenium, url:%s, proxy:%s' % (site_url, proxy_ip))

            self.driver.set_page_load_timeout(self.SITE_CONNECT_TIMEOUT)
            self.driver.get(site_url)

            return True
        except Exception as e:
            if is_proxy is True:
                self.remove_proxy_server_ip_list()
            self.destroy()
            log.logger.error(e, exc_info=True)
            return False

    # 버튼 클릭
    def selenium_click_by_xpath(self, tag = None, etc=None):
        try:
            xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
            if etc is not None:
                xpath = xpath + etc
            element_present = EC.element_to_be_clickable((By.XPATH, xpath))
            element_found = WebDriverWait(self.driver, 15).until(element_present)
            element_found.click()
            return True
        except Exception as e:
            return False

    # 텍스트 입력
    def selenium_input_text_by_xpath(self, text=None, tag=None, etc=None):
        try:
            xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
            if etc is not None:
                xpath = xpath + etc
            element_present = EC.element_to_be_clickable((By.XPATH, xpath))
            element_found = WebDriverWait(self.driver, 10).until(element_present)
            element_found.send_keys(text)
            return True
        except Exception as e:
            return False

    def selenium_extract_by_xpath(self, tag = None, etc=None):
        try:
            xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
            if etc is not None:
                xpath = xpath + etc
            element_present = EC.visibility_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, self.SITE_CONNECT_TIMEOUT).until(element_present)
            return True
        except Exception as e:
            return False

    def selenium_is_alert_exist(self):
        try:
            alert_element = Alert(self.driver)
            if alert_element:
                alert_element.accept()
                return True
            else:
                return False
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    def selenium_wait_second(self, second=0):
        self.driver.implicitly_wait(second)

    # 프록시 서버 IP 1개 획득
    def get_proxy_server_ip_list(self):
        try:
            proxy_list_from_file = filewriter.get_log_file('proxy')

            if proxy_list_from_file is None or len(proxy_list_from_file) == 0:
                self.request_proxy_server_ip_list()

            if proxy_list_from_file is None or len(proxy_list_from_file) == 0:
                return False
            else:
                return proxy_list_from_file[0]
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    # 프록시 서버 IP 리스트 재수집
    def request_proxy_server_ip_list(self):
        try:
            from proxy import Proxy
            proxy = Proxy()
            proxy.start()

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    # 첫번째 프록시 서버 IP 삭제
    def remove_proxy_server_ip_list(self):
        proxy_list_from_file = filewriter.get_log_file('proxy')

        if proxy_list_from_file:
            del proxy_list_from_file[0]
            if len(proxy_list_from_file) == 0:
                self.request_proxy_server_ip_list()
            else:
                filewriter.save_log_file('proxy', proxy_list_from_file)

    def utf_8_reload(self):
        try:
            import sys
            from six.moves import reload_module
            reload_module(sys)
            sys.setdefaultencoding('utf-8')
            return True
        except:
            return False

    def send_messge_and_save(self, id, text):
        if text and id:
            telegrambot.send_message(text)
            log.logger.info('New hotdeal has just been registerd. (%s)' % (id))
            if id not in self.log:
                self.log.append(id)
                filewriter.save_log_file(self.name, self.log)

    def destroy(self):
        self.driver.quit()
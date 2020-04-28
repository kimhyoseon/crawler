#-*- coding: utf-8 -*-

import os
import log
import pickle
import requests
import filewriter
from time import sleep
from datetime import datetime

import telegrambot
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class Crawler:
    PATH_NAME = os.path.dirname(os.path.realpath(__file__))
    PATH_USER_DATA = os.path.join(PATH_NAME, 'driver/userdata')
    PATH_CHROME_DRIVER = os.path.join(PATH_NAME, 'driver/chromedriver')
    PATH_PHANTOMJS_DRIVER = os.path.join(PATH_NAME, 'driver/phantomjs')
    SITE_CONNECT_TIMEOUT = 30

    def __init__(self):
        # 자식 클래스명
        self.name = self.__class__.__name__.lower()
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

                options.add_argument("--user-data-dir=" + self.PATH_USER_DATA)
                options.add_argument("--headless");
                options.add_argument("--no-sandbox");
                options.add_argument("--disable-gpu");
                options.add_argument("--window-size=1920,1080");
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")

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
                self.driver.set_window_size(1400, 1000)

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
    def selenium_click_by_xpath(self, tag=None, etc=None, index=None, xpath=None, element=None):
        try:
            if element is not None:
                element_found = element
            else:
                if xpath is None:
                    xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
                    if etc is not None:
                        xpath = xpath + etc
                    if index is not None:
                        xpath = '(%s)[%s]' % (xpath, index)

                element_present = EC.element_to_be_clickable((By.XPATH, xpath))
                element_found = WebDriverWait(self.driver, 15).until(element_present)

            element_found.click()
            return True
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    # 텍스트 입력
    def selenium_input_text_by_xpath(self, text=None, tag=None, etc=None, xpath=None, clear=True):
        try:
            if xpath is None:
                xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
                if etc is not None:
                    xpath = xpath + etc
            element_present = EC.element_to_be_clickable((By.XPATH, xpath))
            element_found = WebDriverWait(self.driver, 10).until(element_present)
            if clear is True:
                element_found.clear()
            element_found.send_keys(text)
            return True
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    # 키누름
    def selenium_enterkey_by_xpath(self, tag=None, etc=None, index=None, xpath=None, element=None):
        try:
            if element is not None:
                element_found = element
            else:
                if xpath is None:
                    xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
                    if etc is not None:
                        xpath = xpath + etc
                    if index is not None:
                        xpath = '(%s)[%s]' % (xpath, index)

                element_present = EC.visibility_of_element_located((By.XPATH, xpath))
                element_found = WebDriverWait(self.driver, 15).until(element_present)

            element_found.send_keys(Keys.ENTER)
            return True
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    def selenium_extract_by_xpath(self, tag = None, etc=None, xpath=None):
        try:
            if xpath is None:
                xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
                if etc is not None:
                    xpath = xpath + etc
            element_present = EC.visibility_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, self.SITE_CONNECT_TIMEOUT).until(element_present)
            return True
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    def selenium_exist_by_xpath(self, tag = None, etc=None, xpath=None, second=1):
        try:
            if xpath is None:
                xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
                if etc is not None:
                    xpath = xpath + etc
            element_present = EC.visibility_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, second).until(element_present)
            return True
        except:
            return False

    def selenium_focus_by_xpath(self, tag = None, etc=None, xpath=None, element=None):
        try:
            if element is not None:
                element_found = element
            else:
                if xpath is None:
                    xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
                    if etc is not None:
                        xpath = xpath + etc
                element_present = EC.visibility_of_element_located((By.XPATH, xpath))
                element_found = WebDriverWait(self.driver, 15).until(element_present)

            ActionChains(self.driver).move_to_element(element_found).perform()
            return True
        except:
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

    # 특정 영역이 변경될때까지 기다림 (시작)
    def selenium_wait_change_start_by_xpath(self, tag=None, etc=None):
        try:
            xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
            if etc is not None:
                xpath = xpath + etc
            element_present = EC.element_to_be_clickable((By.XPATH, xpath))
            element_found = WebDriverWait(self.driver, 10).until(element_present)  
               
            return element_found.text
        except Exception as e:
            return False

    # 특정 영역이 변경될때까지 기다림 (끝)
    def selenium_wait_change_end_by_xpath(self, text=None, tag=None, etc=None):
        try:
            xpath = '//%s[@%s="%s"]' % (tag['tag'], tag['attr'], tag['name'])
            if etc is not None:
                xpath = xpath + etc
            element_present = EC.element_to_be_clickable((By.XPATH, xpath))
            element_found = WebDriverWait(self.driver, 10).until(element_present)  
            
            for i in range(0, 10):                 
                if element_found.text != text:                                    
                    return True
                sleep(0.2)

            return False
        except Exception as e:
            return False
    

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

    # 당일 성공로그
    def record_success_log(self):

        try:
            if self.is_record_call is True:
                return False
        except:
            self.is_record_call = True

        # print('called')

        log_success = filewriter.get_log_file('success', is_json=True)
        date = datetime.now().strftime('%Y_%m_%d')
        try:
            if not log_success or not log_success[date]:
                # print('new')
                log_success[date] = {};
        except:
            log_success[date] = {};

        try:
            if log_success[date][self.name]:
                return False
        except:
            log_success[date][self.name] = 1

        log_success[date][self.name] = 1

        # print('recorded')

        filewriter.save_log_file('success', log_success)

    def utf_8_reload(self):
        try:
            import sys
            from six.moves import reload_module
            reload_module(sys)
            sys.setdefaultencoding('utf-8')
            return True
        except:
            return False

    def send_messge_and_save(self, id=None, text=None, bot_name=None):
        if text and id and bot_name:
            if id not in self.log:
                self.log.append(id)
                filewriter.save_log_file(self.name, self.log)
                log.logger.info('New hotdeal has just been registerd. (%s)' % (id))
                telegrambot.send_message(text, bot_name)

    def destroy(self):
        try:
            self.driver = None
            self.driver.quit()
        except:
            return False

    def set_cookie(self):
        try:

            pickle.dump(self.driver.get_cookies(), open(self.name + "_cookies.pkl", "wb"))
        except:
            return False

    def get_cookie(self):
        try:
            cookies = pickle.load(open(self.name + "_cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except:
            return False

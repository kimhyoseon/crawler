#-*- coding: utf-8 -*-

import os
import log
import filewriter
import telegrambot
from time import sleep
from crawler2 import Crawler
from bs4 import BeautifulSoup

class SmartstoreOrderJshk(Crawler):

    DETAIL_URL = 'http://sell.storefarm.naver.com'

    def start(self):
        try:
            self.login()

            self.scan_page()

            self.destroy()
            exit()

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            sleep(5)

            self.remove_layer()


            # -- 문의체크 --
            try:
                ask = self.driver.find_elements_by_xpath('//*[@name="inquery"]/div/div[2]/ul/li')

                if ask:
                    is_ask = False
                    for ask_li in ask:
                        ask_number = ask_li.find_element_by_xpath('.//p[@class="text-number"]').text
                        ask_number = int(ask_number)
                        if ask_number > 0:
                            is_ask = True

                    if is_ask == True:
                        telegrambot.send_message('정성한끼 고객이 상담을 기다리고 있습니다.', 'jshk')
            except:
                pass


            # -- 신규주문 페이지로 이동 --

            if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'orddel.new'}) is False:
                raise Exception('selenium_click_by_xpath fail. orddel.new')

            sleep(10)

            self.remove_layer()

            # 주문 데이터 가져오기 iframe으로 변경
            self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))
            list = self.driver.find_element_by_xpath('//*[@id="__app_root__"]/div/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[1]/table').find_elements_by_xpath('.//tbody/tr')

            order_list = {}

            for i, li in enumerate(list):
                try:
                    if li:
                        soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                        tds = soup_order_info.find_all('td')

                        if tds:
                            item_option = tds[16].getText().strip()
                            item_amount = tds[18].getText().strip()
                            item_amount = int(item_amount)
                            destination = tds[40].getText()

                            if item_option not in order_list:
                                order_list[item_option] = item_amount
                            else:
                                order_list[item_option] = order_list[item_option] + item_amount

                            # 제주도인 경우 알림
                            if destination in '제주특별자치도':
                                telegrambot.send_message('제주도 주문건을 확인해주세요.', 'jshk')


                except Exception as e:
                    log.logger.error(e, exc_info=True)
                    self.destroy()
                    exit()


            # -- 발송대기 주문 페이지로 이동 --

            if self.selenium_click_by_xpath(xpath='//*[@id="__app_root__"]/div/div[2]/div[1]/div/div[2]/ul/li[4]/div/a[1]') is False:
                raise Exception('selenium_click_by_xpath fail. orddel.wait')

            sleep(5)

            # 주문 데이터 가져오기 iframe으로 변경
            list = self.driver.find_element_by_xpath('//*[@id="__app_root__"]/div/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[1]/table').find_elements_by_xpath('.//tbody/tr')

            for i, li in enumerate(list):
                try:
                    if li:
                        soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                        tds = soup_order_info.find_all('td')

                        if tds:
                            item_option = tds[16].getText().strip()
                            item_amount = tds[18].getText().strip()
                            item_amount = int(item_amount)

                            if item_option not in order_list:
                                order_list[item_option] = item_amount
                            else:
                                order_list[item_option] = order_list[item_option] + item_amount

                except Exception as e:
                    log.logger.error(e, exc_info=True)
                    self.destroy()
                    exit()


            # -- 데이터 저장 --
            if dict:
                filewriter.save_log_file('jshk_order_data', order_list)
                print(order_list)

            return True
        except Exception as e:
            # self.driver.save_screenshot('smartstore_screenshot.png')
            log.logger.error(e, exc_info=True)
            self.destroy()
            exit()

        return False

    def remove_layer(self):
        try:
            # 레이어가 있다면 닫기 (에스크로, 임시)
            try:
                if self.selenium_exist_by_xpath(xpath='/html/body/div[1]/div/div/div[3]/div/div/label') is True:
                    self.selenium_click_by_xpath(xpath='/html/body/div[1]/div/div/div[3]/div/div/label')
            except:
                pass

            try:
                if self.selenium_exist_by_xpath(xpath='/html/body/div[1]/div/div/div[3]/div/div/label/input') is True:
                    self.selenium_click_by_xpath(xpath='/html/body/div[1]/div/div/div[3]/div/div/label/input')
            except:
                pass

            # 레이어가 있다면 닫기
            try:
                if self.selenium_exist_by_xpath(
                        tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'}) is True:
                    self.selenium_click_by_xpath(
                        tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'})
            except:
                pass

            # 레이어가 있다면 닫기
            try:
                if self.selenium_exist_by_xpath(
                        tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.blockPopupNoticeToday()'}) is True:
                    self.selenium_click_by_xpath(
                        tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.blockPopupNoticeToday()'})
            except:
                pass

            # 채널 레이어 닫기
            try:
                if self.selenium_exist_by_xpath(
                        tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'})
                    sleep(1)
            except:
                pass

            sleep(1)

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def login(self):
        try:
            self.PATH_USER_DATA = os.path.join(self.PATH_NAME, 'driver/userdata_naver_jshk')

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            # 계정정보 가져오기
            account_data = filewriter.get_log_file('naver_account_jshk')

            if not account_data[2]:
                self.get_cookie()

                if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                    raise Exception('site connect fail')

                # 로그인 여부 체크
                try:
                    if self.selenium_extract_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'orddel.new'}) is True:
                        log.logger.info('Alreday logined.')
                        return True
                except:
                    pass

            if account_data:
                # self.driver.save_screenshot('smartstore_screenshot.png')

                if not account_data[2]:
                    # 로그인 페이지로 이동
                    if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'main.sellerlogin'}) is False:
                        raise Exception('selenium_click_by_xpath fail. submit')

                    # self.driver.save_screenshot('smartstore_screenshot.png')

                    if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'login.nidlogin'}) is False:
                        raise Exception('site connect nidlogin click fail')

                    # print(self.driver.current_url)
                    # elem = self.driver.find_element_by_xpath("//*")
                    # source_code = elem.get_attribute("outerHTML")
                    # print(source_code)

                    if self.selenium_extract_by_xpath(tag={'tag': 'input', 'attr': 'name', 'name': 'id'}) is False:
                        raise Exception('selenium_extract_by_xpath ID input can not founded.')

                    # 아이디 입력
                    if self.selenium_input_text_by_xpath(text=account_data[0], tag={'tag': 'input', 'attr': 'name', 'name': 'id'}) is False:
                        raise Exception('selenium_input_text_by_xpath fail. username')

                    # 비번 입력
                    if self.selenium_input_text_by_xpath(text=account_data[1], tag={'tag': 'input', 'attr': 'name', 'name': 'pw'}) is False:
                        raise Exception('selenium_input_text_by_xpath fail. password')
                else:
                    # --- 임시로 일회용로그인으로 ---
                    if self.connect(site_url='https://nid.naver.com/nidlogin.login?mode=number', is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                        raise Exception('site connect fail')

                    if self.selenium_extract_by_xpath(tag={'tag': 'input', 'attr': 'name', 'name': 'key'}) is False:
                        raise Exception('selenium_extract_by_xpath ID input can not founded.')

                    # 아이디 입력
                    if self.selenium_input_text_by_xpath(text=account_data[2], tag={'tag': 'input', 'attr': 'name', 'name': 'key'}) is False:
                        raise Exception('selenium_input_text_by_xpath fail. username')

                # 로그인 유지
                if self.selenium_click_by_xpath(xpath='//*[@id="label_login_chk"]') is False:
                    raise Exception('selenium_click_by_xpath fail. login_chk')

                # 로그인 버튼 클릭
                if self.selenium_click_by_xpath(tag={'tag': 'input', 'attr': 'type', 'name': 'submit'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                try:
                    # 기기등록 함
                    if self.selenium_exist_by_xpath(xpath='//*[@id="frmNIDLogin"]/fieldset/span[1]/a') is True:
                        self.selenium_click_by_xpath(xpath='//*[@id="frmNIDLogin"]/fieldset/span[1]/a')

                    # 로그인 상태유지
                    if self.selenium_exist_by_xpath(xpath='//*[@id="login_maintain"]/span[1]/a') is True:
                        if self.selenium_click_by_xpath(xpath='//*[@id="login_maintain"]/span[1]/a') is False:
                            raise Exception('selenium_click_by_xpath fail. submit')
                except:
                    pass

                log.logger.info('login success')
                self.set_cookie()

                sleep(2)

                self.destroy()
                exit()

                return True
        except Exception as e:
            log.logger.error(e, exc_info=True)
            self.destroy()
            exit()

        return False

if __name__ == "__main__":
    jshk = SmartstoreOrderJshk()
    jshk.utf_8_reload()
    jshk.start()

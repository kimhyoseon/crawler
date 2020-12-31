#-*- coding: utf-8 -*-

import os

import pymysql

import log
import filewriter
import telegrambot
import argparse
from time import sleep
from crawler2 import Crawler
from bs4 import BeautifulSoup

class SmartstoreOrderJshk(Crawler):

    DETAIL_URL = 'http://sell.storefarm.naver.com'

    def start(self):
        try:
            # 신규, 대기 중 어떤 것을 수집할지 선택
            parser = argparse.ArgumentParser()

            parser.add_argument(
                '--type',
                type=str,
                default='old',
                choices=['new', 'old'],
                help='new or old',
            )

            args = parser.parse_args()
            self.type = args.type

            self.channels = ['스마트스토어쿠힛', '스마트스토어쿠힛마트', '스마트스토어으아니', '스마트스토어우렁청년']

            self.login()

            self.select_channel()

            # self.scan_page()

            log.logger.info('order_jshk_completed!')

            if self.type != 'old':
                self.destroy()
                exit()

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            sleep(5)

            self.remove_layer()

            # -- 신규주문 페이지로 이동 --

            order_list = {}

            # mysql
            self.mysql = filewriter.get_log_file('mysql')

            # MySQL Connection 연결
            conn = pymysql.connect(host=self.mysql[0], port=3306, db=self.mysql[1], user=self.mysql[2], password=self.mysql[3], charset='utf8')

            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()

            if self.type == 'new':
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

                if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'orddel.new'}) is False:
                    raise Exception('selenium_click_by_xpath fail. orddel.new')

                log.logger.info('Move to new 10 sec.')

                sleep(10)

                self.remove_layer()

                # 주문 데이터 가져오기 iframe으로 변경
                self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))
                list = self.driver.find_element_by_xpath('//*[@id="__app_root__"]/div/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[1]/table').find_elements_by_xpath('.//tbody/tr')

                for i, li in enumerate(list):
                    try:
                        if li:
                            soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                            tds = soup_order_info.find_all('td')

                            if tds:
                                item_option = tds[17].getText().strip()
                                item_amount = tds[19].getText().strip()
                                item_amount = int(item_amount)
                                # destination = tds[41].getText()

                                # print(item_option)
                                # print(item_amount)
                                # exit()

                                log.logger.info(item_option)

                                if item_option not in order_list:
                                    order_list[item_option] = item_amount
                                else:
                                    order_list[item_option] = order_list[item_option] + item_amount

                                # 제주도인 경우 알림
                                # if destination in '제주특별자치도':
                                #     telegrambot.send_message('제주도 주문건을 확인해주세요!.', 'jshk')


                    except Exception as e:
                        log.logger.error(e, exc_info=True)
                        self.destroy()
                        exit()

                # -- 데이터 저장 --
                if dict:
                    filename = 'jshk_order_data_' + self.type
                    filewriter.save_log_file(filename, order_list)
                    print(order_list)

                # 100개 넘는지 체크

                # 기존 주문
                sql = "SELECT * FROM smartstore_order_hanki_wait"
                curs.execute(sql)

                # 데이타 Fetch
                rows = curs.fetchall()
                old_dict = {}

                jshk_notice = filewriter.get_log_file('jshk_notice')

                if len(rows) > 0:
                    for row in rows:
                        options = row[0].split(' / ')
                        date = options[0]
                        amount = int(options[1].split('개')[0][-1]) * int(row[1])

                        # print('기존주문')
                        # print(date)
                        # print(amount)

                        if date in old_dict:
                            old_dict[date] = old_dict[date] + amount
                        else:
                            old_dict[date] = amount

                #  새 주문
                if len(order_list) > 0:
                    for key, value in order_list.items():
                        options = key.split(' / ')
                        date = options[0]
                        amount = int(options[1].split('개')[0][-1]) * int(value)

                        # print('새주문')
                        # print(date)
                        # print(amount)

                        if date in old_dict:
                            old_dict[date] = old_dict[date] + amount
                        else:
                            old_dict[date] = amount

                if len(old_dict) > 0:
                    for key, value in old_dict.items():
                        if value > 110:
                            if key not in jshk_notice:
                                jshk_notice.append(key)
                                telegrambot.send_message('[%s] %d개 (주문제한필요)' % (key, value), 'jshk')
                                filewriter.save_log_file('jshk_notice', jshk_notice)

                # print(old_dict)
                # conn.close()
                # exit()

            elif self.type == 'old':

                if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'orddel.wait'}) is False:
                    raise Exception('selenium_click_by_xpath fail. orddel.wait')

                log.logger.info('Move to wait 5 sec.')
                sleep(5)

                # 주문 데이터 가져오기 iframe으로 변경
                self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))
                log.logger.info('switch to frame completed')

                sleep(2)
                log.logger.info('click select list')

                # 500개씩보기
                if self.selenium_click_by_xpath(xpath='//*[@id="__app_root__"]/div/div[2]/div[3]/div[1]/div/div[2]') is False:
                    raise Exception('selenium_click_by_xpath fail. select list')
                sleep(2)
                if self.selenium_click_by_xpath(tag={'tag': 'option', 'attr': 'value', 'name': '500'}) is False:
                    raise Exception('selenium_click_by_xpath fail. option 500')

                log.logger.info('Wait list 5 sec.')
                sleep(5)

                log.logger.info('list loaded')

                # self.remove_layer()

                # log.logger.info('----')
                # self.destroy()
                # exit()

                list = self.driver.find_element_by_xpath('//*[@id="__app_root__"]/div/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[1]/table').find_elements_by_xpath('.//tbody/tr')

                for i, li in enumerate(list):
                    try:
                        if li:
                            soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                            tds = soup_order_info.find_all('td')

                            if tds:
                                item_option = tds[17].getText().strip()
                                item_amount = tds[19].getText().strip()
                                item_amount = int(item_amount)

                                log.logger.info(item_option)

                                if item_option not in order_list:
                                    order_list[item_option] = item_amount
                                else:
                                    order_list[item_option] = order_list[item_option] + item_amount

                    except Exception as e:
                        log.logger.error(e, exc_info=True)
                        self.destroy()
                        exit()

                # -- 데이터 저장 (mysql) --
                if len(order_list) > 0:
                    # DB 데이터 모두 삭제
                    sql = "DELETE FROM smartstore_order_hanki_wait;"
                    curs.execute(sql)
                    conn.commit()

                    # loop
                    for key, value in order_list.items():
                        sql = "INSERT INTO smartstore_order_hanki_wait (opt, amount) VALUES ('%s', '%s')" % (key, value)
                        # print(sql)
                        curs.execute(sql)
                        conn.commit()

            conn.close()

            return True
        except Exception as e:
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
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'})
                    sleep(1)
            except:
                pass

            # 신규 상점 레이어 닫기
            try:
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'})
                    sleep(1)
            except:
                pass

            try:
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'})
                    sleep(1)
            except:
                pass

            sleep(1)

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def login(self):
        try:
            self.PATH_USER_DATA = os.path.join(self.PATH_NAME, 'driver/userdata_naver')

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            self.get_cookie()

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            log.logger.info(self.driver.execute_script("return navigator.userAgent;"))

            # 로그인 여부 체크
            try:
                if self.selenium_extract_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'orddel.new'}) is True:
                    log.logger.info('Alreday logined.')
                    return True
                else:
                    log.logger.info('Not logined.')
            except:
                pass

            # aws에서 네이버 로그인 안되는 이슈 있음...

            # 계정정보 가져오기
            account_data = filewriter.get_log_file('naver_account_jshk')

            if account_data:
                # self.driver.save_screenshot('smartstore_screenshot.png')

                # 로그인 페이지로 이동
                if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'main.sellerlogin'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                sleep(3)

                if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'login.nidlogin'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                # if self.connect(site_url='http://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fsell.smartstore.naver.com%2F%23%2FnaverLoginCallback%3Furl%3Dhttps%253A%252F%252Fsell.smartstore.naver.com%252F%2523', is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                #     raise Exception('login page connect fail')

                sleep(3)

                # self.driver.save_screenshot('smartstore_login_screenshot.png')


                if self.selenium_extract_by_xpath(tag={'tag': 'input', 'attr': 'name', 'name': 'id'}) is False:
                    raise Exception('selenium_extract_by_xpath fail.')

                # 아이디 입력
                if self.selenium_input_text_by_xpath(text=account_data[0], tag={'tag': 'input', 'attr': 'name', 'name': 'id'}) is False:
                    raise Exception('selenium_input_text_by_xpath fail. username')

                # 비번 입력
                if self.selenium_input_text_by_xpath(text=account_data[1], tag={'tag': 'input', 'attr': 'name', 'name': 'pw'}) is False:
                    raise Exception('selenium_input_text_by_xpath fail. password')

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

                return True
        except Exception as e:
            # 스크린샷 base64
            log.logger.info('smartstore_login_screenshot')
            self.save_screenshot_jpg(filename='smartstore_login_screenshot')
            # self.driver.save_screenshot('smartstore_login_screenshot.png')
            log.logger.error(e, exc_info=True)
            self.destroy()
            exit()

        return False
    # def login(self):
    #     try:
    #         self.PATH_USER_DATA = os.path.join(self.PATH_NAME, 'driver/userdata_naver_jshk')
    #
    #         if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
    #             raise Exception('site connect fail')
    #
    #         self.get_cookie()
    #
    #         # 계정정보 가져오기
    #         account_data = filewriter.get_log_file('naver_account_jshk')
    #
    #         try:
    #             temp_login = account_data[2]
    #         except IndexError:
    #             temp_login = None
    #
    #         if not temp_login:
    #             if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
    #                 raise Exception('site connect fail')
    #
    #             # 로그인 여부 체크
    #             try:
    #                 if self.selenium_extract_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'orddel.new'}) is True:
    #                     log.logger.info('Alreday logined.')
    #                     return True
    #             except:
    #                 pass
    #
    #         log.logger.info('Not logined.')
    #
    #         if account_data:
    #             if not temp_login:
    #                 # 로그인 페이지로 이동
    #                 if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'main.sellerlogin'}) is False:
    #                     raise Exception('selenium_click_by_xpath fail. submit')
    #
    #                 sleep(1)
    #
    #                 if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'login.nidlogin'}) is False:
    #                     raise Exception('site connect nidlogin click fail')
    #
    #                 sleep(3)
    #
    #                 if self.selenium_extract_by_xpath(tag={'tag': 'input', 'attr': 'name', 'name': 'id'}) is False:
    #                     raise Exception('selenium_extract_by_xpath ID input can not founded.')
    #
    #                 # 아이디 입력
    #                 if self.selenium_input_text_by_xpath(text=account_data[0], tag={'tag': 'input', 'attr': 'name', 'name': 'id'}) is False:
    #                     raise Exception('selenium_input_text_by_xpath fail. username')
    #
    #                 # 비번 입력
    #                 if self.selenium_input_text_by_xpath(text=account_data[1], tag={'tag': 'input', 'attr': 'name', 'name': 'pw'}) is False:
    #                     raise Exception('selenium_input_text_by_xpath fail. password')
    #             else:
    #                 # --- 임시로 일회용로그인으로 ---
    #                 if self.connect(site_url='https://nid.naver.com/nidlogin.login?mode=number', is_proxy=False, default_driver='selenium', is_chrome=True) is False:
    #                     raise Exception('site connect fail')
    #
    #                 if self.selenium_extract_by_xpath(tag={'tag': 'input', 'attr': 'name', 'name': 'key'}) is False:
    #                     raise Exception('selenium_extract_by_xpath ID input can not founded.')
    #
    #                 # 아이디 입력
    #                 if self.selenium_input_text_by_xpath(text=temp_login, tag={'tag': 'input', 'attr': 'name', 'name': 'key'}) is False:
    #                     raise Exception('selenium_input_text_by_xpath fail. username')
    #
    #             # 로그인 유지
    #             if self.selenium_click_by_xpath(xpath='//*[@id="label_login_chk"]') is False:
    #                 raise Exception('selenium_click_by_xpath fail. login_chk')
    #
    #             # 로그인 버튼 클릭
    #             if self.selenium_click_by_xpath(tag={'tag': 'input', 'attr': 'type', 'name': 'submit'}) is False:
    #                 raise Exception('selenium_click_by_xpath fail. submit')
    #
    #             try:
    #                 # 기기등록 함
    #                 if self.selenium_exist_by_xpath(xpath='//*[@id="frmNIDLogin"]/fieldset/span[1]/a') is True:
    #                     self.selenium_click_by_xpath(xpath='//*[@id="frmNIDLogin"]/fieldset/span[1]/a')
    #
    #                 # 로그인 상태유지
    #                 if self.selenium_exist_by_xpath(xpath='//*[@id="login_maintain"]/span[1]/a') is True:
    #                     if self.selenium_click_by_xpath(xpath='//*[@id="login_maintain"]/span[1]/a') is False:
    #                         raise Exception('selenium_click_by_xpath fail. submit')
    #             except:
    #                 pass
    #
    #             log.logger.info('login success')
    #             self.set_cookie()
    #
    #             return True
    #     except Exception as e:
    #         log.logger.error(e, exc_info=True)
    #         self.destroy()
    #         exit()
    #
    #     return False

    def select_channel(self):
        try:
            sleep(3)

            self.driver.switch_to.default_content()

            self.remove_layer()

            sleep(2)

            # 채널선택버튼 클릭
            if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'ui-sref', 'name': 'work.channel-select'}) is False:
                raise Exception('selenium_click_by_xpath fail. channel-select')

            sleep(1)

            # 현재 상점명 가져오기
            channel_current = self.driver.find_element_by_xpath('//div[contains(@class,"search-area")]').find_element_by_xpath('.//span[@class="text-title"]').text
            channel_current = channel_current.strip()

            # 현재 상점이 진행 전이라면 진행
            if channel_current not in self.channels:
                self.channels.append(channel_current)
                log.logger.info(channel_current)
                self.remove_layer()
                self.scan_page()
                self.select_channel()

            # 현재 상점이 진행 후라면 채널 변경
            channel_list = self.driver.find_elements_by_xpath('//li[contains(@ng-repeat,"vm.channelList")]')

            for li in channel_list:
                try:
                    if li:
                        channel_name = li.find_element_by_xpath('.//span[@class="text-title"]').text

                        # 선택할 상점이 진행 전이라면 진행
                        if channel_name not in self.channels:
                            self.channels.append(channel_name)
                            log.logger.info(channel_name)
                            li.find_element_by_xpath('.//label').click()
                            self.scan_page()
                            self.select_channel()
                            return True
                except:
                    pass

        except Exception as e:
            self.driver.save_screenshot('smartstore_screenshot.png')
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    jshk = SmartstoreOrderJshk()
    jshk.utf_8_reload()
    jshk.start()

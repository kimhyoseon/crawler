#-*- coding: utf-8 -*-

import os
import log
import filewriter
import xmltodict
import requests
from time import sleep
from pytz import timezone
from crawler2 import Crawler
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup

class SmartstoreTalktalk(Crawler):

    DETAIL_URL = 'http://sell.storefarm.naver.com'

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)
            self.channels = ['스마트스토어정성한끼', '스마트스토어쿠힛마트']

            self.login()

            self.select_channel()

            self.destroy()
            exit()

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            sleep(5)

            self.remove_layer()

            # 신규주문 페이지로 이동
            if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'orddel.new'}) is False:
                raise Exception('selenium_click_by_xpath fail. orddel.new')

            sleep(10)

            self.remove_layer()

            # 주문 데이터 가져오기 iframe으로 변경
            self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))
            list_id = self.driver.find_element_by_xpath('//*[@id="__app_root__"]/div/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[2]/div/div[1]/table').find_elements_by_xpath('.//tbody/tr')
            list = self.driver.find_element_by_xpath('//*[@id="__app_root__"]/div/div[2]/div[3]/div[4]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[1]/table').find_elements_by_xpath('.//tbody/tr')

            # self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))
            # list = self.driver.find_element_by_xpath('//*[@id="gridbox"]/div[2]/div[2]/table').find_elements_by_xpath('.//tbody/tr')

            window_before = self.driver.window_handles[0]

            # for index, li in enumerate(list):
            #     try:
            #         if li:
            #             soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
            #             tds = soup_order_info.find_all('td')
            #
            #             if tds:
            #                 item_order_id = tds[1].getText().strip()
            #                 order_id = tds[2].getText().strip()
            #                 item_id = tds[17].getText().strip()
            #                 item_name = tds[18].getText().strip()
            #                 item_kind = tds[19].getText().strip()
            #                 item_option = tds[20].getText().strip()
            #                 item_amount = tds[22].getText().strip()
            #                 destination = tds[44].getText().strip()

            for i, li in enumerate(list):
                try:
                    if li:
                        soup_order_info_id = BeautifulSoup(list_id[i].get_attribute('innerHTML'), 'html.parser')
                        tds_id = soup_order_info_id.find_all('td')
                        soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                        tds = soup_order_info.find_all('td')

                        if tds:
                            item_order_id = tds_id[1].getText().strip()
                            buyer = tds[8].getText().strip()
                            item_id = tds[13].getText()
                            item_name = tds[14].getText()
                            item_kind = tds[15].getText()
                            item_option = tds[16].getText().strip()
                            item_amount = tds[18].getText().strip()
                            destination = tds[40].getText()

                            # print(item_order_id)
                            # print(item_id)
                            # print(item_option)
                            # print(item_amount)
                            # print(item_kind)
                            # print(item_name)
                            # print(buyer)
                            # exit()

                            # 테스트
                            # if buyer != '서미숙':
                            #     continue

                            # 수동 발송제한
                            # 2019-06-10 샴푸브러쉬 품절
                            # if item_id in ['4423398036']:
                                # continue

                            # 추가상품 발송제한
                            if item_kind == '추가구성상품':
                                continue

                            # 발송내역에 없는지 확인
                            if not item_order_id or item_order_id in self.log:
                                continue

                            if item_option:
                                item_name = item_name + ' (' + item_option + ')'

                            if item_amount:
                                item_name = item_name + ' ' + item_amount + '개'

                            talktalklink = li.find_element_by_xpath('.//td[6]/div/a')
                            # talktalklink = li.find_element_by_xpath('.//td[10]/a')

                            # 톡톡하기 클릭
                            talktalklink.click()

                            sleep(3)

                            # 톡톡창으로 focus
                            window_after = self.driver.window_handles[1]
                            self.driver.switch_to.window(window_after)

                            # 레이어가 있다면 닫기
                            try:
                                if self.selenium_exist_by_xpath(xpath='//button[contains(@class,"btn_negative")]') is True:
                                    self.selenium_click_by_xpath(xpath='//button[contains(@class,"btn_negative")]')
                            except:
                                pass

                            # 메세지 생성
                            message = self.get_delevery_message(item_id=item_id, item_name=item_name, destination=destination)

                            if not message:
                                raise Exception('messageText genarating fail.')

                            # 메시지 입력
                            self.driver.execute_script('document.getElementById("partner_chat_write").value = "' + message + '";')
                            if self.selenium_input_text_by_xpath(text=' ', xpath='//*[@id="partner_chat_write"]', clear=False) is False:
                                raise Exception('selenium_input_text_by_xpath fail. chat_write')

                            # exit()

                            sleep(1)

                            # 메세지 전송
                            if self.selenium_click_by_xpath(xpath='//*[@id="chat_wrap"]/div/div[1]/div/div[3]/div[2]/button') is False:
                                raise Exception('selenium_click_by_xpath fail. submit')

                            sleep(2)

                            message = message.replace('\\n', '\n')

                            self.log = filewriter.slice_json_by_max_len(self.log, max_len=1000)

                            self.send_messge_and_save(item_order_id, message, 'kuhit')
                            # telegrambot.send_message(message, 'kuhit')

                            # 창 닫고 복귀
                            self.driver.close()
                            self.driver.switch_to.window(window_before)
                            self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))

                            # 테스트로그
                            # print(buyer)
                            # print(item_order_id)
                            # print(item_id)
                            # print(item_name)
                            # print(destination)
                            # print(tds)
                            # for idx, td in enumerate(tds):
                            #     print(idx, td.getText())

                except Exception as e:
                    log.logger.error(e, exc_info=True)
                    self.destroy()
                    exit()

            return True
        except Exception as e:
            self.driver.save_screenshot('smartstore_screenshot.png')
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
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'})
            except:
                pass

            # 레이어가 있다면 닫기
            try:
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.blockPopupNoticeToday()'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.blockPopupNoticeToday()'})
            except:
                pass

            # 채널 레이어 닫기
            try:
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.closeModal()'})
                    sleep(1)
            except:
                pass

            sleep(1)

        except Exception as e:
            log.logger.error(e, exc_info=True)

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

    def get_delevery_message(self, item_id, item_name, destination):
        try:
            delevery_date, destination_date = self.get_delevery_date(item_id=item_id, destination=destination)

            if not delevery_date or not destination_date:
                return False

            delevery_message = ''
            delevery_message += '[배송 안내]'
            delevery_message += '\\n\\n'
            delevery_message += '안녕하세요^^'
            delevery_message += '\\n\\n'
            delevery_message += '쿠힛에서 ​구매하신 '
            delevery_message += '[' + item_name + ']'
            delevery_message += ' 제품의 배송 일정 안내 드립니다~'
            delevery_message += '\\n\\n'
            delevery_message += '배송출발 : '
            delevery_message += delevery_date
            delevery_message += '\\n'
            delevery_message += '도착예정 : '
            delevery_message += destination_date
            delevery_message += '\\n\\n'
            delevery_message += '최대한 빨리 고객님에게 제품이 전달되도록 최선을 다하겠습니다.'
            delevery_message += '\\n\\n'
            delevery_message += '주문해주셔서 감사합니다^^'
            delevery_message += '\\n\\n'
            delevery_message += '※ 수령 위치 또는 택배사의 사정에 따라 1~2일정도 더 소요될 수 있습니다.​'

            log.logger.info(delevery_message)

            return delevery_message

        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    def get_delevery_date(self, item_id=None, destination=None):
        try:
            week_text = ['월', '화', '수', '목', '금', '토', '일']

            # 발송 상세 시간
            start_hour = '오후 7시'

            # 상품별 발송 제한시간 (기본)
            limit_hour = 16

            # 배송일 (오늘)
            delevery_date = datetime.now(timezone('Asia/Seoul'))

            # 짐볼, 요가매트 (오후 2시)
            if item_id in ['4324723046','4529428871']:
                limit_hour = 13
                start_hour = '오후 7시'
            # 폼롤러 (오후 3시)
            elif item_id in ['4318623001']:
                limit_hour = 14
                start_hour = '오후 7시'
            # 그 외 집배송
            # else:
                # 오후 배송일 (기사님이 오후에 오시는 날)
                # if delevery_date.strftime('%Y%m%d') in ['20190802']:
                #     limit_hour = 19

                # 휴가 배송일
                # if delevery_date.strftime('%Y%m%d') in ['20190722']:
                #     limit_hour = 14
                #     start_hour = '오후 6시'

            # 시간이 지났다면 익일발송
            if delevery_date.hour >= limit_hour:
                delevery_date = delevery_date + timedelta(days=1)

            reddays = self.get_reddays()

            # 추석연휴
            reddays.append('20200122')
            reddays.append('20200123')
            reddays.append('20200124')
            reddays.append('20200125')
            reddays.append('20200126')
            reddays.append('20200127')

            # 휴일이라면 휴일이 아닐때까지 1일씩 미룬다 /// 토, 일은 배송안하는 날
            while 1:
                if delevery_date.weekday() in [5, 6] or delevery_date.strftime('%Y%m%d') in reddays:
                    delevery_date = delevery_date + timedelta(days=1)
                else:
                    break

            # 기사님이 안오거나 사정 상 배송이 어려운 날인 경우 +1 처리
            # if item_id not in ['4324723046', '4529428871','4318623001']:
            #     while 1:
            #         if delevery_date.strftime('%Y%m%d') in ['20190801']:
            #             delevery_date = delevery_date + timedelta(days=1)
            #         else:
            #             break

            # 도착예정일
            destination_date = delevery_date + timedelta(days=1)

            # 제주도인 경우 +1
            if destination in '제주특별자치도':
                destination_date = delevery_date + timedelta(days=1)

            # 추석연휴는 도착일에서 제거
            reddays.remove('20200122')
            # reddays.remove('20190910')
            # reddays.remove('20190911')

            # 휴일이라면 휴일이 아닐때까지 1일씩 미룬다
            while 1:
                if destination_date.weekday() in [6] or destination_date.strftime('%Y%m%d') in reddays:
                    destination_date = destination_date + timedelta(days=1)
                else:
                    break

            delevery_date = str(delevery_date.year) + '년 ' + str(delevery_date.month) + '월 ' + str(delevery_date.day) + '일 (' + week_text[delevery_date.weekday()] + ') ' + start_hour
            destination_date = str(destination_date.year) + '년 ' + str(destination_date.month) + '월 ' + str(destination_date.day) + '일 (' + week_text[destination_date.weekday()] + ')'

            # print(delevery_date)
            # print(destination_date)

            return delevery_date, destination_date
        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    def get_reddays(self):
        try:
            urls = []
            reddays = []

            #  공휴일 수동 입력
            # reddays.append('20190501')

            service_key = 'N5FupqoyFxqwcuyheudquznCCBi6IjOliKOT5DpHhTmomTde1WgpW4EkXwCZQ777CmYfcBbtgf%2FBuUqFwbEg2Q%3D%3D'
            now = datetime.now(timezone('Asia/Seoul'))
            next = now + relativedelta(months=1)
            this_year = str(now.year)
            this_month = str('{:02d}'.format(now.month))
            urls.append("http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo?serviceKey="+service_key+"&solYear="+this_year+"&solMonth="+this_month)
            next_year = str(next.year)
            next_month = str('{:02d}'.format(next.month))
            urls.append("http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo?serviceKey=" + service_key + "&solYear=" + next_year + "&solMonth=" + next_month)
            # print(urls)

            for url in urls:
                # file = urllib2.urlopen(url)
                # data = file.read()
                # file.close()
                response = requests.get(url)

                if response.status_code != 200:
                    continue

                data = xmltodict.parse(response.content)

                if data and data['response']['body']['items']:
                    for key, item in data['response']['body']['items'].items():
                        if item and isinstance(item, list) is False:
                            item = [item]

                        for it in item:
                            if it and isinstance(it, dict) is True:
                                try:
                                    if it['isHoliday'] == 'N':
                                        continue
                                except:
                                    pass
                                reddays.append(it['locdate'])

            log.logger.info(','.join(reddays))
            return reddays
        except Exception as e:
            log.logger.error(e, exc_info=True)

        return reddays

    def login(self):
        try:
            self.PATH_USER_DATA = os.path.join(self.PATH_NAME, 'driver/userdata_naver')

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

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

            # 계정정보 가져오기
            account_data = filewriter.get_log_file('naver_account')

            if account_data:
                # 로그인 페이지로 이동
                if self.selenium_click_by_xpath(
                        tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'main.sellerlogin'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                if self.selenium_click_by_xpath(
                        tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'login.nidlogin'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

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
            self.driver.save_screenshot('smartstore_screenshot.png')
            log.logger.error(e, exc_info=True)
            self.destroy()
            exit()

        return False

if __name__ == "__main__":
    cgv = SmartstoreTalktalk()
    cgv.utf_8_reload()
    cgv.start()

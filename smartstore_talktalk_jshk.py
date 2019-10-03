#-*- coding: utf-8 -*-

import os
import log
import sys
import filewriter
import xmltodict
import requests
from time import sleep
from pytz import timezone
from crawler2 import Crawler
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup

class SmartstoreTalktalkJshk(Crawler):

    DETAIL_URL = 'http://sell.storefarm.naver.com'

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

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

            # 신규주문 페이지로 이동
            if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'ord.new'}) is False:
                raise Exception('selenium_click_by_xpath fail. submit')

            sleep(10)

            # 레이어가 있다면 닫기
            try:
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'})
            except:
                pass

            # 주문 데이터 가져오기 iframe으로 변경
            self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))
            list = self.driver.find_element_by_xpath('//*[@id="gridbox"]/div[2]/div[2]/table').find_elements_by_xpath('.//tbody/tr')

            window_before = self.driver.window_handles[0]

            prev_order_id = None

            for li in list:
                try:
                    if li:
                        soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                        tds = soup_order_info.find_all('td')

                        if tds:
                            item_order_id = tds[1].getText().strip()
                            order_id = tds[2].getText().strip()
                            buyer = tds[12].getText().strip()
                            item_id = tds[17].getText()
                            item_name = tds[18].getText()
                            item_kind = tds[19].getText()
                            item_option = tds[20].getText().strip()
                            item_amount = tds[22].getText().strip()
                            destination = tds[44].getText()

                            # 이미 전송한 주문건에 대해서는 전송X
                            if prev_order_id != order_id:
                                prev_order_id = order_id
                                continue

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
                            if not order_id or order_id in self.log:
                                continue

                            if item_option:
                                item_name = item_name + ' (' + item_option + ')'

                            if item_amount:
                                item_name = item_name + ' ' + item_amount + '개'

                            # print(item_option)
                            # print(item_amount)
                            # print(item_kind)
                            # print(item_name)
                            # print(buyer)
                            # exit()

                            talktalklink = li.find_element_by_xpath('.//td[10]/a')

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

                            sleep(1)

                            # 메세지 전송
                            if self.selenium_click_by_xpath(xpath='//*[@id="chat_wrap"]/div/div[1]/div/div[3]/div[2]/button') is False:
                                raise Exception('selenium_click_by_xpath fail. submit')

                            sleep(2)

                            message = message.replace('\\n', '\n')

                            self.log = filewriter.slice_json_by_max_len(self.log, max_len=1000)

                            self.send_messge_and_save(order_id, message, 'jshk')
                            # telegrambot.send_message(message, 'kuhit')

                            # 창 닫고 복귀
                            self.driver.close()
                            self.driver.switch_to.window(window_before)
                            self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))

                            # 테스트로그
                            # print(buyer)
                            # print(order_id)
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
            log.logger.error(e, exc_info=True)
            self.destroy()
            exit()

        return False

    def get_delevery_message(self, item_id, item_name, destination):
        try:
            delevery_date, destination_date = self.get_delevery_date(item_id=item_id, destination=destination)

            if not delevery_date or not destination_date:
                return False

            if delevery_date == '제주특별자치도':
                delevery_message = ''
                delevery_message += '[배송 안내]'
                delevery_message += '\\n\\n'
                delevery_message += '안녕하세요^^'
                delevery_message += '\\n\\n'
                delevery_message += '정성한끼를 믿고 구매해주셔서 감사합니다.'
                delevery_message += '\\n\\n'
                delevery_message += '주문해주신 ' + delevery_date + ' 지역은 익일 배송이 불가한 지역으로'
                delevery_message += '\\n\\n'
                delevery_message += '2일 이상의 배송기간으로 인해 신선한 상태의 반찬을 보내드릴 수 없습니다.'
                delevery_message += '\\n\\n'
                delevery_message += '따라서 부득이하게 판매를 할 수 없는 점 양해를 부탁드립니다.'
                delevery_message += '\\n\\n'
                delevery_message += '주문은 자동으로 취소될 예정입니다.'
                delevery_message += '\\n\\n'
                delevery_message += '감사합니다.'
            else:
                delevery_message = ''
                delevery_message += '[배송 안내]'
                delevery_message += '\\n\\n'
                delevery_message += '안녕하세요^^'
                delevery_message += '\\n\\n'
                delevery_message += '정성한끼에서 구매하신 반찬의 배송 일정 안내 드립니다~'
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

            log.logger.info(delevery_message)

            return delevery_message

        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    def get_delevery_date(self, item_id=None, destination=None):
        try:
            # 제주도인 경우 +1
            if destination in '제주특별자치도':
                return '제주특별자치도', '제주특별자치도'

            week_text = ['월', '화', '수', '목', '금', '토', '일']

            # 상품별 발송 제한시간 (기본)
            limit_hour = 9

            # 배송일 (오늘)
            delevery_date = datetime.now(timezone('Asia/Seoul'))

            # 배송테스트
            # delevery_date = datetime.strptime('20191002', '%Y%m%d')

            # 시간이 지났다면 익일발송
            if delevery_date.hour >= limit_hour:
                delevery_date = delevery_date + timedelta(days=1)

            reddays = self.get_reddays()
            reddays_before = []

            # 연휴에는 도착이 불가능 하므로 연휴의 전날까지 휴일로 취급
            if len(reddays) > 0:
                for redday in reddays:
                    redday = datetime.strptime(redday, '%Y%m%d').date()
                    before_redday = redday - timedelta(days=1)
                    before_redday = before_redday.strftime('%Y%m%d')
                    if before_redday not in reddays:
                        reddays_before.append(before_redday)

                reddays = reddays + reddays_before

            # 추석연휴 또는 배송 안하는 날
            # reddays.append('20190910')
            # reddays.append('20190911')

            # 휴일이라면 휴일이 아닐때까지 1일씩 미룬다 /// 토, 일은 배송안하는 날
            while 1:
                if delevery_date.weekday() in [5, 6] or delevery_date.strftime('%Y%m%d') in reddays:
                    delevery_date = delevery_date + timedelta(days=1)
                else:
                    break

            # 도착예정일 신선식품이므로 다음 날
            destination_date = delevery_date + timedelta(days=1)

            # 추석연휴는 도착일에서 제거
            # reddays.remove('20190910')
            # reddays.remove('20190911')

            delevery_date = str(delevery_date.year) + '년 ' + str(delevery_date.month) + '월 ' + str(delevery_date.day) + '일 (' + week_text[delevery_date.weekday()] + ')'
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
            self.PATH_USER_DATA = os.path.join(self.PATH_NAME, 'driver/userdata_naver_jshk')

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            self.get_cookie()

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            # 로그인 여부 체크
            try:
                if self.selenium_extract_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'ord.new'}) is True:
                    log.logger.info('Alreday logined.')
                    return True
            except:
                pass

            # 계정정보 가져오기
            account_data = filewriter.get_log_file('naver_account_jshk')

            if account_data:
                self.driver.save_screenshot('smartstore_screenshot.png')

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
            log.logger.error(e, exc_info=True)
            self.destroy()
            exit()

        return False

if __name__ == "__main__":
    jshk = SmartstoreTalktalkJshk()
    jshk.utf_8_reload()
    jshk.start()

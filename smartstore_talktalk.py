#-*- coding: utf-8 -*-

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

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False,
                            default_driver='selenium',
                            is_chrome=False) is False:
                raise Exception('site connect fail')

            self.login()

            self.scan_page()

            self.destroy()

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            # 레이어가 있다면 닫기
            try:
                self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'})
            except:
                pass

            # 신규주문 페이지로 이동
            if self.selenium_click_by_xpath(
                    tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'ord.new'}) is False:
                raise Exception('selenium_click_by_xpath fail. submit')

            sleep(2)

            # 레이어가 있다면 닫기
            try:
                self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'})
            except:
                pass

            # 주문 데이터 가져오기
            # iframe으로 변경
            self.driver.switch_to.frame(frame_reference=self.driver.find_element_by_xpath('//iframe[@id="__naverpay"]'))
            list = self.driver.find_element_by_xpath('//*[@id="gridbox"]/div[2]/div[2]/table').find_elements_by_xpath('.//tbody/tr')

            window_before = self.driver.window_handles[0]

            for li in list:
                try:
                    if li:
                        soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                        tds = soup_order_info.find_all('td')

                        if tds:
                            item_order_id = tds[1].getText()
                            buyer = tds[12].getText()
                            item_id = tds[17].getText()
                            item_name = tds[18].getText()
                            destination = tds[44].getText()

                            # 테스트
                            # if buyer != '이재은':
                            #     continue

                            # 수동 발송제한
                            # 2019-05-03 리프팅밴드, 샴푸브러쉬 품절
                            # if item_id in ['4269217982', '4423398036']:
                            #     continue

                            # 발송내역에 없는지 확인
                            if not item_order_id or item_order_id in self.log:
                                continue

                            talktalklink = li.find_element_by_xpath('.//td[10]/a')

                            # 톡톡하기 클릭
                            talktalklink.click()

                            sleep(3)

                            # 톡톡창으로 focus
                            window_after = self.driver.window_handles[1]
                            self.driver.switch_to.window(window_after)

                            # 레이어가 있다면 닫기
                            try:
                                if self.driver.find_element_by_xpath('//*[@id="content"]/div[10]/a').is_displayed():
                                    self.selenium_click_by_xpath(xpath='//*[@id="content"]/div[10]/a')
                            except:
                                pass

                            # 메세지 생성
                            message = self.get_delevery_message(item_id=item_id, item_name=item_name, destination=destination)

                            if not message:
                                raise Exception('messageText genarating fail.')

                            # 메시지 입력
                            self.driver.execute_script('document.getElementsByClassName("_messageText")[0].value = "' + message + '";')

                            sleep(1)

                            # 메세지 전송
                            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'class', 'name': '_sendBtn'}) is False:
                                raise Exception('selenium_click_by_xpath fail. submit')

                            sleep(2)

                            message = message.replace('\\n', '\n')

                            self.log = filewriter.slice_json_by_max_len(self.log, max_len=1000)

                            self.send_messge_and_save(item_order_id, message, 'dev')
                            # telegrambot.send_message(message, 'dev')

                            # 창 닫ㅎ고 복귀
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

            return True
        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

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
            start_hour = '오후 4시'

            # 상품별 발송 제한시간 (기본)
            limit_hour = 7

            # 짐볼, 요가매트 (오후 2시)
            if item_id in ['4324723046','4529428871']:
                limit_hour = 14
                start_hour = '오후 6시'
            # 폼롤러 (오후 4시)
            elif item_id in ['4318623001']:
                limit_hour = 16
                start_hour = '오후 6시'

            delevery_date = datetime.now(timezone('Asia/Seoul'))

            # 시간이 지났다면 익일발송
            if delevery_date.hour >= limit_hour:
                delevery_date = delevery_date + timedelta(days=1)

            reddays = self.get_reddays()

            # 휴일이라면 휴일이 아닐때까지 1일씩 미룬다
            while 1:
                if delevery_date.weekday() in [5, 6] or delevery_date.strftime('%Y%m%d') in reddays:
                    delevery_date = delevery_date + timedelta(days=1)
                else:
                    break

            # 도착예정일
            destination_date = delevery_date + timedelta(days=1)

            # 제주도인 경우 +1
            if destination in '제주특별자치도':
                destination_date = delevery_date + timedelta(days=1)

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
                                reddays.append(it['locdate'])

            log.logger.info(','.join(reddays))
            return reddays
        except Exception as e:
            log.logger.error(e, exc_info=True)

        return reddays

    def login(self):
        try:

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

                # 로그인버튼
                if self.selenium_click_by_xpath(tag={'tag': 'input', 'attr': 'type', 'name': 'submit'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                try:
                    # 기기등록 함
                    self.selenium_click_by_xpath(xpath='//*[@id="frmNIDLogin"]/fieldset/span[1]/a')

                    # 로그인 상태유지
                    if self.selenium_click_by_xpath(xpath='//*[@id="login_maintain"]/span[1]/a') is False:
                        raise Exception('selenium_click_by_xpath fail. submit')
                except:
                    pass

                log.logger.info('login success')

                sleep(2)

                return True
        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

if __name__ == "__main__":
    cgv = SmartstoreTalktalk()
    cgv.utf_8_reload()
    cgv.start()

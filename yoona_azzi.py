#-*- coding: utf-8 -*-

import log
import re
import math
import filewriter
import telegrambot
from time import sleep
from datetime import datetime, date, timedelta
from crawler2 import Crawler

class YoonaAzzi(Crawler):

    # 네이버 부동산 아파트 주소를 입력해주세요.
    DETAIL_URL = {
        '안양(향촌롯데)': 'https://new.land.naver.com/complexes/1480?ms=37.3870621,126.9580029,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '산본(래미안하이어스)': 'https://new.land.naver.com/complexes/101283?ms=37.367926,126.9344305,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '청주(두산위브지웰시티)': 'https://new.land.naver.com/complexes/104637?ms=36.643547,127.429262,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '구미(옥계현진에버빌)': 'https://new.land.naver.com/complexes/25490?ms=36.1388272,128.4244144,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '울산(신정푸르지오)': 'https://new.land.naver.com/complexes/102946?ms=35.547078,129.315543,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '포항(포항자이)': 'https://new.land.naver.com/complexes/113172?ms=36.0092,129.341992,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '천안(천안불당지웰더샵)': 'https://new.land.naver.com/complexes/108766?ms=36.814875,127.105009,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '안산(안산메트로타운푸르지오힐스테이트)': 'https://new.land.naver.com/complexes/111264?ms=37.349242,126.806166,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
    }

    def start(self):
        try:
            self.notice = ''
            self.log = filewriter.get_log_file(self.name)
            self.data = filewriter.get_log_file('yoonaazzi_data', is_json=True)
            self.today = datetime.today().strftime('%Y-%m-%d')
            self.yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

            for apt, url in self.DETAIL_URL.items():
                # 첫아파트라면 초기화
                if apt not in self.data:
                    self.data[apt] = {}

                self.total = 0
                self.prices = {}
                self.prices_filter = {}

                # 어제 데이터가 있다면 어제 데이터로 초기세팅 (0값을 없애기 위해)
                if self.yesterday in self.data[apt]:
                    self.prices_filter = self.data[apt][self.yesterday]

                if self.connect(site_url=url, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                    raise Exception('site connect fail')

                try:
                    # 가격 수집
                    self.collect_price()

                    # 데이터 쌓기
                    self.setLog(apt)
                except:
                    pass

            # ** 모든 아파트 수집 완료 **

            # 오늘의 결과 메세지 발송
            if self.notice:
                telegrambot.send_message(self.notice, 'yoona_azzi')
            
            # 오늘의 데이터 저장
            filewriter.save_log_file('yoonaazzi_data', self.data)

            self.destroy()
            exit()

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

    # 계산
    def setLog(self, apt=''):
        try:
            self.data[apt][self.today] = {
                'total': self.total,
                'prices': self.prices_filter
            }

            self.data[apt] = filewriter.slice_json_by_max_len(self.data[apt], max_len=100)

            # print(self.data)

        except Exception as e:
            log.logger.error(e, exc_info=True)

    # 가격 수집
    def collect_price(self):
        # 매매만 선택
        if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'data-nclk', 'name': 'TAA.fat'}) is False:
            raise Exception('selenium_click_by_xpath fail. 거래방식')

        sleep(1)

        if self.selenium_click_by_xpath(tag={'tag': 'label', 'attr': 'for', 'name': 'complex_article_trad_type_filter_0'}) is False:
            raise Exception('selenium_click_by_xpath fail. 전체선택')

        sleep(1)

        if self.selenium_click_by_xpath(tag={'tag': 'label', 'attr': 'for', 'name': 'complex_article_trad_type_filter_1'}) is False:
            raise Exception('selenium_click_by_xpath fail. 매매선택')

        sleep(1)

        # 스크롤 내려서 모두 불러오기
        if self.scroll_bottom(selectorParent='document.getElementsByClassName("item_list--article")[0]', selectorDom='document.getElementById("articleListArea")') is False:
            raise Exception('scroll bottom fail.')

        # 매물 리스트
        list = self.driver.find_elements_by_xpath('//*[@id="articleListArea"]/div')

        for li in list:
            try:
                # 정보추출
                apt = li.find_element_by_xpath('.//span[contains(@class, "text")]').text.strip()
                price = li.find_element_by_xpath('.//span[contains(@class, "price")]').text.strip()
                spec = li.find_element_by_xpath('.//span[contains(@class, "spec")]').text.strip()
                title = li.find_element_by_xpath('.//em[contains(@class, "title")]').text.strip()

                self.total = self.total + 1

                # 거래완료 패스
                if (title == '거래완료'):
                    continue

                # 정보 정제
                if '억' in price:
                    price_div = price.split('억')
                    price = int(re.sub("\D", "", price_div[0])) * 10000
                    if price_div[1]:
                        price = price + int(re.sub("\D", "", price_div[1]))

                # price = int(re.sub("\D", "", price))
                # if len(str(price)) == 1:
                #     price = price * 10000

                spec = spec.split(', ')
                size = spec[0].split('/')[0]
                
                # 저층 제외
                try :
                    floor = int(spec[1].split('/')[0])

                    floor_top = int(re.sub("\D", "", spec[1].split('/')[1]))

                    if floor < 2:
                        continue
                    if floor == floor_top:
                        continue
                    if floor_top < 11:
                        if floor < 4:
                            continue
                    if floor_top > 10:
                        if floor < 5:
                            continue

                except Exception as e:
                    floor = spec[1].split('/')[0]

                    if floor == '저':
                        continue

                if size not in self.prices:
                    self.prices[size] = []

                self.prices[size].append(price)

                # print(apt)
                # print(price)
                # print(size)
                # print(floor)
                # print(floor_top)
                # print(prices)

            except Exception as e:
                log.logger.error(e, exc_info=True)

        for size, prices in self.prices.items():
            # 전일 데이터가 있다면 비교 후 메세지에 포함
            avg_price = round(sum(prices) / len(prices))

            if size in self.prices_filter:
                yesterday_price = self.prices_filter[size][1]
                increase = (avg_price - yesterday_price) / yesterday_price * 100
                updown = ''

                if increase > 0:
                    updown = '증가'
                elif increase < 0:
                    updown = '감소'

                if updown:
                    self.notice += '%s[%s] %d%% %s \n' % (apt, size, math.ceil(increase), updown)

            self.prices_filter[size] = [min(prices), avg_price, max(prices)]

            # 급매알리미
            if self.prices_filter[size][1] * 0.9 > self.prices_filter[size][0]:
                sale_percent = self.prices_filter[size][0] / self.prices_filter[size][1] * 100
                uniqid = '%s%s%d' % (apt, size, self.prices_filter[size][0])
                if uniqid not in self.log:
                    message = '%s[%s] %d만원 (평균대비 %d%% 저렴)' % (apt, size, self.prices_filter[size][0], math.ceil(sale_percent))
                    self.log = filewriter.slice_json_by_max_len(self.log, max_len=100)
                    self.send_messge_and_save(uniqid, message, 'yoona_azzi')


    # 스크롤 가장 아래로
    def scroll_bottom(self, selectorParent=None, selectorDom=None, limit_page=0):
        try:
            if selectorParent is None or selectorDom is None:
                return False

            is_success = True
            limit = 1

            # Get scroll height
            last_height = self.driver.execute_script("return " + selectorDom + ".scrollHeight")

            while True:
                try:
                    if limit_page > 0:
                        if limit > limit_page:
                            break;

                    # Scroll down to bottom
                    self.driver.execute_script(selectorParent + ".scrollTo(0, " + selectorDom + ".scrollHeight);")

                    # Wait to load page
                    sleep(1)

                    # Calculate new scroll height and compare with last scroll height
                    new_height = self.driver.execute_script("return " + selectorDom + ".scrollHeight")
                    limit = limit + 1
                    if limit % 10 == 0:
                        log.logger.info('scroll bottom %d steps.' % (limit))
                    if new_height == last_height:
                        break
                    last_height = new_height
                except Exception as e:
                    is_success = False
                    log.logger.error(e, exc_info=True)
                    break

            return is_success

            # log.logger.info('last_height: %d' % (last_height))
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

if __name__ == "__main__":
    cgv = YoonaAzzi()
    cgv.utf_8_reload()
    cgv.start()

#-*- coding: utf-8 -*-

import log
import re
import math
import filewriter
import telegrambot
from time import sleep
from pytz import timezone
from datetime import datetime, date, timedelta
from crawler2 import Crawler

class YoonaAzzi(Crawler):

    # 네이버 부동산 아파트 주소를 입력해주세요.
    DETAIL_URL = {
        # 서울
        # 경기
        '과천(래미안에코팰리스)' : 'https://new.land.naver.com/complexes/22779?ms=37.435103,126.993279,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '분당(정자동파크뷰)': 'https://new.land.naver.com/complexes/3621?ms=37.375122,127.106989,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '광명(철산래미안자이)': 'https://new.land.naver.com/complexes/25902?ms=37.471957,126.874532,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '안양(향촌롯데)': 'https://new.land.naver.com/complexes/1480?ms=37.3870621,126.9580029,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '산본(래미안하이어스)': 'https://new.land.naver.com/complexes/101283?ms=37.367926,126.9344305,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '안산(안산메트로타운푸르지오힐스테이트)': 'https://new.land.naver.com/complexes/111264?ms=37.349242,126.806166,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '구리(신명)': 'https://new.land.naver.com/complexes/3577?ms=37.58576,127.13688,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '의왕(인덕원푸르지오엘센트로)': 'https://new.land.naver.com/complexes/114329?ms=37.394849,126.983405,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '부천(중동리첸시아)': 'https://new.land.naver.com/complexes/27435?ms=37.494956,126.778913,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '수원(자연앤힐스테이트)': 'https://new.land.naver.com/complexes/101273?ms=37.2876875,127.0515751,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '용인(성복역롯데캐슬골드타운)': 'https://new.land.naver.com/complexes/111555?ms=37.312559,127.083225,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '고양(삼송2차아이파크)': 'https://new.land.naver.com/complexes/106995?ms=37.650636,126.8874,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '화성(시범우남퍼스트빌)': 'https://new.land.naver.com/complexes/105405?ms=37.203542,127.100877,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '김포(한강신도시반도유보라2차)': 'https://new.land.naver.com/complexes/103407?ms=37.654361,126.680649,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 광역시
        '인천연수구(송도센트럴파크푸르지오)': 'https://new.land.naver.com/complexes/105037?ms=37.392635,126.6442,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '인천서구(청라푸르지오)': 'https://new.land.naver.com/complexes/100594?ms=37.5341587,126.6403646,16&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '울산남구(신정푸르지오)': 'https://new.land.naver.com/complexes/102946?ms=35.547078,129.315543,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '울산북구(울산송정반도유보라아이비파크)': 'https://new.land.naver.com/complexes/115848?ms=35.60241,129.367527,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '대전서구(크로바)': 'https://new.land.naver.com/complexes/5986?ms=36.352128,127.392725,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '대전유성구(도룡SK뷰)': 'https://new.land.naver.com/complexes/114293?ms=36.384888,127.375014,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '부산해운대구(해운대자이2차)': 'https://new.land.naver.com/complexes/110398?ms=35.1684326,129.1445628,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '대구수성구(범어SK뷰)': 'https://new.land.naver.com/complexes/25632?ms=35.8557724,128.6368092,18&a=APT:ABYG:JGC&e=RETAIL&h=99&i=132&ad=true',
        '광주광산구(해솔마을현진에버빌1단지)': 'https://new.land.naver.com/complexes/101762?ms=35.1955652,126.8225117,16&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '세종(새뜸6단지힐스테이트메이저시티)': 'https://new.land.naver.com/complexes/109173?ms=36.4844937,127.2538593,16&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 강원도
        '강릉(홍제동우미린)': 'https://new.land.naver.com/complexes/108396?ms=37.755976,128.867898,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '원주(무실우미린)': 'https://new.land.naver.com/complexes/107637?ms=37.326796,127.932406,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 충청북도
        '청주(두산위브지웰시티)': 'https://new.land.naver.com/complexes/104637?ms=36.643547,127.429262,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 충청남도
        '천안(천안불당지웰더샵)': 'https://new.land.naver.com/complexes/108766?ms=36.814875,127.105009,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 전라북도
        '전주(서부신시가지아이파크)': 'https://new.land.naver.com/complexes/23720?ms=35.828118,127.107512,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 전라남도
        '목포(한라비발디)': 'https://new.land.naver.com/complexes/24772?ms=34.806836,126.454859,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '여수(웅천지)': 'https://new.land.naver.com/complexes/101892?ms=34.748113,127.671499,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '순천(중흥S-클래스메가타운6단지)': 'https://new.land.naver.com/complexes/105572?ms=34.936236,127.54367,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 경상북도
        '포항(포항자이)': 'https://new.land.naver.com/complexes/113172?ms=36.0092,129.341992,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '구미(옥계현진에버빌)': 'https://new.land.naver.com/complexes/25490?ms=36.1388272,128.4244144,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        # 경상남도
        '창원(용지아이파크)': 'https://new.land.naver.com/complexes/109465?ms=35.230528,128.678886,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '김해(부원역푸르지오)': 'https://new.land.naver.com/complexes/104220?ms=35.224961,128.882874,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
        '양산(양산대방노블랜드7차메가시티)': 'https://new.land.naver.com/complexes/109396?ms=35.316014,128.993835,17&a=APT:ABYG:JGC&e=RETAIL&ad=true',
    }

    def start(self):
        try:
            self.notice = ''
            self.log = filewriter.get_log_file(self.name)
            self.data = filewriter.get_log_file('yoonaazzi_data', is_json=True)
            date_now = datetime.now(timezone('Asia/Seoul'))
            self.today = date_now.strftime('%Y-%m-%d')
            self.yesterday = (date_now - timedelta(days=1)).strftime('%Y-%m-%d')

            print(self.data)
            exit()

            for apt, url in self.DETAIL_URL.items():
                # 첫아파트라면 초기화
                if apt not in self.data:
                    self.data[apt] = {}

                # 오늘 데이터가 있다면 continue
                if self.today in self.data[apt]:
                    continue

                self.total_prices = 0
                self.total_jeonses = 0
                self.prices = {}
                self.prices_filter = {}
                self.jeonses = {}
                self.jeonses_filter = {}

                # 어제 데이터가 있다면 어제 데이터로 초기세팅 (0값을 없애기 위해)
                if self.yesterday in self.data[apt]:
                    if 'prices' in self.data[apt][self.yesterday]:
                        # 데이터만 복사 (참조하지 않도록)
                        self.prices_filter = self.data[apt][self.yesterday]['prices'].copy()

                if self.connect(site_url=url, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                    raise Exception('site connect fail')

                try:
                    # 가격 수집
                    self.collect_price()
                    
                    # 전세 수집
                    self.collect_jeonse()

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
            if self.total_prices == 0 and self.total_jeonses == 0:
                return False

            self.data[apt][self.today] = {
                'total_prices': self.total_prices,
                'total_jeonses': self.total_jeonses,
                'prices': self.prices_filter,
                'jeonses': self.jeonses_filter,
            }

            self.data[apt] = filewriter.slice_json_by_max_len(self.data[apt], max_len=100)
            print(self.data[apt])

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
        try:
            if self.scroll_bottom(selectorParent='document.getElementsByClassName("item_list--article")[0]', selectorDom='document.getElementById("articleListArea")') is False:
                raise Exception('scroll bottom fail.')
        except:
            pass

        # 매물 리스트
        list = self.driver.find_elements_by_xpath('//*[@id="articleListArea"]/div')

        for li in list:
            try:
                # 정보추출
                apt = li.find_element_by_xpath('.//span[contains(@class, "text")]').text.strip()
                price = li.find_element_by_xpath('.//span[contains(@class, "price")]').text.strip()
                spec = li.find_element_by_xpath('.//span[contains(@class, "spec")]').text.strip()
                title = li.find_element_by_xpath('.//em[contains(@class, "title")]').text.strip()

                self.total_prices = self.total_prices + 1

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
                minus = avg_price - yesterday_price
                increase = round((minus) / yesterday_price * 100, 1)
                updown = ''

                if increase > 0:
                    updown = '증가'
                elif increase < 0:
                    updown = '감소'

                if updown:
                    self.notice += '%s[%s] %d만원 (%.1f%%) %s \n' % (apt, size, minus, increase, updown)

            self.prices_filter[size] = [min(prices), avg_price, max(prices)]

            # 급매알리미
            if self.prices_filter[size][1] * 0.9 > self.prices_filter[size][0]:
                sale_percent = self.prices_filter[size][0] / self.prices_filter[size][1] * 100
                uniqid = '%s%s%d' % (apt, size, self.prices_filter[size][0])
                if uniqid not in self.log:
                    message = '%s[%s] %d만원 (평균대비 %d%% 저렴)' % (apt, size, self.prices_filter[size][0], math.ceil(sale_percent))
                    self.log = filewriter.slice_json_by_max_len(self.log, max_len=100)
                    self.send_messge_and_save(uniqid, message, 'yoona_azzi')

    # 전세 수집
    def collect_jeonse(self):
        # 전세만 선택
        if self.selenium_click_by_xpath(
                tag={'tag': 'label', 'attr': 'for', 'name': 'complex_article_trad_type_filter_0'}) is False:
            raise Exception('selenium_click_by_xpath fail. 전체선택')

        sleep(1)

        if self.selenium_click_by_xpath(
                tag={'tag': 'label', 'attr': 'for', 'name': 'complex_article_trad_type_filter_2'}) is False:
            raise Exception('selenium_click_by_xpath fail. 전세선택')

        sleep(1)

        # 스크롤 내려서 모두 불러오기
        try:
            if self.scroll_bottom(selectorParent='document.getElementsByClassName("item_list--article")[0]', selectorDom='document.getElementById("articleListArea")') is False:
                raise Exception('scroll bottom fail.')
        except:
            pass

        # 매물 리스트
        list = self.driver.find_elements_by_xpath('//*[@id="articleListArea"]/div')

        for li in list:
            try:
                # 정보추출
                apt = li.find_element_by_xpath('.//span[contains(@class, "text")]').text.strip()
                price = li.find_element_by_xpath('.//span[contains(@class, "price")]').text.strip()
                spec = li.find_element_by_xpath('.//span[contains(@class, "spec")]').text.strip()
                title = li.find_element_by_xpath('.//em[contains(@class, "title")]').text.strip()

                self.total_jeonses = self.total_jeonses + 1

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
                try:
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

                if size not in self.jeonses:
                    self.jeonses[size] = []

                self.jeonses[size].append(price)

                # print(apt)
                # print(price)
                # print(size)
                # print(floor)
                # print(floor_top)
                # print(prices)

            except Exception as e:
                log.logger.error(e, exc_info=True)

        for size, prices in self.jeonses.items():
            # 전일 데이터가 있다면 비교 후 메세지에 포함
            avg_price = round(sum(prices) / len(prices))

            self.jeonses_filter[size] = [min(prices), avg_price, max(prices)]


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
                    # sleep(1)

                    # Calculate new scroll height and compare with last scroll height
                    new_height = self.driver.execute_script("return " + selectorDom + ".scrollHeight")
                    limit = limit + 1

                    if new_height == last_height:
                        break
                    last_height = new_height
                except Exception as e:
                    is_success = False
                    # log.logger.error(e, exc_info=True)
                    break

            return is_success

            # log.logger.info('last_height: %d' % (last_height))
        except Exception as e:
            # log.logger.error(e, exc_info=True)
            return False

if __name__ == "__main__":
    cgv = YoonaAzzi()
    cgv.utf_8_reload()
    cgv.start()

#-*- coding: utf-8 -*-

import os
import log
import re
import math
import requests
import filewriter
import telegrambot
from time import sleep
from proxy import Proxy
from pytz import timezone
from random import uniform
from datetime import datetime, timedelta
from crawler2 import Crawler

class YoonaAzzi(Crawler):

    # 네이버 부동산 아파트 id를 입력해주세요.
    DETAIL_URL = {
        # 서울
        # 경기
        '과천(래미안에코팰리스)' : '22779',
        '분당(정자동파크뷰)': '3621',
        '광명(철산래미안자이)': '25902',
        '안양(향촌롯데)': '1480',
        '산본(래미안하이어스)': '101283',
        '안산(안산메트로타운푸르지오힐스테이트)': '111264',
        '구리(신명)': '3577',
        '의왕(인덕원푸르지오엘센트로)': '114329',
        '부천(중동리첸시아)': '27435',
        '수원(자연앤힐스테이트)': '101273',
        '용인(성복역롯데캐슬골드타운)': '111555',
        '고양(삼송2차아이파크)': '106995',
        '화성(시범우남퍼스트빌)': '105405',
        '김포(한강신도시반도유보라2차)': '103407',
        # 광역시
        '인천연수구(송도센트럴파크푸르지오)': '105037',
        '인천서구(청라푸르지오)': '100594',
        '울산남구(신정푸르지오)': '102946',
        '울산북구(울산송정반도유보라아이비파크)': '115848',
        '대전서구(크로바)': '5986',
        '대전유성구(도룡SK뷰)': '114293',
        '부산해운대구(해운대자이2차)': '110398',
        '대구수성구(범어SK뷰)': '25632',
        '광주광산구(해솔마을현진에버빌1단지)': '101762',
        '세종(새뜸6단지힐스테이트메이저시티)': '109173',
        # 강원도
        '강릉(홍제동우미린)': '108396',
        '원주(무실우미린)': '107637',
        # 충청북도
        '청주(두산위브지웰시티)': '104637',
        # 충청남도
        '천안(천안불당지웰더샵)': '108766',
        # 전라북도
        '전주(서부신시가지아이파크)': '23720',
        # 전라남도
        '목포(한라비발디)': '24772',
        '여수(웅천지)': '101892',
        '순천(중흥S-클래스메가타운6단지)': '105572',
        # 경상북도
        '포항(포항자이)': '113172',
        '구미(옥계현진에버빌)': '25490',
        # 경상남도
        '창원(용지아이파크)': '109465',
        '김해(부원역푸르지오)': '104220',
        '양산(양산대방노블랜드7차메가시티)': '109396',
    }

    URL = 'https://new.land.naver.com/api/articles/complex/%s?realEstateType=APT:ABYG:JGC&tradeType=A1:B1&tag=::::::::&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=true&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&complexNo=22779&buildingNos=&areaNos=&type=list&order=rank&page=%s'
    REQUEST_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def start(self):
        try:
            # 프록시
            proxy = Proxy()
            self.ips = proxy.get()
            self.ips_index = 0
            count = 0

            if self.ips == False:
                log.logger.info('proxy ip empty')
                exit()
            log.logger.info(', '.join(self.ips))

            self.notice = ''
            self.log = filewriter.get_log_file(self.name)
            date_now = datetime.now(timezone('Asia/Seoul'))
            self.today = date_now.strftime('%Y-%m-%d')
            self.yesterday = (date_now - timedelta(days=1)).strftime('%Y-%m-%d')
            self.data = filewriter.get_log_file('yoonaazzi_data', is_json=True)

            for apt, id in self.DETAIL_URL.items():
                count = count + 1

                # 아파트별로 페이지 초기화
                self.page = 1
                exists = False
                
                # 첫아파트라면 초기화
                for apted in self.data.keys():
                    if apted == apt:
                        apt = apted
                        exists = True

                if exists == False:
                    print('없음')
                    self.data[apt] = {}

                # 오늘 데이터가 있다면 continue
                try:
                    if self.today in self.data[apt].keys():
                        log.logger.info('%s today exists.' % (apt))
                        continue
                except:
                    pass

                log.logger.info('%s collecting start...($d/$d)' % (apt, count, len(self.DETAIL_URL)))

                self.total_prices_complete = 0
                self.total_jeonses_complete = 0
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

                try:
                    # 가격 수집
                    while 1:
                        if self.collect_price(apt=apt, id=id) == False:
                            break

                    if self.total_prices == 0 and self.total_jeonses == 0:
                        continue
                    
                    # 가격 필터
                    self.filter_price(apt=apt)
                    
                    # 로그 저장
                    self.set_log(apt=apt)

                    sleep(round(uniform(1.0, 3.0), 1))
                except:
                    pass

            # ** 모든 아파트 수집 완료 **

            # 오늘의 결과 메세지 발송
            if self.notice:
                telegrambot.send_message(self.notice, 'yoona_azzi')

            # 오늘의 데이터 저장
            filewriter.save_log_file('yoonaazzi_data', self.data)

            log.logger.info('yoona_azzi complete.')

            exit()

        except Exception as e:
            log.logger.error(e, exc_info=True)
            exit()

    # 계산
    def set_log(self, apt=''):
        try:
            self.data[apt][self.today] = {
                'total_prices_complete': self.total_prices_complete,
                'total_jeonses_complete': self.total_jeonses_complete,
                'total_prices': self.total_prices,
                'total_jeonses': self.total_jeonses,
                'prices': self.prices_filter,
                'jeonses': self.jeonses_filter,
            }

            self.data[apt] = filewriter.slice_json_by_max_len(self.data[apt], max_len=100)
            log.logger.info('%s collecting done.' % (apt))

        except Exception as e:
            log.logger.error(e, exc_info=True)

    # 가격 수집
    def collect_price(self, id='', apt=''):
        # url 생성 (아파트번호, 페이지)
        try:
            log.logger.info('[%s %dpage] proxy:%s' % (apt, self.page, self.ips[self.ips_index]))
            url = self.URL % (id, self.page)
            proxy = {'http': 'http://' + self.ips[self.ips_index], 'https': 'https://' + self.ips[self.ips_index]}
            res = requests.get(url, headers=self.REQUEST_HEADER, proxies=proxy, timeout=5)
            data = res.json()
        except Exception as e:
            log.logger.info('proxy %s failed.' % (self.ips[self.ips_index]))
            # log.logger.error(e, exc_info=True)
            # 데이터를 가져오지 못했다면 프록시 다시 생성
            self.ips_index = self.ips_index + 1
            try:
                if not self.ips[self.ips_index]:
                    self.ips_index = 0
            except:
                self.ips_index = 0

            return True

        try:
            if not data:
                return False

            if not data['articleList']:
                return False

            # print(data['isMoreData'])
            # print(data['articleList'])

            log.logger.info(data['isMoreData'])
            
            # 데이터 분류
            for list in data['articleList']:
                price = list['sameAddrMinPrc']
                size = list['area1']
                floor_full = list['floorInfo']
                trade = list['tradeTypeName']
                status = list['articleStatus']

                # print(trade)
                # print(price)
                # print(size)
                # print(floor_full)

                # 거래완료
                if status != 'R0':
                    if trade == '매매':
                        self.total_prices_complete = self.total_prices_complete + 1
                    elif trade == '전세':
                        self.total_jeonses_complete = self.total_jeonses_complete + 1
                    continue

                # 매물 갯수 파악
                if trade == '매매':
                    self.total_prices = self.total_prices + 1
                elif trade == '전세':
                    self.total_jeonses = self.total_jeonses + 1

                # 저층 제외
                try:
                    floor = int(floor_full.split('/')[0])

                    floor_top = int(re.sub("\D", "", floor_full.split('/')[1]))

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
                    floor = floor_full.split('/')[0]

                    if floor == '저':
                        continue

                #  가격 숫자로 변환
                if '억' in price:
                    price_div = price.split('억')
                    price = int(re.sub("\D", "", price_div[0])) * 10000
                    if price_div[1]:
                        price = price + int(re.sub("\D", "", price_div[1]))
                
                # 가격정보 담기
                if trade == '매매':
                    if size not in self.prices:
                        self.prices[size] = []

                    self.prices[size].append(price)
                elif trade == '전세':
                    if size not in self.jeonses:
                        self.jeonses[size] = []

                    self.jeonses[size].append(price)

            # 남은 데이터가 있다면 재귀
            if data['isMoreData'] == True:
                self.page = self.page + 1
                sleep(round(uniform(0.3, 0.7), 1))
                return True

            return False

        except:
            return False

    # 가격 필터
    def filter_price(self, apt=''):
        try:
            # 매매
            for size, prices in self.prices.items():
                avg_price = round(sum(prices) / len(prices))

                # 전일 데이터가 있다면 비교 후 메세지에 포함
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

            # 전세
            for size, prices in self.jeonses.items():
                avg_price = round(sum(prices) / len(prices))

                self.jeonses_filter[size] = [min(prices), avg_price, max(prices)]

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

if __name__ == "__main__":
    cgv = YoonaAzzi()
    cgv.utf_8_reload()
    cgv.start()

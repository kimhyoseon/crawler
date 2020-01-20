#-*- coding: utf-8 -*-

import log
import re
import math
from time import sleep
from pytz import timezone
from datetime import datetime
from crawler2 import Crawler
from bs4 import BeautifulSoup

class YoonaRentCalc(Crawler):

    # 네이버 부동산 아파트 주소를 입력해주세요.
    DETAIL_URL = 'https://new.land.naver.com/search?ms=37.3095194,126.8384171,11&a=APT:JGC:ABYG&e=RETAIL&ad=true'

    def start(self):
        try:
            self.prices_filter = {}
            self.prices_kb = {}

            if self.connect(site_url=self.DETAIL_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            self.collect_kb()

            self.collect_price()

            # 샘플
            # self.prices_filter = {'71BAY3': [18000, 18830.0, 20000], '71BAY2': [19500, 20340.0, 22000], '54N': [16500, 16500.0, 16500], '54S': [14700, 14800.0, 15000]}
            # self.prices_kb = {'54': [17000, 12500], '71': [20500, 16750]}
            self.calc()

            # self.destroy()
            exit()

        except Exception as e:
            # self.destroy()
            log.logger.error(e, exc_info=True)

    # 계산
    def calc(self):
        try:
            etc_rate = 1.35 / 100 # 수수료 등
            estate_agency_maemae_rate = 0.4 / 100 # 매매중개비
            estate_agency_jeonse_rate = 0.3 / 100 # 전세중개비
            loan_interest_rate = 3.9 / 100
            loan_interest_return_rate = 1.5 / 100
            price_estate_manage_4month  = 20 # 공실관리비
            price_estate_fix = 0 # 수리비, 인테리어비
            price_yoongza_loan_rate = 1.5 / 100
            price_yoongza_loan_max = 10000 # 집주인 융자대출 최대금액 (수도권 10000, 광역시 8000, 기타 6000)
            price_yoongza_findout = 55  # 집주인 융자대출 시세조사비용
            jeonse_assurance_interest_rate = 0.128 / 100
            jeonse_to_month_rate = 4.75 / 100 # 전세 > 전월세로 전환시 요율 (렌트홈에서 확인)

            print(self.prices_kb)
            print(self.prices_filter)

            for key in self.prices_filter:
                try:
                    value = self.prices_filter[key]

                    # 사이즈에서 문자 제거
                    # size = key[:2]
                    size = re.findall(r'^\D*(\d+)', key)[0]
                    sizeExtra = str(int(size) + 1)

                    # 사이즈 보정
                    if size not in self.prices_kb and sizeExtra in self.prices_kb:
                        size = sizeExtra

                    if size not in self.prices_kb:
                        continue

                    price_maemae = value[0]
                    price_maemae_kb = self.prices_kb[size][0]
                    price_jeonse_kb = self.prices_kb[size][1]

                    # 대출
                    price_loan_max = (price_maemae_kb - 1700) * 0.7 # 방빼기 (서울 3700, 과밀억제권 3400, 광역시 2000, 기타 1700)
                    price_loan_interest = price_loan_max * loan_interest_rate / 12
                    price_loan_interest_4month = price_loan_interest * 4
                    price_loan_interest_return = price_loan_max * loan_interest_return_rate

                    # 초기비용
                    price_etc = price_maemae * etc_rate
                    price_agency_maemae = price_maemae * estate_agency_maemae_rate
                    price_start = price_maemae + price_etc + price_agency_maemae - price_loan_max + price_loan_interest_4month + price_loan_interest_return + price_estate_manage_4month + price_estate_fix

                    # 집주인융자 전환
                    price_estate_jerdang = price_yoongza_loan_max * 1.2
                    price_yoongza_loan_interest = price_yoongza_loan_max * price_yoongza_loan_rate / 12
                    price_max_jeonse_85per = price_jeonse_kb * 0.85

                    # 전세보증보험
                    price_max_jeonse_assurance = price_maemae_kb - price_estate_jerdang

                    # 전세금액 계산
                    price_jeonse_confirm = price_max_jeonse_85per
                    price_month = 0

                    if price_max_jeonse_assurance < price_max_jeonse_85per:
                        # 전월세로 전환
                        price_jeonse_confirm = price_max_jeonse_assurance
                        price_month = (price_max_jeonse_85per - price_max_jeonse_assurance) * jeonse_to_month_rate / 12

                    price_agency_jeonse = price_jeonse_confirm * estate_agency_jeonse_rate
                    price_jeonse_assurance_interest = price_jeonse_confirm *  jeonse_assurance_interest_rate / 12

                    # 총 투자금
                    price_total = price_start + price_loan_max + price_yoongza_findout + price_agency_jeonse + (price_yoongza_loan_interest * 24) + (price_jeonse_assurance_interest * 24) - (price_month * 24) - price_jeonse_confirm - price_yoongza_loan_max

                    print('')
                    print('*************')
                    print('[%s] 결과' % (key))
                    print('KB매매시세: %s만원' % ("{:,d}".format(math.ceil(price_maemae_kb))))
                    print('최저매매가격: %s만원' % ("{:,d}".format(math.ceil(price_maemae))))
                    print('-------------')
                    print('초기투자금: %s만원' % ("{:,d}".format(math.ceil(price_start))))
                    print('-------------')
                    print('KB전세시세: %s만원' % ("{:,d}".format(math.ceil(price_jeonse_kb))))
                    print('전세(시세85): %s만원' % ("{:,d}".format(math.ceil(price_max_jeonse_85per))))
                    print('전세(보증보험): %s만원' % ("{:,d}".format(math.ceil(price_max_jeonse_assurance))))
                    print('전세금액: %s만원' % ("{:,d}".format(math.ceil(price_jeonse_confirm))))
                    if price_month > 0:
                        print('월세금액: %s만원(월)' % ("{:,d}".format(math.ceil(price_month))))
                    print('-------------')
                    print('집주인융자이자(월): %s만원' % ("{:,d}".format(math.ceil(price_yoongza_loan_interest))))
                    print('전세보증보험비(월): %s만원' % ("{:,d}".format(math.ceil(price_jeonse_assurance_interest))))
                    print('-------------')
                    print('총 투자금: %s만원' % ("{:,d}".format(math.ceil(price_total))))
                    print('*************')
                except Exception as e:
                    log.logger.error(e, exc_info=True)
        except Exception as e:
            log.logger.error(e, exc_info=True)
        

    # KB 시세
    def collect_kb(self):
        try:
            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'data-nclk', 'name': 'CID.sise'}) is False:
                raise Exception('selenium_click_by_xpath fail. 시세/실거래가')

            window_before = self.driver.window_handles[0]

            sleep(1)

            buttons = self.driver.find_elements_by_xpath('//button[contains(@class,"detail_tab_button")]')

            for button in buttons:
                try:
                    # 정보추출
                    button_name = button.text.strip()
                    # print(button_name)
                    if button_name == 'KB부동산':
                        button.click()
                except:
                    pass

            sleep(1)

            # KB시세 이동 클릭
            self.driver.find_element_by_xpath('//a[@class="detail_company_link"]').click()

            sleep(1)

            # KB시세창으로 focus
            window_after = self.driver.window_handles[1]
            self.driver.switch_to.window(window_after)

            build = self.driver.find_element_by_xpath('//*[@class="info_right"]/table/tbody/tr/td[3]').text.strip()

            # 년도 제한 (준공 20년 이하)
            s1 = datetime.now(timezone('Asia/Seoul')).strftime('%Y.%m')
            tdelta = datetime.strptime(s1, '%Y.%m') - datetime.strptime(build, '%Y.%m')
            year_gap = math.ceil(tdelta.days / 365)
            if year_gap > 20:
                print('준공 %s년이 지나서 해당사항 없음' % ("{:,d}".format(year_gap)))
                exit()

            trs = self.driver.find_elements_by_xpath('//tbody[@id="siseDataTbodyArea"]/tr')

            for tr in trs:
                try:
                    soup_order_info = BeautifulSoup(tr.get_attribute('innerHTML'), 'html.parser')
                    tds = soup_order_info.find_all('td')

                    size = tds[0].getText().strip()
                    size1 = size.split('/')[0]
                    size1 = size.split('.')[0]
                    size2 = size.split('/')[1]
                    size2 = size2.split('.')[0]
                    maemae = int(re.sub("\D", "", tds[2].getText().strip()))
                    jeonse = int(re.sub("\D", "", tds[5].getText().strip()))

                    # 가격 제한 (2.7억 이하)
                    if maemae > 27000:
                        print('%s만원 이상의 매매가로 인해 주의 필요(공시가격 확인 필)' % ("{:,d}".format(math.ceil(maemae))))

                    # 평수 제한 (85제곱 이하)
                    size2 = re.findall(r'^\D*(\d+)', size2)[0]
                    size_number = int(size2)  # 사이즈에서 문자 제거
                    if size_number > 85:
                        print('해당 단지는 %s제곱미터로 84제곱미터 이상은 해당사항 없음' % ("{:,d}".format(size_number)))
                        continue

                    self.prices_kb[size1] = [maemae, jeonse]

                    # print(size)
                    # print(maemae)
                    # print(jeonse)
                except Exception as e:
                    log.logger.error(e, exc_info=True)

            # 창 닫고 복귀
            self.driver.close()
            self.driver.switch_to.window(window_before)

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

        prices = {}

        for li in list:
            try:
                # 정보추출
                apt = li.find_element_by_xpath('.//span[contains(@class, "text")]').text.strip()
                price = li.find_element_by_xpath('.//span[contains(@class, "price")]').text.strip()
                spec = li.find_element_by_xpath('.//span[contains(@class, "spec")]').text.strip()
                title = li.find_element_by_xpath('.//em[contains(@class, "title")]').text.strip()

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

                if size not in prices:
                    prices[size] = []

                prices[size].append(price)

                # print(apt)
                # print(price)
                # print(size)
                # print(floor)
                # print(floor_top)
                # print(prices)

            except Exception as e:
                log.logger.error(e, exc_info=True)

        for size, prices in prices.items():
            self.prices_filter[size] = [min(prices), sum(prices) / len(prices), max(prices)]

            # 급매
            if (self.prices_filter[size][1] * 0.9 > self.prices_filter[size][0]):
                sale_percent = self.prices_filter[size][0] / self.prices_filter[size][1] * 100
                print('[%s] 평균가격 대비 %d 가격으로 저렴한 급매물 발견' % (size, math.ceil(sale_percent)))
                # self.prices_filter[size][3] = self.prices_filter[size][0] / self.prices_filter[size][1] * 100

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
    cgv = YoonaRentCalc()
    cgv.utf_8_reload()
    cgv.start()

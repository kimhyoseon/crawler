#-*- coding: utf-8 -*-

import re
import log
import telegrambot
from crawler2 import Crawler
from bs4 import BeautifulSoup
from decimal import Decimal

class Jejuair(Crawler):
    result_list = []
    process_count = 0

    def start(self):
        try:
            log.logger.info('[%s] collection start.' % self.name)

            if jejuair.connect(site_url='http://www.jejuair.net/jejuair/kr/main.do', is_proxy=False, default_driver='selenium',
                        is_chrome=False) is False:
                raise Exception('site connect fail')

            # 출발지 선택
            if self.selenium_click_by_xpath(tag={'tag': 'div', 'attr': 'id', 'name': 'divDepStn1'}) is False:
                raise Exception('selenium_click_by_xpath fail.')

            # 인천 선택
            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'aircode', 'name': 'ICN'}) is False:
                raise Exception('selenium_click_by_xpath fail.')

            # 도착지 리스트 획득
            if len(self.result_list) == 0:
                if self.get_return_country_list() is False:
                    raise Exception('get_return_country_list fail.')

            # 이번에 검색할 도착국가
            return_country = self.result_list[self.process_count]

            log.logger.info('searching start %s %s'%(return_country['title'], return_country['airport']))

            # 검색해야 할 도착지 리스트 선택
            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'aircode', 'name': self.result_list[self.process_count]['airport']}) is False:
                raise Exception('selenium_click_by_xpath fail.')

            # 날짜 선택완료 선택
            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'id', 'name': 'btnDoubleOk'}) is False:
                raise Exception('selenium_click_by_xpath fail. btnDoubleOk')

            # 예매하기 선택
            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'id', 'name': 'btnReservation'}) is False:
                raise Exception('selenium_click_by_xpath fail. btnReservation')

            # 항공권 검색 선택
            if self.selenium_click_by_xpath(tag={'tag': 'div', 'attr': 'id', 'name': 'btnSearch'}) is False:
                # 레이어 확인
                if self.selenium_click_by_xpath(tag={'tag': 'label', 'attr': 'for', 'name': 'svch3'}) is False:
                    raise Exception('selenium_click_by_xpath fail. svch3')
                else:
                    # 레이어 확인버튼 선택
                    if self.selenium_click_by_xpath(tag={'tag': 'div', 'attr': 'id', 'name': 'divAgreeConfirm'}) is False:
                        raise Exception('selenium_click_by_xpath fail. divAgreeConfirm')
                    else:
                        # 항공권 검색 선택
                        if self.selenium_click_by_xpath(tag={'tag': 'div', 'attr': 'id', 'name': 'btnSearch'}) is False:
                            raise Exception('selenium_click_by_xpath fail. btnSearch')

            # 가격 추출 시작
            for country in return_country:
                if self.collect_price() is False:
                    raise Exception('collect_price fail.')
                else:
                    self.process_count = self.process_count + 1
                    log.logger.info('searching complete %s %s' % (return_country['title'], return_country['airport']))
                    log.logger.info(return_country)
                    # 다음 국가 수집 시작
                    self.start()

        except IndexError:
            # 종료
            log.logger.info('[%s] collection complete.'%self.name)
            log.logger.info(self.result_list)
            self.send_message()
            self.driver.quit()
            exit()

        except Exception as e:
            log.logger.error(e, exc_info=True)
            # 국가 수집 다시 시작
            self.start()

    # 도착지 리스트 획득
    def get_return_country_list(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'id', 'name': 'divAirportTbl'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            for list_return in soup.find('div', id='divAirportTbl').find_all('dd'):
                try:
                    element = list_return.find('button')
                    title = element['title']
                    airport = element['aircode']
                    price_depature = price_return = 99999999999
                    date_depature = date_return = []
                    dict = {'title': title, 'airport': airport, 'price_depature': price_depature, 'price_return': price_return, 'date_depature': date_depature, 'date_return': date_return}
                    self.result_list.append(dict)
                except Exception as errorMessage:
                    pass

            # 테스트
            # test_result = self.result_list[0]
            # self.result_list = [test_result]

            return True
        except Exception as e:
            return False

    def collect_price(self):
        try:
            # 현재 검색중인 국가 정보
            return_country = self.result_list[self.process_count]

            # 가격 리스트 노출 확인
            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'id', 'name': 'divDepDateRoll'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # 출발 가격 엘리먼트
            depature_element = soup.find('div', id='divDepDateRoll').find('ul', class_='dataList').find_all('li', recursive=False)
            # 도착 가격 엘리먼트
            return_element = soup.find('div', id='divRetDateRoll').find('ul', class_='dataList').find_all('li', recursive=False)

            log.logger.info('collect_price')

            # 출발 가격 추출
            for depature in depature_element:
                try:
                    price = depature.find('strong', class_='price0').getText()
                    price = Decimal(re.sub(r'[^\d.]', '', price))
                    date = depature.find('span').getText()

                    # 목금토일만
                    #if any(s in date for s in ['목', '금', '토', '일']):
                    # 최저가와 같거나 작을 때
                    if price <= return_country['price_depature']:
                        # 최저가라면 날짜 초기화
                        if price < return_country['price_depature']:
                            return_country['date_depature'] = []

                        return_country['price_depature'] = price
                        return_country['date_depature'].append(date)

                except Exception as e:
                    pass

            # 도착 가격 추출
            for returns in return_element:
                try:
                    price = returns.find('strong', class_='price0').getText()
                    price = Decimal(re.sub(r'[^\d.]', '', price))
                    date = returns.find('span').getText()

                    # 토일월화만
                    # if any(s in date for s in ['토', '일', '월', '화']):
                    # 최저가와 같거나 작을 때
                    if price <= return_country['price_return']:
                        # 최저가라면 날짜 초기화
                        if price < return_country['price_return']:
                            self.date_return = []
                            return_country['price_return'] = price
                            return_country['date_return'].append(returns.find('span').getText())

                except Exception:
                    pass

            log.logger.info(return_country)

            # 다음 구간 검색 버튼 선택
            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'id', 'name': 'btnNextDep'}) is False:
                raise Exception('selenium_click_by_xpath fail.')

            # 다음 구간 버튼을 누른 후 알럿 확인 후 없다면 다시 수집
            if self.selenium_is_alert_exist() == False:
                self.collect_price()
            else:
                return True

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    def send_message(self):
        try:
            text = '[%s]'%self.name
            for result in self.result_list:
                if result['price_depature'] < 99999999999 or result['price_return'] < 99999999999:
                    text_each = '\n\n%s(%s):'%(result['title'], result['airport'])
                    if result['price_depature'] < 99999999999:
                        price_depature = 'depature price: {:0,.0f} won'.format(result['price_depature'])
                        date_depature = 'depature date: %s' % ",".join(result['date_depature'])
                        text_each += '\n%s\n%s' % (price_depature, date_depature)
                    if result['price_return'] < 99999999999:
                        price_return = 'return price: {:0,.0f} won'.format(result['price_return'])
                        date_return = 'return date: %s' % ",".join(result['date_return'])
                        text_each += '\n%s\n%s' % (price_return, date_return)

                    log.logger.info(text_each)
                    text += text_each

                telegrambot.send_message(text)
        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    jejuair = Jejuair()
    jejuair.start()

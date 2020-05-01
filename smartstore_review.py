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

class SmartstoreReview(Crawler):

    DETAIL_URL = 'http://sell.storefarm.naver.com'
    REVIEW_URL = 'https://sell.smartstore.naver.com/#/review/search'

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)
            self.channels = ['스마트스토어정성한끼', '스마트스토어쿠힛마트', '스마트스토어으아니']

            self.login()

            self.select_channel()

            self.destroy()
            exit()

        except Exception as e:
            self.destroy()
            log.logger.error(e, exc_info=True)

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
            sleep(5)

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

    def scan_page(self):
        try:
            sleep(5)

            self.remove_layer()

            # 문의/리뷰관리
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-lnb"]/div/div[1]/ul/li[4]/a') is False:
                raise Exception('selenium_click_by_xpath fail. 문의/리뷰관리')

            sleep(1)

            # 리뷰관리
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-lnb"]/div/div[1]/ul/li[4]/ul/li[3]/a') is False:
                raise Exception('selenium_click_by_xpath fail. 리뷰관리')

            sleep(10)

            # 레이어가 있다면 닫기
            try:
                if self.selenium_exist_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'}) is True:
                    self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'data-dismiss', 'name': 'mySmallModalLabel'})
            except:
                pass

            # 리뷰 검색 세팅

            sleep(3)

            # 오늘리뷰
            # if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[1]/div/ul/li[1]/div/div/ncp-datetime-range-picker2/div[1]/div/div/button[1]') is False:
            #     raise Exception('selenium_click_by_xpath fail. 오늘')

            # 답글여부
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[1]/div/ul/li[6]/div/div[1]/div[2]/div[2]/div') is False:
                raise Exception('selenium_click_by_xpath fail. 답글여부')

            # 미답글
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[1]/div/ul/li[6]/div/div[1]/div[2]/div[2]/div/div[2]/div/div[3]') is False:
                raise Exception('selenium_click_by_xpath fail. 미답글')

            # 구매자평점 (전체)
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[1]/div/ul/li[6]/div/div[1]/div[1]/div[2]/div/label[1]') is False:
                raise Exception('selenium_click_by_xpath fail. 미구매자평점 (전체)')

            # 구매자평점 (1점)
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[1]/div/ul/li[6]/div/div[1]/div[1]/div[2]/div/label[2]') is False:
                raise Exception('selenium_click_by_xpath fail. 미구매자평점 (1점)')

            # 구매자평점 (2점)
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[1]/div/ul/li[6]/div/div[1]/div[1]/div[2]/div/label[3]') is False:
                raise Exception('selenium_click_by_xpath fail. 미구매자평점 (2점)')

            # # 구매자평점 (5점)
            # if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[1]/div/ul/li[6]/div/div[1]/div[1]/div[2]/div/label[6]') is False:
            #     raise Exception('selenium_click_by_xpath fail. 미구매자평점 (5점)')

            # 검색
            if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[2]/div/button[1]') is False:
                raise Exception('selenium_click_by_xpath fail. 검색')

            sleep(2)

            # self.scroll_bottom(selectorParent='document.getElementsByClassName("ag-body-viewport")[0]', selectorDom='document.getElementsByClassName("ag-center-cols-container")[0]')

            self.review()

            # 리뷰수집 > 스크롤 내리기 반복
            # while True:
            #     try:
            #         if self.review() is False:
            #             break
            #
            #         # if self.scroll_bottom(selectorParent='document.getElementsByClassName("ag-body-viewport")[0]', selectorDom='document.getElementsByClassName("ag-center-cols-container")[0]') is False:
            #         #     break
            #
            #     except Exception as e:
            #         log.logger.error(e, exc_info=True)
            #         break

            return True
        except Exception as e:
            log.logger.error(e, exc_info=True)
            self.destroy()
            exit()

        return False

    # 리뷰 작업
    def review(self):
        try:
            # 리스트 획득
            list = self.driver.find_elements_by_xpath('//*[@id="seller-content"]/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[3]/div[2]/div/div/div')
            # list = self.driver.find_elements_by_xpath('//*[@id="center"]/div/div[4]/div[3]/div/div/div')

            is_success = False

            # print(len(list))

            if len(list) == 0:
                return False

            for li in list:
                try:
                    if li:
                        soup_order_info = BeautifulSoup(li.get_attribute('innerHTML'), 'html.parser')
                        tds = soup_order_info.find_all('div', class_='ag-cell')
                        # print(len(tds))
                        if len(tds) > 0:
                            review_link = li.find_element_by_xpath('.//div[contains(@col-id, "reviewContent")]/span/a')
                            review_text = review_link.text.strip()
                            review_id = li.find_element_by_xpath('.//div[contains(@col-id, "id")]').text.strip()
                            item_name = li.find_element_by_xpath('.//div[contains(@col-id, "productName")]').text.strip()
                            photo_empty_dash = li.find_element_by_xpath('.//div[contains(@col-id, "reviewAttach")]').text.strip()
                            score = li.find_element_by_xpath('.//div[contains(@col-id, "reviewScore")]').text.strip()

                            if not review_id or review_id in self.log:
                                continue

                            answer = self.get_review_message(review_text, item_name, photo_empty_dash, score)

                            message = ''
                            message += '\n\n'
                            message += '리뷰: %s' % (review_text)
                            if answer:
                                message += '\n'
                                message += '답변: %s' % (answer)
                            else:
                                message += '\n'
                                message += '실패: %s' % (self.reason)

                            # 테스트 로그보기
                            # print(message)
                            # continue

                            self.log = filewriter.slice_json_by_max_len(self.log, max_len=1000)
                            self.send_messge_and_save(review_id, message, 'kuhit_review')

                            if not answer or answer is False:
                                continue

                            # 리뷰 포커스
                            self.selenium_focus_by_xpath(element=review_link)

                            sleep(1)

                            # 리뷰 클릭
                            review_link.click()

                            sleep(2)

                            # 답글 입력
                            self.driver.execute_script('document.getElementsByClassName("form-control ng-valid-maxlength")[0].value = "' + answer + '";')
                            if self.selenium_input_text_by_xpath(text=' ', xpath='//*[@ng-model="vm.viewData.inputCommentContent"]', clear=False) is False:
                                raise Exception('selenium_input_text_by_xpath fail. chat_write')

                            sleep(1)

                            # exit()

                            # 답글 전송
                            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'progress-button', 'name': 'vm.func.createCommentContent()'}) is False:
                                raise Exception('selenium_click_by_xpath fail. 답글전송')

                            sleep(1)

                            # 답글 닫기
                            if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'ng-click', 'name': 'ok()'}) is False:
                                raise Exception('selenium_click_by_xpath fail. 답글닫기1')

                            sleep(1)

                            # 답글 닫기
                            if self.selenium_click_by_xpath(
                                    tag={'tag': 'button', 'attr': 'ng-click', 'name': 'vm.func.closeModal()'}) is False:
                                raise Exception('selenium_click_by_xpath fail. 답글닫기2')

                            sleep(1)

                            # print('reply done.')
                            # self.driver.save_screenshot('review_screenshot.png')
                            # self.destroy()
                            # exit()

                            is_success = True

                            if is_success == True:
                                # 리스트에 전부 달았다면 다시 검색버튼 클릭
                                if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[2]/div/button[1]') is False:
                                    raise Exception('selenium_click_by_xpath fail. 검색')

                                sleep(4)

                                # 다시 댓글달기
                                self.review()

                except Exception as e:
                    log.logger.error(e, exc_info=True)
                    continue
                    return False

            sleep(1)

            if is_success == True:
                # 리스트에 전부 달았다면 다시 검색버튼 클릭
                if self.selenium_click_by_xpath(xpath='//*[@id="seller-content"]/div/div[1]/form/div/div[2]/div/button[1]') is False:
                    raise Exception('selenium_click_by_xpath fail. 검색')

                sleep(4)

                # 다시 댓글달기
                self.review()

            return True

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    def get_review_message(self, review_text, item_name, photo_empty_dash, score):
        try:
            if not review_text or not item_name:
                return False

            self.reason = ''
            self.nagative = False

            # 리뷰 답글
            delevery_message = []

            log.logger.info('--------------')
            log.logger.info('리뷰: %s' % (' '.join(review_text)))

            # 100자가 넘고 사진이 있는 후기 패스 (베스트일 가능성이 있음)
            if len(review_text) > 200 and photo_empty_dash != '-' and score == '5':
                self.reason = '베스트후보'
                return False

            # 부정문구가 있는 리뷰 패스
            if '?' in review_text:
                self.reason = '?'
                self.nagative = True
            elif '하면' in review_text:
                self.reason = '하면'
                self.nagative = True
            elif '한데' in review_text:
                self.reason = '한데'
                self.nagative = True
            elif '좀' in review_text and '냄새' not in review_text:
                self.reason = '좀'
                self.nagative = True
            elif '그래도' in review_text:
                self.reason = '그래도'
                self.nagative = True
            elif '보단' in review_text:
                self.reason = '보단'
                self.nagative = True
            elif '듯' in review_text:
                self.reason = '듯'
                self.nagative = True
            elif 'ㅜ' in review_text and '감동' not in review_text:
                self.reason = 'ㅜ'
                self.nagative = True
            elif 'ㅠ' in review_text and '감동' not in review_text:
                self.reason = 'ㅠ'
                self.nagative = True
            elif '다만' in review_text:
                self.reason = '다만'
                self.nagative = True
            elif '결국' in review_text:
                self.reason = '결국'
                self.nagative = True
            elif '조금' in review_text:
                self.reason = '조금'
                self.nagative = True
            elif '차이' in review_text:
                self.reason = '차이'
                self.nagative = True
            elif '소리' in review_text:
                self.reason = '소리'
                self.nagative = True
            elif '불편' in review_text:
                self.reason = '불편'
                self.nagative = True
            elif '의문' in review_text:
                self.reason = '의문'
                self.nagative = True
            elif '근데' in review_text:
                self.reason = '근데'
                self.nagative = True
            elif '알' in review_text and '빠' in review_text:
                self.reason = '알+빠'
                self.nagative = True
            elif '후회' in review_text and '안' not in review_text  and '없' not in review_text:
                self.reason = '후회'
                self.nagative = True


            # 리뷰 케이스 분류
            if '감동' in review_text:
                delevery_message.append('남겨주신 리뷰에 저도 감동..ㅠ')
            elif '선물' in review_text or '효도' in review_text:
                delevery_message.append('다른 분들도 선물 용으로 많이 구매하세요~ 선물용으로 괜찮은 제품인듯 합니다!')
            elif '편해' in review_text or '편하' in review_text or '편리' in review_text:
                delevery_message.append('편하고 쉽게 사용하고 계시니 저희도 기분이 좋습니다^^')
            elif '유용' in review_text:
                delevery_message.append('유용하게 사용하고 계시니 저희도 기분이 좋습니다^^')
            elif '짱' in review_text and '짱짱' not in review_text:
                delevery_message.append('남겨주신 리뷰도 짱!')
            elif '굿' in review_text:
                delevery_message.append('남겨주신 리뷰도 굿굿입니다!')
            elif '임신' in review_text or '순산' in review_text or '출산' in review_text and '후' not in review_text and '하고' not in review_text:
                delevery_message.append('안전하고 조심히 사용해주시구 꼭 효과 보시기 바랄께요~')
            elif '보여' in review_text or '보이' in review_text or '듯' in review_text:
                delevery_message.append('자주 사용하시면서 제품의 효과를 보시길 응원하겠습니다!')
            elif '잘' in review_text and ('쓰고' in review_text or '사용하고' in review_text):
                delevery_message.append('잘 쓰고 계신다니 한결 마음이 편해지네요^^')
            elif '잘' in review_text and ('께요' in review_text or '습니다' in review_text or '사용' in review_text):
                delevery_message.append('제품 자주자주 사용하셔서 효과보시길 빌께요!')
            elif '꾸준히' in review_text or '열심히' in review_text:
                delevery_message.append('제품 자주자주 사용하셔서 효과보시길 빌께요!')
            elif '확실' in review_text and ('효과' in review_text or '느낌' in review_text):
                delevery_message.append('눈에 보이는 효과를 경험하고 계시니 저도 기분이 좋아지네요~ ')
            elif '효과' in review_text or '도움' in review_text or '시원' in review_text and '아직' not in review_text and '더' not in review_text and '면' not in review_text and '보고' not in review_text:
                delevery_message.append('저희 제품을 잘 사용해주시고 효과를 보신다니 감사합니다~')
            elif '재구매' in review_text and ('입' in review_text or '했' in review_text):
                delevery_message.append('재구매 너무너무 감사드려요~!')
            elif '번째' in review_text and ('구매' in review_text or '샀' in review_text):
                delevery_message.append('재구매 너무너무 감사드려요~!')
            elif '좋' in review_text or '기뻐' in review_text or '잘쓰' in review_text or '만족' in review_text or '조아' in review_text or '쁘' in review_text or '뻐' in review_text or '괜찮' in review_text or '갠차' in review_text or '잘샀' in review_text or '편안' in review_text or '맘에' in review_text:
                delevery_message.append('받아보신 제품이 맘에 드신다니 다행이예요~')
            elif '잘' in review_text and ('받' in review_text):
                delevery_message.append('소중하고 정성스런 후기 감사합니다~')
            elif '배송' in review_text and '배송비' not in review_text:
                delevery_message.append('로켓배송을 따라잡는 그날까지 더 힘내겠습니다!')
            elif '주문했어' in review_text or '주문했습' in review_text or '시켰어' in review_text or '시켰습' in review_text or '샀네' in review_text or '샀습' in review_text or '시작' in review_text or '아직' in review_text:
                delevery_message.append('주문하신 제품 꾸준히 잘 사용하셔서 효과 보시길 바래요~')

            if '냄새' in review_text and '없' not in review_text and '안나' not in review_text and '안났' not in review_text and '날라' not in review_text and '않' not in review_text and '정도' not in review_text and '거의' not in review_text and '크게' not in review_text and '그닥' not in review_text and '편' not in review_text and '괜' not in review_text and '갠' not in review_text and '빠' not in review_text:
                delevery_message.append('냄새는 불편하시겠지만 몇 일만 바람이 잘 부는 곳에 보관해주시면 좋아질꺼예요~')

            # 문구가 없다면 기본 문구로
            if len(delevery_message) == 0 or self.nagative is True:
                delevery_message = []
                delevery_message.append('더 만족을 드릴 수 있는 제품으로 인사드릴 수 있도록 노력하겠습니다! 소중하고 정성스런 후기 감사드려요~')
            else:
                # 마지막 추가 인사문구
                message_extra = self.get_review_message_extra(review_text, item_name)

                if message_extra:
                    delevery_message.append(message_extra)

            log.logger.info('답변: %s' % (' '.join(delevery_message)))

            return ' '.join(delevery_message)

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

        return False

    def get_review_message_extra(self, review_text, item_name):
        try:
            if not review_text or not item_name:
                return ''

            # 리뷰 답글
            delevery_message = []

            if '가성비' in review_text or '가격대비' in review_text or '저렴' in review_text:
                return '앞으로도 저렴하고 가성비 좋은 제품들로 찾아뵙겠습니다!'
            elif self.nagative == True:
                return '더 좋은 제품들로 만족을 드릴 수 있도록 노력하는 쿠힛이 되겠습니다~'
            else:
                return '앞으로도 더 만족하실 수 있는 좋은 제품들로 인사드릴께요!'

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return ''

        return ''

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

    # # 스크롤 아래로
    # def scroll_bottom(self, selectorParent=None, selectorDom=None, height=500):
    #     try:
    #         if selectorParent is None or selectorDom is None:
    #             return False
    #
    #         # Get scroll height
    #         last_height = self.driver.execute_script("return " + selectorParent + ".scrollTop")
    #         last_height = int(last_height)
    #
    #         try:
    #             # Scroll down to bottom
    #             self.driver.execute_script(selectorParent + ".scrollTo(0, " + str(height + last_height) + ");")
    #
    #             # Calculate new scroll height and compare with last scroll height
    #             new_height = self.driver.execute_script("return " + selectorParent + ".scrollTop")
    #             new_height = int(new_height)
    #             log.logger.info('scroll. (%s)' % (new_height))
    #
    #             if new_height == last_height:
    #                 return False
    #             else:
    #                 return True
    #         except Exception as e:
    #             log.logger.error(e, exc_info=True)
    #             return False
    #     except Exception as e:
    #         log.logger.error(e, exc_info=True)
    #         return False

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
                self.driver.save_screenshot('smartstore_screenshot.png')

                # 로그인 페이지로 이동
                if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'main.sellerlogin'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                sleep(1)

                if self.selenium_click_by_xpath(tag={'tag': 'a', 'attr': 'data-nclicks-code', 'name': 'login.nidlogin'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                sleep(2)

                self.driver.save_screenshot('smartstore_review_screenshot.png')

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
    cgv = SmartstoreReview()
    cgv.utf_8_reload()
    cgv.start()

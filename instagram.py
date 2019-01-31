#-*- coding: utf-8 -*-

import re
import log
import random
import filewriter
from time import sleep
from crawler2 import Crawler
from bs4 import BeautifulSoup
from datetime import datetime

class Instagram (Crawler):

    LOGIN_URL = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
    TAG_URL = 'https://www.instagram.com/explore/tags/'
    FOLLOW_CNT_NEW = 0;
    FOLLOW_CNT_OLD = 0;
    LIKE_CNT_NEW = 0;
    LIKE_CNT_OLD = 0;
    FAIL_CNT = 0;
    REPLY = [];

    def start(self):
        try:
            starttime = datetime.now()

            self.tag = filewriter.get_log_file('instagramcollecttag')

            if self.tag is None:
                raise Exception('Tags are not founded.')

            # 랜덤
            random.shuffle(self.tag)

            # 10개 (30분)
            # self.tag = self.tag[:10]

            self.login()

            self.scan_page()

            self.destroy()

            endtime = datetime.now()

            duration = int((endtime - starttime).total_seconds() / 60)

            log.logger.info('[duration %d min] Instagram process has completed. LIKE_CNT_NEW (%d), LIKE_CNT_OLD (%d), FOLLOW_CNT_NEW (%d), FOLLOW_CNT_OLD (%d), FAIL_CNT (%d)' % (duration, self.LIKE_CNT_NEW, self.LIKE_CNT_OLD, self.FOLLOW_CNT_NEW, self.FOLLOW_CNT_OLD, self.FAIL_CNT))

            self.start()

        except Exception as e:
            log.logger.error(e, exc_info=True)
            self.destroy()
            self.start()

    def login(self):
        try:
            if self.connect(site_url=self.LOGIN_URL, is_proxy=False,
                            default_driver='selenium',
                            is_chrome=True) is False:
                raise Exception('site connect fail')

            # 계정정보 가져오기
            account_data = filewriter.get_log_file(self.name + '_account')
            # log.logger.info(account_data)

            if account_data:
                if self.selenium_extract_by_xpath(tag={'tag': 'input', 'attr': 'name', 'name': 'username'}) is False:
                    raise Exception('selenium_extract_by_xpath fail.')

                # 아이디 입력
                if self.selenium_input_text_by_xpath(text=account_data[0], tag={'tag': 'input', 'attr': 'name', 'name': 'username'}) is False:
                    raise Exception('selenium_input_text_by_xpath fail. username')

                # 비번 입력
                if self.selenium_input_text_by_xpath(text=account_data[1], tag={'tag': 'input', 'attr': 'name', 'name': 'password'}) is False:
                    raise Exception('selenium_input_text_by_xpath fail. password')

                # 로그인하기 선택
                if self.selenium_click_by_xpath(tag={'tag': 'button', 'attr': 'type', 'name': 'submit'}) is False:
                    raise Exception('selenium_click_by_xpath fail. submit')

                sleep(3)

                log.logger.info('login success')

                return True
        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    def scan_page(self):
        try:
            if self.connect(site_url=self.TAG_URL + self.tag[0] + '/', is_proxy=False,
                            default_driver='selenium',
                            is_chrome=True) is False:
                raise Exception('site connect fail')

            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'EZdmt'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            # 상단의 인기게시글 (최대 9개)
            list = self.driver.find_element_by_xpath("//div[@class='EZdmt']").find_elements_by_xpath('.//div[contains(@class,"v1Nh3")]')

            # li = list[2]
            for li in list:
                try:
                    is_need_sleep = False

                    # 리스트 클릭
                    li.click()

                    # 레이어 기다림
                    if self.selenium_extract_by_xpath(xpath='//article[contains(@class,"M9sTE")]') is False:
                        raise Exception('selenium_extract_by_xpath fail.')

                    # 채널명
                    # channel_name = self.driver.find_element_by_xpath('//article[contains(@class,"M9sTE")]/header/div[2]/div[1]/div[1]/h2/a')
                    #
                    # if channel_name:
                    #     print(channel_name.text)

                    # # 좋아요
                    # btn_like = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/article/div[2]/section[1]/span[1]/button/span')
                    #
                    # if btn_like:
                    #     print(btn_like.get_attribute("class"))
                    #     print(btn_like.get_attribute("aria-label"))
                    #
                    #     if 'grey' in btn_like.get_attribute("class"):
                    #         self.selenium_click_by_xpath(xpath='/html/body/div[2]/div/div[2]/div/article/div[2]/section[1]/span[1]/button')
                    #         self.LIKE_CNT_NEW = self.LIKE_CNT_NEW + 1
                    #         is_need_sleep = True
                    #     else:
                    #         self.LIKE_CNT_OLD = self.LIKE_CNT_OLD + 1
                    #

                    # 팔로우 + 댓글
                    if len(self.REPLY) > 0:
                        btn_follow = self.driver.find_element_by_xpath('//article[contains(@class,"M9sTE")]/header/div[2]/div[1]/div[2]/button')

                        if btn_follow:
                            #print(btn_follow.text)

                            if '팔로우' in btn_follow.text or 'Follow' == btn_follow.text:
                                self.selenium_click_by_xpath(xpath='//article[contains(@class,"M9sTE")]/header/div[2]/div[1]/div[2]/button')
                                self.FOLLOW_CNT_NEW = self.FOLLOW_CNT_NEW + 1
                                is_need_sleep = True

                                # 댓글 달기
                                self.selenium_click_by_xpath(xpath='//article[contains(@class,"M9sTE")]/div[2]/section[1]/span[2]/button')

                                while (True):
                                    try:
                                        if len(self.REPLY) == 0:
                                            break
                                        if self.selenium_input_text_by_xpath(text=self.REPLY[0], xpath='//article[contains(@class,"M9sTE")]/div[2]/section[3]/div/form/textarea') is True:
                                            log.logger.info('%s' % (self.REPLY[0]))
                                            break
                                        self.REPLY.pop(0)
                                    except Exception:
                                        continue

                                self.selenium_enterkey_by_xpath(xpath='//article[contains(@class,"M9sTE")]/div[2]/section[3]/div/form/textarea')
                                self.REPLY.pop(0)
                            else:
                                self.FOLLOW_CNT_OLD = self.FOLLOW_CNT_OLD + 1

                    # 댓글 수집
                    try:
                        group_reply = self.driver.find_element_by_xpath('//article[contains(@class,"M9sTE")]/div[2]/div[1]/ul')
                        if group_reply:
                            soup_list_reply = BeautifulSoup(group_reply.get_attribute('innerHTML'), 'html.parser')
                            for reply in soup_list_reply.find_all('li'):
                                try:
                                    if reply:
                                        soup_reply = reply.find('div', class_='C4VMK').find('span')
                                        if soup_reply:
                                            if soup_reply.a:
                                                soup_reply.a.clear()
                                            reply_text = soup_reply.getText().strip()
                                            # print('%s (%d)' % (reply_text, len(reply_text)))
                                            if any(word in reply_text for word in ['선팔','맞팔','소통해','소통하','잘보고','잘보구','구경']):
                                                if len(reply_text) > 30:
                                                    continue
                                                if any(word in reply_text for word in ['#','무료','신발','그램','진행','세요','세용','운동','이쁘','이뻐','님','가세요','?','부탁','방문','옷','몸']):
                                                    continue
                                                reply_text = re.sub(' +', ' ', reply_text)
                                                # log.logger.info('%s' % (reply_text))

                                                if reply_text not in self.REPLY:
                                                    self.REPLY.append(reply_text)
                                except Exception:
                                    continue
                    except Exception as e:
                        log.logger.error(e, exc_info=True)
                        continue

                    # 작업이 있었다면 block을 피하기 위해 sleep
                    if is_need_sleep is True:
                        sleep_second = random.randint(20, 30)
                        log.logger.info('sleeping.. %d' % (sleep_second))
                        sleep(sleep_second)
                        is_need_sleep = True

                    # 레이어 닫기
                    self.selenium_click_by_xpath(xpath='//button[contains(@class,"ckWGn")]')

                except Exception as e:
                    self.FAIL_CNT = self.FAIL_CNT + 1
                    continue
                    # self.driver.save_screenshot('screenshot_error.png')
                    # log.logger.error(e, exc_info=True)

            self.tag.pop(0)

            if len(self.tag) > 0:
                self.scan_page()

        except Exception as e:
            # self.driver.save_screenshot('screenshot_error.png')
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    cgv = Instagram()
    cgv.utf_8_reload()
    cgv.start()

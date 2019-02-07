#-*- coding: utf-8 -*-

import re
import log
import random
import telegrambot
import filewriter
from time import sleep
from crawler2 import Crawler
from bs4 import BeautifulSoup
from datetime import datetime

class Instagram (Crawler):

    LOGIN_URL = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
    TAG_URL = 'https://www.instagram.com/explore/tags/'
    UNFOLLOW_URL = 'https://www.instagram.com/kuhitlove/'
    FOLLOW_CNT = 0;
    FOLLOW_ACCEPT_CNT = 0;
    FOLLOWING_CANCEL_CNT = 0;
    LIKE_CNT = 0;
    REPLY_CNT = 0;
    FAIL_CNT = 0;
    CRITICAL_CNT = 0;
    REPLY = [];
    FOLLOWERS = [];
    FOLLOWINGS = [];

    starttime = datetime.now()

    def start(self):
        try:
            # 복사된 태그 가져오기
            self.tag = filewriter.get_log_file('instagramcollecttag_copied')

            # 파일이 없다면 태그파일 복사본을 생성
            if self.tag is None or len(self.tag) == 0:
                self.tag = filewriter.get_log_file('instagramcollecttag')
                filewriter.save_log_file('instagramcollecttag_copied', self.tag)

            # 태그를 생성할 수 없다면 종료
            if self.tag is None:
                self.destroy()
                exit()

            # 태그 랜덤으로 섞기
            random.shuffle(self.tag)

            self.login()

            # 작업 시작
            self.scan_page()

            # 팔로워 정리
            if self.follower() is True:
                # 팔로윙 정리
                self.following()

            self.end_restart()

        except Exception as e:
            log.logger.error(e, exc_info=True)
            self.end_restart()

    def end_restart(self):
        duration = int((datetime.now() - self.starttime).total_seconds() / 60)
        log.logger.info('[duration %d min] Instagram process has completed. FOLLOW_CNT (%d), LIKE_CNT (%d), REPLY_CNT (%d), FOLLOW_ACCEPT_CNT (%d), FOLLOWING_CANCEL_CNT (%d), FAIL_CNT (%d)' % (duration, self.FOLLOW_CNT, self.LIKE_CNT, self.REPLY_CNT, self.FOLLOW_ACCEPT_CNT, self.FOLLOWING_CANCEL_CNT, self.FAIL_CNT))

        self.FOLLOW_CNT = 0;
        self.LIKE_CNT = 0;
        self.REPLY_CNT = 0;
        self.FAIL_CNT = 0;
        self.REPLY = [];

        self.destroy()
        exit()

        log.logger.info('Waiting browser rebooting.... (2 min)')

        # 2분 대기
        sleep(60 * 2)

        # 오류가 반복되면 텔레그램 메세지 보내고 종료
        if self.CRITICAL_CNT > 2:
            telegrambot.send_message('Instagram bot has just stopoed!!!!', 'dev')
            exit();

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
            self.CRITICAL_CNT = self.CRITICAL_CNT + 1
            self.end_restart()

        return False

    def scan_page(self):
        try:
            if self.connect(site_url=self.TAG_URL + self.tag[0] + '/', is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'EZdmt'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            # 상단의 인기게시글 (최대 9개)
            list = self.driver.find_element_by_xpath("//div[@class='EZdmt']").find_elements_by_xpath('.//div[contains(@class,"v1Nh3")]/a')

            for li in list:
                try:
                    self.is_need_sleep = False

                    # 레이어 열기
                    li.click()

                    # 레이어 기다림
                    if self.selenium_extract_by_xpath(xpath='//article[contains(@class,"M9sTE")]') is False:
                        raise Exception('selenium_extract_by_xpath fail.')

                    # 채널명
                    # channel_name = self.driver.find_element_by_xpath('//article[contains(@class,"M9sTE")]/header/div[2]/div[1]/div[1]/h2/a')
                    #
                    # if channel_name:
                    #     print(channel_name.text)

                    # 사용할 댓글이 없다면 수집만 먼저
                    # if len(self.REPLY) == 0:
                        # self.reply_collect()
                        # self.selenium_click_by_xpath(xpath='//button[contains(@class,"ckWGn")]')
                        # continue

                    # 일단 팔로우를 모아야 해서
                    if self.follow() is True:
                        self.like()
                        # self.reply_collect()
                        # self.reply_send()

                    # 작업이 있었다면 block을 피하기 위해 sleep
                    if self.is_need_sleep is True:
                        sleep_second = random.randint(100, 120)
                        log.logger.info('sleeping.. %d' % (sleep_second))
                        sleep(sleep_second)
                        self.is_need_sleep = True

                    # 레이어 닫기
                    self.selenium_click_by_xpath(xpath='//button[contains(@class,"ckWGn")]')

                except Exception as e:
                    log.logger.error(e, exc_info=True)
                    self.FAIL_CNT = self.FAIL_CNT + 1
                    break
                    # self.driver.save_screenshot('screenshot_error.png')

            self.tag.pop(0)
            filewriter.save_log_file('instagramcollecttag_copied', self.tag)

            self.CRITICAL_CNT = 0

            # 팔로우 100개 마다 브라우저 리셋
            duration = int((datetime.now() - self.starttime).total_seconds() / 60)
            print(duration)
            # 30분 동안 작업 했다면 종료
            if duration > 30:
            # if (self.FOLLOW_CNT > 5):
                return True

            if len(self.tag) > 0:
                self.scan_page()

        except Exception as e:
            # self.driver.save_screenshot('screenshot_error.png')
            self.CRITICAL_CNT = self.CRITICAL_CNT + 1
            log.logger.error(e, exc_info=True)
            self.end_restart()

    # 팔로우
    def follow(self):
        try:
            btn_follow = self.driver.find_element_by_xpath('//article[contains(@class,"M9sTE")]/header/div[2]/div[1]/div[2]/button')

            if btn_follow:
                if '팔로우' in btn_follow.text or 'Follow' == btn_follow.text:
                    # 팔로우 버튼 클릭
                    self.selenium_click_by_xpath(xpath='//article[contains(@class,"M9sTE")]/header/div[2]/div[1]/div[2]/button')
                    self.FOLLOW_CNT = self.FOLLOW_CNT + 1
                    self.is_need_sleep = True

                    #             # 사진분석
                    #             try:
                    #                 reply_prev = ''
                    #
                    #                 photo_analytics = self.driver.find_element_by_xpath('//article[contains(@class,"M9sTE")]/div[1]/div/div/div[1]').find_element_by_xpath('.//img')
                    #
                    #                 if photo_analytics:
                    #                     photo_analytics_text = photo_analytics.get_attribute("alt")
                    #                     if photo_analytics_text:
                    #                         if any(word in photo_analytics_text for word in ['selfie']):
                    #                             reply_prev = '외모가 미쳤다!! '
                    #                         elif any(word in photo_analytics_text for word in ['1 person']):
                    #                             reply_prev = '멋짐이 폭팔 '
                    #                         elif any(word in photo_analytics_text for word in ['food']):
                    #                             reply_prev = '아 배고파......ㅜ '
                    #                         elif any(word in photo_analytics_text for word in ['nature']):
                    #                             reply_prev = '사진 퀄리티 대박........ '
                    #                         elif any(word in photo_analytics_text for word in ['dog']):
                    #                             reply_prev = '멍멍이 귀욤귀욤~ '
                    #
                    #                         print(photo_analytics_text)
                    #             except Exception as e:
                    #                 log.logger.error(e, exc_info=True)
                    #
                    #

                    return True

        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    # 댓글 달기
    def reply_send(self):
        try:
            # 댓글은 팔로우 3회당 1회씩 적자
            if self.FOLLOW_CNT % 3 != 0:
                return True

            # 댓글 달기
            self.selenium_click_by_xpath(xpath='//article[contains(@class,"M9sTE")]/div[2]/section[1]/span[2]/button')

            # chrome에서 허용하는 댓글이 아니라면 제거하면서 탐색
            while (True):
                try:
                    # 댓글이 없다면 종료
                    if len(self.REPLY) == 0:
                        break

                    # 댓글 입력
                    if self.selenium_input_text_by_xpath(text=self.REPLY[0], xpath='//article[contains(@class,"M9sTE")]/div[2]/section[3]/div/form/textarea') is True:
                        # 엔터
                        self.selenium_enterkey_by_xpath(xpath='//article[contains(@class,"M9sTE")]/div[2]/section[3]/div/form/textarea')
                        log.logger.info('%s' % (self.REPLY[0]))
                        # log.logger.info(self.REPLY)
                        self.REPLY_CNT = self.REPLY_CNT + 1
                        self.REPLY.pop(0)
                        break

                    self.REPLY.pop(0)
                except Exception:
                    continue

            return True

        except Exception as e:
            log.logger.error(e, exc_info=True)
            # return False

        return False

    # 좋아요
    def like(self):
        try:
            # 좋아요
            btn_like = self.driver.find_element_by_xpath('//article[contains(@class,"M9sTE")]/div[2]/section[1]/span[1]/button/span')

            if btn_like:
                if 'grey' in btn_like.get_attribute("class"):
                    # 좋아요 버튼 클릭
                    self.selenium_click_by_xpath(xpath='//article[contains(@class,"M9sTE")]/div[2]/section[1]/span[1]/button')
                    self.LIKE_CNT = self.LIKE_CNT + 1
                    self.is_need_sleep = True

                    return True

        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    # 댓글 수집
    def reply_collect(self):
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
                                # 허용 문구
                                if any(word in reply_text for word in ['선팔', '맞팔', '소통해', '소통하', '잘보고', '잘보구', '구경']):
                                    # 길이 제한
                                    if len(reply_text) > 30:
                                        continue
                                    # 금지 문구
                                    if any(word in reply_text for word in ['넹','필라','요가','군요','귀','입니다','염','덕','레슨','맘', '육아', '#', '무료', '신발', '그램', '진행', '세', '셔', '운동', '이쁘', '이뻐', '예', '쁜', '님', '가세요', '?', '부탁', '방문', '옷', '몸','누나','옆구리']):
                                        continue

                                    # 공백 제거
                                    reply_text = re.sub(' +', ' ', reply_text)
                                    # log.logger.info('%s' % (reply_text))

                                    # 댓글 목록에 추가
                                    if reply_text not in self.REPLY:
                                        self.REPLY.append(reply_text)
                    except Exception:
                        continue

                return True

        except Exception:
            log.logger.error(e, exc_info=True)
            # return False

        return False

    # 팔로워 정리
    def follower(self):
        try:
            if self.connect(site_url=self.UNFOLLOW_URL, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            if self.selenium_click_by_xpath(xpath='//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a') is False:
                raise Exception('selenium_extract_by_xpath fail.')

            if self.selenium_extract_by_xpath(xpath='/html/body/div[2]/div/div[2]/ul/div/li[1]') is False:
                raise Exception('selenium_extract_by_xpath fail.')

            # 스크롤 내려서 모두 불러오기
            self.scroll_bottom(selectorParent='document.getElementsByClassName("isgrP")[0]', selectorDom='document.getElementsByClassName("_6xe7A")[0]')

            # 맞팔이 아닌 경우 팔로우 클릭
            list = self.driver.find_elements_by_xpath('/html/body/div[2]/div/div[2]/ul/div/li')

            for li in list:
                try:
                    accept_follow = li.find_element_by_xpath('.//button[text() = "Follow"]')
                    if accept_follow:
                        accept_follow.click()
                        self.FOLLOW_ACCEPT_CNT = self.FOLLOW_ACCEPT_CNT + 1
                        log.logger.info('New follow accepted.')
                        sleep(2)
                except Exception as e:
                    continue

            followers = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/ul')
            if followers:
                soup_list_follewers = BeautifulSoup(followers.get_attribute('innerHTML'), 'html.parser')
                for follower in soup_list_follewers.find_all('li'):
                    try:
                        if follower:
                            soup_follower_link = follower.find('a', class_='FPmhX')
                            if soup_follower_link:
                                follower_id = soup_follower_link.getText().strip()
                                # print('%s' % (follower_id))

                                # 팔로워 목록에 추가
                                if follower_id not in self.FOLLOWERS:
                                    self.FOLLOWERS.append(follower_id)
                    except Exception:
                        continue

            print(self.FOLLOWERS)

            self.selenium_click_by_xpath(xpath='/html/body/div[2]/div/div[1]/div/div[2]/button')

            return True

        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    # 팔로윙 정리
    def following(self):
        try:
            if self.selenium_click_by_xpath(
                    xpath='//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a') is False:
                raise Exception('selenium_extract_by_xpath fail.')

            if self.selenium_extract_by_xpath(xpath='/html/body/div[2]/div/div[2]/ul/div/li[1]') is False:
                raise Exception('selenium_extract_by_xpath fail.')

            # 스크롤 내려서 모두 불러오기
            self.scroll_bottom(selectorParent='document.getElementsByClassName("isgrP")[0]',
                               selectorDom='document.getElementsByClassName("_6xe7A")[0]')

            # 아래부터 팔로우 취소
            list = self.driver.find_elements_by_xpath('/html/body/div[2]/div/div[2]/ul/div/li')

            for li in reversed(list):
                try:
                    # 15분동안 30회 취소 후 종료
                    if self.FOLLOWING_CANCEL_CNT > 30:
                        break;

                    elem_following = li.find_element_by_xpath('.//a[contains(@class,"FPmhX")]')
                    if elem_following:
                        id_following = elem_following.text
                        if id_following not in self.FOLLOWERS:
                            cancel_following = li.find_element_by_xpath('.//button[contains(@class,"_8A5w5")]')
                            if cancel_following:
                                cancel_following.click()
                                self.selenium_click_by_xpath(xpath='/html/body/div[3]/div/div/div[3]/button[1]')
                                self.FOLLOWING_CANCEL_CNT = self.FOLLOWING_CANCEL_CNT + 1
                                log.logger.info('following canceled. (%s)' % (id_following))
                                sleep(30)
                except Exception as e:
                    continue

            return True

        except Exception as e:
            log.logger.error(e, exc_info=True)

        return False

    # 스크롤 가장 아래로
    def scroll_bottom(self, selectorParent=None, selectorDom=None):
        try:
            if selectorParent is None or selectorDom is None:
                return False

            limit = 0

            # Get scroll height
            last_height = self.driver.execute_script("return "+selectorDom+".scrollHeight")

            while True:
                # if limit > 50:
                #     break;

                # Scroll down to bottom
                self.driver.execute_script(selectorParent+".scrollTo(0, "+selectorDom+".scrollHeight);")

                # Wait to load page
                sleep(1)

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return "+selectorDom+".scrollHeight")
                limit = limit + 1
                if new_height == last_height:
                    break
                last_height = new_height

            # log.logger.info('last_height: %d' % (last_height))
        except Exception as e:
            log.logger.error(e, exc_info=True)

if __name__ == "__main__":
    cgv = Instagram()
    cgv.utf_8_reload()
    cgv.start()

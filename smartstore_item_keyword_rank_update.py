#-*- coding: utf-8 -*-

import log
import pymysql
import filewriter
from time import sleep
from pytz import timezone
from datetime import datetime, timedelta
from crawler2 import Crawler

class SmartstoreItemKeywordRankUpdate(Crawler):

    SHOPPING_URL = 'https://search.shopping.naver.com/search/all?frm=NVSHATC&pagingSize=40&productSet=total&sort=rel&timestamp=&viewType=thumb&pagingIndex=%s&query=%s'

    def start(self):
        try:
            # self.results = []
            
            self.mysql = filewriter.get_log_file('mysql')

            self.main_keywords = [
                ['리프팅밴드', 'https://smartstore.naver.com/kuhit/products/4269217982']
            ]

            # 날짜
            today = datetime.now(timezone('Asia/Seoul'))
            today = today.strftime('%Y%m%d')
            today = str(today)
            log.logger.info(today)

            # MySQL Connection 연결
            conn = pymysql.connect(host=self.mysql[0], db=self.mysql[1], user=self.mysql[2], password=self.mysql[3],
                                   charset='utf8')

            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()

            # 상품별로 loop
            for main_keyword in self.main_keywords:
                # 메인키워드 정보
                keyword_current = main_keyword[0]
                url_current = main_keyword[1]

                sql = "SELECT id FROM keywords WHERE keyword='" + keyword_current + "';"
                curs.execute(sql)

                # 데이타 Fetch
                rows = curs.fetchall()
                keyword_id_current = str(rows[0][0])

                # print(keyword_id_current)
                # conn.close()
                # exit()

                # 메인키워드에 넣을 상품정보 가져오기
                title, tag = self.getInfoItem(url=url_current)
                
                # 연관키워드 초기화
                self.keywords = []                

                # 연관키워드 정보 가져오기
                sql = "SELECT keyword, id FROM keywords WHERE id in (SELECT keywords_rel_id FROM keywords_rel WHERE keywords_id IN (SELECT id FROM keywords WHERE keyword='" + keyword_current + "'));"
                curs.execute(sql)

                # 데이타 Fetch
                rows = curs.fetchall()

                if rows:
                    for row in rows:
                        # 가져온 연관키워드 정보
                        self.keywords.append([row[0], row[1]])

                # 상품의 연관 키워드별 loop
                for keyword in self.keywords:
                    self.rank = 1
                    keyword_rel_current = keyword[0]
                    keyword_rel_id_current = str(keyword[1])
                    self.findRank(keyword=keyword_rel_current, page=1)
                    keyword_rel_title = ''
                    keyword_rel_tag = ''

                    if keyword_rel_id_current == keyword_id_current:
                        keyword_rel_title = title
                        keyword_rel_tag = tag


                    # 기록이 있는지 확인
                    sql = "SELECT count(*) FROM keywords_ranking WHERE date='" + today + "' AND keywords_id='" + keyword_id_current + "' AND keywords_rel_id='" + keyword_rel_id_current + "';"
                    curs.execute(sql)
                    rows = curs.fetchall()

                    # print(rows[0][0])
                    # conn.close()
                    # exit()

                    if rows[0][0] == 0:
                        sql = "INSERT INTO keywords_ranking (date, keywords_id, keywords_rel_id, ranking, title, tag) VALUES ('" + today + "', '" + keyword_id_current + "', '" + keyword_rel_id_current + "', '" + str(self.rank) + "', '" + keyword_rel_title + "', '" + keyword_rel_tag + "');"
                    else:
                        sql = "UPDATE keywords_ranking SET ranking='" + str(self.rank) + "', title='" + keyword_rel_title + "', tag='" + keyword_rel_tag + "' WHERE date='" + today + "' AND keywords_id='" + keyword_id_current + "' AND keywords_rel_id='" + keyword_rel_id_current + "';"

                    log.logger.info(sql)
                    curs.execute(sql)
                    conn.commit()

                # for result in self.results:
                #     log.logger.info(result)


            conn.close()
            self.destroy()
            exit()

        except Exception as e:
            conn.close()
            self.destroy()
            log.logger.error(e, exc_info=True)
            exit()
    
    # 상품 정보 획득
    def getInfoItem(self, url=''):
        # 사이트 접속
        if self.connect(site_url=url, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
            raise Exception('site connect fail')

        title = self.driver.find_element_by_xpath('//dt[@class="prd_name"]/strong').text.strip()
        tags = self.driver.find_elements_by_xpath('//div[@class="goods_tag"]/ul/li')
        tags_array = []

        for i, tag in enumerate(tags):
            try:
                tag_text = tag.text.strip()
                tags_array.append(tag_text)

            except Exception as e:
                log.logger.error(e, exc_info=True)
                pass

        tag = ','.join(tags_array)
        log.logger.info('%s / %s' % (title, tag))
        return title, tag


    def findRank(self, keyword='', page=1):

        log.logger.info('%s %d페이지 탐색 (순위:%d)' % (keyword, page, self.rank))

        is_founded = False
        url = self.SHOPPING_URL % (page, keyword)

        # 사이트 접속
        if self.connect(site_url=url, is_proxy=False, default_driver='selenium', is_chrome=True) is False:
            raise Exception('site connect fail')

        # 스크롤 아래로 1회
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        sleep(1)

        #리스트 읽기
        uls = self.driver.find_elements_by_xpath('//ul[@class="imgList_search_list__32YnP"]')

        for i, ul in enumerate(uls):
            try:
                if ul:
                    lis = ul.find_elements_by_xpath('.//li')

                    for j, li in enumerate(lis):
                        try:
                            channel_name = li.find_element_by_xpath('.//em[@class="imgList_mall_title__3fLr4"]').text.strip()
                            title = li.find_element_by_xpath('.//a[@class="imgList_link__XUg6J"]').text.strip()

                            if channel_name and title:
                                if channel_name in ['쿠힛', '으아니', '정성한끼']:
                                    message = '%s - 페이지:%d, 순위:%d 발견 [%s]%s' % (keyword, page, self.rank, channel_name, title)
                                    # self.results.append(message)
                                    log.logger.info(message)
                                    is_founded = True

                        except Exception as e:
                            # log.logger.error(e, exc_info=True)
                            pass

                        if is_founded is False:
                            self.rank = self.rank + 1

            except Exception as e:
                log.logger.error(e, exc_info=True)
                self.destroy()
                exit()

        if is_founded is False:
            if page > 4:
                message = '%s - 페이지:%d, 순위:%d 못찾음' % (keyword, page, self.rank)
                # self.results.append(message)
                log.logger.info(message)
                self.rank = 0
                return True
            else:
                self.findRank(keyword=keyword, page=page+1)

        return True


if __name__ == "__main__":
    jshk = SmartstoreItemKeywordRankUpdate()
    jshk.utf_8_reload()
    jshk.start()

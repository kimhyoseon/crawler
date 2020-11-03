#-*- coding: utf-8 -*-

import log
import filewriter
from crawler2 import Crawler
from bs4 import BeautifulSoup

class Encar(Crawler):

    DETAIL_URL = 'http://www.encar.com'

    def start(self):
        try:
            self.log = filewriter.get_log_file(self.name)

            # 제네시스DH 주행거리 14만 이하, 주행보조, 엔카진단
            if self.connect(site_url='http://www.encar.com/dc/dc_carsearchlist.do?carType=kor&searchType=model&wtClick_kor=003&TG.R=A#!%7B%22action%22%3A%22(And.Hidden.N._.(C.CarType.Y._.(C.Manufacturer.%ED%98%84%EB%8C%80._.(C.ModelGroup.%EC%A0%9C%EB%84%A4%EC%8B%9C%EC%8A%A4._.Model.%EC%A0%9C%EB%84%A4%EC%8B%9C%EC%8A%A4%20DH.)))_.Trust.Warranty._.Options.%EC%B0%A8%EC%84%A0%EC%9D%B4%ED%83%88%20%EA%B2%BD%EB%B3%B4%20%EC%8B%9C%EC%8A%A4%ED%85%9C(LDWS_)._.Condition.Inspection._.Condition.Record._.Mileage.range(..140000).)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22PriceAsc%22%2C%22page%22%3A1%2C%22limit%22%3A20%7D', is_proxy=False, default_driver='selenium', is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            # 전기차 주행보조
            if self.connect(site_url='http://www.encar.com/ev/ev_carsearchlist.do?carType=ev&searchType=model&TG.R=D#!%7B%22action%22%3A%22(And.Hidden.N._.CarType.A._.Options.%EC%B0%A8%EC%84%A0%EC%9D%B4%ED%83%88%20%EA%B2%BD%EB%B3%B4%20%EC%8B%9C%EC%8A%A4%ED%85%9C(LDWS_)._.Options.%ED%81%AC%EB%A3%A8%EC%A6%88%20%EC%BB%A8%ED%8A%B8%EB%A1%A4(%EC%96%B4%EB%8C%91%ED%8B%B0%EB%B8%8C_)._.(C.GreenType.Y._.EvType.%EC%A0%84%EA%B8%B0%EC%B0%A8.))%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22PriceAsc%22%2C%22page%22%3A1%2C%22limit%22%3A20%7D', is_proxy=False, default_driver='selenium', is_chrome=False) is False:
                raise Exception('site connect fail')

            self.scan_page()

            self.destroy()

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def scan_page(self):
        try:
            if self.selenium_extract_by_xpath(tag={'tag': 'table', 'attr': 'class', 'name': 'car_list'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('tbody', id='sr_normal')

            # 핫딜리스트
            if element:
                for list in element.find_all('tr'):
                    try:
                        cls = list.find('span', class_='cls').getText().strip()
                        dtl = list.find('span', class_='dtl').getText().strip()
                        year = list.find('span', class_='yer').getText().strip()
                        km = list.find('span', class_='km').getText().strip()
                        link = self.DETAIL_URL + list.find('a', class_='newLink _link')['href'].strip()
                        id = link.split('carid=')[1]
                        id = id.split('&')[0]

                        # print(cls)
                        # print(dtl)
                        # print(year)
                        # print(km)
                        # print(link)
                        # print(id)
                        # exit()

                        text = cls + ' ' + dtl + '\n' + year + ' ' + km + '\n' + link + '\n' + link

                        self.send_messge_and_save(id, text, 'encar')

                    except Exception as e:
                        continue

        except Exception as e:
            log.logger.error(e, exc_info=True)

    def get_item_link(self, url=None):
        try:
            if self.connect(site_url=url, is_proxy=False, default_driver='selenium',
                        is_chrome=False) is False:
                raise Exception('site connect fail')

            if self.selenium_extract_by_xpath(tag={'tag': 'div', 'attr': 'class', 'name': 'wordfix'}) is False:
                raise Exception('selenium_extract_by_xpath fail.')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            element = soup.find('div', class_='wordfix')

            # 핫딜리스트
            if element:
                try:
                    if not element.find('a', recursive=False):
                        raise Exception('link is not founded!.')

                    link = element.find('a', recursive=False).getText()

                    if link is None:
                        raise Exception('link is not founded.')

                    encarLinkGenerator = encarLinkGenerator()
                    apiliateLink = encarLinkGenerator.genLink(url=link)

                    if apiliateLink is None:
                        raise Exception('apiliateLink is not generated.')

                    return apiliateLink

                except Exception as e:
                    log.logger.error(e, exc_info=True)
                    return False
            else:
                return False

        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

if __name__ == "__main__":
    encar = Encar()
    encar.utf_8_reload()
    encar.start()

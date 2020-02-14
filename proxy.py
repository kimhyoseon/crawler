#-*- coding: utf-8 -*-

import log
import requests
from crawler2 import Crawler
from bs4 import BeautifulSoup

class Proxy(Crawler):

    ips = []

    def start(self):
        try:
            self.extract()

            # print(self.ips)
            # exit()

        except Exception as e:
            self.driver.quit()
            self.destroy()

            log.logger.error(e, exc_info=True)
            return False

    def get(self):
        try:
            self.extract()

            if len(self.ips) == 0:
                return False

            return self.ips
        except Exception as e:
            self.driver.quit()
            self.destroy()

            log.logger.error(e, exc_info=True)
            return False

    # 내용 추출 정의
    def extract(self):
        try:
            if self.connect(site_url='https://www.proxynova.com/proxy-server-list/country-kr/', is_proxy=False,
                            default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            trs = soup.findAll('tr', {'data-proxy-id': True})

            # print(len(trs))

            for tr in trs:
                tds = tr.findAll('td')
                [s.extract() for s in tds[0]('script')]
                ip = tds[0].getText().strip() + ':' + tds[1].getText().strip()
                self.ips.append(ip)
        except:
            pass

        try:
            if self.connect(site_url='http://freeproxylists.net/kr.html', is_proxy=False, default_driver='selenium',
                            is_chrome=True) is False:
                raise Exception('site connect fail')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            trs = soup.findAll('tr', {'class': ['Odd', 'Even']})

            for tr in trs:
                tds = tr.findAll('td')
                [s.extract() for s in tds[0]('script')]
                ip = tds[0].getText() + ':' + tds[1].getText()
                self.ips.append(ip)
        except:
            pass

        try:
            if self.connect(site_url='https://premproxy.com/proxy-by-country/Korea-Republic-of-01.htm', is_proxy=False,
                            default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            trs = soup.findAll('td', {'data-label': 'IP:port '})

            for tr in trs:
                [s.extract() for s in tr('script')]
                self.ips.append(tr.getText())
        except:
            pass

        try:
            if self.connect(site_url='https://proxygather.com/proxylist/country?c=Republic+of+Korea', is_proxy=False,
                            default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            trs = soup.findAll('tr')

            for tr in trs:
                if (tr.has_attr('prx')):
                    self.ips.append(tr['prx'])
        except:
            pass

        self.driver.quit()
        self.destroy()

if __name__ == "__main__":
    proxy = Proxy()
    # proxy.start()
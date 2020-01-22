#-*- coding: utf-8 -*-

import log
import requests
from crawler2 import Crawler
from bs4 import BeautifulSoup

class Proxy(Crawler):
    def start(self):
        try:
            ips = []
            if self.connect(site_url='http://spys.one/free-proxy-list/KR/', is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            trs = soup.findAll(True, {"class":["spy1xx", "spy1x"]})

            for tr in trs:
                tds = tr.findAll('td')
                scheme = tds[1].getText()

                if scheme == 'HTTPS' or scheme == 'HTTP':
                    [s.extract() for s in tds[0]('script')]
                    ips.append(tds[0].getText())

            self.destroy()
            exit()
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    def get(self):
        try:
            ips = []
            if self.connect(site_url='http://spys.one/free-proxy-list/KR/', is_proxy=False, default_driver='selenium', is_chrome=True) is False:
                raise Exception('site connect fail')

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            trs = soup.findAll(True, {"class":["spy1xx", "spy1x"]})

            for tr in trs:
                tds = tr.findAll('td')
                scheme = tds[1].getText()

                if scheme == 'HTTPS' or scheme == 'HTTP':
                    [s.extract() for s in tds[0]('script')]
                    ips.append(tds[0].getText())

            self.driver.quit()
            self.destroy()

            if len(ips) == 0:
                return False

            return ips
        except Exception as e:
            log.logger.error(e, exc_info=True)
            return False

    # 내용 추출 정의
    def extract(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('table', id='tbl_proxy_list')

        list_ip = []

        # if element:
        #     for idx, list in enumerate(element.find_all('tr')):
        #         try:
        #             if idx == 0:
        #                 continue
        #
        #             td = list.find_all('td')
        #
        #             ip_address = td[0].find('abbr').getText()
        #             ip_address = ip_address.split(';')
        #             ip_address = ip_address[1].strip()
        #             port = td[1].find('a').getText().strip()
        #
        #             if ip_address and port:
        #                 socket.inet_aton(ip_address)
        #                 ip_port = ip_address + ':' + port
        #                 request_status = requests.get('http://' + ip_address, timeout=3).status_code
        #                 print(request_status)
        #
        #                 if request_status == 200:
        #                     list_ip.append(ip_port)
        #
        #         except Exception as errorMessage:
        #             print(errorMessage)
        #             pass
        #
        #     print(len(list_ip))
        #
        #     if len(list_ip) > 0:
        #         filewriter.save_log_file(self.name, list_ip)

if __name__ == "__main__":
    proxy = Proxy()
    # proxy.start()
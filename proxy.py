#-*- coding: utf-8 -*-

import socket
import requests
from crawler import Crawler
from bs4 import BeautifulSoup

class Proxy(Crawler):

    # 크롤링 할 사이트 주소를 입력
    SITE_URL = ['http://www.proxynova.com/proxy-server-list/country-kr/']

    IS_REPORT = False

    # 내용 추출 정의
    def extract(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('table', id='tbl_proxy_list')

        list_ip = []

        if element:
            for idx, list in enumerate(element.find_all('tr')):
                try:
                    if idx == 0:
                        continue

                    td = list.find_all('td')

                    ip_address = td[0].find('abbr')['title']
                    port = td[1].find('a').getText()
                    if ip_address and port:
                        socket.inet_aton(ip_address)
                        ip_port = ip_address + ':' + port
                        request_status = requests.get('http://' + ip_address, timeout=1).status_code
                        if request_status == 200:
                            list_ip.append(ip_port)

                except Exception as errorMessage:
                    #print(errorMessage)
                    pass

            if len(list_ip) > 0:
                self.save_file(list_ip)

if __name__ == "__main__":
    proxy = Proxy()
    proxy.start()
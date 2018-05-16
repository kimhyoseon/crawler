#-*- coding: utf-8 -*-

import log
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Shortener:

    ACCESS_TOKEN_BITLY = 'e7ba39901afa8c862e6dd463f92c5585ced96c91';
    ACCESS_TOKEN_POLR = '8659e8eea0fb0735cb4c98c93b6057';

    # def __init__(self):

    def genShortenerBitly(self, url=None):
        query_params = {
            'access_token': self.ACCESS_TOKEN_BITLY,
            'longUrl': url
        }

        endpoint = 'https://api-ssl.bitly.com/v3/shorten'
        response = requests.get(endpoint, params=query_params, verify=False)

        data = response.json()

        if not data['status_code'] == 200:
            log.logger.error("Unexpected status_code: {} in bitly response. {}".format(data['status_code'], response.text), exc_info=True)

        return data['data']['url']

    def genShortenerPolr(self, url=None):
        query_params = {
            'key': self.ACCESS_TOKEN_POLR,
            'url': url
        }

        endpoint = 'http://demo.polr.me/api/v2/action/shorten'
        response = requests.get(endpoint, params=query_params, verify=False)

        if not response.status_code == 200:
            log.logger.error("Unexpected status_code: {} in polr response. {}".format(response.status_code, response.text), exc_info=True)

        return response.text

if __name__ == "__main__":
    shortener = Shortener()
    #tinyurl
    #print(shortener.genShortenerPolr(url='https://click.linkprice.com/click.php?m=gmarket&a=A100528376&l=9999&l_cd1=3&l_cd2=0&tu=http://item.gmarket.co.kr/detailview/item.asp?goodscode=1401721949'))

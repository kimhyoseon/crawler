#-*- coding: utf-8 -*-

import os
import xlrd
#import urllib3
import tldextract
from shortener import Shortener

class PpomppuLinkGenerator:
    LINKPRICE_ID = 'A100528376'

    def __init__(self):
        self.listLinkPrice = self.getLinkPriceData()

    def genLink(self, url=None):
        extracted = tldextract.extract(url)
        domain = "{}.{}".format(extracted.domain, extracted.suffix)

        if domain in self.listLinkPrice.keys():
            #shortener = Shortener()
            #return shortener.genShortenerPolr(url=self.getLinkLinkPrice(key=self.listLinkPrice[domain], url=url))
            return self.getLinkLinkPrice(key=self.listLinkPrice[domain], url=url)

        return False

    def getLinkPriceData(self):
        data = dict()

        wb = xlrd.open_workbook(os.path.join(os.path.join(os.path.dirname(__file__), 'data'), 'linkprice.xlsx'))

        # Get the first sheet either by index or by name
        sh = wb.sheet_by_index(0)

        # Iterate through rows, returning each as a list that you can index:
        for rownum in range(sh.nrows):
            if rownum == 0:
                continue

            extracted = tldextract.extract(sh.row_values(rownum)[1])
            domain = "{}.{}".format(extracted.domain, extracted.suffix)

            if len(domain) > 0:
                if len(sh.row_values(rownum)[0]) > 0:
                    data[domain] = sh.row_values(rownum)[0]


        return data

    def getLinkLinkPrice(self, key=None , url=None):
        if key is None or url is None:
            return False

        #url = urllib3.parse.quote_plus(url)

        return 'http://click.linkprice.com/click.php?m=%s&a=%s&l=9999&l_cd1=3&l_cd2=0&tu=%s' % (key, self.LINKPRICE_ID, url)

if __name__ == "__main__":
    ppomppuLinkGenerator = PpomppuLinkGenerator()
    #print(ppomppuLinkGenerator.genLink(url='http://item.gmarket.co.kr/detailview/item.asp?goodscode=1401721949'))
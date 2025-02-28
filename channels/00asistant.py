import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse
else:
    import urlparse

import re

from platformcode import config, logger, platformtools
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from bs4 import BeautifulSoup
from modules import filtertools
from lib import alfa_assistant


host = "https://www.babestube.com/latest-updates/?sort_by=post_date&from=01"

url1 = "https://evoload.io/SecurePlayer"


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="%s" %host, action="create_soup", url=host))
    itemlist.append(item.clone(title="urlsVisited" , action="urlsVisited", url=host))
    itemlist.append(item.clone(title="post" , action="post", url=url1))
    return itemlist


def create_soup(item):
    logger.info()
    data = ""
    alfa_assistant.open_alfa_assistant()
    data = alfa_assistant.get_source_by_page_finished(item.url, 5, closeAfter=True)
    if not data:
        platformtools.dialog_ok("Alfa Assistant: Error", "ACTIVE la app Alfa Assistant para continuar")
        data = alfa_assistant.get_source_by_page_finished(item.url, 5, closeAfter=True)
        if not data:
            return False
    logger.debug(data)
    data = alfa_assistant.find_htmlsource_by_url_pattern(data, item.url)
    if isinstance(data, dict):
        data = data.get('source', '')
        if not data:
            return False
    logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    logger.debug(data)
    if data:
        soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
        # logger.debug(soup)
        return soup
    return False


def post(item):
    logger.info()
    itemlist = []
    post = {"code":"kENw2aPCEzkZmY","token":"03AGdBq26ogZwGvjuhOAOhzY88y00d_v2PKsoQmP-FxL_cORX-9LZrl6_VlmTj80dmPorAPWLI1br-Amtw-6d8bjF39lmhX9k1SrNQZSaIhSg7nidwHh05JJKb0zaqYLn8EQ75COGWOthB4hNT4LU_EgA2c_ItTE3_N1JHzF-mKaUmn06fYdxTVgNV-k0cPFCJLPg0nbJ4yodcXTuNx8pTUigql5Tv8M8ll8Hhwo3TyZrPAGKmhUbma0dfmNxralYvRaU5lRM3-8rUD524XtCdy76szcUguUfcGdFXRQvNxYJNNXxh9ucYrNs_3atStXVk_TjoeRozntubBy5inT37GmDDMYVBxRU6IRiytVBx5f3slkK3iobZFeN1PwodXKsy-bI_uK2sUjSoFmhYU1d2tEMcBoB0b0ibi8jT42EHCe6Br_N8IgauCI8"}
    referer = host
    # data = httptools.downloadpage(item.url, headers={'Referer': referer}).data
    data = httptools.downloadpage(item.url, post=post, headers={'Referer': referer}).data

    logger.debug(data)
    return 



def urlsVisited(item):
    logger.info()
    itemlist = []
    alfa_assistant.open_alfa_assistant()
    data = alfa_assistant.get_source_by_page_finished(item.url, 5, closeAfter=True)
    for cat in  data["urlsVisited"]:
        logger.debug(cat)
        url = cat["url"]
        method = cat['method']
        if "POST" in method:
            header = []
            req = cat['requestHeaders']
            logger.debug(url)
            for pot in req:
                logger.debug(pot)
        title = "[COLOR yellow]%s[/COLOR] %s" % (method,url)
        itemlist.append(item.clone(action="call_browser", title=title, url=url) )
    return itemlist


def call_browser(item, lookup=False):
    from lib import generictools

    if lookup:
        browser, resultado = generictools.call_browser(item.url, lookup=lookup)
    else:
        browser, resultado = generictools.call_browser(item.url)
    
    return browser, resultado


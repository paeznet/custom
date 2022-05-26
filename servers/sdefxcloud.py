# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from lib import jsunhunt
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    data = httptools.downloadpage(page_url).data
    if ">404</h1>" in data or '<title>404 - Tubeload.co</title>' in data:
        return False, "[sdefxcloud] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    # itemlist = []
    video_urls = []
    # data = httptools.downloadpage(page_url, headers={'Referer': page_url}).data
    code = scrapertools.find_single_match(data, 'dhYas638H\("([^"]+)"')
    decod = decode(code)
    code = scrapertools.find_single_match(decod, 'dhYas638H\("([^"]+)"')
    decod = decode(code)
    url = scrapertools.find_single_match(decod, '<iframe src="([^"]+)"')
    server = servertools.get_server_from_url(url)
    url = servertools.resolve_video_urls_for_playing(server, url)
    logger.debug(url)
    # itemlist = servertools.find_video_items(item.clone(url = url))
    # itemlist.append(Item(title= "%s", url=url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # logger.debug(servertools.get_server_from_url(url))
    # url = servertools.resolve_video_urls_for_playing(url)
    # logger.debug(url)
    video_urls.append(["[%s]" %server, url])
    return video_urls

def decode(code):
    logger.info()
    import base64
    decode = base64.b64decode(code).decode('utf-8')
    decode = base64.b64decode(decode).decode('utf-8')
    return decode


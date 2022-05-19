# -*- coding: utf-8 -*-
import re
from core import httptools
from core import scrapertools
from lib import jsunhunt
from platformcode import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data, server
    data = httptools.downloadpage(page_url).data
    server = scrapertools.find_single_match(page_url, '//(?:www.|es.|)([A-z0-9-]+).(?:co|net)')
    if ">404</h1>" in data or '<title>404 - Tubeload.co</title>' in data:
        return False, "[%s] El fichero no existe o ha sido borrado" %server
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url, headers={'Referer': page_url}).data
    if jsunhunt.detect(data):
        data = re.findall('<head>(.*?)</head>', data, re.S)[0]
        data = jsunhunt.unhunt(data)
        logger.debug(data)
    urljs = 'https://tubeload.co/assets/js/main.min.js'
    datajs = httptools.downloadpage(urljs, headers={'Referer': page_url}).data
    if jsunhunt.detect(datajs):
        datajs = jsunhunt.unhunt(datajs)
        var, rep1, rep2 = re.findall(r'''var\s*res\s*=\s*([^.]+)\.replace\("([^"]+).+?replace\("([^"]+)''', datajs, re.DOTALL)[0]
        r = re.search(r'var\s*{0}\s*=\s*"([^"]+)'.format(var), data)
        if r:
            url = r.group(1).replace(rep1, '')
            url = url.replace(rep2, '')
            import base64
            url = base64.b64decode(url).decode('utf-8')
        url += "|verifypeer=false"
        video_urls.append(["[%s]" %server, url])
    return video_urls


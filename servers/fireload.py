# Conector fireload By Alfa development Group
# --------------------------------------------------------

import sys
import re

from core import httptools
from core import scrapertools
from lib import jsunpack
from platformcode import logger
from core import urlparse


kwargs = {'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 5, 'ignore_response_code': True, 'cf_assistant': False}


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    
    global data
    
    response = httptools.downloadpage(page_url, **kwargs)
    data = response.data
    # logger.debug(data)
    if response.code == 404:
    # if response.code == 404 or "not found" in data:
        return False,  "[fireload] El fichero no existe o ha sido borrado"
    return True, ""

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    
    url = scrapertools.find_single_match(data, '"dlink":\s*"([^"]+)"')
    url = url.replace("%3D", "=")
    url += "|Referer=%s" % page_url
    
    video_urls.append(['[fireload]',url])
    return video_urls

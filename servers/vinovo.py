# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if not PY3: from lib import alfaresolver
else: from lib import alfaresolver_py3 as alfaresolver
# from lib import alfaresolver_source as alfaresolver

import re
from core import httptools
from core import scrapertools
from platformcode import logger
import base64


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    
    global data
    data = httptools.downloadpage(page_url, referer=page_url).data
    
    if "<h2>WE ARE SORRY</h2>" in data or 'Not Found' in data:
        return False, "[4tube] El fichero no existe o ha sido borrado"
    return True, ""


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    text = page_url.split("/e/")
    host = text[0]
    id = text[1]
    
    data = httptools.downloadpage(page_url, referer=page_url).data
    tok = scrapertools.find_single_match(data, 'name="token" content="([^"]+)"')
    url = scrapertools.find_single_match(data, '<video.*?data-base="([^"]+)"')
    
    co = base64.b64encode((host + ':443').encode('utf-8')).decode('utf-8').replace('=', '')
    rcap = alfaresolver.rcap(data, url, co)
    
    payload = {'token': tok, 'recaptcha': rcap}
    api = '%s/api/file/url/%s' %(host,id)
    data = httptools.downloadpage(api, post=payload, referer=page_url).json
    if data.get('token', ''):
        token= data['token']
    url = "%s/stream/%s" %(url, token)
    url += "|Referer=%s" %page_url
    video_urls.append(["[vinovo]", url])
    return video_urls

# -*- coding: utf-8 -*-
# -*- Server Voe -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

from core import httptools
from core import scrapertools
from core.jsontools import json
from platformcode import logger
import sys
import base64
import re

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int


# https://voe.sx/e/q1hvet1drcpe  ESTE NO RESUELVE es de PORNEZ
# https://voe.sx/e/s6kw3qgchq62

def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "Not found" in data or "File is no longer available" in data or "Error 404" in data:
        return False, "[Voe] El fichero no existe o ha sido borrado"

    if "permanentToken" in data:
        match = scrapertools.find_single_match(data, "(?i)window\.location\.href\s*=\s*'([^']+)'")
        data = httptools.downloadpage(match).data
    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    r = re.search(r'\w+="([^"]+)";function', data)
    repl = re.search(r"{var\s*_\w+\s*=\s*\['(.+?)'\],", data)
    if r and repl:
        s = voe_decode(r.group(1), repl.group(1))
        if s.get('source', ''):
            url = s['source']
        elif s.get('direct_access_url', ''):
            url = s['direct_access_url']
        video_urls.append(["[Voe]", url])
    video_srcs = scrapertools.find_multiple_matches(data, r"(?:mp4|hls)': '([^']+)'")
    if not video_srcs:
        bloque = scrapertools.find_single_match(data, "sources.*?\}")
        video_srcs = scrapertools.find_multiple_matches(bloque, ": '([^']+)")
        
    if video_srcs:
        for url in video_srcs:
            if url.startswith("aHR0"):
                url = base64.b64decode(url).decode("utf-8")
            video_urls.append([" [Voe]", url])
    else:
        try:
            match = scrapertools.find_single_match(data, "(?i)let\s[0-9a-f]+\s=\s'(.*?)'")
            dec_string = base64.b64decode(match).decode("utf-8")
            data_json = json.loads(dec_string[::-1])
            video_urls.append([" [Voe]", data_json['file']])
        except Exception as error:
            logger.error("Exception: {}".format(error))

    return video_urls


def voe_decode(ct, luts):
    lut = [''.join([('\\' + x) if x in '.*+?^${}()|[]\\' else x for x in i]) for i in luts.split("','")]
    txt = ''
    for i in ct:
        x = ord(i)
        if 65 <= x <= 90:
            x = (x - 52) % 26 + 65
        elif 97 <= x <= 122:
            x = (x - 84) % 26 + 97
        txt += chr(x)
    for i in lut:
        txt = re.sub(i, '_', txt)
    txt = "".join(txt.split("_"))
    ct = base64.b64decode(txt)
    txt = ''.join([chr(i - 3) for i in ct])
    txt = base64.b64decode(txt[::-1])
    return json.loads(txt)

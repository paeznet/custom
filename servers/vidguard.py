# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector vidguard By Alfa development Group
# --------------------------------------------------------


import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re
from core import httptools
from core import scrapertools
from platformcode import logger
from lib import aadecode
import base64
import binascii
from core import jsontools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "<h2>WE ARE SORRY</h2>" in data or 'Not Found' in data or 'The requested video was not found.' in data:
        return False, "[4tube] El fichero no existe o ha sido borrado"
    return True, ""

# https://vembed.net/e/MAlwEMZea4OJ39X  #360 720 1080


def get_video_url(page_url, video_password):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    r = re.search(r'eval\("window\.ADBLOCKER\s*=\s*false;\\n(.+?);"\);</script', data)
    if r:
        r = r.group(1).replace('\\u002b', '+')
        r = r.replace('\\u0027', "'")
        r = r.replace('\\u0022', '"')
        r = r.replace('\\/', '/')
        r = r.replace('\\\\', '\\')
        r = r.replace('\\"', '"')
        text_decode = aadecode.decode(r, alt=True)
        json_data = jsontools.load(text_decode[11:])  #quita window.svg=
        url = json_data['stream']
        if url:
            if isinstance(url, list):
                sources = [(x.get('Label'), x.get('URL')) for x in url]
                stream_url = helpers.pick_source(helpers.sort_sources_list(sources))
            if not url.startswith('https://'):
                url = re.sub(':/*', '://', stream_url)
            url = sig_decode(url)
            url += "|Referer=%s" % page_url
            video_urls.append(["[vidguard]", url])
        # video_urls.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return video_urls


    # Adapted from PHP code by vb6rocod
    # Copyright (c) 2019 vb6rocod
def sig_decode(url):
    sig = url.split('sig=')[1].split('&')[0]
    t = ''
    for v in binascii.unhexlify(sig):
        t += chr((v if isinstance(v, int) else ord(v)) ^ 2)
    t += "=="
    t = list(base64.b64decode(t)[:-5][::-1])
    for i in range(0, len(t) - 1, 2):
        t[i + 1], t[i] = t[i], t[i + 1]
    s=""
    for v in t:
        s += chr(v)
    url = url.replace(sig, s[:-5])
    return url
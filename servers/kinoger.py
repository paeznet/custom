# Conector KinoGer By Alfa development Group
# Thanks to ResolveURL for the logic
# --------------------------------------------------------

import pyaes
import binascii
import json
from core import httptools
from platformcode import logger

# https://xfuntaxy.upns.xyz/#onaa9w
# https://amg.upns.live/#x6diue

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    global data
    
    response = httptools.downloadpage(page_url)
    data = response.data
    if response.code == 404:
        return False,  "[%s] El fichero no existe o ha sido borrado" % page_url
    return True, ""

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    try:
        edata = binascii.unhexlify(data[:-1])
        key = b'\x6b\x69\x65\x6d\x74\x69\x65\x6e\x6d\x75\x61\x39\x31\x31\x63\x61'
        iv = b'\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30\x6f\x69\x75\x79\x74\x72'
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
        ddata = decrypter.feed(edata)
        ddata += decrypter.feed()
        ddata = ddata.decode('utf-8')
        ddata = json.loads(ddata)
        url = ddata.get('source')
        if url:
            url += "|User-Agent={0}&Referer={1}/&Origin={1}".format(httptools.get_user_agent(), page_url)
            video_urls.append(['[KinoGer] m3u8', url])
    except Exception as e:
        logger.error(e)
    
    return video_urls

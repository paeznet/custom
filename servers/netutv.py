# -*- coding: utf-8 -*-

from builtins import chr
from builtins import range

import re
import random

from core import httptools
from core import jsontools
from core import scrapertools
from core import urlparse
from platformcode import config, logger, platformtools
from core import filetools


import xml.etree.ElementTree as ET


# https://veev.to/e/2IVw98bXUifPchjcPnQapmKuvHPWsJ1I1Hf6MZe
# resolveurl.resolver.ResolverError: Video removed


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    
    server = scrapertools.get_domain_from_url(page_url).split(".")[-2]
    
    # page_url = httptools.downloadpage(page_url, follow_redirects=False).headers["location"]
    
    # response = httptools.downloadpage(page_url, **kwargs)
    # data = response.data
    # if response.code == 404 or "not found" in response.data:
        # return False,  "[%s] El fichero no existe o ha sido borrado" %server

    ADDON_RUNTIME_PATH = config.get_runtime_path()
    ADDON_DATA_PATH = config.get_data_path()
    comparar = "%saddon.xml" %ADDON_RUNTIME_PATH
    
    logger.debug(comparar)
    
    tree = ET.parse(comparar)
    root = tree.getroot()
    texto = ET.tostring(root, encoding='utf8').decode('utf8')
    requires =root[0]
    
    #<import addon="script.module.resolveurl" optional="true"/>
    
    importar = ET.Element('import')
    importar.set("addon", "script.module.resolveurl")
    importar.set("optional", "true")
    if not "resolveurl" in texto:
        requires.append(importar)
        tree.write(comparar)

    url = urlsolver(page_url)
    video_urls.append(["[%s]" %server, url])
    
    return video_urls


def urlsolver(url):
    logger.info("url=" + url)
    # try:
        # import resolveurl
    # except:
        # import urlresolver as resolveurl
    import resolveurl

    if resolveurl.HostedMediaFile(url).valid_url():
        logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        logger.debug(resolveurl.resolver.ResolverError)
        logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        resolved = resolveurl.resolve(url)
    else:
        # platformtools.dialog_ok("Error", "%s" %url)
        resolved = url
    return resolved
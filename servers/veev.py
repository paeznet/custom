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
import resolveurl

# https://veev.to/e/2IVw98bXUifPchjcPnQapmKuvHPWsJ1I1Hf6MZe
# resolveurl.resolver.ResolverError: Video removed

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    
    ADDON_RUNTIME_PATH = config.get_runtime_path()
    ADDON_DATA_PATH = config.get_data_path()
    comparar = "%saddon.xml" %ADDON_RUNTIME_PATH
    
    # logger.debug(comparar)
    
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
    video_urls.append(["[veev]", url])
    
    return video_urls


def urlsolver(url):
    # try:
        # import resolveurl
    # except:
        # import urlresolver as resolveurl

    if resolveurl.HostedMediaFile(url).valid_url():
        resolved = resolveurl.resolve(url)
    else:
        # platformtools.dialog_ok("Error", "%s" %url)
        resolved = url
    return resolved
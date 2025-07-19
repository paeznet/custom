# -*- coding: utf-8 -*-

from builtins import chr
from builtins import range

import re
import random

from core import httptools
from core import jsontools
from core import scrapertools
from core import urlparse
from platformcode import logger, platformtools

import resolveurl

# https://hqq.to/e/Y2pXRFFMd0xuSG1oaUxTcWhkaDRHdz09

# https://github.com/Gujal00/ResolveURL
# addon.xml
# <requires>
    # <import addon="script.module.resolveurl" optional="true" />


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    
    logger.debug(page_url)
    url = urlsolver(page_url)
    video_urls.append(["[netu.tv]", url])
    
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
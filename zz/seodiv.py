# -*- coding: utf-8 -*-
# -*- Channel Seodiv -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re
import string

from channels import filtertools
from bs4 import BeautifulSoup
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import tmdb
from channels import autoplay
from platformcode import config, logger

host = 'https://areliux.com/'
list_idiomas = ["LAT"]
list_servers = ['sendvid', 'okru']
list_quality = list()

canonical = {
             'channel': 'seodiv', 
             'host': config.get_setting("current_host", 'seodiv', default=''), 
             'host_alt': ["https://areliux.com/"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def create_soup(url, referer=None, unescape=False):
    logger.info()

    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")

    return soup


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)
    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Todas", action="list_all", url=host, first=0))
    itemlist.append(Item(channel=item.channel, title="Alfabético", action="alpha_list"))
    autoplay.show_option(item.channel, itemlist)

    return itemlist


def list_all(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    matches = soup.find_all("div", class_="shortstory-in")
    if item.alfabetico:
        return alpha_results(item, matches)
    first = item.first
    last = first + 25
    if last >= len(matches):
        last = len(matches)

    for elem in matches[first:last]:
        url = host + elem.a["href"]
        title = elem.a["title"]
        if title.lower() == "promo": continue
        thumb = host + elem.a.img["src"]

        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, action="episodios",
                             contentSerieName=title,))

    tmdb.set_infoLabels_itemlist(itemlist, True)

    url_next_page = item.url
    first = last

    if url_next_page and len(matches) > 26:
        itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=url_next_page, action='list_all',
                             first=first))
    return itemlist


def episodios(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url)
    itemlist.extend(episodesxpage(item, item.url))
    pages = soup.find("div", class_="pages-numbers").find_all("a")

    for page in pages:
        itemlist.extend(episodesxpage(item, page["href"]))

    return itemlist


def episodesxpage(item, page):
    logger.info()

    itemlist = list()

    elem = create_soup(page).find_all("div", class_="shortstory-news")

    for epi in elem:

        url = epi.a["href"]
        if not epi.a.img["src"].startswith("http"):
            thumb = host + epi.a.img["src"]
        else:
            thumb = epi.a.img["src"]
        scrp_title = epi.a["title"]
        season = scrapertools.find_single_match(scrp_title, r"(?:Temporada) (\d+)")
        info = scrapertools.find_single_match(scrp_title, r"(?:Capitulo) (\d+\w?) - (.*$)")
        if not info:
            continue
        episode = str(info[0])
        epi_name = str(info[1])
        title = "%sx%s - %s" % (season, episode, epi_name)

        itemlist.append(Item(channel=item.channel, url=url, title=title, action="findvideos", thumbnail=thumb))


    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()

    soup = create_soup(item.url).find("div", id="full-video")
    for elem in soup.find_all("iframe")[1:]:
        url = elem["src"]

        itemlist.append(Item(channel=item.channel, url=url, title="%s", action="play", language='LAT'))

    itemlist = servertools.get_servers_itemlist(itemlist, lambda x: x.title % x.server)

    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_idiomas, list_quality)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist


def alpha_list(item):
    logger.info()

    itemlist = list()

    for letra in string.ascii_uppercase:
        itemlist.append(item.clone(action="list_all", title=letra, alfabetico=True, url=host))

    return itemlist


def alpha_results(item, matches):
    logger.info()

    itemlist = list()

    for elem in matches:
        if elem.a["title"].startswith(item.title):
            url = host + elem.a["href"]
            title = elem.a["title"]
            thumb = host + elem.a.img["src"]

            itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=thumb, action="episodios",
                                 contentSerieName=title))

    tmdb.set_infoLabels_itemlist(itemlist, True)
    return itemlist

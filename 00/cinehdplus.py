# -*- coding: utf-8 -*-
# -*- Channel CineHDPlus -*-
# -*- Created for Rebel-addon -*-
# -*- By the Rebel Developer -*-

import sys
import base64
import codecs

# PY3 = False
# if sys.version_info[0] >= 3:
    # PY3 = True
    # unicode = str
    # unichr = chr
    # long = int


import re

from core import urlparse
from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, tmdb
from core import servertools, channeltools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from modules import filtertools
from modules import autoplay


# from lib.AlfaChannelHelper import CustomChannel



IDIOMAS = {'Latino': 'Latino'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['fembed', 'streamtape', 'gvideo', 'Jawcloud']


forced_proxy_opt = 'ProxySSL'


#  "https://repelishd.cam/"
#  "https://cinehdplus.gratis/"  "https://cinehdplus.cam/" 

#  "https://cinehdplus.org/"  "https://cinehdplus.net/"(OUT)


canonical = {
             'channel': 'cinehdplus', 
             'host': config.get_setting("current_host", 'cinehdplus', default=''), 
             'host_alt': ["https://cinehdplus.org/"], 
             'host_black_list': ["https://cinehdplus.net/"], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*title='], 
             # 'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 20, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             # 'cf_assistant': False, 'CF_stat': True, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 15, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }

host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = list()
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Peliculas", action="list_all", url="%s%s/" % (host, "peliculas"), thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Series", action="list_all", url="%s%s/" % (host, "series"), thumbnail=get_thumb("tvshows", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Generos", action="section", url=host, sect="generos",
                         thumbnail=get_thumb("genres", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Años", action="section", url=host, sect="years",
                         thumbnail=get_thumb("year", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=host, thumbnail=get_thumb("search", auto=True)))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def create_soup(url, referer=None, post=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    if post:
        data = httptools.downloadpage(url, post=post, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def list_all(item):
    logger.info()

    itemlist = list()
    
    # data = httptools.downloadpage(item.url).data
    # logger.debug(data)
    soup = create_soup(item.url, referer=host)
    matches = soup.find_all("div", class_="card")

    for elem in matches:
        lang = list()
        if elem.find('div', class_='placebo'): continue
        url = elem.a["href"]
        title = elem.img["alt"]
        try:
            thumb = elem.img["data-src"]
        except:
            thumb = elem.img["src"]
        
        languages = elem.find_all("img", class_="idioma")
        for l in languages:
            lang.append(l["alt"])

        year = elem.find("span", class_="year").text

        new_item = Item(channel=item.channel, title=title, url=url, thumbnail=thumb, action="findvideos",
                        language=lang, infoLabels={"year": year})

        if "peliculas-" in url:
            new_item.contentTitle = title
            new_item.action = "findvideos"
        else:
            new_item.contentSerieName = title
            new_item.action = "seasons"

        itemlist.append(new_item)

    tmdb.set_infoLabels_itemlist(itemlist, True)

    try:
        next_page = soup.find(class_="catalog__paginator").find_all("a")[-1]["href"]
        if next_page:
            itemlist.append(Item(channel=item.channel, title="Siguiente >>", url=next_page, action='list_all'))
    except:
        pass

    return itemlist


def section(item):
    logger.info()

    itemlist = list()
    sections = {"generos": ["genre", "genero"],
                "years": ["year", "ano"]}

    soup = create_soup(host)
    matches = soup.find("ul", {"aria-labelledby": "filter-%s" % sections[item.sect][0]}).find_all("li")

    for elem in matches:
        title = elem.text
        url = "%s%s/%s" % (host, sections[item.sect][1], elem["id"])

        itemlist.append(Item(channel=item.channel, title=title, url=url, action="list_all"))

    return itemlist


def seasons(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url)

    matches = soup.find_all("option")
    infoLabels = item.infoLabels

    for elem in matches:
        season = elem["value"]
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, action='episodesxseasons',
                             infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)

    return itemlist


def episodesxseasons(item):
    logger.info()

    itemlist = list()

    infoLabels = item.infoLabels
    season = infoLabels["season"]
    try:
        matches = create_soup(item.url).find("div", id="season-%s" % season).find("ul").find_all("li")
    except:
        return itemlist

    for elem in matches:
        url = elem.a["href"]
        epi = scrapertools.find_single_match(url, r"(\d+x\d+)")
        epi_title = elem.find("small").text
        title = "%s - %s" % (epi, epi_title)
        infoLabels['episode'] = epi.split("x")[1]
        itemlist.append(Item(channel=item.channel, title=title, url=url, action='findvideos', infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = list()
    soup = create_soup(item.url)
    matches = soup.find_all("iframe")

    for elem in matches:
        if elem.has_attr("title"):
            continue
        v_id = scrapertools.find_single_match(elem["data-src"], r"h=([^\&]+)")
        url = dec(v_id)
        itemlist.append(Item(
                                channel=item.channel,
                                contentTitle=item.contentTitle,
                                contentThumbnail=item.thumbnail,
                                infoLabels=item.infoLabels,
                                language="Latino",
                                title='%s', action="play",
                                url=url
                               ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    # Requerido para FilterTools
    
    itemlist = filtertools.get_links(itemlist, item, list_language)
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    
    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(Item(channel=item.channel,
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]',
                             url=item.url,
                             action="add_pelicula_to_library",
                             extra="findvideos",
                             contentTitle=item.contentTitle))

    return itemlist

# <form action="https://interdecoracion.net/?stream" id="GVid0" method="POST">
                    # <input type="hidden" id="vid" name="vid" value="dWdnY2Y6Ly9pYnIuZmsvci9odjdpazNlN2J5cGg=" />
                    # <input type="hidden" id="hash" name="hash" value="1b682727fc6dbc524015b3c08f72ea5c" />


def dec(v_id):
    # https://api.cinehdplus.org/ir/redir_ddh.php
    # https://api.cinehdplus.org/ir/go_ddh.php?h=
    post = {"url": v_id, "dl": 0}
    url_api = host.replace("https://", "https://api.")
    
    # r = httptools.downloadpage("%sir/rd.php" %url_api, post=post, canonical=canonical)
    # value = scrapertools.find_single_match(r.data, r'value="([^"]+)"', )
    # post = {"url": value}
    r = httptools.downloadpage("%sir/rd.php" %url_api, post=post, canonical=canonical)
    vid_value = scrapertools.find_single_match(r.data, r'value="([^"]+)"')
    url = codecs.decode(base64.b64decode(vid_value).decode("utf-8"), "rot_13")

    return url


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/?s=" + texto
    if texto != '':
        return list_all(item)
    else:
        return []


def newest(categoria):
    logger.info()
    item = Item()

    try:
        if categoria in ['peliculas','latino']:
            item.url = host
        elif categoria == 'infantiles':
            item.url = host + '/genero/animacion/'
        elif categoria == 'terror':
            item.url = host + '/genero/terror/'
        itemlist = list_all(item)
        if "Pagina" in itemlist[-1].title:
            itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

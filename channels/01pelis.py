# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, tmdb
from core import servertools, channeltools
from bs4 import BeautifulSoup
from channelselector import get_thumb
from modules import filtertools
from modules import autoplay

forced_proxy_opt = 'ProxySSL'


canonical = {
             'channel': 'peliplayhd', 
             'host': config.get_setting("current_host", 'peliplayhd', default=''), 
             'host_alt': ["https://peliplayhd.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
# url1 = "%s/?v=Opciones" %host


SERVER = {"fviplions": "Tiwikiwi", 'filelions': "Tiwikiwi", "sbbrisk": "Streamsb"}
          
IDIOMAS = {"castellano": "CAST", "latino": "LAT", "ingles": "VOSE", "sub-es": "VOSE"}

list_language = list(IDIOMAS.values())
list_quality = []
list_servers = list(SERVER.values())

__channel__='01pelis'
__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', __channel__)
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', __channel__)
try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


parameters = channeltools.get_channel_parameters(__channel__)
unif = parameters['force_unify']

logger.debug(unif)

def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista_all", url= host + "peliculas/page/20/", thumbnail=get_thumb("movies", auto=True)))
    # itemlist.append(Item(channel=item.channel, title="      Mas Vistas" , action="lista", url= host + "/Seccion.html?ver=PelisMasVistos", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Series", action="lista_all", url= host + "series/", thumbnail=get_thumb("tvshows", auto=True)))
    # itemlist.append(Item(channel=item.channel, title="      Mas Vistas" , action="lista", url= host + "/Seccion.html?ver=MasVistos", thumbnail=get_thumb("movies", auto=True)))
    # itemlist.append(Item(channel=item.channel, title="Anime", action="lista", url= host + "/Anime.html?page=1", thumbnail=get_thumb("anime", auto=True)))
    # itemlist.append(Item(channel=item.channel, title="Novela", action="lista", url= host + "/Novelas.html?page=1", thumbnail=get_thumb("tvshows", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Genero" , action="categorias", url= host, thumbnail=get_thumb('genres', auto=True)))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", thumbnail=get_thumb("search", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Configurar canal...", action="configuracion", text_color="gold", folder=False, thumbnail=get_thumb("setting_0.png")))
    
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "%20")
        item.url = "%s/Buscar.html?s=%s" % (host, texto)
        if texto != "":
            return lista_all(item)
        else:
            return []
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('div', class_='panel-title')
    matches = soup.find_all('option')
    for elem in matches:
        url = elem['value']
        title = elem.text
        url = urlparse.urljoin(item.url,url)
        if "Buscar" in url:
            itemlist.append(Item(channel=item.channel, action="lista_all", title=title , url=url, 
                              section=item.section) )
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



def lista_all(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('ul', class_='post-lst').find_all("li", class_=re.compile(r"^post-\d+"))
    for elem in matches:
        logger.debug(elem)
        datos = elem['class']
        trid = scrapertools.find_single_match(datos[0], 'post-(\d+)')
        ctype = scrapertools.find_single_match(datos[2], 'type-(\w+)')
        language = []
        if elem.find(class_="lang"):
            flags = elem.find(class_="lang").find_all('img')
            for flag in flags:
                lang = scrapertools.find_single_match(flag['src'], '/([A-z-]+).(?:png|webp|jpg)').lower()
                language.append(IDIOMAS.get(lang, lang))
        thumbnail = elem.img['src']
        title = elem.h2.text.strip()
        info = elem.find('div', class_='post_info')
        year = elem.find('span', class_='year').text.strip()
        if year == '':
            year = '-'
            
        url = elem.a['href']
        new_item = Item(channel=item.channel, url=url, trid=trid, title=title, thumbnail=thumbnail, 
                        language=language, infoLabels={"year": year})
        if "series" in ctype:
            new_item.trtype=1
            new_item.action = "seasons"
            new_item.contentSerieName = title
        else:
            new_item.trtype=1
            new_item.action = "findvideos"
            new_item.contentTitle = title
        itemlist.append(new_item)
    tmdb.set_infoLabels(itemlist, True)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)


    next_page = soup.find('a', class_='current')
    if next_page and next_page.find_next_sibling("a"):
        next_page = next_page.find_next_sibling("a")['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista_all", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

         # 'seasons': {'find_all': [{'tag': ['div'], 'class': ['choose-season']}]}, 
         # 'season_num': dict([('find', [{'tag': ['a']}]), 
                             # ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]),

def seasons(item):
    logger.info()
    itemlist = list()
    infoLabels = item.infoLabels
    soup = create_soup(item.url, post=item.url)
    matches = soup.find('div', class_='choose-season').find_all('a')
    for elem in matches:
        season = elem['data-season']
        id = elem['data-post']
        post= "action=action_select_season&season=%s&post=%s" %(season,id)
        if int(season) < 10:
            season = "0%s" %season
        title = "Temporada %s" % season
        infoLabels["season"] = season
        itemlist.append(Item(channel=item.channel, title=title, url=item.url, post=post, action="episodesxseasons",
                             infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(Item(channel=item.channel, title="[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]", url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName))
    return itemlist


def episodesxseasons(item):
    logger.info()
    itemlist = list()
    infoLabels = item.infoLabels
    season = infoLabels["season"]
    url= "%swp-admin/admin-ajax.php" %host
    soup = create_soup(url, post=item.post)
    matches = soup.find_all('article')
    for elem in matches:
        url = elem.a['href']
        cap = elem.find('span', class_='num-epi').text.strip()
        cap = scrapertools.find_single_match(cap, 'x(\d+)')
        if int(cap) < 10:
            cap = "0%s" % cap
        title = "%sx%s" % (season, cap)
        infoLabels["episode"] = cap
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="findvideos",
                                 infoLabels=infoLabels))
    tmdb.set_infoLabels_itemlist(itemlist, True)
    
    a = len(itemlist)-1
    for i in itemlist:
        if a >= 0:
            title= itemlist[a].title
            titulo = itemlist[a].infoLabels['episodio_titulo']
            title = "%s %s" %(title, titulo)
            itemlist[a].title = title
            a -= 1
    return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = seasons(item)
    for tempitem in templist:
        itemlist += episodesxseasons(tempitem)
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    
    soup = create_soup(item.url).find('section', class_='player')
    matches = soup.find_all('iframe')
    servers = soup.find_all('a')
    for indice, elem in enumerate(matches): 
        if elem.get('data-src'):
            url = elem['data-src']
        else:
            url = elem['src']
        data = servers[indice].find(class_='server').text.strip()
        # server, lang = scrapertools.find_single_match(data, '(\w+)\s*(?:-|)(\w+)')
        data =scrapertools.find_multiple_matches(data, '(\w+)')  ###  a partir de pagina 30 aparece solo idioma
        if len(data) > 1:
            server = data[0].lower()
            lang = data[1].lower()
        else:
            server = 'directo'      #Etiqueto directo por no cargar la url para 
            lang = data[0].lower()
        language = IDIOMAS.get(lang, lang)
        server = SERVER.get(server,server)
        itemlist.append(Item(channel=item.channel, url=url, action='play',
                             language=language, infoLabels=item.infoLabels, 
                             server=server))
    # itemlist = servertools.get_servers_itemlist(itemlist)

    # Requerido para Filtrar enlaces
    if __comprueba_enlaces__:
        itemlist = servertools.check_list_links(itemlist, __comprueba_enlaces_num__)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra !='findvideos' and not "/episodios/" in item.url :
        itemlist.append(Item(channel=item.channel, action="add_pelicula_to_library", 
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                             extra="findvideos", contentTitle=item.contentTitle)) 
    return itemlist


# def descarga(page,server):
    # logger.info()
    # itemlist = []
    # url = "%s/?m=Descargas" %host
    # data = httptools.downloadpage(url, post=page).data
    # url = scrapertools.find_single_match(data, "nclick=\"dl_emergencia\('https://.*?(https[^']+)'")
    # url1 = urlparse.unquote(url)
    # if "Fembed" in server:
        # data = httptools.downloadpage(url1).data
        # url = scrapertools.find_single_match(data, "location.href='([^']+)'")
        # if "code=" in url:
            # id= scrapertools.find_single_match(url, "code=(.*?)&")
            # url = "https://femax20.com/v/%s" %id
    # else:
        # soup = create_soup(url1).find('div', class_='cont')
        # if soup:
            # url = soup.find('a')['href']
        # else:
            # platformtools.dialog_ok("Peliserieslive:  Error", "El archivo no existe o ha sido borrado")
            # return
    # logger.debug(url1 + "  ===>  " + url)
    # return url


# def fembe(page):
    # logger.info()
    # soup = create_soup(page)
    # url = soup.find('iframe')
    # if url.has_attr('data-src'):  url = url['data-src']
    # else:                url = url['src']
    # if "code=" in url:
        # id= scrapertools.find_single_match(url, "code=(.*?)&")
        # url = "https://femax20.com/v/%s" %id
    # return url


# def player(page, pid):
    # logger.info()
    # pub_url = scrapertools.find_single_match(data, 'Ajax\("([^"]+)"')
    # pub_url = "%s/?m=rate_played%s" %(host,pid)
    # httptools.downloadpage(pub_url)
    # data = httptools.downloadpage(page).data
    # url = scrapertools.find_single_match(data, "var mp4_url='([^']+)'")
    # if "clipwatching" in page:
        # url = scrapertools.find_single_match(data, "var Original='([^']+)'")
    # return url


def play(item):
    logger.info()
    itemlist = []
    logger.debug("ITEM: %s" % item)
    soup = create_soup(item.url, referer=item.referer)
    url = soup.iframe['src']
    # if "Fembed" in item.server and not "Descargar" in item.tipo:
        # url = fembe(item.url)
    # if "Descargar" in  item.tipo:
        # url = descarga(item.url, item.server)
    # if "Ver" in  item.tipo and not "Fembed" in item.server:
        # url = player(item.url, item.pid)
    # item.server=""
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

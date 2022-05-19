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

from channels import autoplay
from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, tmdb
from core import servertools, channeltools
from channels import filtertools
from bs4 import BeautifulSoup
from channelselector import get_thumb

canonical = {
             'channel': 'peliseries', 
             'host': config.get_setting("current_host", 'peliseries', default=''), 
             'host_alt': ["https://peliseries.live"], 
             'host_black_list': [], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
url1 = "%s/?v=Opciones" %host


SERVER = {'www.fembed.com': 'Fembed','www.myurlshort.live': 'Fembed', 'feurl.com': 'Fembed', '1fichier.com': 'onefichier', 'www.mediafire.com': 'mediafire' , 'mixdrop.co': 'Mixdrop',
          'pandafiles.com': 'Directo', 'primeuploads.com': 'Directo', 'streamzz.to': 'Directo', 'clicknupload.co': 'Directo', 'maxiseries24.com': 'Directo',
          'www.mp4upload.com': 'Directo', 'anonfiles.com': 'Directo', 'powvideo.net': 'Directo', 'zeus.pelisplay.tv': 'Directo', 'jkanime.net': 'Directo',
          'dragonball.sullca.com': 'Directo', 'www.solidfiles.com':'Directo', 'treshost.com': 'player.treshost.com', 'www.youtube.com': 'Directo',
          
          'supervideo.tv': 'Directo', 'tune.pk': 'Directo', 
          'vev.io': 'Directo', 'nitroflare.com': 'Directo', 'flixplayer.xyz': 'Directo', 'netu.tv': 'Directo',
          }
          
          # https://tune.pk/js/open/load.js?vid=8103645
          # https://supervideo.tv/e/8ve4fsn4x5t5

          
IDIOMAS = {"esp": "CAST", "lat": "LAT", "sub": "VOSE"}

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
    
    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="lista", url= host + "/Peliculas.html?page=1", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(Item(channel=item.channel, title="      Mas Vistas" , action="lista", url= host + "/Seccion.html?ver=PelisMasVistos", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Series", action="lista", url= host + "/Series.html?page=1", thumbnail=get_thumb("tvshows", auto=True)))
    itemlist.append(Item(channel=item.channel, title="      Mas Vistas" , action="lista", url= host + "/Seccion.html?ver=MasVistos", thumbnail=get_thumb("movies", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Anime", action="lista", url= host + "/Anime.html?page=1", thumbnail=get_thumb("anime", auto=True)))
    itemlist.append(Item(channel=item.channel, title="Novela", action="lista", url= host + "/Novelas.html?page=1", thumbnail=get_thumb("tvshows", auto=True)))
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
            return lista(item)
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
            itemlist.append(Item(channel=item.channel, channel=item.channel, action="lista", title=title , url=url, 
                              section=item.section) )
    return itemlist


def create_soup(url, referer=None, post=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    if post:
        data = httptools.downloadpage(url, post=post).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url, referer=host)
    matches = soup.find_all("div", class_=re.compile(r"^pitem\d+"))
    for elem in matches:
        tipo = ""
        ref = "%s%s" % (host, elem.find("a", class_="item lazybg")["href"])
        lg = elem.find_all(class_="idioma-icons")
        language = []
        for l in lg:
            lang = l['class'][1]
            language.append(IDIOMAS.get(lang, lang))
        pid = elem['pid']
        thumbnail = elem['data-bg-img']
        title = elem.find('div', class_='def-title').text.strip()
        contentTitle = title
        info = elem.find('div', class_='post_info')
        ajo = info.text.strip()
        if "Serie" in ajo: tipo="Serie"
        if "Anime" in ajo: tipo="Anime"
        if "Novela" in ajo: tipo="Novela"
        year = scrapertools.find_single_match(ajo,'.*?Estreno: (\d{4})-')
        if year == '':
            year = '-'
            
        if not config.get_setting('unify') and not channeltools.get_channel_parameters(__channel__)['force_unify']:
            if tipo:
                title = "[COLOR darkorange]%s[/COLOR]" % title
            if year != "-":
                title = "%s [COLOR cyan](%s)[/COLOR] [COLOR darkgrey]%s[/COLOR]" % (title,year, language)
            else:
                title = "%s [COLOR darkgrey]%s[/COLOR]" % (title, language)
        else:
            title = title
        new_item = Item(channel=item.channel, pid=pid, title=title, thumbnail=thumbnail, language=language,
                        infoLabels={"year": year})
        if tipo:
            new_item.url= "pid=%s&tipo=%s&temp=-1&cap=-1" %(pid,tipo)
            new_item.action = "seasons"
            new_item.contentSerieName = contentTitle
        else:
            new_item.url = "pid=%s&tipo=Pelicula&temp=-1&cap=-1" %pid
            new_item.action = "findvideos"
            new_item.contentTitle = contentTitle
        itemlist.append(new_item)
    tmdb.set_infoLabels(itemlist, True)

    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)


    next_page = soup.find('li', class_='num active')
    if next_page:
        next_page = next_page.find_next_sibling("li").a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def seasons(item):
    logger.info()
    itemlist = list()
    infoLabels = item.infoLabels
    soup = create_soup(url1, post=item.url)
    matches = soup.find_all('div', class_='temp')
    for elem in matches:
        title= elem.a.text.strip()
        season = re.sub("\D", "", title)
        if int(season) < 10:
            season = "0%s" %season
        title = "Temporada %s" % season
        infoLabels["season"] = season
        url= "pid=%s&tipo=Serie&temp=%s&cap=-1" %(item.pid,season)
        itemlist.append(Item(channel=item.channel, title=title, url=url, action="episodesxseasons",
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
    soup = create_soup(url1, post=item.url)
    matches = soup.find_all('div', class_='temp')
    for elem in matches:
        title= elem.a.text.strip()
        cap = re.sub("\D", "", title)
        if int(cap) < 10:
            cap = "0%s" % cap
        title = "%sx%s" % (season, cap)
        infoLabels["episode"] = cap
        url= "pid=%s&tipo=Serie&temp=%s&cap=%s" %(item.pid,season,cap)
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
    soup = create_soup(url1, post=item.url)
    matches = soup.find_all('div', class_='lOpcion')
    serv=[]
    for elem in matches:
        if not "btNavs" in elem['class']:
            code= elem.a['code']
            pid= elem.a['pid']
            lid= elem.a['lid']
            hst= elem.a['hst']
            code= elem.a['code']
            pos= elem.a['pos']
            info = elem.a.text.split('\n')
            inf = info[-1].strip().split()
            ply = info[-2].strip()
            lang = inf[0]
            # logger.debug(elem.a.text.strip())
            if "español" in lang.lower(): lang = "esp"
            if "latino" in lang.lower(): lang = "lat" 
            if "sub" in lang.lower(): lang = "sub" 
            if "ing." in lang.lower(): lang = "sub" 
            if "nodefinido" in lang.lower() or "undefined" in lang.lower(): lang = item.language[0]
            lang = IDIOMAS.get(lang, lang)
            server = SERVER.get(hst, hst)
            quality = re.sub("\D", "", inf[-1])
            if quality:
                quality = "%sp" %quality
            if "play" in ply:
                url = "%s/?v=Player3&pid=%s&lid=%s&h=%s&pos=%s&u=%s"  %  (host,pid,lid,hst,pos,code)
                if "clicknupload" in hst:
                    url += "&port=80"
                if "myurlshort" in hst:
                    url = "%s/?v=Player&pid=%s&lid=%s&h=%s&pos=%s&u=%s"  %  (host,pid,lid,hst,pos,code)
                option = "Ver"
                option1 = 1
            else:
                url = "pid=%s&lid=%s&hst=%s&code=%s"  %  (pid,lid,hst,code)
                option = "Descargar"
                option1 = 2


            # log = option + ": %s [%s] (%s)(%s) " % (hst,server,quality, lang)
            # log += url
            # logger.debug(log)


            if not config.get_setting('unify') and not channeltools.get_channel_parameters(__channel__)['force_unify']:
                # title = "%s: [%s] [COLOR greenyellow]%s[/COLOR] [COLOR darkgrey][%s][/COLOR]" %(option,server,quality,lang)  # Ver/Descargar
                if quality:
                    quality = "(%s)" %quality
                title = "%s: [%s] [COLOR greenyellow]%s[/COLOR] [COLOR darkgrey][%s][/COLOR]" %(option,server,quality,lang)
            else:
                title = hst
            itemlist.append(Item(channel=item.channel, action="play", title=title, url=url, server=server, language=lang, quality=quality, tipo=option, tipo1=option1 ))

    # itemlist.sort(key=lambda it: (it.tipo1, it.language))  # Ordenar 1 Ver y 2 Descargar por lenguage

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


def descarga(page,server):
    logger.info()
    itemlist = []
    url = "%s/?m=Descargas" %host
    data = httptools.downloadpage(url, post=page).data
    url = scrapertools.find_single_match(data, "nclick=\"dl_emergencia\('https://.*?(https[^']+)'")
    url1 = urlparse.unquote(url)
    if "Fembed" in server:
        data = httptools.downloadpage(url1).data
        url = scrapertools.find_single_match(data, "location.href='([^']+)'")
        if "code=" in url:
            id= scrapertools.find_single_match(url, "code=(.*?)&")
            url = "https://femax20.com/v/%s" %id
    else:
        soup = create_soup(url1).find('div', class_='cont')
        if soup:
            url = soup.find('a')['href']
        else:
            platformtools.dialog_ok("Peliserieslive:  Error", "El archivo no existe o ha sido borrado")
            return
    # logger.debug(url1 + "  ===>  " + url)
    return url


def fembe(page):
    logger.info()
    soup = create_soup(page)
    url = soup.find('iframe')
    if url.has_attr('data-src'):  url = url['data-src']
    else:                url = url['src']
    if "code=" in url:
        id= scrapertools.find_single_match(url, "code=(.*?)&")
        url = "https://femax20.com/v/%s" %id
    return url


def player(page, pid):
    logger.info()
    # pub_url = scrapertools.find_single_match(data, 'Ajax\("([^"]+)"')
    pub_url = "%s/?m=rate_played%s" %(host,pid)
    httptools.downloadpage(pub_url)
    data = httptools.downloadpage(page).data
    url = scrapertools.find_single_match(data, "var mp4_url='([^']+)'")
    if "clipwatching" in page:
        url = scrapertools.find_single_match(data, "var Original='([^']+)'")
    return url


def play(item):
    logger.info()
    itemlist = []
    logger.debug("ITEM: %s" % item)
    if "Fembed" in item.server and not "Descargar" in item.tipo:
        url = fembe(item.url)
    if "Descargar" in  item.tipo:
        url = descarga(item.url, item.server)
    if "Ver" in  item.tipo and not "Fembed" in item.server:
        url = player(item.url, item.pid)
    item.server=""
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

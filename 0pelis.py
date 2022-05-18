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
from core import servertools
from channels import filtertools

host = 'https://www.estrenoscinesaa.com'

list_language = []
list_servers = ['Rapidvideo', 'Vidoza', 'Openload', 'Youtube']
list_quality = []
__channel__='mundopelis'
__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', __channel__)
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', __channel__)
try:
    __modo_grafico__ = config.get_setting('modo_grafico', __channel__)
except:
    __modo_grafico__ = True


def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(item.clone(title="Novedades" , action="lista", url= host + "/movies/", first=0))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url= host))
    itemlist.append(item.clone(title="Buscar", action="search"))
    
    itemlist.append(item.clone(title="Configurar canal...", text_color="gold", action="configuracion", folder=False))
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def configuracion(item):
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = host + "/?option=com_spmoviedb&view=searchresults&searchword=%s&type=movies&Itemid=544" % texto
    item.first = 0
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<a class="btn btn-xs btn-primary" href="/index.php([^"]+)".*?</i> ([^"]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle 
        itemlist.append(item.clone(channel=item.channel, action="lista", title=title , url=url, first=0,
                              thumbnail=scrapedthumbnail, plot=scrapedplot) )
    return itemlist


# <article id="post-featured-6773" class="item movies"><div class="poster">
# <img src="https://www.estrenoscinesaa.com/wp-content/uploads/2020/06/g8HBoXNY6yQ8uOYA1drGs24ZlGo-185x278.jpg" alt="Los últimos días del crimen"><div class="rating"><span class="icon-star2"></span> 3.6</div><div class="featu">Destacado</div>
# <a href="https://www.estrenoscinesaa.com/movies/los-ultimos-dias-del-crimen/"><div class="see"></div></a></div><div class="data dfeatur">
# <div class="mark"><i class="icon-local_play"></i></div>
# <h3><a href="https://www.estrenoscinesaa.com/movies/los-ultimos-dias-del-crimen/">Los últimos días del crimen</a></h3>
# <span>2020</span></div></article>

# <article id="post-6920" class="item movies">
# <div class="poster">
    # <img src="https://www.estrenoscinesaa.com/wp-content/uploads/2020/06/eurovision_song_contest_the_story_of_fire_saga-124265593-mmed-185x278.jpg" alt="Festival de la Canción de Eurovisión: La historia de Fire Saga">
    # <div class="rating"><span class="icon-star2"></span> </div>
    # <div class="mepo"> </div>
    # <a href="https://www.estrenoscinesaa.com/movies/festival-de-la-cancion-de-eurovision-la-historia-de-fire-saga/"><div class="see"></div></a>
# </div>
# <div class="data">
    # <h3><a href="https://www.estrenoscinesaa.com/movies/festival-de-la-cancion-de-eurovision-la-historia-de-fire-saga/">Festival de la Canción de Eurovisión: La historia de Fire Saga</a></h3> <span>Jun. 26, 2020</span>
# </div> 
# <div class="animation-1 dtinfo"> 
# <div class="title"> <h4>Festival de la Canción de Eurovisión: La historia de Fire Saga</h4> </div> 
# <div class="metadata"> <span>2020</span> <span>123 min</span> <span>33 vistas</span> </div> <div class="texto">Dos cantantes luchan por convertirse en estrellas del pop en un importante concurso musical, donde la presión, los rivales y otros percances ...</div> <div class="genres"><div class="mta"><a href="https://www.estrenoscinesaa.com/genre/comedia/" rel="tag">Comedia</a><a href="https://www.estrenoscinesaa.com/genre/musica/" rel="tag">Música</a><a href="https://www.estrenoscinesaa.com/genre/netflix/" rel="tag">Netflix</a></div></div> </div> </article

# <article id="post-5836" class="item movies"><div class="poster">
# <img src="https://www.estrenoscinesaa.com/wp-content/uploads/2020/03/luZH1jlEYtEaRUmDvc88mV6PlGO-185x278.jpg" alt="Guns Akimbo"><div class="rating"><span class="icon-star2"></span> 6.3</div><div class="mepo"> </div><a href="https://www.estrenoscinesaa.com/movies/guns-akimbo/"><div class="see"></div></a></div><div class="data">
# <h3><a href="https://www.estrenoscinesaa.com/movies/guns-akimbo/">Guns Akimbo</a></h3> <span>Feb. 27, 2020</span></div> <div class="animation-1 dtinfo"> <div class="title"> <h4>Guns Akimbo</h4> </div> 
# <div class="metadata"> <span class="imdb">IMDb: 6.3</span> <span>2020</span> <span>95 min</span> <span>470 vistas</span> </div> <div class="texto">Miles (Daniel Radcliffe) se siente atascado en la vida: su trabajo no tiene futuro y sigue enamorado de su exnovia Nova. Un día descubre que un ...</div> <div class="genres"><div class="mta"><a href="https://www.estrenoscinesaa.com/genre/accion/" rel="tag">Acción</a><a href="https://www.estrenoscinesaa.com/genre/comedia/" rel="tag">Comedia</a></div></div> </div> </article>


def lista(item):
    logger.info()
    itemlist = []
    
    next = False
    data = httptools.downloadpage(item.url).data
    patron  = '<article id="post-\d+".*?'
    patron += '<img src="([^"]+)".*?'
    patron += '<h3><a href="([^"]+)">([^<]+)<.*?'
    patron += '<div class="metadata">.*?<span>([^<]+)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    first = item.first
    last = first+20
    if last > len(matches):
        last = len(matches)
        next = True
    scrapertools.printMatches(matches)
    for scrapedthumbnail, scrapedurl, scrapedtitle,scrapedyear  in matches[first:last]:
        # scrapedyear = "-"
        title = scrapedtitle.replace(" (2018)", "")
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(item.clone(channel=item.channel, action = 'findvideos', title=title, contentTitle = scrapedtitle,
                                   url=url, thumbnail=scrapedthumbnail, infoLabels={'year':scrapedyear} ))
    tmdb.set_infoLabels(itemlist, True)
    # Paginación    
    if not next:
        url_next_page = item.url
        first = last
    else:
        url_next_page = scrapertools.find_single_match(data, '<a title="Siguiente" href="([^"]+)"')
        url_next_page = urlparse.urljoin(item.url,url_next_page)
        first = 0
    if url_next_page:
        itemlist.append(item.clone(title="Siguiente >>", url=url_next_page, action='lista', first=first))    
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron = '<(?:iframe|IFRAME).*?(?:src|SRC)="([^"]+)"'
    matches = scrapertools.find_multiple_matches(data, patron)
    for url in matches:
        lang = "VOSE"
        if not config.get_setting('unify'):
            title = ' (%s)' % (lang)
        else:
            title = ''
        if url != '':  
            itemlist.append(item.clone(action="play", title='%s'+title, url=url, language=lang ))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

    # Requerido para Filtrar enlaces
    if __comprueba_enlaces__:
        itemlist = servertools.check_list_links(itemlist, __comprueba_enlaces_num__)
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)


    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra !='findvideos' and not "/episodios/" in item.url :
        itemlist.append(item.clone(action="add_pelicula_to_library", 
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                             extra="findvideos", contentTitle=item.contentTitle)) 
    return itemlist



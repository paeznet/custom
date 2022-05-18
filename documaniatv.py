# -*- coding: utf-8 -*-

from __future__ import division
from past.utils import old_div
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                                             # Es muy lento en PY2.  En PY3 es nativo
    import urllib.parse as urllib
else:
    import urlparse                                                             # Usamos el nativo de PY2 que es más rápido
    import urllib

import re
import sys
import time

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import tmdb
from lib import generictools
from channels import filtertools
from channels import autoplay


#IDIOMAS = {'CAST': 'Castellano', 'LAT': 'Latino', 'VO': 'Version Original'}
IDIOMAS = {'Castellano': 'CAST', 'Latino': 'LAT', 'Version Original': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['directo']

host = 'https://www.documaniatv.com/'
channel = "documaniatv"

categoria = channel.capitalize()
__modo_grafico__ = config.get_setting('modo_grafico', channel)
timeout = config.get_setting('timeout_downloadpage', channel)

#headers = dict()
#headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.105 Safari/537.36"
#httptools.HTTPTOOLS_DEFAULT_RANDOM_HEADERS = True                               #No funciona en Episodios !!!???


def mainlist(item):
    logger.info()
    itemlist = []
    
    thumb_docus = get_thumb("channels_documentary.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_buscar = get_thumb("search.png")
    thumb_separador = get_thumb("next.png")
    thumb_settings = get_thumb("setting_0.png")
    thumb_cartelera = get_thumb("now_playing.png")
    thumb_pelis_vos = get_thumb("channels_vos.png")
    thumb_popular = get_thumb("popular.png")
    thumb_generos = get_thumb("genres.png")

    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Novedades", action="listado", url=host + "newvideos.html", thumbnail=thumb_docus, extra="novedades"))
    itemlist.append(Item(channel=item.channel, title="Los Más Vistos", action="listado", url=host + "topvideos.html", thumbnail=thumb_popular, extra="populares"))
    itemlist.append(Item(channel=item.channel, title="Por Géneros", action="categorias", url=host + "categorias-y-canales.html", thumbnail=thumb_generos, extra="categorias"))
    itemlist.append(Item(channel=item.channel, title="Series", action="listado", url=host + "top-series-documentales.html", thumbnail=thumb_series, extra="series", headers={"referer": host + "top-series-documentales.html"}))
    
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host + "search.php?keywords=", thumbnail=thumb_buscar, extra="search"))
    
    itemlist.append(Item(channel=item.channel, url=host, title="[COLOR yellow]Configuración:[/COLOR]", folder=False, thumbnail=thumb_separador))
    
    itemlist.append(Item(channel=item.channel, action="configuracion", title="Configurar canal", thumbnail=thumb_settings))
    
    autoplay.show_option(item.channel, itemlist)                                #Activamos Autoplay

    return itemlist

def configuracion(item):
    from platformcode import platformtools
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return

    
def categorias(item):
    logger.info()
    
    itemlist = []
    
    data = ''
    try:
        data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url, timeout=timeout).data)
        if not PY3:
            data = unicode(data, "utf-8", errors="replace").encode("utf-8")
    except:
        pass
        
    patron = '<a href="([^"]+)" title="([^"]+)">'
    #Verificamos si se ha cargado una página, y si además tiene la estructura correcta
    if not data or not scrapertools.find_single_match(data, patron):
        item = generictools.web_intervenida(item, data)                         #Verificamos que no haya sido clausurada
        if item.intervencion:                                                   #Sí ha sido clausurada judicialmente
            for clone_inter, autoridad in item.intervencion:
                thumb_intervenido = get_thumb(autoridad)
                itemlist.append(item.clone(action='', title="[COLOR yellow]" + clone_inter.capitalize() + ': [/COLOR]' + intervenido_judicial + '. Reportar el problema en el foro', thumbnail=thumb_intervenido))
            return itemlist                                                     #Salimos
        
        logger.error("ERROR 01: SUBMENU: La Web no responde o ha cambiado de URL: " + item.url + data)
    if not data:    #Si no ha logrado encontrar nada, salimos
        itemlist.append(item.clone(action='', title=item.category + ': ERROR 01: SUBMENU: La Web no responde o ha cambiado de URL. Si la Web está activa, reportar el error con el log'))
        return itemlist                                 #si no hay más datos, algo no funciona, pintamos lo que tenemos

    matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        logger.error("ERROR 02: SUBMENU: Ha cambiado la estructura de la Web " + " / PATRON: " + patron + " / DATA: " + data)
        itemlist.append(item.clone(action='', title=item.category + ': ERROR 02: SUBMENU: Ha cambiado la estructura de la Web.  Reportar el error con el log'))
        return itemlist                                 #si no hay más datos, algo no funciona, pintamos lo que tenemos

    #logger.debug(matches)

    for scrapedurl, scrapedtitle in matches:
        if 'series documentales' in scrapedtitle.lower():
            continue
        itemlist.append(item.clone(action="listado", title=scrapedtitle.capitalize().strip(), url=scrapedurl))

    return itemlist
    
    
def listado(item):
    logger.info()
    itemlist = []
    item.category = categoria

    #logger.debug(item)
    
    curr_page = 1                                                               # Página inicial Web
    curr_page_foot = 1                                                          # Página inicial Alfa
    last_page = 99999                                                           # Última página inicial
    last_page_foot = 1                                                          # Última página inicial
    cnt_tot = 40                                                                # Poner el num. máximo de items por página
    cnt_title = 0                                                               # Contador de líneas insertadas en Itemlist
    cnt_title_tot = 0                                                           # Contador de líneas insertadas en Itemlist, total
    matches_len = 0                                                             # Longitud total de matches []
    if item.curr_page:
        curr_page = int(item.curr_page)                                         # Si viene de una pasada anterior, lo usamos
        del item.curr_page                                                      # ... y lo borramos
    if item.curr_page_foot:
        curr_page_foot = int(item.curr_page_foot)                               # Si viene de una pasada anterior, lo usamos
        del item.curr_page_foot                                                 # ... y lo borramos
    if item.last_page:
        last_page = int(item.last_page)                                         # Si viene de una pasada anterior, lo usamos
        del item.last_page                                                      # ... y lo borramos
    if item.last_page_foot:
        last_page_foot = int(item.last_page_foot)                               # Si viene de una pasada anterior, lo usamos
        del item.last_page_foot                                                 # ... y lo borramos
    if item.cnt_tot:
        cnt_tot = int(item.cnt_tot)                                             # Si viene de una pasada anterior, lo usamos
        del item.cnt_tot                                                        # ... y lo borramos
    if item.cnt_title_tot:
        cnt_title_tot = int(item.cnt_title_tot)                                 # Si viene de una pasada anterior, lo usamos
        del item.cnt_title_tot                                                  # ... y lo borramos
    
    inicio = time.time()                                    # Controlaremos que el proceso no exceda de un tiempo razonable
    fin = inicio + 10                                                           # Después de este tiempo pintamos (segundos)
    timeout_search = timeout                                                    # Timeout para descargas
    if item.extra == 'search':
        timeout_search = timeout * 2                                            # Timeout un poco más largo para las búsquedas
        if timeout_search < 5:
            timeout_search = 5                                                  # Timeout un poco más largo para las búsquedas

    if not item.extra2:                                                         # Si viene de Catálogo o de Alfabeto
        item.extra2 = ''
        
    if item.headers:
        headers = item.headers
    else:
        headers = {}
    
    next_page_url = item.url
    #Máximo num. de líneas permitidas por TMDB. Máx de 10 segundos por Itemlist para no degradar el rendimiento
    while cnt_title < cnt_tot and curr_page <= last_page and fin > time.time():

        # Descarga la página
        data = ''
        try:
            data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)|&nbsp;", "", httptools.downloadpage(next_page_url, timeout=timeout_search, headers=headers).data)
            if not PY3:
                data = unicode(data, "utf-8", errors="replace").encode("utf-8")
        except:
            pass
        
        if not data:                                    #Si la web está caída salimos sin dar error
            logger.error("ERROR 01: LISTADO: La Web no responde o ha cambiado de URL: " + item.url + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 01: LISTADO:.  La Web no responde o ha cambiado de URL. Si la Web está activa, reportar el error con el log'))
            break                                       #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        #Patrón para todo, menos para Series
        patron = '<span class="pm-label-duration">(.*?)<\/span>.*?<a href="([^"]+)" title="([^"]+)">.*?data-echo="([^"]+)"'
        
        #Si viene de Series, ponemos un patrón especializado
        if item.extra == 'series':
            patron = '(?:<span class="pm-label-duration">(.*?)<\/span>.*?)?<a href="([^"]+)" title="([^"]+)">.*?<img src="([^"]+)"'
            
        matches = re.compile(patron, re.DOTALL).findall(data)
        if not matches and not 'Lo siento, tu búsqueda no arrojó ningún resultado, intenta con otras palabras.' in data:  #error
            item = generictools.web_intervenida(item, data)                         #Verificamos que no haya sido clausurada
            if item.intervencion:                                                   #Sí ha sido clausurada judicialmente
                item, itemlist = generictools.post_tmdb_episodios(item, itemlist)   #Llamamos al método para el pintado del error
                return itemlist                                                     #Salimos
            
            logger.error("ERROR 02: LISTADO: Ha cambiado la estructura de la Web " + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: LISTADO: Ha cambiado la estructura de la Web.  Reportar el error con el log'))
            break                                       #si no hay más datos, algo no funciona, pintamos lo que tenemos
        
        matches_len = len(matches)
        if matches_len > cnt_title_tot and cnt_title_tot > 0:
            matches = matches[cnt_title_tot:]
        
        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)
        
        #Buscamos la url de paginado y la última página
        data_page = scrapertools.find_single_match(data, '<ul class="pagination pagination-sm pagination-arrows">.*?<\/li><\/ul>(?:<\/nav>)?<\/div><\/div> <\/div>')
        if item.extra == 'series':
            patron = '>(\d+)?<\/a><\/li><li class=""><a href="([^"]+-(\d+).html)"[^>]*><i class="fa fa-arrow-right"><\/i><\/a><\/li><\/ul><\/div><\/div>\s?<\/div>'
        elif item.extra == 'categorias':
            patron = '>(\d+)?<\/a><\/li><li class=""><a href="([^"]+-(\d+)-date.html)"[^>]*>&raquo;<\/a><\/li><\/ul>(?:<\/nav>)?<\/div><\/div>\s?<\/div>'
            if not scrapertools.find_single_match(data, patron):
                patron = '>(\d+)?<\/a><\/li><li class=""><a href="([^"]+page-(\d+)\/)"[^>]*>&raquo;<\/a><\/li><\/ul>(?:<\/nav>)?<\/div><\/div>\s?<\/div>'
        else:
            patron = '>(\d+)?<\/a><\/li><li\s*class="">\s*<a\s*href="([^"]+&page=(\d+))"'
            patron += '[^>]*>&raquo;<\/a><\/li><\/ul>(?:<\/nav>)?<\/div><\/div>\s?<\/div>'

        #Si la página de la web es superior a la página del canal, se ponen los limites
        if item.extra == 'novedades': cnt_tot = matches_len
        elif item.extra == 'populares': cnt_tot = 25
        elif item.extra == 'categorias': cnt_tot = matches_len
        elif item.extra == 'series': cnt_tot = 25
        elif item.extra == 'search': cnt_tot = matches_len
        else: cnt_tot = 40
        
        if last_page == 99999:                                              #Si es el valor inicial, buscamos
            #Se busca el píe de página
            try:
                last_page, next_page_url, next_page = scrapertools.find_single_match(data, patron)
                last_page = int(last_page)
                curr_page = int(next_page)-1
                next_page_url = urlparse.urljoin(host, next_page_url)
            except:                                                         #Si no lo encuentra, lo ponemos a 1
                logger.error('ERROR 03: LISTADO: Al obtener la paginación: ' + patron)
                curr_page = 1
                last_page = 0
                if item.extra == 'series':
                    next_page_url = item.url
                else:
                    next_page_url = item.url + '?&page=1'
        
            #Calculamos el num  de páginas totales si la página web es más grande que la del canal
            last_page_foot = last_page
            if matches_len > cnt_tot:
                if last_page == 0:
                    last_page = 1
                if last_page_foot == 0:
                    last_page_foot = 1
                if item.extra == 'series':
                    last_page_foot = last_page_foot * (old_div(100, cnt_tot))
                else:
                    last_page_foot = last_page_foot * (old_div(matches_len, cnt_tot))
        
        #Calculamos la url de la siguiente página
        if last_page > 1 or last_page_foot > 1:
            curr_page_foot += 1                                                 #Apunto ya a la página siguiente
            if item.extra == 'series':
                curr_page += 1                                              #Apunto ya a la página siguiente
                cnt_title_tot = 0 - len(matches)
                if len(matches) < cnt_tot:                                  #Si va a cargar otra página, no lo cuento
                    curr_page_foot -= 1                                     #Vuelvo a la página actual
                next_page_url = re.sub(r'(?:-\d+)?.html', '-%s.html' % curr_page, next_page_url)
                item.url = next_page_url
            elif item.extra == 'categorias':
                curr_page += 1                                                  #Apunto ya a la página siguiente
                if scrapertools.find_single_match(next_page_url, '(?:-\d+)-date.html'):
                    next_page_url = re.sub(r'(?:-\d+)-date.html', '-%s-date.html' % curr_page, next_page_url)
                else:
                    next_page_url = re.sub(r'\/page-\d+', '/page-%s' % curr_page, next_page_url)
            elif item.extra == 'populares':
                next_page_url = item.url
            else:
                curr_page += 1                                                  #Apunto ya a la página siguiente
                next_page_url = re.sub(r'page=\d+', 'page=%s' % curr_page, next_page_url)
        
        #logger.debug('curr_page: ' + str(curr_page) + ' / last_page: ' + str(last_page) + ' / url: ' + next_page_url + ' / cnt_title: ' + str(cnt_title) + ' / cnt_title_tot: ' + str(cnt_title_tot) + ' / cnt_tot: ' + str(cnt_tot) + ' / matches_len: ' + str(matches_len))
        
        #Empezamos el procesado de matches
        for scrapedduration, scrapedurl, scrapedtitle, scrapedthumb in matches:

            title = scrapedtitle
            title = title.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ü", "u").replace("ï¿½", "ñ").replace("Ã±", "ñ").replace("&atilde;", "a").replace("&etilde;", "e").replace("&itilde;", "i").replace("&otilde;", "o").replace("&utilde;", "u").replace("&ntilde;", "ñ").replace("&#8217;", "'")
            
            item_local = item.clone()                                                   #Creamos copia de Item para trabajar
            if item_local.tipo:                                                         #... y limpiamos
                del item_local.tipo
            if item_local.totalItems:
                del item_local.totalItems
            if item_local.post_num:
                del item_local.post_num
            if item_local.intervencion:
                del item_local.intervencion
            if item_local.viewmode:
                del item_local.viewmode
            if item_local.headers:
                del item_local.headers
            item_local.text_bold = True
            del item_local.text_bold
            item_local.text_color = True
            del item_local.text_color
            if item_local.url_plus:
                del item_local.url_plus
                
            title_subs = []                                                 #creamos una lista para guardar info importante
            item_local.language = []                                        #iniciamos Lenguaje
            item_local.quality = ""                                         #iniciamos calidad
            item_local.url = scrapedurl                                     #guardamos la url
            item_local.thumbnail = scrapedthumb                             #guardamos el thumb
            if channel not in item_local.thumbnail:                         #si el thumb está encriptado, paamos
                item_local.thumbnail = get_thumb("channels_tvshow.png")     #... y ponemos el de Series por defecto
            item_local.context = "['buscar_trailer']"
            
            item_local.contentType = "movie"                                #por defecto, son películas
            item_local.action = "findvideos"

            #Analizamos los formatos de series
            if '/top-series' in scrapedurl or item_local.extra == 'series':
                item_local.contentType = "tvshow"
                item_local.action = "episodios"
                
            #Buscamos calidades adicionales
            if "3d" in title.lower() and not "3d" in item_local.quality.lower():
                if item_local.quality:
                    item_local.quality += " 3D"
                else:
                    item_local.quality = "3D"
                title = re.sub('(?i)3D', '', title)
                title = title.replace('[]', '')
            if item_local.quality:
                item_local.quality += ' %s' % scrapertools.find_single_match(title, '\[(.*?)\]')
            else:
                item_local.quality = '%s' % scrapertools.find_single_match(title, '\[(.*?)\]')
            
            #Detectamos idiomas
            if ("latino" in scrapedurl.lower() or "latino" in title.lower()) and "LAT" not in item_local.language:
                item_local.language += ['LAT']
            elif ('subtitulado' in scrapedurl.lower() or 'subtitulado' in title.lower() or 'vose' in title.lower()) and "VOSE" not in item_local.language:
                item_local.language += ['VOSE']
            elif ('version-original' in scrapedurl.lower() or 'version original' in title.lower()) and "VO" not in item_local.language:
                item_local.language += ['VO']
            
            if item_local.language == []:
                item_local.language = ['CAST']

            #Detectamos info interesante a guardar para después de TMDB
            if scrapertools.find_single_match(title, '[m|M].*?serie'):
                title = re.sub(r'[m|M]iniserie', '', title)
                title_subs += ["Miniserie"]
            if scrapertools.find_single_match(title, '[s|S]aga'):
                title = re.sub(r'[s|S]aga', '', title)
                title_subs += ["Saga"]
            if scrapertools.find_single_match(title, '[c|C]olecc'):
                title = re.sub(r'[c|C]olecc...', '', title)
                title_subs += ["Colección"]
                
            if "duolog" in title.lower():
                title_subs += ["[Saga]"]
                title = title.replace(" Duologia", "").replace(" duologia", "").replace(" Duolog", "").replace(" duolog", "")
            if "trilog" in title.lower():
                title_subs += ["[Saga]"]
                title = title.replace(" Trilogia", "").replace(" trilogia", "").replace(" Trilog", "").replace(" trilog", "")
            if "extendida" in title.lower() or "v.e." in title.lower()or "v e " in title.lower():
                title_subs += ["[V. Extendida]"]
                title = title.replace("Version Extendida", "").replace("(Version Extendida)", "").replace("V. Extendida", "").replace("VExtendida", "").replace("V Extendida", "").replace("V.Extendida", "").replace("V  Extendida", "").replace("V.E.", "").replace("V E ", "").replace("V:Extendida", "")
            
            #Ponemos el año a '-'
            item_local.infoLabels["year"] = '-'
            
            #Limpiamos el título de la basura innecesaria
            title = re.sub(r'(?i)TV|Online|Spanish|Torrent|en Espa\xc3\xb1ol|Español|Latino|Subtitulado|Blurayrip|Bluray rip|\[.*?\]|R2 Pal|\xe3\x80\x90 Descargar Torrent \xe3\x80\x91|Completa|Temporada|Descargar|Torren', '', title)
            
            title = title.replace("Dual", "").replace("dual", "").replace("Subtitulada", "").replace("subtitulada", "").replace("Subt", "").replace("subt", "").replace("(Proper)", "").replace("(proper)", "").replace("Proper", "").replace("proper", "").replace("#", "").replace("(Latino)", "").replace("Latino", "").replace("LATINO", "").replace("Spanish", "").replace("Trailer", "").replace("Audio", "")

            #Terminamos de limpiar el título
            title = re.sub(r'\??\s?\d*?\&.*', '', title)
            title = re.sub(r'[\(|\[]\s+[\)|\]]', '', title)
            title = title.replace('()', '').replace('[]', '').strip().lower().title()
            
            item_local.from_title = title.strip().lower().title()   #Guardamos esta etiqueta para posible desambiguación de título

            #Salvamos el título según el tipo de contenido
            if item_local.contentType == "movie":
                item_local.contentTitle = title.strip().lower().title()
            else:
                item_local.contentSerieName = title.strip().lower().title()

            item_local.title = title.strip().lower().title()

            #Añadimos la duración a la Calidad
            if scrapedduration:
                if item_local.quality:
                    item_local.quality += ' [%s]' % scrapedduration
                else:
                    item_local.quality = '[%s]' % scrapedduration
                
            #Guarda la variable temporal que almacena la info adicional del título a ser restaurada después de TMDB
            item_local.title_subs = title_subs

            #Ahora se filtra por idioma, si procede, y se pinta lo que vale
            if config.get_setting('filter_languages', channel) > 0:     #Si hay idioma seleccionado, se filtra
                itemlist = filtertools.get_link(itemlist, item_local, list_language)
            else:
                itemlist.append(item_local.clone())                     #Si no, pintar pantalla
            
            cnt_title = len(itemlist)                                   #Contador de líneas añadidas
            if cnt_title >= cnt_tot:                                    #Si hemos llegado al límite de la página, pintamos
                cnt_title_tot += cnt_title
                break
            
            #logger.debug(item_local)

    #Pasamos a TMDB la lista completa Itemlist
    tmdb.set_infoLabels(itemlist, __modo_grafico__)
    
    #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
    item, itemlist = generictools.post_tmdb_listado(item, itemlist)

    # Si es necesario añadir paginacion
    if (curr_page <= last_page and item.extra not in ['populares']) or (cnt_title_tot < matches_len and 'populares' in item.extra):
        try:
            if last_page_foot > 1:
                title = '%s de %s' % (curr_page_foot-1, last_page_foot)
            else:
                title = '%s' % curr_page_foot-1
        except:
            last_page = 0
        
        if item.extra not in ['populares', 'series']:
            cnt_title_tot = 0

        if last_page > 0:
            itemlist.append(Item(channel=item.channel, action="listado", title=">> Página siguiente " + title, url=next_page_url, extra=item.extra, extra2=item.extra2, last_page=str(last_page), last_page_foot=str(last_page_foot), curr_page=str(curr_page), curr_page_foot=str(curr_page_foot), cnt_tot=str(cnt_tot), cnt_title_tot=str(cnt_title_tot), headers=headers))
            
            #logger.debug(str(cnt_tot) + ' / ' + str(cnt_title) + ' / ' + str(cnt_title_tot))

    return itemlist

    
def findvideos(item):
    logger.info()
    itemlist = []
    itemlist_t = []                                     #Itemlist total de enlaces
    itemlist_t_download = []                            #Itemlist total de enlaces descargas
    itemlist_f = []                                     #Itemlist de enlaces filtrados
    itemlist_f_download = []                            #Itemlist de enlaces filtrados
    if not item.language:
        item.language = ['CAST']                        #Castellano por defecto
    matches = []
    item.category = categoria
    
    item.extra2 = 'xyz'
    del item.extra2
    
    #logger.debug(item)

    #Bajamos los datos de la página
    data = ''
    #patron = '<link itemprop="embedUrl"\s*href="([^"]+)"\s*\/>(?:<iframe src="([^"]*)")?'
    patron = '"Url"\s*:\s*"([^"]+)"\s*\s*,"name"\s*:\s*"[^"]+"\s*,\s*"description"\s*:\s*"[^"]+"\s*,\s*"contentUrl"\s*:\s*"([^"]+)"\s*,\s*"embedUrl"\s*:'
    try:
        data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url, timeout=timeout).data)
        if not PY3:
            data = unicode(data, "utf-8", errors="replace").encode("utf-8")
    except:
        pass
        
    if not data:
        logger.error("ERROR 01: FINDVIDEOS: La Web no responde o la URL es erronea: " + item.url)
        itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 01: FINDVIDEOS:.  La Web no responde o la URL es erronea. Si la Web está activa, reportar el error con el log'))
        return itemlist                                 #si no hay más datos, algo no funciona, pintamos lo que tenemos
    if "Lo sentimos este documental ha sido eliminado" in data:
        itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': El documental ha sido eliminado'))
        return itemlist                                 #documental eliminado, pintamos lo que tenemos

    matches = re.compile(patron, re.DOTALL).findall(data)
    if not matches:                                     #error
        logger.error("ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web " + " / PATRON: " + patron + data)
        itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web.  Verificar en la Web esto último y reportar el error con el log'))
        return itemlist                                 #si no hay más datos, algo no funciona, pintamos lo que tenemos
    
    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)
    #logger.debug(data)
    
    #Llamamos al método para crear el título general del vídeo, con toda la información obtenida de TMDB
    item, itemlist = generictools.post_tmdb_findvideos(item, itemlist)
    
    #Si es un episodio suelto, se ofrece la posibilidad de ver la lista de Episodios completa
    if scrapertools.find_single_match(item.contentTitle, ':\s*(\d+)-\s*') and item.contentType != 'episode':
        serie = item.contentTitle
        url_serie = scrapertools.find_single_match(data, '<dt><span>Serie Documental<\/span><\/dt>\s*<dd><a href="([^"]+)"\s*>')
        serie = scrapertools.find_single_match(data, '<dt><span>Serie Documental<\/span><\/dt><dd><a href="[^"]+"\s*>(.*?)<')
        if url_serie:
            itemlist.append(item.clone(title="**-[COLOR yellow] Ver TODOS los episodios de la Serie [/COLOR]-**", action="episodios", contentType='tvshow', url=url_serie, extra="series", from_title=serie, wanted=serie, contentSerieName=serie, contentTitle=serie, quality="", language=[]))
   
    #Recorremos la lista de servidores Directos, excluyendo YouTube para trailers
    for scrapedurl, scrapedplayer in matches:
        #Generamos una copia de Item para trabajar sobre ella
        item_local = item.clone()
        
        #Buscamos la url del vídeo
        if 'cnubis.com' in scrapedplayer:
            videourl = conector_cnubis(scrapedurl, scrapedplayer)
            if not videourl[0][1]:
                logger.error("ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web")
                itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: FINDVIDEOS: No hay enlaces o ha cambiado la estructura de la Web.  Verificar en la Web esto último y reportar el error con el log'))
                continue                                        #si no hay más datos, algo no funciona, pintamos lo que tenemos
        else:
            videourl = servertools.findvideos(scrapedurl)
            
        #Ya tenemos un  enlace, lo pintamos
        if len(videourl) > 0:
            server = videourl[0][0]
            enlace = videourl[0][1]
            typefile = 'mp4'
            if videourl[0][2]:
                typefile = videourl[0][2]
            mostrar_server = True
            if config.get_setting("hidepremium"):                               #Si no se aceptan servidore premium, se ignoran
                mostrar_server = servertools.is_server_enabled(server)
            
            #Se comprueba si el vídeo existe
            if mostrar_server:
                item_local.alive = "??"                                         #Se asume poe defecto que es link es dudoso
                item_local.alive = servertools.check_video_link(enlace, server, timeout=timeout)
                if '?' in item_local.alive:
                    alive = '?'                                                 #No se ha podido comprobar el vídeo
                elif 'no' in item_local.alive.lower():
                    continue                                                    #El enlace es malo
                else:
                    alive = ''                                                  #El enlace está verificado

            #Ahora pintamos el link del Servidor Directo
            item_local.url = enlace
            item_local.title = '[COLOR yellow][%s][/COLOR] [COLOR yellow][%s][/COLOR] [COLOR limegreen][%s][/COLOR] [COLOR red]%s[/COLOR]' % (alive, server.capitalize(), item_local.quality, str(item_local.language))
            
            #Preparamos título y calidad, quitamos etiquetas vacías
            item_local.title = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.title)    
            item_local.title = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.title)
            item_local.title = item_local.title.replace("--", "").replace("[]", "").replace("()", "").replace("(/)", "").replace("[/]", "").strip()
            item_local.quality = re.sub(r'\s?\[COLOR \w+\]\[\[?\s?\]?\]\[\/COLOR\]', '', item_local.quality)
            item_local.quality = re.sub(r'\s?\[COLOR \w+\]\s?\[\/COLOR\]', '', item_local.quality)
            item_local.quality = item_local.quality.replace("--", "").replace("[]", "").replace("()", "").replace("(/)", "").replace("[/]", "").strip()
            
            item_local.action = "play"                                          #Visualizar vídeo
            item_local.server = server.lower()                                  #Servidor Directo
            
            itemlist_t.append(item_local.clone())                               #Pintar pantalla, si no se filtran idiomas
            
            #guardar el nombre del archivo para la descarga.  Añadir el tipo de archivo
            if item_local.contentType == 'episode':
                downloadFilename = '%s: %s.%s' % (item_local.contentSerieName, item_local.contentTitle, typefile)
            else:
                downloadFilename = '%s.%s' % (item_local.contentTitle, typefile)
            downloadFilename = downloadFilename.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ü", "u").replace("ï¿½", "ñ").replace("Ã±", "ñ").replace(':', '-')                #limpiar nombre de archivo de caracteres raros
            
            itemlist_t_download.append(item_local.clone(downloadFilename=downloadFilename))    #Pintar pantalla (descarga), si no se filtran idiomas
    
            # Requerido para FilterTools
            if config.get_setting('filter_languages', channel) > 0:             #Si hay idioma seleccionado, se filtra
                itemlist_f = filtertools.get_link(itemlist_f, item_local, list_language)  #Pintar pantalla, si no está vacío
                item_local.downloadFilename = downloadFilename
                itemlist_f_download = filtertools.get_link(itemlist_f_download, item_local, list_language)  #Pintar pantalla (descarga), si no está vacío
            
            #logger.debug("DIRECTO: " server + ' / ' + enlace + " / title: " + item.title + " / " + item_local.title + " / calidad: " + item_local.quality + " / content: " + item_local.contentTitle + " / " + item_local.contentSerieName)
            
            #logger.debug(item_local)

    if len(itemlist_f) > 0:                                                     #Si hay entradas filtradas...
        itemlist.extend(itemlist_f)                                             #Pintamos pantalla filtrada
    else:                                                                       
        if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t) > 0: #Si no hay entradas filtradas ...
            thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
            itemlist.append(Item(channel=item.channel, url=host, title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", thumbnail=thumb_separador))
        itemlist.extend(itemlist_t)                                             #Pintar pantalla con todo si no hay filtrado
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)                                              #Lanzamos Autoplay
    
    #Ahora pintamos las opciones de descarga
    if not item.unify:                                                          #Si Titulos Inteligentes NO seleccionados:
        title_gen = '**- [COLOR hotpink]Enlaces DESCARGAR: -**[/COLOR]'
    else:                                                                       #Si Titulos Inteligentes SÍ seleccionados:
        title_gen = '[COLOR hotpink]Enlaces DESCARGAR: [/COLOR]'  
    itemlist.append(item.clone(action="", server = "", title=title_gen))
    if len(itemlist_f_download) > 0:                                            #Si hay entradas filtradas...
        itemlist.extend(itemlist_f_download)                                    #Pintamos pantalla filtrada
    else:                                                                       
        if config.get_setting('filter_languages', channel) > 0 and len(itemlist_t_download) > 0:    #Si no hay entradas filtradas ...
            thumb_separador = get_thumb("next.png")                             #... pintamos todo con aviso
            itemlist.append(Item(channel=item.channel, url=host, title="[COLOR red][B]NO hay elementos con el idioma seleccionado[/B][/COLOR]", thumbnail=thumb_separador))
        itemlist.extend(itemlist_t_download)                                    #Pintar pantalla con todo si no hay filtrado
    
    return itemlist


def play(item):                                                                 #Permite preparar la descarga del vídeo para guardarlo
    logger.info()
    itemlist = []
    headers = []
    import os
    from core import downloadtools
    
    if item.downloadFilename:                                                   #Si hay nombre de vídeo, es descarga
        headers.append(["User-Agent", httptools.random_useragent()])            #Se busca un User-Agent aleatorio
        filepath = os.path.join(config.get_setting("downloadpath"), item.downloadFilename)  #Path de descarga
        ret = downloadtools.downloadfile(item.url, filepath, headers=headers, continuar=True, silent=False)     #Descarga del vídeo
        del item.downloadFilename
        item.url = filepath                                                     #Reproducir el vídeo descargado

    itemlist.append(item.clone())                                               #Reproducción normal
        
    return itemlist
    
    
def episodios(item):
    logger.info()
    itemlist = []
    item.category = categoria
    
    #logger.debug(item)

    if item.from_title:
        item.title = item.from_title
    item.extra2 = 'xyz'
    del item.extra2
    next_page_url = item.url
    
    inicio = time.time()                                    # Controlaremos que el proceso no exceda de un tiempo razonable
    fin = inicio + 10                                                           # Después de este tiempo pintamos (segundos)
    timeout_search = timeout                                                    # Timeout para descargas
    
    item.quality = re.sub(r'\s?\[\d+:\d+\]', '', item.quality)                  #quitamos la duración de la serie

    # Obtener la información actualizada de la Serie.  TMDB es imprescindible para Videoteca
    if not item.infoLabels['tmdb_id']:
        tmdb.set_infoLabels(item, True)
    
    #Bucle para recorrer todas las páginas
    epis = 1
    while next_page_url and fin > time.time():
    
        # Descarga la página
        data = ''                                                                   #Inserto en num de página en la url
        try:
            data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)|&nbsp;", "", httptools.downloadpage(next_page_url, timeout=timeout).data)
            if not PY3:
                data = unicode(data, "utf-8", errors="replace").encode("utf-8")
        except:                                                                     #Algún error de proceso, salimos
            pass
            
        if not data:
            logger.error("ERROR 01: EPISODIOS: La Web no responde o la URL es erronea" + item.url)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 01: EPISODIOS:.  La Web no responde o la URL es erronea. Si la Web está activa, reportar el error con el log'))
            return itemlist

        #Buscamos los episodios
        patron = '<span class="pm-label-duration">(.*?)<\/span>.*?<a href="([^"]+)" title="([^"]+)">.*?data-echo="([^"]+)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        if not matches:                                                             #error
            item = generictools.web_intervenida(item, data)                         #Verificamos que no haya sido clausurada
            if item.intervencion:                                                   #Sí ha sido clausurada judicialmente
                item, itemlist = generictools.post_tmdb_episodios(item, itemlist)   #Llamamos al método para el pintado del error
                return itemlist                                                     #Salimos
            
            logger.error("ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web " + " / PATRON: " + patron + " / DATA: " + data)
            itemlist.append(item.clone(action='', title=item.channel.capitalize() + ': ERROR 02: EPISODIOS: Ha cambiado la estructura de la Web.  Reportar el error con el log'))
            return itemlist                         #si no hay más datos, algo no funciona, pintamos lo que tenemos

        #logger.debug("PATRON: " + patron)
        #logger.debug(matches)
        #logger.debug(data)
        
        patron = '<li class=""><a href="([^"]+)">&raquo;<\/a><\/li><\/ul><\/div><\/div>\s*<\/div>'
        next_page_url = ''
        next_page_url = scrapertools.find_single_match(data, patron)
        if next_page_url:
            next_page_url = urlparse.urljoin(host, next_page_url)
        #logger.debug(next_page_url)

        # Recorremos todos los episodios generando un Item local por cada uno en Itemlist
        for scrapedduration, scrapedurl, scrapedtitle, scrapedthumbnail in matches:
            item_local = item.clone()
            item_local.action = "findvideos"
            item_local.contentType = "episode"
            item_local.extra = "episodios"
            if item_local.library_playcounts:
                del item_local.library_playcounts
            if item_local.library_urls:
                del item_local.library_urls
            if item_local.path:
                del item_local.path
            if item_local.update_last:
                del item_local.update_last
            if item_local.update_next:
                del item_local.update_next
            if item_local.channel_host:
                del item_local.channel_host
            if item_local.active:
                del item_local.active
            if item_local.contentTitle:
                del item_local.infoLabels['title']
            if item_local.season_colapse:
                del item_local.season_colapse
            if item_local.unify:
                del item_local.unify
            if item_local.tmdb_stat:
                del item_local.tmdb_stat
            item_local.wanted = 'xyz'
            del item_local.wanted
            
            item_local.title = ''
            item_local.context = "['buscar_trailer']"
            item_local.url = scrapedurl
            title = scrapedtitle
            item_local.language = []
            
            #Buscamos calidades del episodio
            if 'hdtv' in scrapedtitle.lower() or 'hdtv' in scrapedurl:
                item_local.quality = 'HDTV'
            elif 'hd7' in scrapedtitle.lower() or 'hd7' in scrapedurl:
                item_local.quality = 'HD720p'
            elif 'hd1' in scrapedtitle.lower() or 'hd1' in scrapedurl:
                item_local.quality = 'HD1080p'
                
            if not item_local.quality:
                item_local.quality = '[%s]' % scrapedduration
            
            #Buscamos idiomas del episodio
            lang = scrapedtitle.strip()
            if ('v.o' in lang.lower() or 'v.o' in scrapedurl.lower()) and not 'VO' in item_local.language:
                item_local.language += ['VO']
            elif ('vose' in lang.lower() or 'v.o.s.e' in lang.lower() or 'vose' in scrapedurl.lower() or 'v.o.s.e' in scrapedurl.lower()) and not 'VOSE' in item_local.language:
                item_local.language += ['VOSE']
            elif ('latino' in lang.lower() or 'latino' in scrapedurl.lower()) and not 'LAT' in item_local.language:
                item_local.language += ['LAT']
                
            if not item_local.language:
                item_local.language += ['CAST']

            #Buscamos la Temporada y el Episodio
            item_local.contentSeason = 0
            item_local.contentEpisodeNumber = 0
            try:
                #Extraemos los episodios
                patron = ':\s*(\d+)-\s*'
                if scrapertools.find_single_match(title, patron):
                    item_local.contentEpisodeNumber = int(scrapertools.find_single_match(title, patron))
                
                #Extraemos la temporada
                patron = '\s*\(t|T(\d+)\):'
                if scrapertools.find_single_match(title, patron):
                    item_local.contentSeason = int(scrapertools.find_single_match(title, patron))
            except:
                logger.error('ERROR al extraer Temporada/Episodio: ' + title)
                
            if item_local.contentSeason == 0:
                if 'ii:' in title.lower(): item_local.contentSeason = 2
                elif 'iii:' in title.lower(): item_local.contentSeason = 3
                elif 'iv:' in title.lower(): item_local.contentSeason = 4
                else: item_local.contentSeason = 1
                    
            if item_local.contentEpisodeNumber == 0:
                item_local.contentEpisodeNumber = epis
            
            #Formateamos el título compatible con la Videoteca
            item_local.title = '%sx%s -' % (str(item_local.contentSeason), str(item_local.contentEpisodeNumber).zfill(2))
            patron = ':(?:\s*\d+-)?\s*(.*?)$'
            item_local.infoLabels['episodio_titulo'] = scrapertools.find_single_match(title, patron)
            
            itemlist.append(item_local.clone())
            epis += 1
            
            #logger.debug(item_local)
            
    if len(itemlist) > 1:
        itemlist = sorted(itemlist, key=lambda it: (int(it.contentSeason), int(it.contentEpisodeNumber)))       #clasificamos

    # Pasada por TMDB y clasificación de lista por temporada y episodio
    tmdb.set_infoLabels(itemlist, True)

    #Llamamos al método para el maquillaje de los títulos obtenidos desde TMDB
    item, itemlist = generictools.post_tmdb_episodios(item, itemlist)
    
    #logger.debug(item)

    return itemlist
    
    
def actualizar_titulos(item):
    logger.info()
    
    item = generictools.update_title(item) #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels
    
    #Volvemos a la siguiente acción en el canal
    return item


def conector_cnubis(scrapedurl, scrapedplayer):
    #logger.info("url=%s, player=https:%s" % (scrapedurl, scrapedplayer))
    videourl = []
    url_serv = 'directo'

    if scrapedplayer.endswith('.mp4') or scrapedplayer.endswith('.mkv') or scrapedplayer.endswith('.avi'):
        url_type = scrapertools.find_single_match(scrapedplayer, '\.\w+$')
        videourl.append([url_serv, scrapedplayer, url_type])                    #responde como si volviera de servertools.findvideos()
        return videourl

    #headers.update(dict({ 'Referer': scrapedurl }))                            #Referer con la url inical
    headers = { 'Referer': scrapedurl }                                         #Referer con la url inical
    #busca el video a partir del player + url inical
    if not scrapedplayer.startswith("https:"):
        https_header = 'https:'
    else:
        https_header = ''
    data = httptools.downloadpage(https_header + scrapedplayer, headers=headers, timeout=timeout).data

    if scrapertools.find_single_match(data, 'file\s*:\s*"([^"]*)"\s*,\s*type\s*:\s*"([^"]*)'):                  #obtiene la url de vídeo
        url_file, url_type = scrapertools.find_single_match(data, 'file\s*:\s*"([^"]*)"\s*,\s*type\s*:\s*"([^"]*)')
        if not url_file.startswith("https:"):
            url_file = 'https:%s' % (url_file)
    else:
        url_file = scrapertools.find_single_match(data, '<meta itemprop="contentURL" content="([^"]+)" />')     #obtiene la url de vídeo
        if not url_file.startswith("https:"):
            url_file = 'https:%s' % (url_file)
        url_type = scrapertools.find_single_match(data, 'file\s*:\s*"[^"]*"\s*,\s*type\s*:\s*"([^"]*)')

    videourl.append([url_serv, url_file, url_type])                             #responde como si volviera de servertools.findvideos()
    
    #logger.info(videourl)
    return videourl

    
def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    
    try:
        item.url = item.url + texto

        if texto != '':
            return listado(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []
 
 
def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    
    try:
        if categoria == 'documentales':
            item.url = host + "newvideos.html"
            item.extra = "novedades"
            item.channel = channel
            item.category_new= 'newest'

            itemlist = listado(item)
            if ">> Página siguiente" in itemlist[-1].title:
                itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

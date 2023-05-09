# -*- coding: utf-8 -*-
# -*- Channel AnimeSpace -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

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

from core import httptools
from core import scrapertools
from core import servertools
from channelselector import get_thumb
from core import tmdb
from core.item import Item
from platformcode import logger, config
from channels import autoplay
from channels import filtertools
from channels import renumbertools


IDIOMAS = {'VOSE': 'VOSE'}
list_language = list(IDIOMAS.values())
list_quality = []
list_servers = ['directo', 'okru', 'fembed', 'yourupload', 'rapidvideo', 'streamango']

canonical = {
             'channel': 'hitokin', 
             'host': config.get_setting("current_host", 'hitokin', default=''), 
             'host_alt': ["https://hitokin.net/"], 
             'host_black_list': [], 
             'status': 'WEB DESACTIVADA', 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = []

    itemlist.append(Item(channel=item.channel, title="Nuevos Episodios",
                         action="new_episodes",
                         thumbnail='https://i.imgur.com/IexJg5R.png',
                         url=host+'recientes.php'))

    itemlist.append(Item(channel=item.channel, title="Últimos Animes",
                               action="list_all", not_post=True,
                               thumbnail='https://i.imgur.com/tABpHJX.png',
                               url=host + 'animes.php',
                               ar_post='buscar=&from=&pinput=0&orden=0'))

    itemlist.append(Item(channel=item.channel, title="Más Populares",
                               action="list_all",
                               thumbnail='https://i.imgur.com/0CGZAoH.png',
                               url=host + 'tops.php'))

    itemlist.append(Item(channel=item.channel, title="Géneros",
                              action="generos",
                              thumbnail='https://i.imgur.com/Xcuwfu5.png',
                              url=host + 'categorias.php'))

    itemlist.append(Item(channel=item.channel, title="Películas",
                         action="list_all",
                         thumbnail='https://i.imgur.com/aYBo36W.png',
                         url=host + 'animes.php',
                         ar_post='buscar=&from=&pinput=0&tipo%5B%5D=2&orden=0'))

    itemlist.append(Item(channel=item.channel, title="OVAs",
                              action="list_all",
                              thumbnail='https://i.imgur.com/zaDtLD3.png',
                              url=host + 'animes.php',
                              ar_post='buscar=&from=&pinput=0&tipo%5B%5D=4&orden=0'))


    itemlist.append(Item(channel=item.channel, title="Especiales",
                              action="list_all",
                              thumbnail='https://i.imgur.com/NMfafYV.png',
                              url=host + 'animes.php',
                              ar_post='buscar=&from=&pinput=0&tipo%5B%5D=3&orden=0'))

    itemlist.append(Item(channel=item.channel, title="Buscar",
                               action="search",
                               url=host + '%s/animes.php',
                               thumbnail='https://i.imgur.com/ZVMl3NP.png'))

    autoplay.show_option(item.channel, itemlist)
    itemlist = renumbertools.show_option(item.channel, itemlist)

    return itemlist


def get_source(url, post=None):
    logger.info()
    data = httptools.downloadpage(url, post=post, canonical=canonical).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    return data


def list_all(item):
    logger.info()

    itemlist = []

    if item.ar_post and not item.not_post:
      data = get_source(item.url, post=item.ar_post)
    else:
      data = get_source(item.url)
    patron = '<div class="col-6.*?href="([^"]+)".*?>(.*?)<img.*?'#url, info
    patron += 'data-src="([^"]+)".*?<p.*?>([^<]+)</p>'#thumb,title
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, info, scrapedthumbnail, scrapedtitle in matches:
        _type = scrapertools.find_single_match(info,'>([^<]+)</').lower()
        year = '-'
        year = scrapertools.find_single_match(scrapedtitle,'\(\d{4}\)')
        url = scrapedurl
        if not url.startswith('http'):
            url = urlparse.urljoin(host, url)
        thumbnail = scrapedthumbnail
        thumb = scrapertools.find_single_match(thumbnail,'portadas/(.*)')
        lang = 'VOSE'
        title = scrapedtitle
        scrapedtitle = re.sub('\(.*?\)$', '', scrapedtitle).strip()
        if _type:
          title += '[COLOR darkgrey] (%s)[/COLOR]' % _type.capitalize()
        context = renumbertools.context(item)
        context2 = autoplay.context
        context.extend(context2)
        new_item= Item(channel=item.channel,
                       title=title,
                       thumbnail=thumbnail,
                       language=lang,
                       thumb=thumb,
                       infoLabels={'year':year}
                       )
        if 'pel' in _type:
            new_item.contentTitle=scrapedtitle
            new_item.action = 'findvideos'
            new_item.url = url.replace(host, '%s1/' % host)
        else:
            new_item.plot=_type.capitalize()
            new_item.contentSerieName=scrapedtitle
            new_item.context = context
            new_item.action = 'episodios'
            new_item.url = url
        itemlist.append(new_item)

        # Paginacion
    next_page = scrapertools.find_single_match(data,
                                               ' data-id="(\d+)" aria-label="Next">')

    if next_page != "":
        ar_post = re.sub('pinput=(\d+)&', 'pinput=%s&' % next_page, item.ar_post)
        itemlist.append(Item(channel=item.channel,
                             action="list_all",
                             title=">> Página siguiente",
                             url=item.url,
                             ar_post= ar_post,
                             thumbnail='https://s16.postimg.cc/9okdu7hhx/siguiente.png'
                             ))
    tmdb.set_infoLabels(itemlist, seekTmdb=True)
    return itemlist

def generos(item):
    logger.info()
    itemlist = []
    data = get_source(item.url)
    patron = '(?s)<a class="block.*?href="([^"]+)">.*?'
    patron += '>(\d+).*?<img .*? src="([^"]+)".*?<p .*?>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url, num, thumb, title in matches:
        titles = '%s [COLOR darkgrey](%s animes)[/COLOR]' % (title.strip(), num)
        thumb = urlparse.urljoin(host, thumb)
        itemlist.append(
            Item(channel=item.channel, action="list_all", title=titles,
                 url=url, thumbnail=thumb, plot=title))
    return itemlist

def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url % texto
    try:
        if texto != '':
            return list_all(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def new_episodes(item):
    logger.info()

    itemlist = []

    full_data = get_source(item.url)
    #data = scrapertools.find_single_match(full_data, 'id="episodios_index">(.*?)>Anuncio</h3>')
    
    patron = '<div class="col-6.*?href="([^"]+)">.*?>isodio</span> (\d+)<.*?'
    patron += 'data-src="([^"]+)".*?<p.*?>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(full_data)

    for scrapedurl, epi, scrapedthumbnail, scrapedtitle in matches:
        url = host+scrapedurl
        lang = 'VOSE'
        title = '%s: 1x%s' % (scrapedtitle, epi)
        itemlist.append(Item(channel=item.channel, title=title, url=url, thumbnail=scrapedthumbnail,
                             action='findvideos', contentSerieName=scrapedtitle, language=lang))
    tmdb.set_infoLabels(itemlist, seekTmdb=True)
    return itemlist

def episodios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, canonical=canonical).data

    list_episodes = eval(scrapertools.find_single_match(data, r'var episodios = (.*?),\s'))


    infoLabels = item.infoLabels
    for episode in list_episodes:
        episode = int(episode[0])
        lang = 'VOSE'
        season, episode = renumbertools.numbered_for_tratk(item.channel, item.contentSerieName, 1, episode)
        title = "%sx%s - %s" % (season, str(episode).zfill(2),item.contentSerieName)
        url = item.url.replace(host, '%s%s/' % (host, episode))
        thumbnail = '%sSubidas/anime/miniaturas/t_%s_%s' % (host, episode, item.thumb)
        infoLabels['season'] = season
        infoLabels['episode'] = episode

        itemlist.append(Item(channel=item.channel, title=title, contentSerieName=item.contentSerieName, url=url,
                             action='findvideos', language=lang, thumbnail=thumbnail, infoLabels=infoLabels))

    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    itemlist = itemlist[::-1]
    if item.contentSerieName != '' and config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(
            Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la videoteca[/COLOR]', url=item.url,
                 action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName,
                 extra1='library'))

    return itemlist


def findvideos(item):
    logger.info()
    servers_l = {'sm': 'streamango',
              'natsuki': 'directo',
              'izanagui': 'directo',
              'media': 'mediafire',
              'streamium': 'oprem'}
    itemlist = []
    p_data = ""

    data = get_source(item.url)

    p_nombre = scrapertools.find_single_match(item.url, "/\d+/(.*)")
    p_seccion = 'reproductor'
    matches0 = re.compile('<input type="hidden" name="([^"]+)" value="([^"]+)">',
                           re.DOTALL).findall(data)
    for name, value in matches0:
        p_data += '%s=%s&' % (name, value)
    p_data = urllib.quote(p_data)
    patron = 'data-tipo="(\d+)".*?title="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for p_servidor,scrapedtitle in matches:
        server = ""

        scrapedurl = '%s%s.php' % (host, p_seccion)
        logger.error(scrapedurl)
        '''post = {'seccion': p_seccion,
                'data': p_data,
                'nombre': p_nombre,
                'servidor': p_servidor}
        post = jsontools.dump(post)'''
        post = 'seccion=%s&data=%s&nombre=%s&servidor=%s' % (p_seccion,
                p_data, p_nombre, p_servidor)
        title = scrapedtitle.replace('Embed', 'Fembed')
        server = servers_l.get(title.lower(), title.lower())
        if scrapedurl != '':
            itemlist.append(Item(channel=item.channel, title=title, p_post=post, 
                                url=scrapedurl, action='play',
                                language = item.language, infoLabels=item.infoLabels, 
                                server=server, thumbnail=item.thumbnail))


    # Requerido para FilterTools

    itemlist = filtertools.get_links(itemlist, item, list_language)

    # Requerido para AutoPlay

    autoplay.start(itemlist, item)

    return itemlist

def play(item):
    itemlist = []
    if item.p_post:
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        json = httptools.downloadpage(item.url, post=item.p_post, headers=headers).json
        data = json.get('html', '')
        mess = json.get('mensaje', '')
        if data:
            url = scrapertools.find_single_match(data, 'src="([^"]+)"')
            if not url.startswith('http'):
                url = 'http:'+url
            #parchear enlace mediafire
            if 'mediafire' in url and not '/file/' in url:
                url = re.sub('://(.*?)\.mediafire', "://www.mediafire", url)
                url = re.sub('\.mediafire.*?/(\w+)/', ".mediafire.com/file/", url)
            elif 'streamium' in url and not '/files/' in url:
                _hash = scrapertools.find_single_match(url, 'hash=([a-zA-Z0-9]+)')
                url = 'http://streamium.xyz/files/%s' % _hash
            item.url = url
        else:
            item.url = ''
            logger.error(mess)

    return [item]

def newest(categoria):
    itemlist = []
    item = Item()
    if categoria == 'anime':
        item.url=host
        itemlist = new_episodes(item)
    return itemlist

# -*- coding: utf-8 -*-
# -*- Channel HDporn92 -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAdultChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_A
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_A
list_quality_tvshow = []
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_A
forced_proxy_opt = 'ProxySSL'

# https://xnxx2.tv/   https://aagmaal.to/   MISMO CONTENIDO INDI  https://video.nangiphotos.com/
# https://hentay.co/
# https://xnxxxvideosxxx.com/  CAMBIO ESTRUCTURA

canonical = {
             'channel': 'xnxxxvideoshd', 
             'host': config.get_setting("current_host", 'xnxxxvideoshd', default=''), 
             'host_alt': ["https://www.xnxxxvideoshd.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 10
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['video-list-content ','videos-list']}]),
                       ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
            # {'find_all': [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]},
         'categories': dict([('find', [{'tag': ['div'], 'class': ['video-list-content ','videos-list']}]),
                             ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_stime': dict([('find', [{'tag': ['span'], 'itemprop': ['duration']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['hd-video']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['span'], 'class': ['vids']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                            },
         'controls': {'url_base64': False, 'cnt_tot': 16, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    # autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="xnxxxvideoshd" , action="submenu", url= "https://www.xnxxxvideoshd.com/", chanel="xnxxxvideoshd", thumbnail = "https://i.postimg.cc/PqJ99VBk/xnxxxvideoshd.png"))
    itemlist.append(Item(channel=item.channel, title="hentayco" , action="submenu", url= "https://hentay.co/", chanel="hentayco", thumbnail = "https://i.postimg.cc/ZYscDKJ0/hentayco.png"))
    itemlist.append(Item(channel=item.channel, title="xnxx2" , action="submenu", url= "https://xnxx2.tv/", chanel="xnxx2", thumbnail = "https://i.postimg.cc/hGwCQDhX/xnxxtv.png"))
    itemlist.append(Item(channel=item.channel, title="nangivideos" , action="submenu", url= "https://video.nangiphotos.com/", chanel="nangivideos", thumbnail = "https://i.postimg.cc/SRr0F3Sy/nangivideos.png"))
    # itemlist.append(Item(channel=item.channel, title="xnxxxvideosxxx" , action="submenu", url= "https://xnxxxvideosxxx.com/", chanel="xnxxxvideosxxx", thumbnail = "https://i.postimg.cc/26vLLtSW/xnxxxvideosxxx.png"))
    
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    
    # autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "page/1/?filter=latest", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "page/1/?filter=most-viewed", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "page/1/?filter=popular", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "page/1/?filter=longest", chanel=item.chanel))
    if not "hentayco" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "actors/page/1/", extra="PornStar", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categories" , action="section", url=item.url + "categories/page/1/", extra="Canal", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars|actor)\/[^$]+$)', r'\1page/1/?filter=latest']]
    
    # if item.extra == 'Categorias':
        # findS['controls']['cnt_tot'] = 9999
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    # findS['controls']['action'] = 'findvideos'
    if item.extra == 'PornStar':
        findS['controls']['cnt_tot'] = 12
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    if soup.find('div', id=re.compile(r"^video-actor(?:s|)")):
        pornstars = soup.find('div', id=re.compile(r"^video-actor(?:s|)")).find_all('a', href=re.compile("/actor/[A-z0-9-]+/"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        lista.insert (2, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    match = soup.find('div', class_="responsive-player")
    if match.find('source'):
        url = match.source['src']
    elif match.iframe.get('data-lazy-src', ''):
        url = match.iframe['data-lazy-src']
    else:
        url = match.iframe['src']
    if "php?q=" in url:
        import base64
        url = url.split('php?q=')
        url_decode = base64.b64decode(url[-1]).decode("utf8")
        decode = urlparse.unquote(url_decode)
        # url += "|Referer=%s" % host
        url = scrapertools.find_single_match(decode, '<(?:iframe|source) src="([^"]+)"')
        if not url:
            url = scrapertools.find_single_match(decode, "<(?:iframe|source) src='([^']+)'")
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    # item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    item.url = "%s?s=%s&filter=latest" % (item.url, texto.replace(" ", "+"))
    
    try:
        if texto:
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

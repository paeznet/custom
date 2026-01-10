# -*- coding: utf-8 -*-
# -*- Channel pornegy -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAdultChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = {}
list_language = list(set(IDIOMAS.values()))
list_quality = []
list_quality_movies = []
list_quality_tvshow = []
list_servers = []
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'pornegy', 
             'host': config.get_setting("current_host", 'pornegy', default=''), 
             'host_alt': ["https://pornegy.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': {'find_all': [{'tag': ['div'], 'id': re.compile(r"^vid-\d+")}]},
         'categories': dict([('find', [{'tag': ['div'], 'class': ['studios']}]),
                             ('find_all', [{'tag': ['a'], 'href': re.compile(r"^post-\d+")}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['/\d+.html', '/%s.html'], ['&p=\d+', '&p=%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/01.html"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=host + "most-viewed/1.html"))
    itemlist.append(Item(channel=item.channel, title="MissaX" , action="list_all", url=host + "tags/missax/01.html"))
    itemlist.append(Item(channel=item.channel, title="Bang Bros" , action="list_all", url=host + "tags/bang-bros/01.html"))
    itemlist.append(Item(channel=item.channel, title="Blacked" , action="list_all", url=host + "tags/blacked/01.html"))
    itemlist.append(Item(channel=item.channel, title="Bratty Sis" , action="list_all", url=host + "tags/brattysis/01.html"))
    itemlist.append(Item(channel=item.channel, title="Pure Taboo" , action="list_all", url=host + "tags/pure-taboo/01.html"))
    itemlist.append(Item(channel=item.channel, title="Shoplyfter" , action="list_all", url=host + "tags/shoplyfter/01.html"))
    itemlist.append(Item(channel=item.channel, title="Sis Loves Me" , action="list_all", url=host + "tags/sislovesme/01.html"))
    itemlist.append(Item(channel=item.channel, title="My Pervy Family" , action="list_all", url=host + "tags/mypervyfamily/01.html"))
    itemlist.append(Item(channel=item.channel, title="XNXX" , action="list_all", url=host + "tags/xnxx/01.html"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()
    
    # return AlfaChannel.list_all(item, **kwargs)
    return AlfaChannel.list_all(item, matches_post=list_all_matches, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        
        elem_json = {}
        
        try:
            id = elem['id'].replace('vid-', '')
            
            # elem_json['url'] = "%sembed/%s.html" %(host,id)
            elem_json['url'] = "https://www.trendyporn.com/embed/%s" %id
            elem_json['title'] = elem.a.get('title', '') \
                                 or elem.find(class_='title').get_text(strip=True) if elem.find(class_='title') else ''
            if not elem_json['title']:
                elem_json['title'] = elem.img.get('alt', '')
            elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                     or elem.img.get('data-src', '') or elem.img.get('data-lazy-src', '') \
                                     or elem.img.get('src', '')
            elem_json['stime'] = elem.find(class_='timer').get_text(strip=True) if elem.find(class_='timer') else ''
            if elem.find('div', class_='res-badge'):
                elem_json['quality'] = 'HD'
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    return matches


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    itemlist = []
    
    # data = AlfaChannel.httptools.downloadpage(item.url, **kwargs).data  ## "%sembed/%s.html" %(host,id)
    # data = re.sub(r'\\"', '"', data)
    # logger.debug(data)
    # matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)" title="(\d+p)" type="video/mp4"')
    # for url, quality in matches:
        # url += "|REferer=%s" %host
        # itemlist.append(['[pornegy] %s' %quality, url])
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch?q=%s&p=1" % (host, texto.replace(" ", "+"))
    
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

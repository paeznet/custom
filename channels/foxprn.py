# -*- coding: utf-8 -*-
# -*- Channel foxprn -*-
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
             'channel': 'foxprn', 
             'host': config.get_setting("current_host", 'foxprn', default=''), 
             'host_alt': ["https://foxprn.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['li'], 'class': ['thumb']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': dict([('find', [{'tag': ['div'], 'class': ['studios']}]),
                             ('find_all', [{'tag': ['a'], 'href': re.compile(r"^post-\d+")}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['/page/\d+.html', '/page/%s.html']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 45, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "page/01.html"))
    itemlist.append(Item(channel=item.channel, title="Brazzers" , action="list_all", url=host + "tags/brazzers/01.html"))
    itemlist.append(Item(channel=item.channel, title="Bang Bros" , action="list_all", url=host + "tags/bang-bros/01.html"))
    itemlist.append(Item(channel=item.channel, title="Blacked" , action="list_all", url=host + "tags/blacked/01.html"))
    itemlist.append(Item(channel=item.channel, title="Bratty Sis" , action="list_all", url=host + "tags/brattysis/01.html"))
    itemlist.append(Item(channel=item.channel, title="Pure Taboo" , action="list_all", url=host + "tags/pure-taboo/01.html"))
    itemlist.append(Item(channel=item.channel, title="Shoplyfter" , action="list_all", url=host + "tags/shoplyfter/01.html"))
    itemlist.append(Item(channel=item.channel, title="Sis Loves Me" , action="list_all", url=host + "tags/sislovesme/01.html"))
    itemlist.append(Item(channel=item.channel, title="Team Skeet" , action="list_all", url=host + "tags/teamskeet/01.html"))
    itemlist.append(Item(channel=item.channel, title="XNXX" , action="list_all", url=host + "tags/xnxx/01.html"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()
    
    return AlfaChannel.list_all(item, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    data = soup.find('iframe', class_='embed-responsive-item')['src']
    url = scrapertools.find_single_match(data, '/([a-z0-9]+).html')
    url = " https://mydaddy.cc/video/%s" %url
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/01.html" % (host, texto.replace(" ", "-"))
    
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

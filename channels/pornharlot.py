# -*- coding: utf-8 -*-
# -*- Channel pornharlot -*-
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

IDIOMAS = AlfaChannelHelper.IDIOMAS_A
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_A
list_quality_tvshow = []
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_A
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'pornharlot', 
             'host': config.get_setting("current_host", 'pornharlot', default=''), 
             'host_alt': ["https://www.pornharlot.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['div'],  'class': ['col-md-4']}]},
         'categories': {'find_all': [{'tag': ['div'], 'class': ['col-md-4']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['page=\d+', 'page=%s']], 
         'last_page': dict([('find', [{'tag': ['ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'href', '@TEXT': 'page=(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_stime': dict([('find', [{'tag': ['div'], 'class': ['duration']}]),
                                                    ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(?:\d+:\d+:\d+|\d+:\d+)'}])]),
                            'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['hd-text-icon']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['float-right']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                            },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    plot = '[COLOR yellow]No existen los videos[/COLOR]'
    
    itemlist.append(Item(channel=item.channel, title="Nuevos", action="list_all", url=host + "videos?o=mr&page=1", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Más visto", action="list_all", url=host + "videos?o=mv&t=m&page=1", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado", action="list_all", url=host + "videos?o=tr&t=m&page=1", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Mas comentado", action="list_all", url=host + "videos?o=md&t=m&page=1", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Favoritos", action="list_all", url=host + "videos?o=tf&t=m&page=1", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Mas largo", action="list_all", url=host + "videos?o=lg&t=m&page=1", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="section", url=host + "categories", extra="Categorias", contentPlot=plot))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", contentPlot=plot))

    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/videos\/[^$]+$)', r'\1?o=mr&page=1']]
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


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
    if soup.find('div', class_='video-embedded'):
        item.url = soup.find('div', class_='video-embedded').find(re.compile("(?:iframe|source)"))['src']
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/videos/%s?o=mr&page=1" % (host, texto.replace(" ", "-"))
    
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

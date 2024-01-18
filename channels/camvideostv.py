# -*- coding: utf-8 -*-
# -*- Channel CamvideosTV -*-
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
             'channel': 'camvideostv', 
             'host': config.get_setting("current_host", 'camvideostv', default=''), 
             'host_alt': ["http://www.camvideos.tv/"], 
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


finds = {'find':  dict([('find', [{'tag': ['div'], 'class': ['video-list', 'list-videos']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['item', 'video-item']}])]),
         'categories': dict([('find', [{'tag': ['div'], 'class': ['models_list', 'list-models', 'category_list', 'list-categories', 'video-list', 'list-videos', 'list-channels', 'list-sponsors']}]),
                             ('find_all', [{'tag': ['div', 'a'], 'class': ['item', 'video-item']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'data-parameters', '@TEXT': '\:(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default', 'premium_skip': 'Private'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "search/?sort_by=post_date&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "search/?sort_by=video_viewed_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorada" , action="list_all", url=host + "search/?sort_by=rating_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Favoritas" , action="list_all", url=host + "search/?sort_by=most_favourited&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentadas" , action="list_all", url=host + "search/?sort_by=most_commented&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Largas" , action="list_all", url=host + "search/?sort_by=duration&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels/?sort_by=avg_videos_popularity&from=1", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "models/?sort_by=avg_videos_rating&from=1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|category-name|channels|sites|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
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
    if soup.find_all('a', href=re.compile("/(?:pornstars|models|model)/[A-z0-9-]+/")):
        pornstars = soup.find_all('a', href=re.compile("/(?:pornstars|models|model)/[A-z0-9-]+/"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if "HD" in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    # item.url = "%ssearch/%s/?sort_by=post_date&from_videos=01" % (host,texto.replace(" ", "-"))
    item.url = "%ssearch/?q=%s&sort_by=post_date&from_videos=1" % (host, texto.replace(" ", "+"))
    
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

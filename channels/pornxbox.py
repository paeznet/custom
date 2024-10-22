# -*- coding: utf-8 -*-
# -*- Channel PornxBox -*-
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

#  https://porn2all.com/   https://pornxbox.com/
#  https://tonicporn.com/ OUT

canonical = {
             'channel': 'pornxbox', 
             'host': config.get_setting("current_host", 'pornxbox', default=''), 
             'host_alt': ["https://porn2all.com/"], 
             'host_black_list': ["https://porn2best.com/", "https://pornxbox.com/"], 
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


finds = {'find':  dict([('find', [{'tag': ['div'], 'class': ['video-list', 'list-videos', 'thumbs_video', 'thumbs_list', 'thumbs', 'items-videos']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['item', 'video-item', 'th']}])]),
         'categories': dict([('find', [{'tag': ['div'], 'class': ['models_list', 'list-models', 'category_list', 'list-categories', 'video-list', 'list-videos', 'list-channels', 'list-sponsors', 'thumbs', 'thumbs_list', 'categories_list']}]),
                             ('find_all', [{'tag': ['div', 'a'], 'class': ['item', 'video-item', 'thumb', 'holder-item', 'th']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s']], 
         # 'last_page': dict([('find', [{'tag': ['div'], 'class': ['load-more']}]), 
                            # ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           # '@ARG': 'data-max-queries', '@TEXT': '(\d+)'}])]), 
         'last_page': dict([('find', [{'tag': ['div', 'nav'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'data-parameters', '@TEXT': '\:(\d+)'}])]), 
         # 'last_page': {}, 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_stime': {'find': [{'tag': ['span'], 'class': ['is-hd'], '@TEXT': '(\d+:\d+)' }]},
                            # 'list_all_url': {'find': [{'tag': ['a'], 'class': ['link'], '@ARG': 'href'}]},
                            # 'list_all_stime': dict([('find', [{'tag': ['div'], 'class': ['time']}]),
                                                    # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_quality': {'find': [{'tag': ['span', 'div'], 'class': ['hd'], '@ARG': 'class',  '@TEXT': '(hd)' }]},
                            # 'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['is-hd']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'list_all_premium': dict([('find', [{'tag': ['span'], 'class': ['ico-private']}]),
                                                       # ('get_text', [{'tag': '', 'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['span', 'div'], 'class': ['videos', 'column', 'rating', 'category-link-icon-videos']}]),
                                                      # ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
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
    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=host + "search/?sort_by=post_date&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=host + "search/?sort_by=video_viewed_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorada" , action="list_all", url=host + "search/?sort_by=rating_month&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Favoritas" , action="list_all", url=host + "search/?sort_by=most_favourited&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Comentadas" , action="list_all", url=host + "search/?sort_by=most_commented&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Mas Largas" , action="list_all", url=host + "search/?sort_by=duration&from_videos=1"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "channels/?sort_by=total_videos&from=1", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Productora" , action="section", url=host + "sites/?sort_by=total_videos&from=1", extra="Sitios"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "models/?sort_by=total_videos&from=1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "categories/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|category-name|category|channels|sites|models|model|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    # if item.extra == 'Categorias':
        # findS['controls']['cnt_tot'] = 99999
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
    if soup.find_all('a', href=re.compile("/(?:pornstars|models|model|pornosztarok)/[A-z0-9-]+/")):
        pornstars = soup.find_all('a', href=re.compile("/(?:pornstars|models|model|pornosztarok)/[A-z0-9-]+/"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s ' %pornstar
        if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    # if soup.find('div', id='kt_player'):
        # url = item.url
    # else:
        # url = soup.iframe['src']
        # url = url.replace("embed", "videos").replace('lol', 'tv')
        # name = item.url.split("/")[-2]
        # url += "/%s/" %name
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

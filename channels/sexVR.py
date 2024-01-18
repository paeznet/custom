# -*- coding: utf-8 -*-
# -*- Channel sexVR -*-
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

#########################       pagination host+page2.html en vez de host/most-viewed/page1.html
                                # son 60 items por lo que la tercera pagina siempre es https://www.sexvr.com/page2.html

canonical = {
             'channel': 'sexVR', 
             'host': config.get_setting("current_host", 'sexVR', default=''), 
             'host_alt': ["https://www.sexvr.com/"], 
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


finds = {'find': {'find_all': [{'tag': ['div'],  'class': ['video-box']}]},
         'categories': dict([('find', [{'tag': ['section'], 'class': ['content-sec']}]),
                             ('find_all', [{'tag': ['div'], 'class': ['paysite-item', 'channel-item', 'item--pornstar']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['prev-next-controls']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['page\d+.html', 'next_page_url']], 
         'last_page': {}, 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_canal': dict([('find', [{'tag': ['span'], 'class': ['title-stud']}]),
                                                    ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tagOR': ['span'], 'class':['s-elem']},
                                                                {'tagOR': ['span'], 'style':['color']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                            },
         'controls': {'url_base64': False, 'cnt_tot': 30, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevo" , action="list_all", url=host + "videos/page1.html"))
    itemlist.append(Item(channel=item.channel, title="Mas Visto" , action="list_all", url=host + "most-viewed/page1.html"))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorado" , action="list_all", url=host + "being-watched/page1.html"))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=host + "longest/page1.html"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host + "studios/", extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "pornstars/videos/page1.html", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "channels/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(:?model|channels|studios)\/[^$]+$)', r'\1page1.html']]
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    itemlist = []
    soup = AlfaChannel.create_soup(item.url, **kwargs).find('div', class_='tags-block')
    logger.debug(soup)
    if soup.find_all('a', href=re.compile("/(?:pornstars|models|model)/[A-z0-9-]+.html")):
        pornstars = soup.find_all('a', href=re.compile("/(?:pornstars|models|model|pornosztarok)/[A-z0-9-]+.html"))
        
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
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/video/%s/page1.html" % (host, texto.replace(" ", "+"))
    
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

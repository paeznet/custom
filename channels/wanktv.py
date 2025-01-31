# -*- coding: utf-8 -*-
# -*- Channel WankTV -*-
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

# https://sextubefun.com/  https://iporntoo.com/  https://wanktv.com/ 
 # https://hdporn-movies.com/  https://www.wetsins.com/  https://freehdporn.xxx/=OUT

canonical = {
             'channel': 'wanktv', 
             'host': config.get_setting("current_host", 'wanktv', default=''), 
             'host_alt': ["https://wanktv.com/"], 
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


finds = {'find': {'find_all': [{'tag': ['div'], 'class': ['-video']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': dict([('find', [{'tag': ['main'], 'class': ['main-col']}]),
                             ('find_all', [{'tag': ['div'], 'class': ['-channel', '-model', '-paysite']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]),
         'next_page_rgx': [['page\d+.html', 'next_page_url']], 
         'last_page':  {},
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_quality': dict([('find', [{'tag': ['span'], 'class': ['q-hd', 'item-quality']}]),
                                                      ('get_text', [{'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['category-videos']}]),
                                                      # ('get_text', [{'strip': True}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 20, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    # itemlist.append(Item(channel=item.channel, title="sextubefun" , action="submenu", url= "https://sextubefun.com/", chanel="sextubefun", thumbnail = "https://i.postimg.cc/qRwRXggy/logo.png"))
    # itemlist.append(Item(channel=item.channel, title="wanktv" , action="submenu", url= "https://wanktv.com/", chanel="wanktv", thumbnail= "https://i.postimg.cc/zGrNd8Wf/logo.png"))
    # itemlist.append(Item(channel=item.channel, title="iporntoo" , action="submenu", url= "https://iporntoo.com/", chanel="iporntoo", thumbnail = "https://i.postimg.cc/vTyrD4kn/logo.png"))
    # itemlist.append(Item(channel=item.channel, title="hdporn-movies" , action="submenu", url= "https://hdporn-movies.com/", chanel="hdporn-movies", thumbnail = "https://i.postimg.cc/7hySW5N6/logo.png"))
    itemlist.append(Item(channel=item.channel, title="wetsins" , action="submenu", url= "https://www.wetsins.com/", chanel="wetsins", thumbnail = "https://i.postimg.cc/zGrNd8Wf/logo.png"))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "most-recent/", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Vistos" , action="list_all", url=item.url + "most-viewed/month/", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "top-rated/month/", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=item.url + "most-discussed/month/", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "longest/month/", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "paysites/", extra="Canal", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "models/rating/page1.html", extra="PornStar", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "channels/", extra="Categorias", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
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
    
    AlfaChannel.host = config.get_setting("current_host", item.chanel, default=host)
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    if soup.find_all('a', href=re.compile("/pornstars/[A-z0-9-]+.html")):
        pornstars = soup.find_all('a', href=re.compile("/pornstars/[A-z0-9-]+.html"))
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        lista.insert (2, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/newest/page1.html" % (item.url, texto.replace(" ", "-"))
    
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

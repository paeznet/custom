# -*- coding: utf-8 -*-
# -*- Channel easyporn -*-
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


# https://www.hd-easyporn.com/  https://www.porndrake.com/   https://www.pornblade.com/
# https://www.pornboxer.com/    https://www.sexmovies69.net/  https://www.sexclips66.com/  https://www.pornolisa.com/
# https://www.porn-monkey.com/    https://www.pornoleon.com/  https://www.meinyouporn.com/ https://www.hd-pornos.info/
# https://www.pornotanja.com/  


canonical = {
             'channel': 'easyporn', 
             'host': config.get_setting("current_host", 'easyporn', default=''), 
             'host_alt': ["https://www.hd-easyporn.com/"], 
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


finds = {'find': dict([('find', [{'tag': ['div', 'section'], 'class': ['videos', 'thumbnail-grid']}]),
                                 ('find_all', [{'tag': ['div', 'figure'], 'class': ['grid_box']}])]),
         'categories': {'find_all': [{'tag': ['div', 'figure'], 'class': ['polaroid', 'grid_box']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&p=\d+', '&p=%s'], ['?p=\d+', '?p=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos':{},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['b-thumb-item__detail']}]),
                                                      # ('get_text', [{'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['category-videos']}]),
                                                      # ('get_text', [{'strip': True}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 36, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="easyporn" , action="submenu", url= "https://www.hd-easyporn.com/", chanel="easyporn", thumbnail = "https://static.hd-easyporn.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="porndrake" , action="submenu", url= "https://www.porndrake.com/", chanel="porndrake", thumbnail = "https://static.porndrake.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornblade" , action="submenu", url= "https://www.pornblade.com/", chanel="pornblade", thumbnail = "https://static.pornblade.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornboxer" , action="submenu", url= "https://www.pornboxer.com/", chanel="pornboxer", thumbnail = "https://i.postimg.cc/ryBNMrhK/pornboxer.png"))
    itemlist.append(Item(channel=item.channel, title="pornolisa" , action="submenu", url= "https://www.pornolisa.com/", chanel="pornolisa", thumbnail = "https://i.postimg.cc/KvW9RDPb/pornolisa.png"))
    itemlist.append(Item(channel=item.channel, title="sexmovies69" , action="submenu", url= "https://www.sexmovies69.net/", chanel="sexmovies69", thumbnail = "https://i.postimg.cc/zfjkNCpT/sexmovies69.png"))
    itemlist.append(Item(channel=item.channel, title="sexclips66" , action="submenu", url= "https://www.sexclips66.com/", chanel="sexclips66", thumbnail = "https://i.postimg.cc/G2mxm4SV/sexclips66.png"))
    itemlist.append(Item(channel=item.channel, title="porn-monkey" , action="submenu", url= "https://www.porn-monkey.com/", chanel="porn-monkey", thumbnail = "https://static.porn-monkey.com/img/header_60.png"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "?o=n&p=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "?o=v&p=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "?o=r&p=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "?o=d&p=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/?p=1", extra="PornStar", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels/", extra="Canal", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias", chanel=item.chanel))
    
    
    # if "porn-monkey" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new-videos/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best-videos/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "videos/1/", extra="Categorias", chanel=item.chanel))
    # if "bestpornstars" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "trending/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/1/", extra="Categorias", chanel=item.chanel))
    # if "bigfuck" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "recent/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Popular" , action="list_all", url=item.url + "most-popular/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "stars/1/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "category/", extra="Categorias", chanel=item.chanel))
    # if "redporn" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "trends/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/1/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "tubes/1/", extra="Categorias", chanel=item.chanel))
    # if "zzztube" in item.chanel:
        # itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "latest/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "hot/1/", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/1/", extra="PornStar", chanel=item.chanel))
        # itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/1/", extra="Categorias", chanel=item.chanel))
    
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels/1/", extra="Canal", chanel=item.chanel))
    
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:category|channel|pornstar)\/[^$]+$)', r'\1?o=n&p=1']]
    
    if item.extra == 'PornStar':
        findS['last_page'] = dict([('find_all', [{'tag': ['a'], 'href': re.compile("/\?p=\d+"), '@POS': [-1], 
                                                '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])])
        findS['next_page_rgx'] = [['?p=\d+', '?p=%s']]

    # if item.extra == 'Canal':
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'id': 'popup-sponsors'}]), 
                                    # ('find_all', [{'tag': ['li']}])])
        # findS['profile_labels']['section_title'] = {'find': [{'tag': ['img'], '@ARG': 'alt'}]}
        # findS['last_page'] = {}
        # findS['controls']['cnt_tot'] = 12
    
    if item.extra == 'Categorias':
        findS['title_clean'] =[['(?i)\s*Porn*\s*', ''], ['(?i)\s*Sex Movies*\s*', ''], ['(?i)\s*Sex Clips*\s*', '']]
        # findS['categories'] = dict([('find', [{'tag': ['div'], 'class': 'list-categories'}]), 
                                    # ('find_all', [{'tag': ['a']}])])
    # return AlfaChannel.section(item, **kwargs)
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
    
    AlfaChannel.host = config.get_setting("current_host", item.chanel, default=host)
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    # if soup.find('div', id='video-info').find_all('a', href=re.compile("/pornstars/[A-z0-9-]+")):
    pornstars =soup.find_all('a', href=re.compile("/pornstar/[A-z0-9-]+/"))
    
    for x, value in enumerate(pornstars):
        pornstars[x] = value.get_text(strip=True)
    pornstar = ""
    pornstar = ' & '.join(pornstars)
    pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
    if pornstar:
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)



    # if "6xtube" in item.url or "blendporn" in item.url:
        # matches = soup.find('div', id='player-container')
        # item.url = matches.iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/1/" % (item.url, texto.replace(" ", "+"))
    
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

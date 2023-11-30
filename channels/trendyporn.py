# -*- coding: utf-8 -*-
# -*- Channel TrendyPorn -*-
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

# https://www.6xtube.com/    https://www.blendporn.com/  https://www.daftsextube.com/
# https://www.hentaiprno.com/   https://www.trendyporn.com/   
# https://www.yespornplease.sexy/ = sexyporn   https://www.youcrazyx.com/   https://www.yrprno.com/   

# 6xtube  thumbnail += "|verifypeer=false"   #SSL peer certificate or SSH remote key was not OK(60)

canonical = {
             'channel': 'trendyporn', 
             'host': config.get_setting("current_host", 'trendyporn', default=''), 
             'host_alt': ["https://www.trendyporn.com/"], 
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
         'categories': {'find_all': [{'tag': ['div'], 'class': ['col-sm-6']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
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
                            'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['hd-text-icon']}]),
                                                      ('get_text', [{'strip': True}])]),
         'controls': {'url_base64': False, 'cnt_tot': 20, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="6xtube" , action="submenu", url= "https://www.6xtube.com/", chanel="6xtube", thumbnail = "https://i.postimg.cc/9fcmnckb/6xtube.png"))
    itemlist.append(Item(channel=item.channel, title="blendporn" , action="submenu", url= "https://www.blendporn.com/", chanel="blendporn", thumbnail = "https://i.postimg.cc/mgVYQ6YN/blendporn.png"))
    itemlist.append(Item(channel=item.channel, title="daftsextube" , action="submenu", url= "https://www.daftsextube.com/", chanel="daftsextube", thumbnail = "https://i.postimg.cc/wjQy1vQN/daftsextube.png"))
    itemlist.append(Item(channel=item.channel, title="hentaiprno" , action="submenu", url= "https://www.hentaiprno.com/", chanel="hentaiprno", thumbnail = "https://i.postimg.cc/wMZvhk83/hentaiprno.png"))
    itemlist.append(Item(channel=item.channel, title="trendyporn" , action="submenu", url= "https://www.trendyporn.com/", chanel="trendyporn", thumbnail = "https://i.postimg.cc/2S3GjkTw/trendyporn.png"))
    itemlist.append(Item(channel=item.channel, title="yespornpleasexy" , action="submenu", url= "https://www.yespornplease.sexy/", chanel="yespornpleasexy", thumbnail = "https://i.postimg.cc/CLsdQbgB/yespornplease.png"))
    itemlist.append(Item(channel=item.channel, title="youcrazyx" , action="submenu", url= "https://www.youcrazyx.com/", chanel="youcrazyx", thumbnail = "https://i.postimg.cc/KcgMJKjB/youcrazyx.png"))
    itemlist.append(Item(channel=item.channel, title="yrprno" , action="submenu", url= "https://www.yrprno.com/", chanel="yrprno", thumbnail = "https://i.postimg.cc/JhGN8prd/yrprno.png"))
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
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "paysites/", extra="Canal", chanel=item.chanel))
    if "trendyporn" in item.url:
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
    
    if "6xtube" in item.url or "blendporn" in item.url:
        soup = AlfaChannel.create_soup(item.url, **kwargs)
        matches = soup.find('div', id='player-container')
        item.url = matches.iframe['src']
    
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
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

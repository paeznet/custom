# -*- coding: utf-8 -*-
# -*- Channel 24porn -*-
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

# https://24porn.com/   https://bigfuck.tv/  https://bestpornstars.xxx/
# https://redporn.porn/  https://zzztube.tv/
# 

canonical = {
             'channel': '24porn', 
             'host': config.get_setting("current_host", '24porn', default=''), 
             'host_alt': ["https://24porn.com/"], 
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


finds = {'find': {'find_all': [{'tag': ['div'], 'class':['b-thumb-item']}]},  # 'id': re.compile(r"^vid-\d+")
         'categories': {'find_all': [{'tag': ['div'], 'class': ['b-thumb-item']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['b-pagination']}]), 
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
                            # 'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['b-thumb-item__detail']}]),
                                                      # ('get_text', [{'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['category-videos']}]),
                                                      # ('get_text', [{'strip': True}])])
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
    itemlist.append(Item(channel=item.channel, title="24porn" , action="submenu", url= "https://24porn.com/", chanel="24porn", thumbnail = "https://i.postimg.cc/fT78YLcR/24porn.png")) # thumbnail += "|verifypeer=false"   #SSL peer certificate or SSH remote key was not OK(60)
    itemlist.append(Item(channel=item.channel, title="bestpornstars" , action="submenu", url= "https://bestpornstars.xxx/", chanel="bestpornstars", thumbnail = "https://i.postimg.cc/wjxq51mq/bestpornstars.png"))
    itemlist.append(Item(channel=item.channel, title="bigfuck" , action="submenu", url= "https://bigfuck.tv/", chanel="bigfuck", thumbnail = "https://i.postimg.cc/MpLD0jFV/bigfuck.png"))
    itemlist.append(Item(channel=item.channel, title="redporn" , action="submenu", url= "https://redporn.porn/", chanel="redporn", thumbnail = "https://i.postimg.cc/mkGzTT6P/redporn.png"))
    itemlist.append(Item(channel=item.channel, title="zzztube" , action="submenu", url= "https://zzztube.tv/", chanel="zzztube", thumbnail = "https://i.postimg.cc/dtLwHb0d/zzztube.png"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})

    if "24porn" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new-videos/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best-videos/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "videos/1/", extra="Categorias", chanel=item.chanel))
    if "bestpornstars" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "trending/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/1/", extra="Categorias", chanel=item.chanel))
    if "bigfuck" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "recent/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mas Popular" , action="list_all", url=item.url + "most-popular/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "stars/1/", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "category/", extra="Categorias", chanel=item.chanel))
    if "redporn" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "trends/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/1/", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "tubes/1/", extra="Categorias", chanel=item.chanel))
    if "zzztube" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "latest/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "best/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mas Caliente" , action="list_all", url=item.url + "hot/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornstars/1/", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/1/", extra="Categorias", chanel=item.chanel))
    
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels/1/", extra="Canal", chanel=item.chanel))
    
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
    
    if soup.find('div', id='video-info').find_all('a', href=re.compile("/pornstars/[A-z0-9-]+")):
        pornstars = soup.find('div', id='video-info').find_all('a', href=re.compile("/pornstars/[A-z0-9-]+"))
        
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)



    if "6xtube" in item.url or "blendporn" in item.url:
        matches = soup.find('div', id='player-container')
        item.url = matches.iframe['src']
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

# -*- coding: utf-8 -*-
# -*- Channel bingato -*-
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

# https://bingato.com/    https://sexmex.to/    https://taboodude.com/   https://arabporn.xxx/

canonical = {
             'channel': 'bingato', 
             'host': config.get_setting("current_host", 'bingato', default=''), 
             'host_alt': ["https://bingato.com/"], 
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


finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['list-videos']}]),
                             ('find_all', [{'tag': ['div'], 'class': ['item']}])]),  # 'id': re.compile(r"^vid-\d+")
         'categories': dict([('find', [{'tag': ['div'], 'class': ['list-categories']}]),
                             ('find_all', [{'tag': ['a'], 'class': ['item']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['li'], 'class': ['next']}, {'tag': ['a'], '@ARG': 'href'}])]),         'next_page_rgx': [['\/page-\d+', '/page-%s/'],['\/page\/\d+', '/page/%s/']], #
         'last_page': {}, 
         'plot': {}, 
         'findvideos': {},
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
    itemlist.append(Item(channel=item.channel, title="bingato" , action="submenu", url= "https://bingato.com/", chanel="bingato", thumbnail = "https://i.postimg.cc/63z8Hc1y/bingato.png")) # thumbnail += "|verifypeer=false"   #SSL peer certificate or SSH remote key was not OK(60)
    itemlist.append(Item(channel=item.channel, title="sexmexto" , action="submenu", url= "https://sexmex.to/", chanel="sexmexto", thumbnail = "https://i.postimg.cc/rpNTvXDg/sexmex.png"))
    itemlist.append(Item(channel=item.channel, title="taboodude" , action="submenu", url= "https://taboodude.com/", chanel="taboodude", thumbnail = "https://i.postimg.cc/bJkWM43L/taboodude.png"))
    # itemlist.append(Item(channel=item.channel, title="arabporn" , action="submenu", url= "https://arabporn.xxx/", chanel="arabporn", thumbnail = "https://i.postimg.cc/SKXttnK4/arabporn.png"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "?sort_by=latest&page=1", chanel=item.chanel))
    if "bingato" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "?sort_by=most&page=1", chanel=item.chanel))
    else:
        itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "?sort_by=most%20viewed&page=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "?sort_by=longest&page=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Calidad" , action="list_all", url=item.url + "?sort_by=quality&page=1", chanel=item.chanel))
    if "bingato" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "stars", extra="PornStar", chanel=item.chanel))
    if "taboodude" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "models", extra="PornStar", chanel=item.chanel))
    if not "sexmex" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories?sort_by=alphabetic", extra="Categorias", chanel=item.chanel))
    
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
    
    if soup.find('a', href=re.compile("/(?:performerb|model)/[A-z0-9-]+")):
        pornstars = soup.find_all('a', href=re.compile("/(?:performerb|model)/[A-z0-9-]+"))
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
    
    item.url = "%ssearch?q=%s&sort_by=latest&page=1" % (item.url, texto.replace(" ", "+"))
    
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

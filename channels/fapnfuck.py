# -*- coding: utf-8 -*-
# -*- Channel fapnfuck -*-
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

# https://fapnfuck.com/  https://fuqster.com/  https://sexpester.com/   https://w1mp.com/   https://w4nkr.com/ 
# https://3sumxl.com/  https://cuminstead.com/  https://extremewhores.com/  https://hugewangs.com/  https://jizzpov.com/

canonical = {
             'channel': 'fapnfuck', 
             'host': config.get_setting("current_host", 'fapnfuck', default=''), 
             'host_alt': ["https://fapnfuck.com/"], 
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


finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['thumbs']}]),
                       ('find_all', [{'tag': ['div'], 'class': ['item']}])]),
         'categories': dict([('find', [{'tag': ['div'], 'class': ['thumbs']}]),
                             ('find_all', [{'tag': ['div'], 'class': ['item']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination', 'load-more']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'data-parameters', '@TEXT': '\:(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_stime': {'find': [{'tag': ['div'], 'class': ['time'], '@TEXT': '(\d+:\d+)' }]},
                            'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['qualtiy', 'quality']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                            'list_all_premium': dict([('find', [{'tag': ['span'], 'class': ['ico-premium']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['thumb-item']}]),
                                                      ('get_text', [{'tag': '', 'strip': True}])])
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
    itemlist.append(Item(channel=item.channel, title="fapnfuck" , action="submenu", url= "https://fapnfuck.com/", chanel="fapnfuck", thumbnail = "https://cdnstatic.fapnfuck.com/static/images/logo.png", type=1)) 
    itemlist.append(Item(channel=item.channel, title="fuqster" , action="submenu", url= "https://fuqster.com/", chanel="fuqster", thumbnail = "https://cdnstatic.fuqster.com/static/images/logo.png", type=1))
    itemlist.append(Item(channel=item.channel, title="sexpester" , action="submenu", url= "https://sexpester.com/", chanel="sexpester", thumbnail = "https://cdnstatic.sexpester.com/static/images/logo.png", type=1))
    itemlist.append(Item(channel=item.channel, title="w1mp" , action="submenu", url= "https://w1mp.com/", chanel="w1mp", thumbnail = "https://cdnstatic.w1mp.com/static/images/logo.png", type=1))
    itemlist.append(Item(channel=item.channel, title="w4nkr" , action="submenu", url= "https://w4nkr.com/", chanel="w4nkr", thumbnail = "https://cdnstatic.w4nkr.com/static/images/logo.png", type=1))
    itemlist.append(Item(channel=item.channel, title="3sumxl" , action="submenu", url= "https://3sumxl.com/", chanel="3sumxl", thumbnail = "https://cdnstatic.3sumxl.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="cuminstead" , action="submenu", url= "https://cuminstead.com/", chanel="cuminstead", thumbnail = "https://cdnstatic.cuminstead.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="extremewhores" , action="submenu", url= "https://extremewhores.com/", chanel="extremewhores", thumbnail = "https://cdnstatic.extremewhores.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="hugewangs" , action="submenu", url= "https://hugewangs.com/", chanel="hugewangs", thumbnail = "https://cdnstatic.hugewangs.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="jizzpov" , action="submenu", url= "https://jizzpov.com/", chanel="jizzpov", thumbnail = "https://cdnstatic.jizzpov.com/static/images/logo.png"))
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
    
    itemlist.append(Item(channel = item.channel, title="Nuevos", action="list_all", url=item.url + "search/?sort_by=post_date&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=item.url + "search/?sort_by=video_viewed&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorado" , action="list_all", url=item.url + "search/?sort_by=rating&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Favoritos" , action="list_all", url=item.url + "search/?sort_by=most_favourited&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Comentado" , action="list_all", url=item.url + "search/?sort_by=most_commented&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Largo" , action="list_all", url=item.url + "search/?sort_by=duration&from_videos=1", chanel=item.chanel))
    if item.type:
        itemlist.append(Item(channel = item.channel, title="Canal", action="section", url=item.url + "channels/?sort_by=total_videos&from=1", extra="Canal", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "models/?sort_by=total_videos&from=1", extra="PornStar", chanel=item.chanel))
    itemlist.append(Item(channel = item.channel, title="Categorias", action="section", url=item.url + "categories/?sort_by=title&from=1", extra="Categorias", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|series|models)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    if item.extra == 'Categorias':
        findS['controls']['cnt_tot'] = 9999
    
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
    
    if soup.find('div', class_='top-options').find_all('a', href=re.compile("/models/[A-z0-9-]+")):
        pornstars = soup.find('div', class_='top-options').find_all('a', href=re.compile("/models/[A-z0-9-]+"))
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
    
    
    if  soup.find('div', class_='player-holder').iframe:
        item.url = soup.find('div', class_='player-holder').iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
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

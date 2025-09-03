# -*- coding: utf-8 -*-
# -*- Channel onlinetube -*-
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


canonical = {
             'channel': 'onlinetube', 
             'host': config.get_setting("current_host", 'onlinetube', default=''), 
             'host_alt': ["https://x.onlinetube.tv/"], 
             'host_black_list': ["https://onlinetube.tv/"], 
             'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant': False, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            }

host = canonical['host'] or canonical['host_alt'][0]

timeout = 45
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['list-videos', 'thumbs__list_video', 'main-flex']}]),
                             ('find_all', [{'tag': ['div'], 'class': ['item']}])]),  # 'id': re.compile(r"^vid-\d+")
         'categories': dict([('find', [{'tag': ['div'], 'class': ['list-categories', 'list-models', 'list-channels', 'thumbs__list']}]),
                             ('find_all', [{'tag': ['a', 'div'], 'class': ['item']}])]),
         'search/': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},#dict([('find', [{'tag': ['li'], 'class': ['next']}, {'tag': ['a'], '@ARG': 'href'}])]),
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s'], ['/videos/\d+/', '/videos/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination', 'load-more']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'data-parameters', '@TEXT': '\:(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_url': {'find': [{'tag': ['span'], 'class': ['ico-fav-0'], '@ARG': 'data-fav-video-id'}]}
                                                      # ('get_text', [{'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['videos']}]),
                                                      ('get_text', [{'strip': True}])])
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
    itemlist.append(Item(channel=item.channel, title="[COLOR red]onlinetube[/COLOR]" , action="submenu", url= "https://onlinetube.tv/", chanel="onlinetube", thumbnail = "https://i.postimg.cc/QdYMpYYG/onlinetube.png"))
    itemlist.append(Item(channel=item.channel, title="huyamba" , action="submenu", url= "https://wvvw.huyamba.mobi/", chanel="huyamba", thumbnail = "https://i.postimg.cc/d1Ycd8Fc/logo-huyamba.png"))
    itemlist.append(Item(channel=item.channel, title="pornoreka" , action="submenu", url= "https://pornoreka.tv/", chanel="pornoreka", thumbnail = "https://i.postimg.cc/28cYJbQn/pornoreka.png"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "search/?q=&sort_by=post_date&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "search/?q=&sort_by=video_viewed&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "search/?q=&sort_by=rating&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Favorito" , action="list_all", url=item.url + "search/?q=&sort_by=most_favourited&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "search/?q=&sort_by=duration&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas comentado" , action="list_all", url=item.url + "search/?q=&sort_by=most_commented&from_videos=1", chanel=item.chanel))
    # itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels/?sort_by=total_videos&from=1", extra="Canal", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/?sort_by=title", extra="Categorias", chanel=item.chanel))
    if item.chanel != 'onlinetube':
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "models/?sort_by=model_viewed&from=1", extra="PornStar", chanel=item.chanel))
    
        itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.chanel == 'huyamba':
        findS['url_replace'] = [['(\/(?:categories|channels|models)\/[^$]+$)', r'\1videos/1/?sort_by=post_date']]
    else:
        findS['url_replace'] = [['(\/(?:categories|channels|models)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
    if item.chanel != 'onlinetube':
        findS['last_page'] = {}
        findS['next_page'] =  dict([('find', [{'tag': ['div'], 'class': ['pagination', 'load-more']}]),
                                    ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href',}])]) 
    if item.extra == 'Categorias':
        findS['controls']['cnt_tot'] = 9999
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.chanel == 'huyamba':
        findS['list_all_stime']= dict([('find', [{'tag': ['div'], 'class': ['box', 'thumb-video__time']}]),
                                       ('get_text', [{'tag': '', 'strip': True}])])
        item.last_page = 9999
    if item.chanel == 'pornoreka':
        item.last_page = 9999
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


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
    if soup.find('div', class_='modelsList__name'):
        pornstars = soup.find_all('div', class_='modelsList__name')
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        
        item.plot = pornstar
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if "HD" in item.contentTitle:
            lista.insert (2, pornstar)
        else:
            lista.insert (0, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    # url = soup.iframe['src']
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url, plot=item.plot))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())

    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/?q=%s&sort_by=latest&from_videos=1" % (item.url, texto.replace(" ", "+"))
    
    try:
        if texto:
            item.c_type = "search/"
            item.texto = texto
            return list_all(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

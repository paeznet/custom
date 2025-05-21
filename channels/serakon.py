# -*- coding: utf-8 -*-
# -*- Channel serakon -*-
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

###### https://serakon.com/  https://vsex.in/

                ####   NETU

canonical = {
             'channel': 'serakon', 
             'host': config.get_setting("current_host", 'serakon', default=''), 
             'host_alt': ["https://serakon.com/"], 
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

finds = {'find': {'find_all': [{'tag': ['article'], 'class': ['movie-box']}]},     #'id': re.compile(r"^browse_\d+")}]},
         'categories': dict([('find', [{'tag': ['div'], 'class': ['generos']}]), 
                             ('find_all', [{'tag': ['li']}])]), 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s/'], ['&search_start=\d+', '&search_start=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['navigation']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1]}]),
                            ('get_text', [{'strip': True}])]), 
         'plot': {},
         # 'findvideos': {'find_all': [{'tag': ['div','h3'], 'class': ['descargas-borde']}]},
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                           },
         'controls': {'url_base64': False, 'cnt_tot': 15, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "allsex/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Calidad" , action="section", url=host, extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=host, extra="Canal"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host, extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    
    if item.extra == 'PornStar':
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['calidad']}]), 
                                    ('find_all', [{'tag': ['li']}])])
    
    if item.extra == 'Canal':
        findS['controls']['cnt_tot'] = 9999
        findS['categories'] = dict([('find', [{'tag': ['div'], 'class': ['estudios']}]), 
                                    ('find_all', [{'tag': ['li']}])])
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    # findS = finds.copy()
    # findS['controls']['action'] = 'findvideos'
    
    # return AlfaChannel.list_all(item, finds=findS, **kwargs)
    return AlfaChannel.list_all(item, **kwargs)


def findvideos(item):
    logger.info()
    
    # soup = AlfaChannel.create_soup(item.url, **kwargs)
    # matches = AlfaChannel.parse_finds_dict(soup, finds['findvideos'])
    # if not matches:
        # from platformcode import launcher
        # item.action = 'play'
        # item.language = ''
        # item.server = 'vsexin'
        # item.setMimeType = 'application/vnd.apple.mpegurl'
        # return launcher.run(item)
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)
    # return AlfaChannel.get_video_options(item, item.url, data=soup, matches_post=findvideos_matches, 
                                         # verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


# def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    # logger.info()
    # matches = []
    # findS = AHkwargs.get('finds', finds)
    
    # for elem in matches_int:
        # elem_json = {}
        
        # try:
            # elem_json['url'] = elem.a.get("href", "")
            # elem_json['title'] = elem.a.get_text(strip=True).capitalize()
            
            # elem_json['language'] = ''
        # except:
            # logger.error(elem)
            # logger.error(traceback.format_exc())

        # if not elem_json.get('url', ''): continue
        # matches.append(elem_json.copy())

    # return matches, langs


def play(item):
    logger.info()
    itemlist = []
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    # descargas = soup.find('div', class_='descargas')
    
    if soup.find_all('a', href=re.compile("/pornstar/[A-z0-9-%20]+/")):
        pornstars = soup.find_all('a', href=re.compile("/pornstar/[A-z0-9-%20]+/"))
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split()
        ## pornstar = pornstar.replace('[/COLOR]', '')
        # pornstar = ' %s' %pornstar
        # lista.insert (0, pornstar)
        # item.contentTitle = ' '.join(lista)
        plot = pornstar
        
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url, plot=plot))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%sindex.php?do=search&subaction=search&search_start=1&story=%s" % (host, texto.replace(" ", "+"))
    
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

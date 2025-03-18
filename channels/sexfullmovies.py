# -*- coding: utf-8 -*-
# -*- Channel SexFullMovies -*-
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
             'channel': 'sexfullmovies', 
             'host': config.get_setting("current_host", 'sexfullmovies', default=''), 
             'host_alt': ["https://sexfullmovies.sbs/"], 
             'host_black_list': ["https://wo.sexfullmovies.com/", "https://go.sexfullmovies.com/"], 
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

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['animation-2', 'search-page']}]),
                       ('find_all', [{'tag': ['article']}])]),
                             # {'find_all': [{'tag': ['article'], 'id': re.compile(r"^post-\d+")}]},
         'categories': {'find_all': [{'tag': ['li'], 'class': ['category']}]}, 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])]), 
         'next_page_rgx': [['\/page\/\d+', '\/page\/%s']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host + "movies/page/1/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
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
    
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    matches = soup.find_all('li', id=re.compile(r"^player-option-\d+"))
    if not matches:
        matches = soup.find_all('a', href=re.compile("/links/[a-z0-9]+/"))
    for elem in matches:
        try:
            if "Download" in elem:
                link = elem['href']
                soup = AlfaChannel.create_soup(link, **kwargs)
                link = soup.find("a", class_="myButton3")['href']
                link = AlfaChannel.urljoin(host,link)
                soup = AlfaChannel.create_soup(link, **kwargs)
                url = soup.find("a", class_="myButton2")['href']
                quality = scrapertools.find_single_match(url, "_(\d+p)_")
                url += "|Referer=%s" %host
            else:
                kwargs['post'] = 'action=doo_player_ajax&post=%s&nume=%s&type=%s' \
                                 % (elem.get('data-post', ''), elem.get('data-nume', ''), elem.get('data-type', ''))
                kwargs['soup'] = False
                kwargs['json'] = True
                
                iframeData = AlfaChannel.create_soup(AlfaChannel.doo_url, hide_infobox=True, **kwargs)
                if not iframeData: continue
                if not iframeData.get('embed_url', ''): continue
                url = iframeData['embed_url']
                if "source=" in url:
                    url = url.split("source=")[-1]
                url = AlfaChannel.do_unquote(url)
                quality = scrapertools.find_single_match(url, "_(\d+p)_")
            itemlist.append(['.mp4 %s' %quality, url])
            
        except:
            logger.error(elem)
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/video/?s=%s&o=recent&page=1" % (host, texto.replace(" ", "+"))
    
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

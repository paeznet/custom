# -*- coding: utf-8 -*-
# -*- Channel xoxostream -*-
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
             'channel': 'xoxostream', 
             'host': config.get_setting("current_host", 'xoxostream', default=''), 
             'host_alt': ["https://xoxostream.com/"], 
             'host_black_list': [], 
             'set_tls': None, 'set_tls_min': False, 'retries_cloudflare': 5, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'cf_assistant': False, 'CF_stat': True, 
             'CF': False, 'CF_test': False, 'alfa_s': True
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['videos-list']}]),
                       ('find_all', [{'tag': ['li'], 'id': re.compile(r"^\d+")}]) ]),
         'categories': dict([('find', [{'tag': ['ul'], 'class': ['tags_list', 'cards']}]),
                             ('find_all', [{'tag': ['li']}]) ]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {'find': [{'tag': ['a'], 'class': ['next'], '@ARG': 'href'}]},
         'next_page_rgx': [['\/\d+', '/%s/']], 
         'last_page': {},
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
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
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=host +"1/"))
    itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=host + "models/", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=host + "tags/", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    # if item.extra == "PornStar":
        # findS['next_page_rgx'] = [['\/\d+', 'next_page_url']]
        # findS['next_page'] = item.url
    return AlfaChannel.section(item, finds=findS, matches_post=section_matches, **kwargs)


def section_matches(item, matches_int, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        
        elem_json = {}
        
        try:
            url = elem.get("href", '') or elem.a.get("href", '')
            elem_json['url'] = "%s%s" %(item.url, url)
            elem_json['title'] = elem.a.get('data-mxptext', '') or elem.a.get('title', '') \
                                                                or (elem.img.get('alt', '') if elem.img else '') \
                                                                or elem.a.get_text(strip=True)
            if elem.img: elem_json['thumbnail'] = elem.img.get('data-thumb_url', '') or elem.img.get('data-original', '') \
                                                                                     or elem.img.get('data-src', '') \
                                                                                     or elem.img.get('src', '')
            if elem.find('span', class_=['videoCount', 'videosNumber']):
                elem_json['cantidad'] = elem.find('span', class_=['videoCount', 'videosNumber']).get_text(strip=True)
            elif elem.find('div', class_='videos'):
                elem_json['cantidad'] = elem.find('div', class_='videos').get_text(strip=True)
            elif elem.find(string=re.compile(r"(?i)videos|movies")):
                elem_json['cantidad'] = elem.find(string=re.compile(r"(?i)videos|movies")).strip()
        
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue
        
        if not elem_json['url']: continue
        matches.append(elem_json.copy())
    
    return matches


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    if item.extra or item.c_type == "search":
        findS['next_page'] = {}
        item.last_page = 9999
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def play(item):
    logger.info()
    itemlist = []
    
    data = AlfaChannel.httptools.downloadpage(item.url, **kwargs).data
    soup = AlfaChannel.do_soup(data, encoding='utf-8')    
    # soup = AlfaChannel.create_soup(item.url, **kwargs)
    
    if soup.find_all('a', href=re.compile("/models/[A-z0-9-]+(?:/|)")):
        pornstars = soup.find_all('a', href=re.compile("/models/[A-z0-9-]+(?:/|)"))
        
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
    
    if soup.find('p', id='description').get('class', ''):
        vid = soup.find('p', id='description')['class']
        url = "https://vdownload-%s.sb-cd.com/%s/%s/%s-%s.mp4?secure=%s,%s&m=%s&d=%s&_tid=%s"  %(vid[0],vid[1],vid[2],vid[3],vid[4],vid[5],vid[6],vid[0],vid[1],vid[3])
    else:
        url = scrapertools.find_single_match(data, '\:player" content="([^"]+)"')
        url += "/"
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    
    return itemlist


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%ssearch/%s/1/" % (host, texto.replace(" ", "_"))
    
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

# -*- coding: utf-8 -*-
# -*- Channel tittytube -*-
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
import ast


IDIOMAS = AlfaChannelHelper.IDIOMAS_A
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_A
list_quality_tvshow = []
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_A
forced_proxy_opt = 'ProxySSL'



#  https://tittytube.com/   https://thenudeporn.com/   https://saucesenpai.com/   https://nudesleaker.com/  https://slutleaks.com/
#  https://nudeleaks.tv/   https://thesauceis.com/   https://gaysdream.com/
#  https://pornasia.net/   https://fullpornclips.com/  https://squirtylatina.com/

# https://sauceplayer.co/e/fUWf5Fb3qkA64A8VZrR3tn

canonical = {
             'channel': 'tittytube', 
             'host': config.get_setting("current_host", 'tittytube', default=''), 
             'host_alt': ["https://tittytube.com/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 10
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []

finds = {'find': {'find_all': [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]},
         'categories': {'find_all': [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page\/\d+', '/page/%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': 'page/(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['div'], 'class': ['responsive-player']}]),
                             ('find_all', [{'tag': ['iframe'], '@ARG': 'src'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', ''], ['View All Post Filed Under ', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            },
         'controls': {'url_base64': False, 'cnt_tot': 40, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    
    itemlist.append(Item(channel=item.channel, title="tittytube" , action="submenu", url= "https://tittytube.com/", chanel="tittytube", thumbnail = "https://tittytube.com/wp-content/uploads/2024/05/TittytubeLOGO.png"))
    itemlist.append(Item(channel=item.channel, title="saucesenpai" , action="submenu", url= "https://saucesenpai.com/", chanel="saucesenpai", thumbnail = "https://saucesenpai.com/wp-content/uploads/2024/06/TRY1-1.webp"))
    itemlist.append(Item(channel=item.channel, title="thenudeporn" , action="submenu", url= "https://thenudeporn.com/", chanel="thenudeporn", thumbnail = "https://thenudeporn.com/wp-content/uploads/2024/05/TNP2.png"))
    itemlist.append(Item(channel=item.channel, title="slutleaks" , action="submenu", url= "https://slutleaks.com/", chanel="slutleaks", thumbnail = "https://slutleaks.com/wp-content/uploads/2023/11/fnal.webp"))
    itemlist.append(Item(channel=item.channel, title="nudeleaks" , action="submenu", url= "https://nudeleaks.tv/", chanel="nudeleaks", thumbnail = "https://nudeleaks.tv/wp-content/uploads/2024/04/Nudeleakslogo.png"))
    itemlist.append(Item(channel=item.channel, title="thesauceis" , action="submenu", url= "https://thesauceis.com/", chanel="thesauceis", thumbnail = "https://thesauceis.com/wp-content/uploads/2024/03/Untitled-1-2.png"))
    itemlist.append(Item(channel=item.channel, title="gaysdream" , action="submenu", url= "https://gaysdream.com/", chanel="gaysdream", thumbnail = "https://gaysdream.com/wp-content/uploads/2024/02/try1gay.png"))
    
    itemlist.append(Item(channel=item.channel, title="nudesleaker" , action="submenu", url= "https://nudesleaker.com/", chanel="nudesleaker", thumbnail = "https://nudesleaker.com/wp-content/uploads/2024/05/LKR.png"))
    itemlist.append(Item(channel=item.channel, title="pornasia" , action="submenu", url= "https://pornasia.net/", chanel="pornasia", thumbnail = "https://pornasia.net/wp-content/uploads/2024/12/email-4.webp"))
    itemlist.append(Item(channel=item.channel, title="fullpornclips" , action="submenu", url= "https://fullpornclips.com/", chanel="fullpornclips", thumbnail = "https://fullpornclips.com/wp-content/uploads/2024/06/FPC.png"))
    
    itemlist.append(Item(channel=item.channel, title="squirtylatina" , action="submenu", url= "https://squirtylatina.com/", chanel="squirtylatina", thumbnail = "https://squirtylatina.com/wp-content/uploads/2024/08/SCLTN1.webp"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist

def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "page/1/?filter=latest", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "page/1/?filter=most-viewed", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "page/1/?filter=popular", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "page/1/?filter=longest", chanel=item.chanel))
    if 'nudesleaker' in item.chanel or 'nudeleaks' in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "actors/page/1/", extra="PornStar", chanel=item.chanel))
    elif 'gaysdream' in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "pornstar/page/1/", extra="PornStar", chanel=item.chanel))
    else:
        itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "Pornstars/page/1/", extra="PornStar", chanel=item.chanel))
    
    if 'nudesleaker' in item.chanel or 'pornasia' in item.chanel or 'squirtylatina' in item.chanel: 
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categoria", chanel=item.chanel))
    elif 'fullpornclips' in item.chanel or 'saucesenpai' in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias", chanel=item.chanel)) ### son tags por eso extra="Categoria"
    else:
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "tags/", extra="Categorias", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|channels|models|pornstars|actor)\/[^$]+$)', r'\1page/1/?filter=latest"']]
    
    if item.extra == 'Categorias':
        # findS['categories'] ={'find_all': [{'tag': ['div'], 'class': ['tag-item']}]}
        findS['categories'] ={'find_all': [{'tag': ['a'], 'href': re.compile(r"/(?:tag|Category)/[A-z0-9-]+/")}]}
    
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)


def findvideos(item):
    logger.info()
    
    # return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         # verify_links=False, findvideos_proc=True, **kwargs)
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    matches = []
    findS = AHkwargs.get('finds', finds)
    
    for elem in matches_int:
        elem_json = {}
        
        try:
            url=""
            data = AlfaChannel.httptools.downloadpage(elem).data
            patron = '"servername":"([^"]+)","link":"([^"]+)"'
            match = re.compile(patron,re.DOTALL).findall(data)
            match = match[:-2]
            
            for server,link in match:
                vid = scrapertools.find_single_match(link, '\.(eyJs.*?)\.')
                vid += "=="
                vid = base64.b64decode(vid).decode("utf-8")
                url = scrapertools.find_single_match(vid, '"link":"([^"]+)"')
                elem_json['url'] = url
                elem_json['server'] = '' 
                elem_json['language'] = ''
                matches.append(elem_json.copy())
            
            if not url:
                elem_json['url'] = elem
                elem_json['server'] = ''
                elem_json['language'] = ''
                matches.append(elem_json.copy())
    
        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): continue

    return matches, langs


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    # item.url = "%sbuscar/?q=%s&sort_by=video_viewed&from_videos=1" % (host, texto.replace(" ", "+"))
    item.url = "%s?s=%s&filter=latest" % (item.url, texto.replace(" ", "+"))
    
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

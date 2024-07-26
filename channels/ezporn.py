# -*- coding: utf-8 -*-
# -*- Channel ezporn -*-
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

# https://www.ezporn.tv/  https://www.fullporno.tv/  https://www.pornwex.tv/
# https://www.4wank.com/ https://www.cremz.com/  https://momzr.com/ https://www.xxam.org/
# https://www.mypornhere.com/  https://viralpornhub.com/
# https://asianviralhub.com/  https://hornyfap.com/  https://nudes7.com/  https://sloppyfans.com/
# https://www.alotporn.com/  https://leak.xxx/  https://love4porn.com/

# https://castingporn.tv/  https://justleaks.tv/  https://onlymoms.tv/  https://sisporn.tv/   enlaces de https://www.pornwex.tv/

canonical = {
             'channel': 'ezporn', 
             'host': config.get_setting("current_host", 'ezporn', default=''), 
             'host_alt': ["https://ezporn.tv/"], 
             'host_black_list': ["https://www.ezporn.tv/"], 
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


finds = {'find': dict([('find', [{'tag': ['div'], 'class': ['list-videos']}]),
                             ('find_all', [{'tag': ['div'], 'class':['item']}])]),
               # {'find_all': [{'tag': ['div'], 'class':['item']}]},  # 'id': re.compile(r"^vid-\d+")
         'categories': dict([('find', [{'tag': ['div'], 'class': ['list-cat', 'list-albums', 'list-channels', 'list-models', 'list-categories', 'list-sponsors']}]),  #, 'list-videos'       porndr['list-cat', 'list-albums', 'list-channels']
                             ('find_all', [{'tag': ['a']}])]),
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&from_videos=\d+', '&from_videos=%s'], ['&from=\d+', '&from=%s']], 
         'last_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'data-parameters', '@TEXT': ':(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_stime': dict([('find', [{'tag': ['div', 'span'], 'class': ['duration', 'video-duration', 'views-counter2']}]),
                                                    ('get_text', [{'tag': '', 'strip': True}])]),
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
    
    
    itemlist.append(Item(channel=item.channel, title="Ezporn" , action="submenu", url= "https://www.ezporn.tv/", chanel="ezporn", thumbnail = "https://i.postimg.cc/28FJxnfS/ezporn.png"))
    itemlist.append(Item(channel=item.channel, title="Fullporno" , action="submenu", url= "https://www.fullporno.tv/", chanel="fullporno", thumbnail = "https://i.postimg.cc/63JLS1rJ/fullporno.png"))
    itemlist.append(Item(channel=item.channel, title="Pornwex" , action="submenu", url= "https://www.pornwex.tv/", chanel="pornwex", thumbnail = "https://i.postimg.cc/02F6cKGh/pornwex.png"))
    
    itemlist.append(Item(channel=item.channel, title="4wank" , action="submenu", url= "https://www.4wank.com/", chanel="4wank", thumbnail = "https://i.postimg.cc/fLD5yrJ7/4wank.png"))
    itemlist.append(Item(channel=item.channel, title="amateurest" , action="submenu", url= "https://www.amateurest.com/", chanel="amateurest", thumbnail = "https://i.postimg.cc/sXhJk7SH/amateurest.png"))
    itemlist.append(Item(channel=item.channel, title="asianviralhub" , action="submenu", url= "https://asianviralhub.com/", chanel="asianviralhub", thumbnail = "https://i.postimg.cc/Y0394pvH/asianviralhub.png"))
    itemlist.append(Item(channel=item.channel, title="Cremz" , action="submenu", url= "https://www.cremz.com/", chanel="cremz", thumbnail = "https://i.postimg.cc/pdpR7s2Z/cremz.png"))
    itemlist.append(Item(channel=item.channel, title="faptor" , action="submenu", url= "https://faptor.com/", chanel="faptor", thumbnail = "https://i.postimg.cc/L4TjSyzq/faptor.png"))
    itemlist.append(Item(channel=item.channel, title="hqbang" , action="submenu", url= "https://hqbang.com/", chanel="hqbang", thumbnail = "https://i.postimg.cc/kMYpcjTq/logo-hqbang.webp"))
    itemlist.append(Item(channel=item.channel, title="in35" , action="submenu", url= "https://in35.com/", chanel="in35", thumbnail = "https://i.postimg.cc/K8phwnry/in35.png"))
    itemlist.append(Item(channel=item.channel, title="love4porn" , action="submenu", url= "https://love4porn.com/", chanel="love4porn", thumbnail = "https://i.postimg.cc/LXJv4zpM/leakxxx.png"))
    itemlist.append(Item(channel=item.channel, title="Momzr" , action="submenu", url= "https://momzr.com/", chanel="momzr", thumbnail = "https://i.postimg.cc/zvHtWRF8/momzr.png"))
    itemlist.append(Item(channel=item.channel, title="mypornhere" , action="submenu", url= "https://www.mypornhere.com/", chanel="mypornhere", thumbnail = "https://i.postimg.cc/hthFxSX0/mypornhere.png"))
    itemlist.append(Item(channel=item.channel, title="pornbimbo" , action="submenu", url= "http://pornbimbo.com/", chanel="pornbimbo", thumbnail = "https://i.postimg.cc/hGY4L8Qj/pornbimbo.png"))######## PRIVATE
    itemlist.append(Item(channel=item.channel, title="porndr" , action="submenu", url= "https://www.porndr.com/", chanel="porndr", thumbnail = "https://i.postimg.cc/sgPnJF9v/Porndr-logo.png"))
    itemlist.append(Item(channel=item.channel, title="pornkinky" , action="submenu", url= "https://pornkinky.com/", chanel="pornkinky", thumbnail = "https://i.postimg.cc/J47whDtd/pornkinky.png"))  ######## PRIVATE
    itemlist.append(Item(channel=item.channel, title="thothd" , action="submenu", url= "https://thothd.com/", chanel="thothd", thumbnail = "https://i.postimg.cc/C5XTysD2/thothd.webp"))
    itemlist.append(Item(channel=item.channel, title="viralpornhub" , action="submenu", url= "https://viralpornhub.com/", chanel="viralpornhub", thumbnail = "https://i.postimg.cc/KcJ3vNBg/logo.png"))
    itemlist.append(Item(channel=item.channel, title="xxam" , action="submenu", url= "https://www.xxam.org/", chanel="xxam", thumbnail = "https://i.postimg.cc/SQ8tGpFB/xxam.png"))

    #### SIN CANAL
    itemlist.append(Item(channel=item.channel, title="alotporn" , action="submenu", url= "https://www.alotporn.com/", chanel="alotporn", thumbnail = "https://i.postimg.cc/rFc78PKG/alotporn.webp"))
    itemlist.append(Item(channel=item.channel, title="hornyfap" , action="submenu", url= "https://hornyfap.com/", chanel="hornyfap", thumbnail = "https://i.postimg.cc/4NhjP8JD/hornyfap.png"))
    # itemlist.append(Item(channel=item.channel, title="leakxxx" , action="submenu", url= "https://leak.xxx/", chanel="leakxxx", thumbnail = "https://i.postimg.cc/LXJv4zpM/leakxxx.png"))   ### models paginacion moore
    itemlist.append(Item(channel=item.channel, title="nudes7" , action="submenu", url= "https://nudes7.com/", chanel="nudes7", thumbnail = "https://i.postimg.cc/nccCQDp9/nudes7.png"))
    itemlist.append(Item(channel=item.channel, title="sloppyfans" , action="submenu", url= "https://sloppyfans.com/", chanel="sloppyfans", thumbnail = "https://i.postimg.cc/Df1qcs9C/sloppyfans.png"))
    itemlist.append(Item(channel=item.channel, title="thothub" , action="submenu", url= "https://thothub.org/", chanel="thothub", thumbnail = "https://i.postimg.cc/Sx41nPyr/thothub.png"))

    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
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


    itemlist.append(Item(channel=item.channel, title="Nuevas" , action="list_all", url=item.url + "search/?sort_by=post_date&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Vistas" , action="list_all", url=item.url + "search/?sort_by=video_viewed_month&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor Valorada" , action="list_all", url=item.url + "search/?sort_by=rating_month&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Favoritas" , action="list_all", url=item.url + "search/?sort_by=most_favourited&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Comentadas" , action="list_all", url=item.url + "search/?sort_by=most_commented&from_videos=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas Largas" , action="list_all", url=item.url + "search/?sort_by=duration&from_videos=1", chanel=item.chanel))
    if not "ezporn" in item.url and not "fullporno" in item.url and not "pornwex" in item.url:
        if "porndr" in item.url:
            itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "channels/?sort_by=total_videos&from=1", extra="Canal", chanel=item.chanel))
        elif not "alotporn" in item.url and not "hornyfap" in item.url and not "leak.xxx" in item.url and not "nudes7" in item.url \
            and not "pornkinky" in item.url and not "pornbimbo" in item.url and not "sloppyfans" in item.url and not "thothub" in item.url:
            itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "sites/?sort_by=total_videos&from=1", extra="Canal", chanel=item.chanel))
        if "love4porn" in item.url:
            itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "performers/?sort_by=avg_videos_popularity&from=1", extra="PornStar", chanel=item.chanel))
        else:
            itemlist.append(Item(channel=item.channel, title="Pornstars" , action="section", url=item.url + "models/?sort_by=total_videos&from=1", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:categories|category-name|channels|sites|models|pornstars)\/[^$]+$)', r'\1?sort_by=post_date&from=1']]
    
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
    
    
    if "4wank" in item.url or "cremz" in item.url or "momzr" in item.url or "faptor" in item.url:
        soup = AlfaChannel.create_soup(item.url, **kwargs)
        
        if soup.find('div', class_='video-info').find_all('a', href=re.compile("/models/[A-z0-9-]+")):
            pornstars = soup.find('div', class_='video-info').find_all('a', href=re.compile("/models/[A-z0-9-]+"))
            
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
    
    item.url = "%ssearch/?q=%s&sort_by=post_date&from_videos=1" % (item.url, texto.replace(" ", "+"))
    
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

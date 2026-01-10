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
# https://fukxl.com/ https://hugedickz.com/
# https://3sumxl.com/  https://cuminstead.com/  https://extremehoes.com/ https://extremewhores.com/  https://hugewangs.com/  https://jizzpov.com/
# https://b1gtits.com/  https://threesomerz.com/  https://babejizz.com/
# https://japflaps.com/  https://jappornxl.com/    https://asianrz.com/  https://asianslutz.com/   https://fetishz.com/  https://bondagenest.com/  https://lesfix.com/
# https://momxl.com/ https://analry.com/   https://maturexy.com/  https://povpoof.com/  https://milfxl.com/  https://ebonypeek.com/  https://an4lporn.com/
# https://bigassz.com/  https://pr1cks.com/  https://porno-cum.com/    https://public-porno.com/


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
         'last_page': dict([('find', [{'tag': ['div', 'ul'], 'class': ['pagination', 'load-more']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-2], 
                                           '@ARG': 'data-parameters', '@TEXT': '\:(\d+)'}])]), 
         'plot': {}, 
         'findvideos': {},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            'list_all_stime': {'find': [{'tag': ['div'], 'class': ['time', 'box-item'], '@TEXT': '(\d+:\d+)' }]},
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
    
    itemlist.append(Item(channel=item.channel, title="fapnfuck" , action="submenu", url= "https://fapnfuck.com/", chanel="fapnfuck", thumbnail = "https://cdnstatic.fapnfuck.com/static/images/logo.webp", type=1)) 
    itemlist.append(Item(channel=item.channel, title="fuqster" , action="submenu", url= "https://fuqster.com/", chanel="fuqster", thumbnail = "https://cdnstatic.fuqster.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="sexpester" , action="submenu", url= "https://sexpester.com/", chanel="sexpester", thumbnail = "https://cdnstatic.sexpester.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="w1mp" , action="submenu", url= "https://w1mp.com/", chanel="w1mp", thumbnail = "https://cdnstatic.w1mp.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="w4nkr" , action="submenu", url= "https://w4nkr.com/", chanel="w4nkr", thumbnail = "https://cdnstatic.w4nkr.com/static/images/logo.png", type=1))
    # itemlist.append(Item(channel=item.channel, title="babejizz" , action="submenu", url= "https://demo3.kvs-themes.com/", chanel="babejizz", thumbnail = "https://demo3.kvs-themes.com/contents/eibtlnubtttd/theme/logo.png", type=1))
    
    itemlist.append(Item(channel=item.channel, title="public-porno" , action="submenu", url= "https://public-porno.com/", chanel="public-porno", thumbnail = "https://cdnstatic.public-porno.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="porno-cum" , action="submenu", url= "https://porno-cum.com/", chanel="porno-cum", thumbnail = "https://cdnstatic.porno-cum.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="pr1cks" , action="submenu", url= "https://pr1cks.com/", chanel="pr1cks", thumbnail = "https://cdnstatic.pr1cks.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="bigassz" , action="submenu", url= "https://bigassz.com/", chanel="bigassz", thumbnail = "https://cdnstatic.bigassz.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="an4lporn" , action="submenu", url= "https://an4lporn.com/", chanel="an4lporn", thumbnail = "https://cdnstatic.an4lporn.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="ebonypeek" , action="submenu", url= "https://ebonypeek.com/", chanel="ebonypeek", thumbnail = "https://cdnstatic.ebonypeek.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="milfxl" , action="submenu", url= "https://milfxl.com/", chanel="milfxl", thumbnail = "https://cdnstatic.milfxl.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="analry" , action="submenu", url= "https://analry.com/", chanel="analry", thumbnail = "https://cdnstatic.analry.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="momxl" , action="submenu", url= "https://momxl.com/", chanel="momxl", thumbnail = "https://cdnstatic.momxl.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="asianslutz" , action="submenu", url= "https://asianslutz.com/", chanel="asianslutz", thumbnail = "https://cdnstatic.asianslutz.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="asianrz" , action="submenu", url= "https://asianrz.com/", chanel="asianrz", thumbnail = "https://cdnstatic.asianrz.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="lesfix" , action="submenu", url= "https://lesfix.com/", chanel="lesfix", thumbnail = "https://cdnstatic.lesfix.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="bondagenest" , action="submenu", url= "https://bondagenest.com/", chanel="bondagenest", thumbnail = "https://cdnstatic.bondagenest.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="fetishz" , action="submenu", url= "https://fetishz.com/", chanel="fetishz", thumbnail = "https://cdnstatic.fetishz.com/static/images/logo.webp", type=1))
    itemlist.append(Item(channel=item.channel, title="3sumxl" , action="submenu", url= "https://3sumxl.com/", chanel="3sumxl", thumbnail = "https://cdnstatic.3sumxl.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="babejizz" , action="submenu", url= "https://babejizz.com/", chanel="babejizz", thumbnail = "https://cdnstatic.babejizz.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="bigbigtits" , action="submenu", url= "https://bigbigtits.com/", chanel="bigbigtits", thumbnail = "https://cdnstatic.bigbigtits.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="cuminstead" , action="submenu", url= "https://cuminstead.com/", chanel="cuminstead", thumbnail = "https://cdnstatic.cuminstead.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="extremehoes" , action="submenu", url= "https://extremehoes.com/", chanel="extremehoes", thumbnail = "https://cdnstatic.extremehoes.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="extremewhores" , action="submenu", url= "https://extremewhores.com/", chanel="extremewhores", thumbnail = "https://cdnstatic.extremewhores.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="hugewangs" , action="submenu", url= "https://hugewangs.com/", chanel="hugewangs", thumbnail = "https://cdnstatic.hugewangs.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="japflaps" , action="submenu", url= "https://japflaps.com/", chanel="japflaps", thumbnail = "https://cdnstatic.japflaps.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="jappornxl" , action="submenu", url= "https://jappornxl.com/", chanel="jappornxl", thumbnail = "https://cdnstatic.jappornxl.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="m1lfs" , action="submenu", url= "https://m1lfs.com/", chanel="m1lfs", thumbnail = "https://cdnstatic.m1lfs.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="maturevices" , action="submenu", url= "https://maturevices.com/", chanel="maturevices", thumbnail = "https://cdnstatic.maturevices.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="maturexy" , action="submenu", url= "https://maturexy.com/", chanel="maturexy", thumbnail = "https://cdnstatic.maturexy.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="gogoasians" , action="submenu", url= "https://gogoasians.com/", chanel="gogoasians", thumbnail = "https://cdnstatic.gogoasians.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="hardwhores" , action="submenu", url= "https://hardwhores.com/", chanel="hardwhores", thumbnail = "https://cdnstatic.hardwhores.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="povpow" , action="submenu", url= "https://povpow.com/", chanel="povpow", thumbnail = "https://cdnstatic.povpow.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="povrz" , action="submenu", url= "https://povrz.com/", chanel="povrz", thumbnail = "https://cdnstatic.povrz.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="jizzpov" , action="submenu", url= "https://jizzpov.com/", chanel="jizzpov", thumbnail = "https://cdnstatic.jizzpov.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="b1gtits" , action="submenu", url= "https://b1gtits.com/", chanel="b1gtits", thumbnail = "https://cdnstatic.b1gtits.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="bigtitsxl" , action="submenu", url= "https://bigtitsxl.com/", chanel="bigtitsxl", thumbnail = "https://cdnstatic.bigtitsxl.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="bigbuttz" , action="submenu", url= "https://bigbuttz.com/", chanel="bigbuttz", thumbnail = "https://cdnstatic.bigbuttz.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="bigbumfun" , action="submenu", url= "https://bigbumfun.com/", chanel="bigbumfun", thumbnail = "https://cdnstatic.bigbumfun.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="thrupnies" , action="submenu", url= "https://thrupnies.com/", chanel="thrupnies", thumbnail = "https://cdnstatic.thrupnies.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="povpoof" , action="submenu", url= "https://povpoof.com/", chanel="povpoof", thumbnail = "https://cdnstatic.povpoof.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="hard3r" , action="submenu", url= "https://hard3r.com/", chanel="hard3r", thumbnail = "https://cdnstatic.hard3r.com/static/images/logo.webp"))
    itemlist.append(Item(channel=item.channel, title="threesomerz" , action="submenu", url= "https://threesomerz.com/", chanel="threesomerz", thumbnail = "https://cdnstatic.threesomerz.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="pumpjap" , action="submenu", url= "https://pumpjap.com/", chanel="pumpjap", thumbnail = "https://cdnstatic.pumpjap.com/static/images/logo.png"))
    itemlist.append(Item(channel=item.channel, title="fukxl" , action="submenu", url= "https://fukxl.com/", chanel="fukxl", thumbnail = "https://i.postimg.cc/bNPy68QQ/fukxl.png"))
    itemlist.append(Item(channel=item.channel, title="hugedickz" , action="submenu", url= "https://hugedickz.com/", chanel="hugedickz", thumbnail = "https://i.postimg.cc/vZQmmMTQ/hugedickz.png"))
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
    
    try:
        if soup.find('div', class_='top-options-player').find_all('a', href=re.compile("/models/[A-z0-9-]+")):
            pornstars = soup.find('div', class_='top-options-player').find_all('a', href=re.compile("/models/[A-z0-9-]+"))
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
    except:
        logger.error()
    
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

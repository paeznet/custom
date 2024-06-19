# -*- coding: utf-8 -*-
# -*- Channel josporn -*-
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

# https://en.joporn.net 
# https://en.pornohd.porn    https://josporn.com/ https://www.lenporno.net/  https://www.pornohd.sex/   
# https://en.pornohd.porn/   https://josporn.club/  https://en.xhdporno.name/
# 

canonical = {
             'channel': 'josporn', 
             'host': config.get_setting("current_host", 'josporn', default=''), 
             'host_alt': ["https://en.pornohd.blue/"], 
             'host_black_list': ["https://en.pornohd.porn/"], 
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


finds = {'find': {'find_all': [{'tag': ['div'], 'class':['preview_screen']}]},  # 'id': re.compile(r"^vid-\d+")
         'categories': {'find_all': [{'tag': ['div'], 'class': ['category_tegs', 'preview_screen']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['\/page-\d+', '/page-%s/'],['\/page\/\d+', '/page/%s/'],['\/page_\d+', '/page_%s']], #
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['navigation']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:/|-)(\d+)'}])]), 
         'plot': {}, 
         'findvideos': dict([('find', [{'tag': ['li'], 'class': 'link-tabs-container', '@ARG': 'href'}]),
                             ('find_all', [{'tag': ['a'], '@ARG': 'href'}])]),
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', ''],['Смотреть ', ''], [' Онлайн','']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['b-thumb-item__detail']}]),
                                                      # ('get_text', [{'strip': True}])]),
                            'section_cantidad': dict([('find', [{'tag': ['span', 'div'], 'class': ['video', 'videototal']}]),
                                                      ('get_text', [{'tag': '', 'strip': True, '@TEXT': '(\d+)'}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 29, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="josporn" , action="submenu", url= "https://josporn.club/", chanel="josporn", thumbnail = "https://i.postimg.cc/BbcNc0xJ/josporn.png"))
    itemlist.append(Item(channel=item.channel, title="pornohd" , action="submenu", url= "https://en.pornohd.blue/", chanel="pornohd", thumbnail = "https://i.postimg.cc/52rF6RZy/pornohd.png")) # thumbnail += "|verifypeer=false"   #SSL peer certificate or SSH remote key was not OK(60)
    itemlist.append(Item(channel=item.channel, title="xhdporno" , action="submenu", url= "https://en.xhdporno.name/", chanel="xhdporno", thumbnail = "https://i.postimg.cc/dQ6HhFs6/xhdporno.png"))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    if "pornohd" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "new-update/page-2/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "most-popular/page-1/?sort=2", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "the-best/page-1/?sort=2", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "best-models/page-1/?sort=2", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias", chanel=item.chanel))
    if "josporn" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "latest-updates/page/1/", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "most-popular/page/1/?sort=2", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "top-rated/page/1/?sort=2", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "categories/", extra="Categorias", chanel=item.chanel))
    if "xhdporno" in item.chanel:
        itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url, chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "pop/page-1/?sort=2", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "reting/page-1/?sort=2", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "porno-models/page-1/?sort=2", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url, extra="Categorias", chanel=item.chanel))
    
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    findS = finds.copy()
    
    if 'Categorias' in item.extra and 'xhdporno' in item.url:
        findS['categories'] = dict([('find', [{'tag': ['div'], 'id': ['catsp']}]), 
                                    ('find_all', [{'tag': ['a']}])])
    return AlfaChannel.section(item, finds=findS, **kwargs)


def list_all(item):
    logger.info()
    findS = finds.copy()
    
    if 'xhdporno' in item.url:
        findS['last_page'] = {}
        findS['next_page'] =  dict([('find', [{'tag': ['div'], 'class': ['navigation']}]), 
                                    ('find_all', [{'tag': ['a'], '@POS': [-1], '@ARG': 'href'}])])
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
    
    pornstars = ""
    plot = ""
    soup = AlfaChannel.create_soup(item.url, **kwargs)
    plot = soup.find('div', class_='story_description')
    if plot and "Pornstars:" in plot.text:
        pornstars = scrapertools.find_single_match(plot.text, "Pornstars: ([^-]+) -")
        pornstars = pornstars.split(",")
    if soup.find('div', string='Models:'):
        pornstars = soup.find('div', string='Models:').parent.find_all('a')
        for x, value in enumerate(pornstars):
            pornstars[x] = value.get_text(strip=True)
    
    if pornstars:
        pornstar = ' & '.join(pornstars)
        pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        lista.insert (1, pornstar)
        item.contentTitle = '[/COLOR]'.join(lista)
    
    if "xhdporno" in item.url:
        matches = soup.find(string=re.compile("file:"))
        videos = scrapertools.find_single_match(matches, 'file:"([^"]+)"')
        videos += ","
        patron = '\[(\d+p)\] ([^,]+),'
        videos = re.compile(patron,re.DOTALL).findall(videos)
        for quality, url in videos:
            itemlist.append(['.mp4 %s' %quality, url])
            itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    else:
        matches = soup.find('ul', id='down_spisok').find_all('div')
        for elem in matches:
            c = elem['data-c'].split(";")
            url = "https://v%s.cdnde.com/x%s/upload%s/%s/JOPORN_NET_%s_%s.mp4" %(c[2],c[2],c[3],c[0],c[0],c[1])
            quality = c[1]
            itemlist.append(['.mp4 %s' %quality, url])
            itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
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

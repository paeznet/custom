# -*- coding: utf-8 -*-
# -*- Channel drsexfilme -*-
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

        # easyporn                      drsexfilme

        # ENGLISH                         DEUTCH
# https://www.hd-easyporn.com/ == https://www.hdpornos.xxx/  
# https://www.porndrake.com/ ==  https://www.pornoente.tv/  
# https://www.pornblade.com/ ==  https://www.pornoklinge.com/
# https://www.porntommy.com/ ==  https://www.pornotommy.com/
# https://www.porn-monkey.com/ == https://www.pornoaffe.net/  https://www.pornomico.com/

                                # https://www.pornolisa.com/
# https://www.pornboxer.com/    https://www.sexmovies69.net/  https://www.sexclips66.com/  


# https://www.drsexfilme.com/  https://www.pornoritze.com/  https://www.pornotanja.com/
# https://www.pornotom.com/   https://www.hd-sexfilme.com/  https://www.gutesexfilme.com/
# https://www.pornodavid.com/    https://www.pornohirsch.net/   https://www.sexvideos-gratis.com/
# https://www.pornofisch.com/   https://www.lesbenhd.com/  https://www.halloporno.net/
# https://www.pornofelix.com/

# https://www.xnxx-pornos.xxx/ 

# https://www.pornoleon.com/  https://www.hd-pornos.info/  https://www.sexfilme-gratis.com/ 
# https://www.meinyouporn.com/ https://www.deinesexvideos.com/  https://www.sexvideos-hd.com/ 
# https://www.tube8-pornos.com/ https://www.deinesexfilme.com/  https://www.pornozebra.com/
# https://www.pornhub-sexfilme.net/  https://www.pornosusi.com/  https://www.pornojenny.net/
# https://www.pornohammer.com/   https://www.sexente.com/  https://www.pornovideos-hd.com/
# https://www.pornoschlange.com/   https://www.beeg-pornos.com/    https://www.herzporno.net/ 
# https://www.einfachtitten.com/  https://www.nursexfilme.com/  https://www.milffabrik.com/
# https://www.pornohans.net/
 
 
# https://www.xnxx-porno.com/   https://www.xnxx-sexfilme.com/


# https://www.sexhamster.org/  https://www.deutscherporno.biz/  https://www.scharfe-pornos.com/
# https://www.sexhamster.biz/  https://www.sexfilme24.org/  https://www.gratis-sex-videos.net/
# https://misex.net/

canonical = {
             'channel': 'drsexfilme', 
             'host': config.get_setting("current_host", 'drsexfilme', default=''), 
             'host_alt': ["https://www.drsexfilme.com/"], 
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


finds = {'find': dict([('find', [{'tag': ['div', 'section'], 'class': ['videos', 'thumbnail-grid']}]),
                                 ('find_all', [{'tag': ['div', 'figure'], 'class': ['grid_box']}])]),
         'categories': {'find_all': [{'tag': ['div'], 'class': ['grid_box']}]},
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {},
         'next_page_rgx': [['&p=\d+', '&p=%s']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1], 
                                           '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])]), 
         'plot': {}, 
         'findvideos':{},
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_quality': dict([('find', [{'tag': ['div'], 'class': ['b-thumb-item__detail']}]),
                                                      # ('get_text', [{'strip': True}])]),
                            # 'section_cantidad': dict([('find', [{'tag': ['div'], 'class': ['category-videos']}]),
                                                      # ('get_text', [{'strip': True}])])
                           },
         'controls': {'url_base64': False, 'cnt_tot': 36, 'reverse': False, 'profile': 'default'},  ##'jump_page': True, ##Con last_page  aparecerá una línea por encima de la de control de página, permitiéndote saltar a la página que quieras
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="hdpornos" , action="submenu", url= "https://www.hdpornos.xxx/", chanel="hdpornos", thumbnail = "https://static.hd-easyporn.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornoente" , action="submenu", url= "https://www.pornoente.tv/", chanel="pornoente", thumbnail = "https://static.porndrake.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornoklinge" , action="submenu", url= "https://www.pornoklinge.com/", chanel="pornoklinge", thumbnail = "https://static.pornblade.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornotommy" , action="submenu", url= "https://www.pornotommy.com/", chanel="pornotommy", thumbnail = "https://static.porntommy.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornoaffe" , action="submenu", url= "https://www.pornoaffe.net/", chanel="pornoaffe", thumbnail = "https://static.porn-monkey.com/img/header_60.png", cat=1))
    
    
    itemlist.append(Item(channel=item.channel, title="drsexfilme" , action="submenu", url= "https://www.drsexfilme.com/", chanel="drsexfilme", thumbnail = "https://i.postimg.cc/0ygw5WzS/drsexfilme.png"))
    itemlist.append(Item(channel=item.channel, title="gutesexfilme" , action="submenu", url= "https://www.gutesexfilme.com/", chanel="gutesexfilme", thumbnail = "https://static.gutesexfilme.com/img/logo/logo_300.png"))
    itemlist.append(Item(channel=item.channel, title="pornofisch" , action="submenu", url= "https://www.pornofisch.com/", chanel="pornofisch", thumbnail = "https://static.pornofisch.com/img/logo/logo_300.png"))
    itemlist.append(Item(channel=item.channel, title="pornoritze" , action="submenu", url= "https://www.pornoritze.com/", chanel="pornoritze", thumbnail = "https://i.postimg.cc/RZkkLV9W/pornoritze.png"))
    itemlist.append(Item(channel=item.channel, title="pornotanja" , action="submenu", url= "https://www.pornotanja.com/", chanel="pornotanja", thumbnail = "https://i.postimg.cc/QxPwjxFf/pornotanja.png"))
    itemlist.append(Item(channel=item.channel, title="pornotom" , action="submenu", url= "https://www.pornotom.com/", chanel="pornotom", thumbnail = "https://static.pornotom.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornodavid" , action="submenu", url= "https://www.pornodavid.com/", chanel="pornodavid", thumbnail = "https://static.pornodavid.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="hd-sexfilme" , action="submenu", url= "https://www.hd-sexfilme.com/", chanel="hd-sexfilme", thumbnail = "https://static.hd-sexfilme.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornohirsch" , action="submenu", url= "https://www.pornohirsch.net/", chanel="pornohirsch", thumbnail = "https://static.pornohirsch.net/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="sexvideos-gratis" , action="submenu", url= "https://www.sexvideos-gratis.com/", chanel="sexvideos-gratis", thumbnail = "https://static.sexvideos-gratis.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="lesbenhd" , action="submenu", url= "https://www.lesbenhd.com/", chanel="lesbenhd", thumbnail = "https://static.lesbenhd.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="halloporno" , action="submenu", url= "https://www.halloporno.net/", chanel="halloporno", thumbnail = "https://static.halloporno.net/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="pornofelix" , action="submenu", url= "https://www.pornofelix.com/", chanel="pornofelix", thumbnail = "https://static.pornofelix.com/img/header_50.png"))
    itemlist.append(Item(channel=item.channel, title="xnxx-pornos" , action="submenu", url= "https://www.xnxx-pornos.xxx/", chanel="xnxx-pornos", thumbnail = "https://static.xnxx-pornos.xxx/img/header_50.png"))
    
    
    itemlist.append(Item(channel=item.channel, title="pornolisa" , action="submenu", url= "https://www.pornolisa.com/", chanel="pornolisa", thumbnail = "https://i.postimg.cc/KvW9RDPb/pornolisa.png", cat=1, canal=1))
    itemlist.append(Item(channel=item.channel, title="pornoleon" , action="submenu", url= "https://www.pornoleon.com/", chanel="pornoleon", thumbnail = "https://static.pornoleon.com/img/logo/logo_300.png", cat=1, canal=1))  #no pornostars
    itemlist.append(Item(channel=item.channel, title="hd-pornos" , action="submenu", url= "https://www.hd-pornos.info/", chanel="hd-pornos", thumbnail = "https://static.hd-pornos.info/img/logo/logo_300.png", cat=1, canal=1)) #no pornostars
    itemlist.append(Item(channel=item.channel, title="pornosusi" , action="submenu", url= "https://www.pornosusi.com/", chanel="pornosusi", thumbnail = "https://static.pornosusi.com/img/logo/logo_300.png", cat=1, canal=1))  #no pornostars
    itemlist.append(Item(channel=item.channel, title="sexente" , action="submenu", url= "https://www.sexente.com/", chanel="sexente", thumbnail = "https://static.sexente.com/img/logo/logo_300.png", cat=1, canal=1))  #no pornostars
    itemlist.append(Item(channel=item.channel, title="einfachtitten" , action="submenu", url= "https://www.einfachtitten.com/", chanel="einfachtitten", thumbnail = "https://static.einfachtitten.com/img/header_60.png", cat=1)) #no tiene canal
    itemlist.append(Item(channel=item.channel, title="pornozebra" , action="submenu", url= "https://www.pornozebra.com/", chanel="pornozebra", thumbnail = "https://static.pornozebra.com/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="sexvideos-hd" , action="submenu", url= "https://www.sexvideos-hd.com/", chanel="sexvideos-hd", thumbnail = "https://static.sexvideos-hd.com/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="pornohammer" , action="submenu", url= "https://www.pornohammer.com/", chanel="pornohammer", thumbnail = "https://static.pornohammer.com/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="pornovideos-hd" , action="submenu", url= "https://www.pornovideos-hd.com/", chanel="pornovideos-hd", thumbnail = "https://static.pornovideos-hd.com/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="pornoschlange" , action="submenu", url= "https://www.pornoschlange.com/", chanel="pornoschlange", thumbnail = "https://static.pornoschlange.com/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="herzporno" , action="submenu", url= "https://www.herzporno.net/", chanel="herzporno", thumbnail = "https://static.herzporno.net/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="nursexfilme" , action="submenu", url= "https://www.nursexfilme.com/", chanel="nursexfilme", thumbnail = "https://static.nursexfilme.com/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="milffabrik" , action="submenu", url= "https://www.milffabrik.com/", chanel="milffabrik", thumbnail = "https://static.milffabrik.com/img/header_60.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="sexfilme-gratis" , action="submenu", url= "https://www.sexfilme-gratis.com/", chanel="sexfilme-gratis", thumbnail = "https://static.sexfilme-gratis.com/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="meinyouporn" , action="submenu", url= "https://www.meinyouporn.com/", chanel="meinyouporn", thumbnail = "https://static.meinyouporn.com/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="tube8-pornos" , action="submenu", url= "https://www.tube8-pornos.com/", chanel="tube8-pornos", thumbnail = "https://static.tube8-pornos.com/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="deinesexfilme" , action="submenu", url= "https://www.deinesexfilme.com/", chanel="deinesexfilme", thumbnail = "https://static.deinesexfilme.com/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="pornhub-sexfilme" , action="submenu", url= "https://www.pornhub-sexfilme.net/", chanel="pornhub-sexfilme", thumbnail = "https://static.pornhub-sexfilme.net/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="pornojenny" , action="submenu", url= "https://www.pornojenny.net/", chanel="pornojenny", thumbnail = "https://static.pornojenny.net/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="beeg-pornos" , action="submenu", url= "https://www.beeg-pornos.com/", chanel="beeg-pornos", thumbnail = "https://static.beeg-pornos.com/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="pornohans" , action="submenu", url= "https://www.pornohans.net/", chanel="pornohans", thumbnail = "https://static.pornohans.net/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="deinesexvideos" , action="submenu", url= "https://www.deinesexvideos.com/", chanel="deinesexvideos", thumbnail = "https://static.deinesexvideos.com/img/logo/logo_300.png", cat=1)) ## cat coge los videoa
    itemlist.append(Item(channel=item.channel, title="xnxx-sexfilme" , action="submenu", url= "https://www.xnxx-sexfilme.com/", chanel="xnxx-sexfilme", thumbnail = "https://static.xnxx-sexfilme.com/img/logo/logo_300.png", cat=1))
    itemlist.append(Item(channel=item.channel, title="xnxx-porno" , action="submenu", url= "https://www.xnxx-porno.com/", chanel="xnxx-porno", thumbnail = "https://static.xnxx-porno.com/img/logo/logo_300.png", cat=1))
    
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    # itemlist.append(Item(channel=item.channel, title="" , action="submenu", url= "", chanel="", thumbnail = ""))
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    
    config.set_setting("current_host", item.url, item.chanel)
    AlfaChannel.host = item.url
    AlfaChannel.canonical.update({'channel': item.chanel, 'host': AlfaChannel.host, 'host_alt': [AlfaChannel.host]})
    
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="list_all", url=item.url + "?o=n&p=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="list_all", url=item.url + "?o=v&p=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="list_all", url=item.url + "?o=r&p=1", chanel=item.chanel))
    itemlist.append(Item(channel=item.channel, title="Mas largo" , action="list_all", url=item.url + "?o=d&p=1", chanel=item.chanel))
    if not item.canal:
        itemlist.append(Item(channel=item.channel, title="PornStar" , action="section", url=item.url + "pornostars/?p=1", extra="PornStar", chanel=item.chanel))
        itemlist.append(Item(channel=item.channel, title="Canal" , action="section", url=item.url + "kanaele/", extra="Canal", chanel=item.chanel))
    if item.cat:
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url, extra="Categorias", chanel=item.chanel, cat=item.cat))
    else:
        itemlist.append(Item(channel=item.channel, title="Categorias" , action="section", url=item.url + "kategorien/", extra="Categorias", chanel=item.chanel))
    
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search", url=item.url, chanel=item.chanel))
    
    return itemlist


def section(item):
    logger.info()
    
    findS = finds.copy()
    findS['url_replace'] = [['(\/(?:category|channel|pornstar)\/[^$]+$)', r'\1?o=n&p=1']]
    
    if item.extra == 'PornStar':
        findS['last_page'] = dict([('find_all', [{'tag': ['a'], 'href': re.compile("/\?p=\d+"), '@POS': [-1], 
                                                '@ARG': 'href', '@TEXT': '(?:/|=)(\d+)'}])])
        findS['next_page_rgx'] = [['?p=\d+', '?p=%s']]
    
    if item.cat:
        findS['categories'] =  dict([('find', [{'tag': ['div'], 'class': ['videos', 'cat', 'grid_container']}]),
                                     ('find_all', [{'tag': ['div', 'figure'], 'class': ['cat', 'grid_box']}])])
    
    if item.extra == 'Categorias':
        findS['title_clean'] =[[' Porn\s*', ''], [' Sexfilme\s*', ''], [' Sex Clips\s*', ''], [' Filme', ''], ['filme', '']]
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
    
    pornstars =soup.find_all('a', href=re.compile("/(?:pornstar|pornostar)/[A-z0-9-]+/"))
    for x, value in enumerate(pornstars):
        pornstars[x] = value.get_text(strip=True)
    pornstar = ""
    pornstar = ' & '.join(pornstars)
    pornstar = AlfaChannel.unify_custom('', item, {'play': pornstar})
    if pornstar:
        lista = item.contentTitle.split('[/COLOR]')
        pornstar = pornstar.replace('[/COLOR]', '')
        pornstar = ' %s' %pornstar
        if AlfaChannel.color_setting.get('quality', '') in item.contentTitle:
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
    
    item.url = "%ssuche/?k=%s&o=n&p=1" % (item.url, texto.replace(" ", "+"))
    
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

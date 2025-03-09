# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from core import urlparse
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup


##########################  NECESITA VPN PARA VER m3u en vodafone

forced_proxy_opt = 'ProxySSL'

# https://kool.to/    https://vavoo.to/    https://huhu.to/  https://www.oha.to/  ETB https://kool.to/play/4016507507/index.m3u8
# https:// NEUER SERVER KOMMT /PointPython.php?coder=MaDoc&username=HYDRAvavoo&password=Germany
# https://kooltown.000webhostapp.com/PointPython.php?coder=MaDoc&username=HYDRAvavoo&password=Spain  # Germany  
# Arabia, Turkey, Germany,
# France, Italy, United Kingdom, 
# Albania, Russia, Balkans, 
# Poland, Spain, Portugal, 
# Netherlands, Romania, Bulgaria
# https://chasmic-curls.000webhostapp.com/Vavoo.php?GroupeHYDRA4=kool_to&username=MaDoc68&password=Spain


timeout =30

canonical = {
             'channel': 'kool', 
             'host': config.get_setting("current_host", 'kool', default=''), 
             'host_alt': ["https://kool.to/"], 
             'host_black_list': [], 
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 3, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
vavoo = "https://vavoo.to/"


def mainlist(item):
    logger.info()
    itemlist = []
    
    url = "%schannels" % host

    itemlist.append(Item(channel=item.channel, title="IPTV" , action="iptv", url=url, pais="Spain"))
    
    headers = {'Referer': host}
    data = httptools.downloadpage(url, headers=headers, canonical=canonical, timeout=timeout).json  #canonical=canonical,
    
    pais= []
    for elem in data:
        if not elem['country'] in pais:
            pais.append(elem['country'])
    for elem in pais:
        itemlist.append(Item(channel=item.channel, title=elem , action="list_all", url=url))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%ssearch/%s/?sort_by=post_date&from_videos=01" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
    return []


def categorias(item):
    logger.info()
    itemlist = []
    
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical, timeout=timeout).data
    else:
        data = httptools.downloadpage(url, canonical=canonical, timeout=timeout).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup

     # {'country': 'Balkans', 'id': 964145822, 'name': 'ARENA SPORT PREMIUM 1 .s', 'p': 0}


def list_all(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    canales = []
    for elem in data:
        if item.title in elem['country']:
            canales.append(elem)
            title = elem['name']
            id = elem['id']
            pos = elem['p']
            url = "%splay/%s/index.m3u8" %(vavoo,id)
            itemlist.append(Item(channel=item.channel, action="play", title=title, url=url))
    # logger.debug(canales)
    # itemlist.sort(key=lambda x: x.title)
    
    return itemlist


# BuenViaje     M+ Música   M+ Documentales     M+ Indie    M+ Suspense     M+ Cine Español     M+ Clásicos     M+ Cracks
# M+ Cine   Movistar plus+      Movistar Plus+ 2    

NOMBRE={'AXN MOVIES': 'AXN Movies', 'AXN WHITE': 'AXN Movies', 'CACAVISION': 'Cazavisión',
        'A PUNT': 'À Punt', 'BETEVE': 'Betevé', 'MOVISTAR+': 'Movistar plus+', 'MOVISTAR ESTRENOS': 'Movistar plus+', 'M.ESTRENOS': 'M+ Cine',
        'ONDA CADIZ': 'Onda Cadiz TV', 'LEVANTE TV': 'Levante TV', 'CANAL 33': 'Canal 33', 'CANAL EXTREMADURA': 'Canal Extremadura',
        'TV CASTILLA LA MANCHA': 'Castilla la Mancha TV', 'TV GALICIA': 'TVG -TV Galicia', 'SEVILLA FC TV': 'Sevilla FC TV',
        'ARAGON TV INTERNACIONAL': 'Aragón TV Int', 'ARAGON': 'Aragón TV', 'LA 7': 'La 7', 'TV3 CATALUNIA': 'TV3 Cat',
        'GOL': 'GOL PLAY', 'GOL TV': 'GOL PLAY', 'CANAL PANDA': 'Enfamilia', 'TV3 CATALUNYA': 'TV3','VIAJAR': 'La Resistencia',
        'CANAL SUR ANDALUCIA': 'Canal Sur', 'CANAL SUR A': 'Canal Sur', 'BLAZE': 'AMC Break', 'FOX LIFE': 'Fox',
        'NAT GEO': 'National Geographic', 'CRIME & INVESTIGATION': 'AMC Crime', 'CRIME DISTRICT': 'AMC Crime',
        'ANTENA 3': 'Antena 3', 'TELECINCO': 'Telecinco', 'HISTORIA': 'Historia', 'CANAL DECASA': 'Canal Decasa', 'DECASA': 'Canal Decasa',
       'NEOX': 'Neox', 'EUROSPORT 1': 'Eurosport 1', 'EUROSPORT 2': 'Eurosport 2', 'CANAL COCINA': 'Canal Cocina',
       'FOX': 'Fox', 'FDF': 'Factoría de Ficción', 'CUATRO': 'Cuatro', 'LA SEXTA': 'La Sexta', 'TVE LA 1 MADRID': 'LA 1',
       'NATIONAL GEOGRAPHIC': 'National Geographic', 'CAZA Y PESCA': 'Caza y Pesca', 'CANAL ODISEA': 'Odisea', 'NOVA': 'Nova',
        'MEGA': 'Mega', 'ENERGY': 'Energy', 'CANAL HOLLYWOOD': 'Hollywood', 'SOMOS': 'Somos',
       'CALLE 13': 'Calle 13', 'TVE LA 2': 'LA 2', 'COMEDY CENTRAL': 'Comedy Central', 'DISCOVERY CHANNEL': 'Discovery',
       'NAT GEO WILD': 'Nat Geo Wild', 'IBERLIA TV': 'Iberalia TV', 'TRECE TV': '13 TV', 'MOVISTAR GOLF': 'M+ Golf',
       'M.GOLF': 'M+ Golf', 'FACTORIA DE FICCION': 'Factoría de Ficción', 'HOLLYWOOD': 'Hollywood', 'A3 SERIES': 'Atreseries',
       'PARAMOUNT CHANNEL': 'Paramount Channel', 'BOING': 'Boing', 'DISCOVERY WORLD': 'Discovery', 'TEN': 'Ten',
       'TOROS TV': 'Onetoro TV', 'TELEDEPORTE': 'Teledeporte', 'DISNEY CHANNEL': 'Disney Channel', 'DIVINITY': 'Divinity',
       'BABY TV': 'Baby TV', 'NICK JUNIOR': 'NICK JR', 'COSMOPOLITAN TV': 'COSMO', 'CLAN TVE': 'Clan TVE', 'D KISS': 'DKISS', 
       'ETB BASQUE': 'EITB Basque', 'ATRESERIES (A3 SERIES)': 'Atreseries', 'AMC BREAK': 'AMC Break', 'NICKELODEON': 'Nickelodeon',
       'REAL MADRID TV': 'Real Madrid TV', 'PARAMOUNT NETWORK': 'Paramount Channel', 'SUNDANCE TV': 'Sundance', 'CLAN': 'Clan TVE',
       'ENFAMILIA': 'Enfamilia', 'CLASSICA': 'Classica', 'MTV ESPANA': 'MTV', 'MTV 90S': 'MTV 00s', 'SOL MUSICA': 'Sol Música',
       'IBERALIA TV': 'Iberalia TV', 'TELE MADRID': 'Telemadrid', 'TNT': 'Warner TV', 'WARNER TV': 'Warner TV', 'ESPORT 3': 'Esport 3',
       'DISNEY JUNIOR': 'Disney Junior', 'DREAMWORKS TV': 'Dreamworks', 'BOM CINE': 'BOM Cine', 'TELEMADRID': 'Telemadrid',
       'M.LIGA DE CAMPEONES': 'M+ Liga de Campeones', 'LIGA CAMPEONES': 'M+ Liga de Campeones', 'LIGA TV': 'M+ LALIGA TV', 'LA LIGA TV': 'M+ LALIGA TV',
       'MOVISTAR LIGA DE CAMPEONES': 'M+ Liga de Campeones',
       'MOVISTAR LIGA DE CAMPEONES 1 (ONLY EVENT)': 'M+ Liga de Campeones', 'MOVISTAR LIGA DE CAMPEONES 2 (ONLY EVENT)': 'M+ Liga de Campeones 2',
       'MOVISTAR LIGA DE CAMPEONES 3 (ONLY EVENT)': 'M+ Liga de Campeones 3', 'MOVISTAR LIGA DE CAMPEONES 4 (ONLY EVENT)': 'M+ Liga de Campeones 4',
       'M+ LIGA DE CAMPEONES 2': 'M+ Liga de Campeones 2', 'LALIGA SMARTBANK TV': 'LALIGA TV HYPERMOTION', 'LALIGA SMARTBANK TV 1': 'LALIGA TV HYPERMOTION',
       'LALIGA SMARTBANK TV 2': 'LALIGA TV HYPERMOTION 2', 'LALIGA SMARTBANK TV 3': 'LALIGA TV HYPERMOTION 3', 'MOVISTAR LA LIGA 1': 'M+ LALIGA TV',
       'MOVISTAR LA LIGA': 'M+ LALIGA TV',
       'MOVISTAR LA LIGA 2': 'M+ LALIGA TV 2', 'MOVISTAR LA LIGA 3': 'M+ LALIGA TV 3', 'MOVISTAR LA LIGA 4': 'M+ LALIGA TV 4', 'MOVISTAR DEPORTES': 'M+ Deportes', 
       'M.DEPORTES': 'M+ Deportes', 'VAMOS': 'M+ Vamos', 'M+ ELLAS #V': 'M+ Ellas V', 'MOVISTAR F1': 'DAZN F1', 'M.FORMULA 1': 'DAZN F1',
       'M.ACCION': 'M+ Acción', 'MOVISTAR ACCI©N': 'M+ Acción', 'MOVISTAR SERIES': 'M+ Series', 'MOVISTAR DRAMA':'M+ Drama', 'MOVISTAR COMEDIA': 'M+ Comedia',
       'MOVISTAR SERIESMANIA': 'M+ Series',
        }
            #  M.ESTRENOS   

# M+ Liga de Campeones     M+ Liga de Campeones 2      M+ Liga de Campeones 3     M+ Liga de Campeones 4
# M+ LALIGA TV    M+ LALIGA TV 2    M+ LALIGA TV 3      M+ LALIGA TV 4
# LALIGA TV HYPERMOTION     LALIGA TV HYPERMOTION 2     LALIGA TV HYPERMOTION 3     
# DAZN LALIGA   DAZN LALIGA 2



def iptv(item):
    logger.info()
    itemlist = []
    # D:\Nexus\portable_data
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    data = httptools.downloadpage(item.url).json
    ficheros =['DAZN', 'FUTBOL', 'RAKUTEN', 'CAMBIO']
    Dazn = ""
    Futbol = ""
    Rakuten = ""
    Cambio = ""
    for elem in data:
        if item.pais in elem['country']:
            x = ""
            titulo = elem['name'].replace(" .b", "").replace(".c", "")
            lang = titulo.replace(" (BACKUP)", "").replace(" FULL HD", "").replace(" HD", "").strip()
            id = elem['id']
            pos = elem['p']
            if lang in NOMBRE:
                title = NOMBRE.get(lang, lang)
            else:
                title = lang
            
            
            if 'dazn' in lang.lower(): 
                grupo = "DAZN"
            elif 'BAR ' in lang or 'liga' in lang.lower() or 'laliga' in lang.lower(): 
                grupo = "FUTBOL"
            elif 'rakuten' in  lang.lower():
                grupo = "RAKUTEN"
            else: 
                grupo = "CAMBIO"
            logger.debug(grupo)
            lin = '#EXTINF:-1 tvg-id="" tvg-name="%s" tvg-logo="" group-title="%s",%s\n' %(titulo,grupo,title)
            x += lin
            url = "%splay/%s/index.m3u8\n" %(vavoo,id)
            x += url
            if grupo == "DAZN": Dazn +=x
            if grupo == "FUTBOL": Futbol +=x
            if grupo == "RAKUTEN": Rakuten +=x
            if grupo == "CAMBIO": Cambio +=x
    # logger.debug(Dazn)
    # logger.debug(Futbol)
    # logger.debug(Rakuten)
    # logger.debug(Cambio)
    for elem in ficheros:
        ficherosubtitulo = filetools.join(path, "Z_%s.txt" %elem)
        if filetools.exists(ficherosubtitulo):
            try:
                filetools.remove(ficherosubtitulo)
            except IOError:
                logger.error("Error al eliminar el archivo " + ficherosubtitulo)
                raise
        if elem == "DAZN": filetools.write(ficherosubtitulo, Dazn)
        if elem == "FUTBOL": filetools.write(ficherosubtitulo, Futbol)
        if elem == "RAKUTEN": filetools.write(ficherosubtitulo, Rakuten)
        if elem == "CAMBIO": filetools.write(ficherosubtitulo, Cambio)

        
            # itemlist.append(Item(channel=item.channel, action="play", title=title, url=url))
            # logger.debug(elem)
            # logger.debug(lin)
            # logger.debug(url)
    # itemlist.sort(key=lambda x: x.title)
    
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    logger.debug("ITEM: %s" % item)
    url = item.url
    headers = {'Referer': host}
    # url = httptools.downloadpage(url, canonical=canonical, headers=headers, timeout=timeout, follow_redirects=False, only_headers=True).headers.get("location", "")
    # url = httptools.downloadpage(url, canonical=canonical, timeout=timeout, headers=headers).headers.get("location", "")
    
    # url += "|Referer=%s" % host
    # url += "|ignore_response_code=True"
    itemlist.append(['m3u', url]) 
    return itemlist
    # import xbmc
    # import xbmcgui
    # listitem = xbmcgui.ListItem(item.title)
    # listitem.setArt({'thumb': item.thumbnail, 'icon': "DefaultVideo.png", 'poster': item.thumbnail})
    # listitem.setInfo('video', {'Title': item.title, 'Genre': 'Porn', 'plot': '', 'plotoutline': ''})
    # listitem.setMimeType('application/vnd.apple.mpegurl')
    # listitem.setContentLookup(False)
    # return xbmc.Player().play(url, listitem)

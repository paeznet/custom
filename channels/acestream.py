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


# canonical = {
             # 'channel': 'acestream', 
             # 'host': config.get_setting("current_host", 'acestream', default=''), 
             # 'host_alt': ["https://kool.to/"], 
             # 'host_black_list': [], 
             # 'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 3, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            # }
# host = canonical['host'] or canonical['host_alt'][0]
# host= ""


forced_proxy_opt = 'ProxySSL'

timeout =30

kwargs = {
    'set_tls': 	True,
    'set_tls_min': True,
    'retries_cloudflare': 1,
	# 'forced_proxy_ifnot_assistant': forced_proxy_opt,
	'cf_assistant': False,
}


acestream_channels = "D://Kodi21/portable_data/addons/plugin.video.acestream_channels/addon.py"
XUPIMARC2 = "https://www.socialcreator.com/xupimarc2/?s=289267"
ciriaco = "https://fr.4everproxy.com/direct/aHR0cHM6Ly9jaXJpYWNvLWxpYXJ0LnZlcmNlbC5hcHAv"  ## "https://ciriaco-liart.vercel.app/"
verceltv = "https://fr.4everproxy.com/direct/aHR0cHM6Ly9ldmVudG9zLWxpYXJ0dmVyY2VsYXBwLnZlcmNlbC5hcHAv"  ## https://eventos-liartvercelapp.vercel.app/
mister = "https://www.misterchire.com/"
shickath = "https://shickat.me/"
probando = "https://github.com/Icastresana/lista1/blob/main/Probando"
peticiones = "https://raw.githubusercontent.com/Icastresana/lista1/refs/heads/main/peticiones"


def mainlist(item):
    logger.info()
    itemlist = []
    
    itemlist.append(Item(channel=item.channel, title="acestream_channels" , action="acestream", url=acestream_channels))
    itemlist.append(Item(channel=item.channel, title="Ciriaco" , action="ciri", url=ciriaco))
    itemlist.append(Item(channel=item.channel, title="Misterchire" , action="misterchire", url=mister))
    itemlist.append(Item(channel=item.channel, title="Shickat" , action="shickat", url=shickath))
    itemlist.append(Item(channel=item.channel, title="Verceltv" , action="vercel", url=verceltv))
    itemlist.append(Item(channel=item.channel, title="XUPIMARC2" , action="xupimarc2", url=XUPIMARC2))
    itemlist.append(Item(channel=item.channel, title="Icastresana" , action="icastresana", url=probando))
    
    
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, timeout=timeout, **kwargs).data
    else:
        data = httptools.downloadpage(url, timeout=timeout, **kwargs).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def vercel(item):
    logger.info()
    itemlist = []
    
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    comparar = "D://Kraken/custom/00/icastresana.m3u"
    comparar = filetools.read(comparar)
    
    soup = create_soup(item.url)
    matches = soup.find_all('a', href=re.compile(r"^acestream://[A-z0-9]+(?:/|)"))
    Verceltv = ""
    for elem in matches:
        x = ""
        title = elem.text.strip()
        url = elem['href']
        id = url.replace("acestream://", "")
        
        lin = '#EXTINF:-1 tvg-name="%s" tvg-logo="" group-title="%s" tvg-id="",%s\n'  %("Verceltv", "Verceltv", title)
        x += lin
        url = "plugin://script.module.horus?action=play&id=%s\n" % id
        x += url
        
        # Verceltv +=x
        if not id in comparar: Verceltv +=x
    
    ficherosubtitulo = filetools.join(path, "Z_aVerceltv.txt")
    if filetools.exists(ficherosubtitulo):
        try:
            filetools.remove(ficherosubtitulo)
        except IOError:
            logger.error("Error al eliminar el archivo " + ficherosubtitulo)
            raise
    filetools.write(ficherosubtitulo, Verceltv)
    # logger.debug(Verceltv)  
    return itemlist


def ciri(item):
    logger.info()
    itemlist = []
    ids = []
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    comparar = "D://Kraken/custom/00/icastresana.m3u"
    comparar = filetools.read(comparar)
    
    soup = create_soup(item.url)
    matches = soup.find_all('a', href=re.compile(r"^acestream://[A-z0-9]+(?:/|)"))
    Ciriaco = ""
    for elem in matches:
        x = ""
        title = elem.text.strip()
        url = elem['href']
        id = url.replace("acestream://", "")
        
        if not id in ids:
            ids.append(id)
        else: continue
        
        lin = '#EXTINF:-1 tvg-name="%s" tvg-logo="" group-title="%s" tvg-id="",%s\n' %("Ciriaco", "Ciriaco", title)
        x += lin
        url = "plugin://script.module.horus?action=play&id=%s\n" % id
        x += url
        
        # Ciriaco +=x
        if not id in comparar: Ciriaco +=x
    
    ficherosubtitulo = filetools.join(path, "Z_aCiriaco.txt")
    if filetools.exists(ficherosubtitulo):
        try:
            filetools.remove(ficherosubtitulo)
        except IOError:
            logger.error("Error al eliminar el archivo " + ficherosubtitulo)
            raise
    filetools.write(ficherosubtitulo, Ciriaco)
    # logger.debug(Ciriaco)  
    return itemlist


def xupimarc2(item):
    logger.info()
    itemlist = []
    
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    comparar = "D://Kraken/custom/00/icastresana.m3u"
    comparar = filetools.read(comparar)
    
    soup = create_soup(item.url)
    matches = soup.find_all('a', href=re.compile(r"^acestream://[A-z0-9]+(?:/|)"))
    Xupimarc2 = ""
    for elem in matches:
        x = ""
        if elem.find('img'):
            title = elem.img['alt']
        else:
            title = elem.text.strip()
        url = elem['href']
        id = url.replace("acestream://", "")
        
        lin = '#EXTINF:-1 tvg-name="%s" tvg-logo="" group-title="%s" tvg-id="",%s\n'  %("Xupimarc2", "Xupimarc2", title)
        x += lin
        url = "plugin://script.module.horus?action=play&id=%s\n" % id
        x += url
        
        # Xupimarc2 +=x
        if not id in comparar: Xupimarc2 +=x
    
    ficherosubtitulo = filetools.join(path, "Z_aXupimarc2.txt")
    if filetools.exists(ficherosubtitulo):
        try:
            filetools.remove(ficherosubtitulo)
        except IOError:
            logger.error("Error al eliminar el archivo " + ficherosubtitulo)
            raise
    filetools.write(ficherosubtitulo, Xupimarc2)
    # logger.debug(Xupimarc2)  
    return itemlist


def shickat(item):
    logger.info()
    itemlist = []
    
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    comparar = "D://Kraken/custom/00/icastresana.m3u"
    comparar = filetools.read(comparar)
    
    soup = create_soup(item.url)
    
    # matches = soup.find_all('a', href=re.compile(r"^acestream://[A-z0-9]+(?:/|)"))
    matches = soup.find_all('article', class_="canal-card")
    Shickat = ""
    for elem in matches:
        x = ""
        if elem.get('data-titulo', ''):
            title = elem['data-titulo']
        else:
            title = elem.text.strip()
        url = elem.a['href']
        id = url.replace("acestream://", "")
        
        lin = '#EXTINF:-1 tvg-name="%s" tvg-logo="" group-title="%s" tvg-id="",%s\n'  %("Shickat", "Shickat", title)
        x += lin
        url = "plugin://script.module.horus?action=play&id=%s\n" % id
        x += url
        
        # Shickat +=x
        if not id in comparar: Shickat +=x
    
    ficherosubtitulo = filetools.join(path, "Z_aShickat.txt")
    if filetools.exists(ficherosubtitulo):
        try:
            filetools.remove(ficherosubtitulo)
        except IOError:
            logger.error("Error al eliminar el archivo " + ficherosubtitulo)
            raise
    filetools.write(ficherosubtitulo, Shickat)
    # logger.debug(Shickat)  
    return itemlist


def icastresana(item):
    logger.info()
    itemlist = []
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    comparar = "D://Kraken/custom/00/icastresana.m3u"
    comparar = filetools.read(comparar)
    
    data = httptools.downloadpage(item.url, timeout=timeout, **kwargs).data
    logger.debug(data)
    patron = '(\#EXTINF.*?)\n'
    patron += 'acestream://([a-z0-9]+)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.debug(matches)
    Icastresana = ""
    for lin, id in matches:
        x = ""
        # id = url.replace("acestream://", "")
        # grupo = title.split("|")
        # name = grupo[-1]
        # if len(grupo) >=1:
            # grupo = grupo[0]
        # else:
            # grupo = scrapertools.find_single_match(name, '(\w+)')
        
        # lin = '#EXTINF:-1 tvg-name="%s" tvg-logo="" group-title="%s" tvg-id="",%s\n'  %(title, grupo, name)
        x += '%s\n' %lin
        url = "plugin://script.module.horus?action=play&id=%s\n" % id
        x += url
        
        # Acestream +=x
        if not id in comparar: Icastresana +=x
    
    ficherosubtitulo = filetools.join(path, "Z_Icastresana.txt")
    if filetools.exists(ficherosubtitulo):
        try:
            filetools.remove(ficherosubtitulo)
        except IOError:
            logger.error("Error al eliminar el archivo " + ficherosubtitulo)
            raise
    filetools.write(ficherosubtitulo, Icastresana)
    # logger.debug(Icastresana)
    
    return itemlist


def misterchire(item):
    logger.info()
    itemlist = []
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    comparar = "D://Kraken/custom/00/icastresana.m3u"
    comparar = filetools.read(comparar)
    
    soup = create_soup(item.url)
    inicio = soup.find_all('a', href=re.compile(r"^https://www.misterchire.com/inicio/[A-z0-9]+(?:/|)"))
    group =[]
    urls = []
    for elem in inicio:
        url = elem['href']
        thumb = elem.img['src'].split("/")
        grupo = thumb[-1].replace("-prueba", "").replace(".png", "").replace("-", " ")
        urls.append(url)
        group.append(grupo)
        
        # logger.debug(grupo +" >>> "+ url)
        
    Misterchire = ""
    for url, grupo in zip(urls, group):
        soup = create_soup(url)
        matches = soup.find_all('a', href=re.compile(r"^acestream://[A-z0-9]+(?:/|)"))
        logger.debug(matches)
        for elem in matches:
            x = ""
            # logger.debug(elem)
            url = elem['href']
            thumb = elem.img['src'].split("/")
            logger.debug(thumb[-1])
            title = thumb[-1].replace(".jpg", "").replace(".png", "").replace("icono", "").replace("-", " ")
            id = url.replace("acestream://", "")
            
            lin = '#EXTINF:-1 tvg-name="%s" tvg-logo="" group-title="%s" tvg-id="",%s\n'  %("misterchire", grupo, title)
            x += lin
            url = "plugin://script.module.horus?action=play&id=%s\n" % id
            x += url
            
            # Misterchire +=x
            if not id in comparar: Misterchire +=x
    
    ficherosubtitulo = filetools.join(path, "Z_aMisterchire.txt")
    if filetools.exists(ficherosubtitulo):
        try:
            filetools.remove(ficherosubtitulo)
        except IOError:
            logger.error("Error al eliminar el archivo " + ficherosubtitulo)
            raise
    filetools.write(ficherosubtitulo, Misterchire)
    # logger.debug(Misterchire)
    
    return itemlist


def acestream(item):
    logger.info()
    itemlist = []
    from core import filetools
    path = filetools.translatePath("special://xbmc")+ 'portable_data/'
    
    comparar = "D://Kraken/custom/00/icastresana.m3u"
    comparar = filetools.read(comparar)
    
    data = filetools.read(item.url)
    
    patron = '\{"name": "([^"]+)", "url": "([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    Acestream = ""
    for title, url in matches:
        x = ""
        id = url.replace("acestream://", "")
        grupo = title.split("|")
        name = grupo[-1]
        if len(grupo) >=1:
            grupo = grupo[0]
        else:
            grupo = scrapertools.find_single_match(name, '(\w+)')
        
        lin = '#EXTINF:-1 tvg-name="%s" tvg-logo="" group-title="%s" tvg-id="",%s\n'  %(title, grupo, name)
        x += lin
        url = "plugin://script.module.horus?action=play&id=%s\n" % id
        x += url
        
        # Acestream +=x
        if not id in comparar: Acestream +=x
    
    ficherosubtitulo = filetools.join(path, "Z_Acestream.txt")
    if filetools.exists(ficherosubtitulo):
        try:
            filetools.remove(ficherosubtitulo)
        except IOError:
            logger.error("Error al eliminar el archivo " + ficherosubtitulo)
            raise
    filetools.write(ficherosubtitulo, Acestream)
    # logger.debug(Acestream)
    
    return itemlist


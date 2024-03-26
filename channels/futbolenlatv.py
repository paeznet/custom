# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

#   https://telegra.ph/AGENDA-DEPORTIVA-2504-04-25    https://telegra.ph/CLONELCANO-08-09
    # acestream://9dad717d99b29a05672166258a77c25b57713dd5


# https://porlacaraveoelfutbol.pages.dev/   https://www.futbolenlatv.es/
# https://tvglobalrpi.blogspot.com/p/canales-acestream-actualizados.html?m=1

# https://hackmd.io/@penaltis/penaltis
# https://github.com/MoDz17/IPTV_MoDz/blob/main/code_iptv
# https://acestreamsearch.net/en/?q=el


canonical = {
             'channel': 'futbolenlatv', 
             'host': config.get_setting("current_host", 'futbolenlatv', default=''), 
             'host_alt': ["https://www.futbolenlatv.es/"], 
             'host_black_list': [], 
             # 'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]



def mainlist(item):
    logger.info()
    itemlist = []
    
    url = "%s?opSearch=1" % host #1 por campeonato 2 por horario)
    
    soup = create_soup(url).find('table', class_='tablaPrincipal')
    matches = soup.find_all('tr')
    itemlist.append(Item(channel=item.channel, title="el barco", action="acestream", url="https://telegra.ph/"))

    itemlist.append(Item(channel=item.channel, title="[COLOR blue]%s[/COLOR]" % matches[0].text.strip()))
    matches.pop(0)
    
# <td class="hora"> 01:00 </td> 
# <td class="detalles"> 
    # <ul> <li> <div class="contenedorImgCompeticion"> 
        # <img alt="Liga de Campeones CONCACAF" class="lazyload" data-src="https://static.futbolenlatv.com/img/32/20171010091020-concacaf-champions.png" height="22" title="Liga de Campeones CONCACAF" width="22"/> 
    # <span class="ajusteDoslineas"> <a class="internalLink" href="/competicion/concacaf-champions"> <label title="Liga de Campeones CONCACAF">Liga de Campeones CONCACAF</label> </a> <span title="1/8 de final">1/8 de final</span> </span> </div> </li> </ul></td>

# <td class="local"> 
    # <a class="internalLink" href="/equipo/fc-cincinnati"> <span title="FC Cincinnati">FC Cincinnati</span> </a> <img alt="FC Cincinnati" class="lazyload" data-src="https://static.futbolenlatv.com/img/32/20190525113431-fc-cincinnati.png" height="32" title="FC Cincinnati" width="32"/></td>

# <td class="visitante"> 
    # <img alt="Monterrey" class="lazyload" data-src="https://static.futbolenlatv.com/img/32/20130210115322_monterrey.png" height="32" title="Monterrey" width="32"/> <a class="internalLink" href="/equipo/monterrey"> <span title="Monterrey">Monterrey</span> </a></td> 

# <td class="canales"> 
    # <div itemscope="" itemtype="https://schema.org/Event"> 
        # <meta content="FC Cincinnati - Monterrey" itemprop="name"/> 
        # <meta content="FC Cincinnati - Monterrey el viernes, 8 de marzo de 2024 a las 1:00" itemprop="description"/> 
        # <meta content="https://www.futbolenlatv.es/competicion/concacaf-champions" itemprop="url"/> 
        # <meta content="2024-03-08T00:00:00" itemprop="startDate"/> 
        # <meta content="T1H45M" itemprop="duration"/> 
        # <div itemprop="location" itemscope="" itemtype="https://schema.org/Place"> 
            # <meta content="TQL Stadium" itemprop="name"/> 
            # <meta content="1501 Central Pkwy, Cincinnati, OH 45214, USA" itemprop="address"/> </div> 
    # </div> 
    # <ul class="listaCanales"> 
        # <li class="colorRojo" title="CONCACAF YouTube"><a class="internalLinkCanal" href="/canal/concacaf-youtube">CONCACAF YouTube</a></li> 
        # <li class="colorRojo" title="CONCACAF GO"><a class="internalLinkCanal" href="/canal/concacaf-go">CONCACAF GO</a></li> </ul> </td></tr>    
    purgar = ['Fanatiz (Regístrate ahora)', 'AFA Play', 'Amazon Prime Video (Prueba gratis)', 'OneFootball PPV']
    for elem in matches:
        ace = []
        if elem.find('td', class_='pTabla'): continue #QUIUTA ULTIMO ELEMENTO
        canales = elem.find('td', class_='canales').find_all('li')
        for x , value in enumerate(canales):
            if value.get('class',''): 
                canales=[]
                continue #purga los rojos
            if not value.text.strip() in purgar:
                ace.append(value.text.strip())
            
        if ace:
            ace = ' & '.join(ace)
            
            hora = elem.find('td', class_='hora').text.strip() #
            # logger.debug(hora)
            det = elem.find('td', class_='detalles')
            local = elem.find('td', class_='local')
            visit = elem.find('td', class_='visitante')
            p1 = local.text.strip()
            p2 = visit.text.strip()
            p1thumb = local.img['data-src']
            p2thumb = visit.img['data-src']
            thumb = det.img['data-src']
            campeonato = det.img['title']
            title = "%s >> %s" %(hora, ace)
            
            # import datetime
            # mi_fecha = datetime.datetime.strptime(hora, '%H:%M')
            # logger.debug(datetime.datetime.now())

            itemlist.append(Item(channel=item.channel, title=title))

    # matches = soup.find_all('strong')[:-2]
    # lista = []
    # n=0
    
    # for x , value in enumerate(matches):
        # if value.text.strip().isupper():
            # lista.append(x)
            # id = x
            # n+= 1
            # corta=[]
        # if len(lista) == n:
            # corta.append(value.text.strip())
            # lista[n-1] = corta
    
    # for elem in lista:
        # itemlist.append(Item(channel=item.channel, title="[COLOR blue]%s[/COLOR]" % elem[0]))
        # for x , value in enumerate(elem):
            # if x % 2 == 0 and not x == 0:
                # url = "plugin://script.module.horus?action=play&id=%s&title=%s" % (value, elem[x-1])
                # title = ".......%s" % elem[x-1]
                # itemlist.append(Item(channel=item.channel, action="play", title=title, url=url))
    return itemlist



def acestream(item):
    logger.info()
    itemlist = []
    url = "%s?opSearch=1" % host #1 por campeonato 2 por horario)
    
    soup = create_soup(url).find('table', class_='tablaPrincipal')
    matches = soup.find_all('tr')
    url = "%sAGENDA-DEPORTIVA-2504-04-25" % item.url
    
    soup = create_soup(url).find('article')
    matches = soup.find_all('strong')[:-2]
    lista = []
    n=0
    
    for x , value in enumerate(matches):
        if value.text.strip().isupper():
            lista.append(x)
            id = x
            n+= 1
            corta=[]
        if len(lista) == n:
            corta.append(value.text.strip())
            lista[n-1] = corta
    
    for elem in lista:
        itemlist.append(Item(channel=item.channel, title="[COLOR blue]%s[/COLOR]" % elem[0]))
        for x , value in enumerate(elem):
            if x % 2 == 0 and not x == 0:
                url = "plugin://script.module.horus?action=play&id=%s&title=%s" % (value, elem[x-1])
                title = ".......%s" % elem[x-1]
                # logger.debug(url + title)
                itemlist.append(Item(channel=item.channel, action="play", title=title, url=url))
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
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

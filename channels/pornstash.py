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
from modules import autoplay

# IDIOMAS = {'vo': 'VO'}
# list_language = list(IDIOMAS.values())
list_quality = ['default']
list_servers = []

#https://secretstash.in
# url_api = host + "/api/v1/releases?Limit=20&Offset=0"
# https://pornstash.in/api/v1/releases?Limit=20&Offset=0

######  fallo de su server una version minimalista

canonical = {
             'channel': 'pornstash', 
             'host': config.get_setting("current_host", 'pornstash', default=''), 
             'host_alt': ["https://pornstash.in/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]



def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="submenu"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="OnlyFans" , action="lista", url=host + "/category/OnlyFans"))
    itemlist.append(Item(channel=item.channel, title="X-Angels" , action="lista", url=host + "/category/X-Angels"))
    itemlist.append(Item(channel=item.channel, title="Tiny4K" , action="lista", url=host + "/category/Tiny4K"))
    itemlist.append(Item(channel=item.channel, title="Nubiles" , action="lista", url=host + "/category/Nubiles"))
    itemlist.append(Item(channel=item.channel, title="FTVGirls" , action="lista", url=host + "/category/FTVGirls"))
    # itemlist.append(Item(channel=item.channel, title="MetArtX" , action="lista", url=host + "/category/MetArtX"))
    itemlist.append(Item(channel=item.channel, title="VivThomas" , action="lista", url=host + "/category/VivThomas"))
    itemlist.append(Item(channel=item.channel, title="NaughtyOffice" , action="lista", url=host + "/category/NaughtyOffice"))
    itemlist.append(Item(channel=item.channel, title="EvilAngel" , action="lista", url=host + "/category/EvilAngel"))
    itemlist.append(Item(channel=item.channel, title="FamilyStrokes" , action="lista", url=host + "/category/FamilyStrokes"))
    itemlist.append(Item(channel=item.channel, title="SexMex" , action="lista", url=host + "/category/SexMex"))
    itemlist.append(Item(channel=item.channel, title="ATK" , action="lista", url=host + "/category/ATK"))
    itemlist.append(Item(channel=item.channel, title="BrazzersExxtra" , action="lista", url=host + "/category/BrazzersExxtra"))
    itemlist.append(Item(channel=item.channel, title="RKPrime" , action="lista", url=host + "/category/RKPrime"))
    itemlist.append(Item(channel=item.channel, title="Private" , action="lista", url=host + "/category/Private"))
    itemlist.append(Item(channel=item.channel, title="Bang" , action="lista", url=host + "/category/Bang"))
    itemlist.append(Item(channel=item.channel, title="ClubSweethearts" , action="lista", url=host + "/category/ClubSweethearts"))
    itemlist.append(Item(channel=item.channel, title="SexArt" , action="lista", url=host + "/category/SexArt"))
    itemlist.append(Item(channel=item.channel, title="SisLovesMe" , action="lista", url=host + "/category/SisLovesMe"))
    itemlist.append(Item(channel=item.channel, title="BangBus" , action="lista", url=host + "/category/BangBus"))
    itemlist.append(Item(channel=item.channel, title="PlayboyPlus" , action="lista", url=host + "/category/PlayboyPlus"))
    itemlist.append(Item(channel=item.channel, title="MyPervyFamily " , action="lista", url=host + "/category/MyPervyFamily"))
    itemlist.append(Item(channel=item.channel, title="PutaLocura " , action="lista", url=host + "/category/PutaLocura"))
    itemlist.append(Item(channel=item.channel, title="JacquieEtMichelTV" , action="lista", url=host + "/category/JacquieEtMichelTV"))
    itemlist.append(Item(channel=item.channel, title="MySistersHotFriend " , action="lista", url=host + "/category/MySistersHotFriend"))
    itemlist.append(Item(channel=item.channel, title="PublicAgent  " , action="lista", url=host + "/category/PublicAgent"))
    itemlist.append(Item(channel=item.channel, title="CzechCasting  " , action="lista", url=host + "/category/CzechCasting"))
    itemlist.append(Item(channel=item.channel, title="MyDirtyMaid  " , action="lista", url=host + "/category/MyDirtyMaid"))
    itemlist.append(Item(channel=item.channel, title="CherryPimps " , action="lista", url=host + "/category/CherryPimps"))
    itemlist.append(Item(channel=item.channel, title="TeamSkeetSelects " , action="lista", url=host + "/category/TeamSkeetSelects"))
    itemlist.append(Item(channel=item.channel, title="NubileFilms  " , action="lista", url=host + "/category/NubileFilms"))
    itemlist.append(Item(channel=item.channel, title="Hegre " , action="lista", url=host + "/category/Hegre"))
    itemlist.append(Item(channel=item.channel, title="BlacksOnBlondes " , action="lista", url=host + "/category/BlacksOnBlondes"))
    itemlist.append(Item(channel=item.channel, title="MassageRooms" , action="lista", url=host + "/category/MassageRooms"))
    itemlist.append(Item(channel=item.channel, title="BlackedRaw " , action="lista", url=host + "/category/BlackedRaw "))
    itemlist.append(Item(channel=item.channel, title="MonstersOfCock " , action="lista", url=host + "/category/MonstersOfCock"))
    itemlist.append(Item(channel=item.channel, title="Blacked" , action="lista", url=host + "/category/Blacked"))
    itemlist.append(Item(channel=item.channel, title="SpyFam " , action="lista", url=host + "/category/SpyFam"))
    itemlist.append(Item(channel=item.channel, title="FamilySwap " , action="lista", url=host + "/category/FamilySwap"))
    itemlist.append(Item(channel=item.channel, title="BigTitsRoundAsses " , action="lista", url=host + "/category/BigTitsRoundAsses"))
    itemlist.append(Item(channel=item.channel, title="JapanHDV " , action="lista", url=host + "/category/JapanHDV"))
    itemlist.append(Item(channel=item.channel, title="GloryHoleSecrets " , action="lista", url=host + "/category/GloryHoleSecrets"))
    itemlist.append(Item(channel=item.channel, title="Joymii" , action="lista", url=host + "/category/Joymii"))
    itemlist.append(Item(channel=item.channel, title="PervsOnPatrol " , action="lista", url=host + "/category/PervsOnPatrol"))
    itemlist.append(Item(channel=item.channel, title="EdgeQueens " , action="lista", url=host + "/category/EdgeQueens"))
    itemlist.append(Item(channel=item.channel, title="Vixen " , action="lista", url=host + "/category/Vixen"))
    itemlist.append(Item(channel=item.channel, title="CastingCouch" , action="lista", url=host + "/category/CastingCouch"))
    itemlist.append(Item(channel=item.channel, title="FamilyHookups" , action="lista", url=host + "/category/FamilyHookups"))
    itemlist.append(Item(channel=item.channel, title="BangBros" , action="lista", url=host + "/category/BangBros"))
    itemlist.append(Item(channel=item.channel, title="ATKHairy " , action="lista", url=host + "/category/ATKHairy"))
    itemlist.append(Item(channel=item.channel, title="Anilos " , action="lista", url=host + "/category/Anilos"))
    itemlist.append(Item(channel=item.channel, title="BrattySis " , action="lista", url=host + "/category/BrattySis"))
    itemlist.append(Item(channel=item.channel, title="PervTherapy " , action="lista", url=host + "/category/PervTherapy"))
    itemlist.append(Item(channel=item.channel, title="GangbangCreampie " , action="lista", url=host + "/category/GangbangCreampie"))
    itemlist.append(Item(channel=item.channel, title="StepSiblings " , action="lista", url=host + "/category/StepSiblings"))
    itemlist.append(Item(channel=item.channel, title="FamilyXXX " , action="lista", url=host + "/category/FamilyXXX"))
    itemlist.append(Item(channel=item.channel, title="ExploitedCollegeGirls" , action="lista", url=host + "/category/ExploitedCollegeGirls"))
    itemlist.append(Item(channel=item.channel, title="PrivateCasting-X" , action="lista", url=host + "/category/PrivateCasting-X"))
    itemlist.append(Item(channel=item.channel, title="FakeTaxi" , action="lista", url=host + "/category/FakeTaxi"))
    itemlist.append(Item(channel=item.channel, title="TushyRaw" , action="lista", url=host + "/category/TushyRaw"))
    itemlist.append(Item(channel=item.channel, title="MyFamilyPies" , action="lista", url=host + "/category/MyFamilyPies"))
    return itemlist



def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s" % (host,texto)
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
    soup = create_soup(item.url)
    matches = soup.find('div', class_='thumbs-holder').find_all('div', class_='item')
    if "models" in item.url:
        matches.pop(0)
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img['src']
        cantidad = elem.find('span', class_='text')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='item-pagin is_last')
    if next_page:
        next_page = next_page.a['data-parameters'].replace(":", "=").split(";").replace("+from_albums", "")
        next_page = "?%s&%s" % (next_page[0], next_page[1])
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
    soup = create_soup(item.url)
    matches = soup.find('main', id='content').find_all("article", id=re.compile(r"^post-\d+"))
    for elem in matches:
        # parte = elem.find('h1', class_='entry-title')
        if not elem.find("img"):
            continue
        url = elem.a['href']
        title = elem.find('h2', class_='entry-title').text.strip()
        if "Siterip" in title or "manyvids" in title:
            title = "[COLOR red]%s[/COLOR]" %title
            
        thumbnail = elem.img['src']
        if "data:image" in thumbnail:
            thumbnail = elem.img['data-lazy-src']
        plot = ""
        itemlist.append(Item(channel = item.channel,action="findvideos", title=title, url=url, 
                                  thumbnail=thumbnail, fanart=thumbnail, plot=plot) )
    next_page = soup.find('a', class_='nextp')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel = item.channel,action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    soup = soup.find("strong", string=re.compile(r"^Download/stream:")).parent
    matches = soup.find_all('a')
    for elem in matches:
        url = elem['href']
        if not ".jpg" in url and not "ddl." in url and not "ddownload." in url and not "growngame." in url:
            itemlist.append(Item(channel = item.channel,action='play',title="%s ", contentTitle=item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist



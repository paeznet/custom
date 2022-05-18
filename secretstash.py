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
from channels import autoplay

# IDIOMAS = {'vo': 'VO'}
# list_language = list(IDIOMAS.values())
list_quality = ['default']
list_servers = []

host = 'https://secretstash.in'
url_api = host + "/api/v1/releases?Limit=20&Offset=0"


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=url_api))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="submenu"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="OnlyFans" , action="lista", url=url_api + "&Studio=OnlyFans"))
    itemlist.append(Item(channel=item.channel, title="X-Angels" , action="lista", url=url_api + "&Studio=X-Angels"))
    itemlist.append(Item(channel=item.channel, title="Tiny4K" , action="lista", url=url_api + "&Studio=Tiny4K"))
    itemlist.append(Item(channel=item.channel, title="Nubiles" , action="lista", url=url_api + "&Studio=Nubiles"))
    itemlist.append(Item(channel=item.channel, title="FTVGirls" , action="lista", url=url_api + "&Studio=FTVGirls"))
    itemlist.append(Item(channel=item.channel, title="MetArtX" , action="lista", url=url_api + "&Studio=MetArtX"))
    itemlist.append(Item(channel=item.channel, title="VivThomas" , action="lista", url=url_api + "&Studio=VivThomas"))
    itemlist.append(Item(channel=item.channel, title="NaughtyOffice" , action="lista", url=url_api + "&Studio=NaughtyOffice"))
    itemlist.append(Item(channel=item.channel, title="EvilAngel" , action="lista", url=url_api + "&Studio=EvilAngel"))
    itemlist.append(Item(channel=item.channel, title="FamilyStrokes" , action="lista", url=url_api + "&Studio=FamilyStrokes"))
    itemlist.append(Item(channel=item.channel, title="SexMex" , action="lista", url=url_api + "&Studio=SexMex"))
    itemlist.append(Item(channel=item.channel, title="ATK" , action="lista", url=url_api + "&Studio=ATK"))
    itemlist.append(Item(channel=item.channel, title="BrazzersExxtra" , action="lista", url=url_api + "&Studio=BrazzersExxtra"))
    itemlist.append(Item(channel=item.channel, title="RKPrime" , action="lista", url=url_api + "&Studio=RKPrime"))
    itemlist.append(Item(channel=item.channel, title="Private" , action="lista", url=url_api + "&Studio=Private"))
    itemlist.append(Item(channel=item.channel, title="Bang" , action="lista", url=url_api + "&Studio=Bang"))
    itemlist.append(Item(channel=item.channel, title="ClubSweethearts" , action="lista", url=url_api + "&Studio=ClubSweethearts"))
    itemlist.append(Item(channel=item.channel, title="SexArt" , action="lista", url=url_api + "&Studio=SexArt"))
    itemlist.append(Item(channel=item.channel, title="SisLovesMe" , action="lista", url=url_api + "&Studio=SisLovesMe"))
    itemlist.append(Item(channel=item.channel, title="BangBus" , action="lista", url=url_api + "&Studio=BangBus"))
    itemlist.append(Item(channel=item.channel, title="PlayboyPlus" , action="lista", url=url_api + "&Studio=PlayboyPlus"))
    itemlist.append(Item(channel=item.channel, title="MyPervyFamily " , action="lista", url=url_api + "&Studio=MyPervyFamily"))
    itemlist.append(Item(channel=item.channel, title="PutaLocura " , action="lista", url=url_api + "&Studio=PutaLocura"))
    itemlist.append(Item(channel=item.channel, title="JacquieEtMichelTV" , action="lista", url=url_api + "&Studio=JacquieEtMichelTV"))
    itemlist.append(Item(channel=item.channel, title="MySistersHotFriend " , action="lista", url=url_api + "&Studio=MySistersHotFriend"))
    itemlist.append(Item(channel=item.channel, title="PublicAgent  " , action="lista", url=url_api + "&Studio=PublicAgent"))
    itemlist.append(Item(channel=item.channel, title="CzechCasting  " , action="lista", url=url_api + "&Studio=CzechCasting"))
    itemlist.append(Item(channel=item.channel, title="MyDirtyMaid  " , action="lista", url=url_api + "&Studio=MyDirtyMaid"))
    itemlist.append(Item(channel=item.channel, title="CherryPimps " , action="lista", url=url_api + "&Studio=CherryPimps"))
    itemlist.append(Item(channel=item.channel, title="TeamSkeetSelects " , action="lista", url=url_api + "&Studio=TeamSkeetSelects"))
    itemlist.append(Item(channel=item.channel, title="NubileFilms  " , action="lista", url=url_api + "&Studio=NubileFilms"))
    itemlist.append(Item(channel=item.channel, title="Hegre " , action="lista", url=url_api + "&Studio=Hegre"))
    itemlist.append(Item(channel=item.channel, title="BlacksOnBlondes " , action="lista", url=url_api + "&Studio=BlacksOnBlondes"))
    itemlist.append(Item(channel=item.channel, title="MassageRooms" , action="lista", url=url_api + "&Studio=MassageRooms"))
    itemlist.append(Item(channel=item.channel, title="BlackedRaw " , action="lista", url=url_api + "&Studio=BlackedRaw "))
    itemlist.append(Item(channel=item.channel, title="MonstersOfCock " , action="lista", url=url_api + "&Studio=MonstersOfCock"))
    itemlist.append(Item(channel=item.channel, title="Blacked" , action="lista", url=url_api + "&Studio=Blacked"))
    itemlist.append(Item(channel=item.channel, title="SpyFam " , action="lista", url=url_api + "&Studio=SpyFam"))
    itemlist.append(Item(channel=item.channel, title="FamilySwap " , action="lista", url=url_api + "&Studio=FamilySwap"))
    itemlist.append(Item(channel=item.channel, title="BigTitsRoundAsses " , action="lista", url=url_api + "&Studio=BigTitsRoundAsses"))
    itemlist.append(Item(channel=item.channel, title="JapanHDV " , action="lista", url=url_api + "&Studio=JapanHDV"))
    itemlist.append(Item(channel=item.channel, title="GloryHoleSecrets " , action="lista", url=url_api + "&Studio=GloryHoleSecrets"))
    itemlist.append(Item(channel=item.channel, title="Joymii" , action="lista", url=url_api + "&Studio=Joymii"))
    itemlist.append(Item(channel=item.channel, title="PervsOnPatrol " , action="lista", url=url_api + "&Studio=PervsOnPatrol"))
    itemlist.append(Item(channel=item.channel, title="EdgeQueens " , action="lista", url=url_api + "&Studio=EdgeQueens"))
    itemlist.append(Item(channel=item.channel, title="Vixen " , action="lista", url=url_api + "&Studio=Vixen"))
    itemlist.append(Item(channel=item.channel, title="CastingCouch" , action="lista", url=url_api + "&Studio=CastingCouch"))
    itemlist.append(Item(channel=item.channel, title="FamilyHookups" , action="lista", url=url_api + "&Studio=FamilyHookups"))
    itemlist.append(Item(channel=item.channel, title="BangBros" , action="lista", url=url_api + "&Studio=BangBros"))
    itemlist.append(Item(channel=item.channel, title="ATKHairy " , action="lista", url=url_api + "&Studio=ATKHairy"))
    itemlist.append(Item(channel=item.channel, title="Anilos " , action="lista", url=url_api + "&Studio=Anilos"))
    itemlist.append(Item(channel=item.channel, title="BrattySis " , action="lista", url=url_api + "&Studio=BrattySis"))
    itemlist.append(Item(channel=item.channel, title="PervTherapy " , action="lista", url=url_api + "&Studio=PervTherapy"))
    itemlist.append(Item(channel=item.channel, title="GangbangCreampie " , action="lista", url=url_api + "&Studio=GangbangCreampie"))
    itemlist.append(Item(channel=item.channel, title="StepSiblings " , action="lista", url=url_api + "&Studio=StepSiblings"))
    itemlist.append(Item(channel=item.channel, title="FamilyXXX " , action="lista", url=url_api + "&Studio=FamilyXXX"))
    itemlist.append(Item(channel=item.channel, title="ExploitedCollegeGirls" , action="lista", url=url_api + "&Studio=ExploitedCollegeGirls"))
    itemlist.append(Item(channel=item.channel, title="PrivateCasting-X" , action="lista", url=url_api + "&Studio=PrivateCasting-X"))
    itemlist.append(Item(channel=item.channel, title="FakeTaxi" , action="lista", url=url_api + "&Studio=FakeTaxi"))
    itemlist.append(Item(channel=item.channel, title="TushyRaw" , action="lista", url=url_api + "&Studio=TushyRaw"))
    itemlist.append(Item(channel=item.channel, title="MyFamilyPies" , action="lista", url=url_api + "&Studio=MyFamilyPies"))
    return itemlist



def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s&Search=%s" % (url_api,texto)
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
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).json
    for Video in  data["Releases"]:
        title = Video["Name"]
        thumbnail =  Video["Covers"][0]["Img"]
        streams = Video["Streams"]
        canal = Video["Studio"]
        urls= []
        for elem in streams:
            urls.append(elem['URL'])
        url = ", ".join(urls)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title , url= url, thumbnail=thumbnail, 
                        fanart=thumbnail, plot=plot, contentTitle=title) )
    total= int(data["Count"])
    page = int(scrapertools.find_single_match(item.url,'&Offset=(\d+)'))
    next_page = (page+ 20)
    if next_page < total:
        next_page = re.sub(r"&Offset=\d+", "&Offset={0}".format(next_page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    urls = item.url.split(",")
    for url in urls:
        if not "ddl."in url:
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist


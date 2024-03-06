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

forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'livesoccer', 
             'host': config.get_setting("current_host", 'livesoccer', default=''), 
             'host_alt': ["https://sportl.ivesoccer.sx/"], 
             'host_black_list': ["https://2.ivesoccer.sx/", "https://1.ivesoccer.sx/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    # itemlist.append(Item(channel=item.channel, title="fastreams play" , action="play", url="https://fastreams.live/18.php"))
    itemlist.append(Item(channel=item.channel, title="Eventos de hoy" , action="lista", url=host + "index.php?"))
    itemlist.append(Item(channel=item.channel, title="Por Deporte" , action="categorias", url=host))
    # itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
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
    soup = create_soup(item.url)
    matches = soup.find('span', class_='hidden-md-down').find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text.strip()
        thumbnail = elem.img['src']
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
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
    streams = ""
    soup = create_soup(item.url)
    matches = soup.find_all('li', class_="itemhov")
    for elem in matches:
        videos = elem.find('div', class_='item-col-stream').a
        id = videos['open-this']
        id = "open_this_%s" %id
        texto = elem.find('div', class_='matchname')
        if texto.find('table'):
            partido = texto.find_all('td')
            for x , value in enumerate(partido):
                partido[x] = value.text.strip()
            title = ' '.join(partido)
            campeonato = texto.span.text
            title = "[COLOR cyan]%s[/COLOR] - %s" % (title,campeonato)
        else:
            title = texto.text.strip()
            campeonato = texto.span.text
            title = title.replace(campeonato, '')
            title = "[COLOR cyan]%s[/COLOR] - %s" % (title,campeonato)
        
        thumbnail = elem.img['src']
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        zonaH = -1  # Quitar una hora para que sea España
        time = elem.find('span', class_='gmt_m_time').text
        time = time.split()[0]
        time = time.split(':')
        time[0]= str(int(time[0])+zonaH)
        time = ':'.join(time)
        
        logger.debug(time)
        if videos.text.lower() == "live":
            title = "[COLOR green]%s[/COLOR] %s" % (time,title)
            streams = soup.find('li', id=id).find_all('div', class_='mytooltip')
        else:
            title = "[COLOR red]%s[/COLOR] %s" % (time,title)

        plot = ""
        if videos.text.lower() == "watch":
            action = "nolive"
        else:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=item.url,
                             fanart=thumbnail, thumbnail=thumbnail, id=id, time=time, plot=plot) )
    return itemlist


def nolive(item):
    from platformcode import config, logger, platformtools
    platformtools.dialog_ok("%s" %item.contentTitle, "Este evento no esta en directo. \nPrueba a las %s" %item.time)
    return

def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('li', id=item.id).find_all('div', class_='mytooltip')
    for elem in matches:
        title = elem.a.text.strip()
        url = elem.a['href']
        thumbnail = elem.img['src']
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        if not "t.me" in url:
            itemlist.append(Item(channel=item.channel, action="play", title= title, contentTitle = item.contentTitle, url=url,
                                 thumbnail=thumbnail))

    # itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=item.url))
    # itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist

kwargs = {'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False} 
# UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.105 Safari/537.36"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
# UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'


def play(item):
    logger.info()
    itemlist = []
    
    ####    FALLA REPRODUCCION 
    if "fastreams" in item.url:
        id = scrapertools.find_single_match(item.url, "(\d+).php")
        id = int(id)
        urlid = "https://windroses.live/"
        god = "%sman/gen.php?playerid=00%s" %(urlid, id)
        referer = 'https://ftmstreams.com/' 
        accept= 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        language = 'es-MX,es;q=0.8,en-US;q=0.5,en;q=0.3'
        encoding = 'gzip,deflate,br'
        used = "ftmstreams.click"
        # 'Accept': accept, 'Accept-Language': language, 'Accept-Encoding': encoding, 'Alt-Used': used, 'Sec-Fetch-Dest': 'iframe'
        headers={'Referer': referer, 'User-Agent':UA, 'Accept-Encoding': encoding, 'Alt-Used': used}
        data = httptools.downloadpage(god, headers=headers, **kwargs).data #, follow_redirects=False
        logger.debug("######################")
        logger.debug(data)
        url = scrapertools.find_single_match(data, 'source: window.atob\("([^"]+)"')
        import base64
        url = base64.b64decode(url).decode('utf-8')
        url += "|Referer=%s" % urlid

        # https://fastreams.live/18.php  https://ftmstreams.click/san/gen.php?playerid=0018  
        # source: window.atob("aHR0cHM6Ly9saXZlLWhscy13ZWItYWplLmdldGFqLm5ldC9BSkUvMDQubTN1OA==")

    if "s2watch" in item.url:
        # https://s2watch.link/flash20
        # https://viwlivehdplay.ru/mono.php?id=20
        
        id = scrapertools.find_single_match(item.url, "/flash(\d+)")
        god = "https://livehdplay.ru/mono.php?id=%s" %id
        accept= 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        headers = {'Referer': item.url, 'Accept': accept}
        data = httptools.downloadpage(god, headers=headers).data
        url = scrapertools.find_single_match(data, "source\:'([^']+)'")
        url += "|Referer=%s" % god
        # https://s2watch.link/flash10  
        # <iframe allowfullscreen="true" frameborder="0" height="100%" scrolling="no" src="https://livehdplay.ru/mono.php?id=10" width="100%"></iframe></div>
        # source:'https://websuit.webhd.ru/fls/cdn/mono10/playlist.m3u8'    
            # https://livehdplay.ru/mono.php?id=10
        # "coolrea.link",
        # "cdn1.link",
        # "cdn2.link",
        # "cdnssd.ru"
        # "smycdn.ru"
        # "istorm.live",
        # "lato.sx",
        # "onlive.sx",
        # "lavents.la",
        # "s2watch.link",
        # "virazo.sx",
        # "webplay.sx",
        # "zvision.link"
    ####    FALLA REPRODUCCION TIENE UNAS //


    if "barsarad7hd" in item.url:   
        god1 = create_soup(item.url + "/").iframe['src']
        id = scrapertools.find_single_match(god1, "/(\d+)")
        god = "https://redittsports.com/rs/tv%s.php" %id
        headers = {'Referer': item.url, 'Acept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}
        data = httptools.downloadpage(god, headers=headers).data
        url = scrapertools.find_single_match(data, "source\:'([^']+)'")
        url += "|Referer=%s" % "https://redittsports.com/"
    else:
        soup = create_soup(item.url).find('div', class_="player")
    
    if "smycdn" in item.url or "coolrea" in item.url:
        if soup.iframe:
            god = soup.iframe['src']
        else:
            dir = soup.find('script').string
            id = scrapertools.find_single_match(dir, "fid='([^']+)'")
            rep = soup.find('script', type='text/javascript')['src']
            rep = rep.replace(".js", "")
            god = "https:%s.php?player=desktop&live=%s" %(rep, id)
            headers = {'Referer': item.url}
            data = httptools.downloadpage(god, headers=headers).data
            letras = scrapertools.find_single_match(data, '("h".*?)\].join')
            url = letras.replace('\/', '/').replace('"', '').replace(',', '')
            url = url.replace('////', '//')
            url += "|Referer=%s" % god
    
    

    
    if "candlesouth" in god:
        from lib import jsunpack
        headers = {'Referer': item.url}
        data = httptools.downloadpage(god, headers=headers).data
        enc_data = scrapertools.find_single_match(data, ">(eval.*?)</script>")
        dec_data = jsunpack.unpack(enc_data)
        url = scrapertools.find_single_match(dec_data,'(?:file|src)="([^"]+)"')
        url += "|Referer=%s" % god
        # https://coolrea.link/flash10   <iframe src="https://candlesouth.net/embed/jwpz3ec0iqz"  
        # function(p, a, c, k, e, d)
    if "nobodywalked" in god:
        headers = {'Referer': item.url}
        data = httptools.downloadpage(god, headers=headers).data
        id,server = scrapertools.find_single_match(data, ',"player","([^"]+)",\{"([^"]+)"')
        url = "https://%s/hls/%s/live.m3u8" %(server, id)
        url += "|Referer=%s" % god
        logger.debug(id + " -- " +server)
    # itemlist.append(["[bitporno] %s" % "m3u", url])
    itemlist.append(Item(channel=item.channel, action="play", title= url, contentTitle = item.contentTitle, url=url, ignore_response_code=True))
     
    return itemlist

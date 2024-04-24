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

timeout = 30

# https://sportl.ivesoccer.sx/  https://2.ivesoccer.sx/  https://1.ivesoccer.sx/
# https://sporthd.me/  https://s2watch.ru/   https://liveon.sx/program

canonical = {
             'channel': 'livesoccer', 
             'host': config.get_setting("current_host", 'livesoccer', default=''), 
             'host_alt': ["https://sportl.ivesoccer.sx/"], 
             'host_black_list': ["https://2.ivesoccer.sx/", "https://1.ivesoccer.sx/"], 
             # 'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             # 'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    # itemlist.append(Item(channel=item.channel, title="fastreams play" , action="play", url="https://fastreams.live/18.php"))
    itemlist.append(Item(channel=item.channel, title="Eventos de hoy" , action="lista", url=host )) #+ "index.php?"
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
        data = httptools.downloadpage(url, canonical=canonical, timeout=timeout).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


# {\"matches\":[{\"_id\":\"6615ac7e79918449572b1d78\",\"slug\":\"fN95tWj11jYbr22ejjTnap-cf-monterrey-vs-inter-miami-cf\",\"league\":\"CONCACAF Champions Cup\",\"leagueImg\":\"https://s2watch.ru/images/CONCACAF Champions Cup.png\",\"sport\":\"Football\",\"sportSlug\":\"football\",\"team1\":\"CF Monterrey\",\"team1Img\":\"https://api.sofascore1.com/api/v1/team/1932/image\",\"team2\":\"Inter Miami CF\",\"team2Img\":\"https://api.sofascore1.com/api/v1/team/337602/image\",\"website\":\"sofascore.ro\",\"channels\":[],\"duration\":120,\"country\":\"North \u0026 Central America\",\"fullName\":\"CF Monterrey vs Inter Miami CF\",\"matchDate\":\"$D2024-04-11T00:00:00.000Z\",\"dateScraped\":\"$D2024-04-09T21:00:46.267Z\",\"timestampInMs\":1712802600000,\"additionalLinks\":[{\"name\":\"TUDN \",\"link\":\"https://smycdn.ru/flash30\",\"lang\":\"ES\"},{\"name\":\"TUDN \",\"link\":\"https://s2watch.link/flash30\",\"lang\":\"ES\"},{\"name\":\"TUDN \",\"link\":\"https://coolrea.link/flash30\",\"lang\":\"ES\"},{\"name\":\"Fox Sports 1 USA\",\"link\":\"https://smycdn.ru/flash31\",\"lang\":\"EN\"},{\"name\":\"Fox Sports 1 USA\",\"link\":\"https://s2watch.link/flash31\",\"lang\":\"EN\"},{\"name\":\"Fox Sports 1 USA\",\"link\":\"https://coolrea.link/flash31\",\"lang\":\"EN\"}],\"fsid\":12164004,\"venue\":\"Mexico Monterrey - Estadio BBVA Bancomer\",\"livetvtimestr\":null,\"sortOrder\":0},
# https://sporthd.me/api/trpc/mutual.getTopTeams,saves.getAllUserSaves,mutual.getFooterData,mutual.getAllChannels,mutual.getWebsiteConfig?batch=1&input=%7B%220%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%2C%221%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%2C%222%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%2C%223%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%2C%224%22%3A%7B%22json%22%3Anull%2C%22meta%22%3A%7B%22values%22%3A%5B%22undefined%22%5D%7D%7D%7D

# <div class="relative flex w-full flex-col gap-1">
    # <button class="flex items-center justify-center gap-4 rounded-2xl border-[1px] border-black/5 bg-transparent px-2 py-3 hover:cursor-pointer hover:bg-black/5 dark:border-white/5 dark:bg-[#1e1e1e] dark:hover:bg-white/5">
        # <div class="flex items-center gap-4" style="width:min(230px, 100%)">
            # <img class="h-[35px] w-[35px]" src="https://cdn.livesoccertv.com/tt/images/teams/new-zealand/logos/wellington-phoenix.png?q=65&amp;w=100"/><p class="text-sm">Wellington Phoenix</p>
        # </div>
        # <div class="animate-pulse h-[38px] w-[90px] rounded-full bg-black/5 dark:bg-white/5"></div>
        # <div class="flex items-center justify-end gap-4" style="width:min(230px, 100%)">
            # <p class="text-right text-sm">Melbourne Victory</p>
            # <img class="h-[35px] w-[35px]" src="https://cdn.livesoccertv.com/tt/images/teams/australia/logos/melbourne-victory.png?q=65&amp;w=100"/></div>
    # </button>
    # <div class="absolute -top-4 left-3 flex items-center gap-2 lg:left-2 lg:top-[13px]">
        # <button class="flex h-[30px] w-[30px] items-center justify-center rounded-full bg-neutral-100 text-neutral-600 hover:bg-neutral-200 disabled:cursor-not-allowed disabled:opacity-70 dark:bg-custom-bg-higlight dark:text-neutral-400 dark:hover:bg-neutral-800 lg:h-[40px] lg:w-[40px] lg:bg-transparent">
            # <svg class="lucide lucide-star h-4 w-4 lg:h-6 lg:w-6" fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                # <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            # </svg>
        # </button>
    # </div>
    # <button class="-top-4 right-3 hidden h-[30px] w-[30px] items-center justify-center rounded-full bg-neutral-100 text-neutral-600 hover:bg-neutral-200 disabled:cursor-not-allowed disabled:opacity-70 dark:bg-custom-bg-higlight dark:text-neutral-400 dark:hover:bg-neutral-800 lg:absolute lg:right-2 lg:top-[13px] lg:flex lg:h-[40px] lg:w-[40px] lg:bg-transparent" disabled="">
        # <svg class="lucide lucide-tv2 h-4 w-4 lg:h-6 lg:w-6" fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
            # <path d="M7 21h10"></path><rect height="14" rx="2" width="20" x="2" y="3"></rect>
        # </svg>
    # </button>
# </div>

def lista(item):
    logger.info()
    itemlist = []
    streams = ""
    data = httptools.downloadpage(item.url).data
    # logger.debug(data)
    
    soup = create_soup(item.url).find('div', class_='mt-4')
    # logger.debug(soup.find('div', class_='relative'))
    matches = soup.find_all('section')
    logger.debug(matches)
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
        ref = "https://websuit.onlinehdhls.ru/" # "https://viwlivehdplay.ru/"  "https://livehdplay.ru/"
        headers = {'Referer': ref, 'Accept': accept}
        m3u_data = httptools.downloadpage(url, headers=headers).data
        logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@")
        logger.debug(m3u_data)
        matches = scrapertools.find_single_match(m3u_data, 'TION=\d+x(\d+).*?\s(.*?)\s')
        if matches:
            for quality, url in matches:
                itemlist.append(["%s  %sp [bitporno]" % (filename, quality), url])
        #EXTM3U
        #EXT-X-STREAM-INF:AVERAGE-BANDWIDTH=520000,BANDWIDTH=650000,RESOLUTION=1024x576,FRAME-RATE=30.000,CODECS="avc1.4d401f,mp4a.40.2",CLOSED-CAPTIONS=NONE
        # tracks-v1a1/mono.m3u8
        
        url += "|Referer=%s" % ref
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

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
from lib import jsunpack

forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'sportsonline', 
             'host': config.get_setting("current_host", 'sportsonline', default=''), 
             'host_alt': ["https://sportsonline.si/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

# (?i)(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(.|\n)*?(\d{2}:\d{2}.*\n)+


def mainlist(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage("https://sportsonline.gl", canonical=canonical).data
    # url = httptools.downloadpage(host, follow_redirects=False).headers["location"]
    # patron = "(?i)(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(.|\n)*?(\d{2}:\d{2}.*\n)+"
    patron = "(?i)(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
    # matches =scrapertools.find_single_match(data, patron)
    matches = re.compile(patron,re.DOTALL).findall(data)
    lista1 = data.split(matches[0])
    lista2 = lista1[-1].split(matches[1])
    lista3 = lista2[-1].split(matches[2])
    # lista = scrapertools.find_single_match(data, "(matches[0].*?)matches[1]")
    # logger.debug(lista2[0])
    # logger.debug(lista3[0])
    # logger.debug(lista3[-1])
    patron = "(?i)(\d{2}:\d{2}.*?)\n"
    eventos = re.compile(patron,re.DOTALL).findall(lista2[0])
    langs = "(HD\d+ .*?)\n"
    idiomas =  re.compile(langs,re.DOTALL).findall(lista2[0])
    IDIOMAS = {"bra": "BRA", "pt": "PT"}
    # logger.debug(idiomas)
    for elem in idiomas:
        n= elem.split()
        lang = n[0].lower()
        n.pop(0)
        txt = '_'.join(n)
        IDIOMAS[lang] = txt
    itemlist.append(Item(channel=item.channel, title=matches[0]))
    for elem in eventos:
        event = elem.split("|")
        url = event[-1].strip()
        if "/bra/" in url: lang= "bra"
        elif "/pt/" in url: lang= "pt"
        else: lang= scrapertools.find_single_match(url, "(hd\d+).php")
        language = IDIOMAS.get(lang, lang)
        title = event[0].strip()
        txt = title.split()
        zonaH = 1  # Añadir una hora para que sea España
        time = txt[0].split(":")
        time[0]= str(int(time[0])+zonaH)
        txt[0] = ':'.join(time)
        
        title = ' '.join(txt)
        # time_gmt: str = '2022-10-01 00:00:00 GMT+0200'
        logger.debug(time)
        # import datetime
        # import pytz
        # from datetime import timezone
        # zonahoraria_utc = pytz.timezone('UTC')
        # logger.debug(zonahoraria_utc)
        # mi_fecha = datetime.datetime.strptime(time, '%H:%M')
        # logger.debug(datetime.datetime.now())
        itemlist.append(Item(channel=item.channel, action="findvideos", title="%s [COLOR cyan]%s[/COLOR]" %(title,language), language=language, contentTitle=title, url=url))
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
    matches = soup.find_all('a', class_='item')
    for elem in matches:
        url = elem['href']
        title = elem['title']
        if elem.find('span', class_='no-thumb'):
            thumbnail = ""
        else:
            thumbnail = elem.img['src']
        if "gif" in thumbnail:
            thumbnail = elem.img['data-src']
        if not thumbnail.startswith("https"):
            thumbnail = "https:%s" % thumbnail
        cantidad = elem.find('div', class_='videos')
        if cantidad:
            title = "%s (%s)" % (title,cantidad.text.strip())
        # url = urlparse.urljoin(item.url,url)
        # thumbnail = urlparse.urljoin(item.url,thumbnail)
        url += "?sort_by=post_date&from=01"
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('li', class_='next')
    if next_page and next_page.find('a'):
        next_page = next_page.a['data-parameters'].split(":")[-1]
        if "from_videos" in item.url:
            next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        else:
            next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
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
    data = httptools.downloadpage(item.url, canonical=canonical).data
    url =  scrapertools.find_single_match(data, "]")
    # logger.debug(data)
    
    soup = create_soup(item.url)
    url = soup.iframe['src']
    logger.debug(url)
    # matches = soup.find_all('div', class_=re.compile(r"^item-\d+"))
    # for elem in matches:
        # url = elem.a['href']
        # title = elem.a['title']
        # thumbnail = elem.img['src']
        # if "gif" in thumbnail:
            # thumbnail = elem.img['data-original']
        # if not thumbnail.startswith("https"):
            # thumbnail = "https:%s" % thumbnail
        # time = elem.find('div', class_='duration').text.strip()
        # quality = elem.find('span', class_='is-hd')
        # if quality:
            # title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        # else:
            # title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        # plot = ""
        # action = "play"
        # if logger.info() == False:
            # action = "findvideos"
        # itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             # fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    # next_page = soup.find('li', class_='next')
    # if next_page and next_page.find('a'):
        # next_page = next_page.a['data-parameters'].split(":")[-1]
        # if "from_videos" in item.url:
            # next_page = re.sub(r"&from_videos=\d+", "&from_videos={0}".format(next_page), item.url)
        # else:
            # next_page = re.sub(r"&from=\d+", "&from={0}".format(next_page), item.url)
        # itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist




# https://h9fm5c5g47vj8f4s.cdnministry.net:8443/hls/dm4f0c0bxcxxsau.m3u8?s=bdMbpeiiwC3gY2jHbouHbQ&e=1709135948
# https://h9fm5c5g47vj8f4s.cdnministry.net:8443/hls/dm4f0c0bxcxxsau-2949014340.ts
# https://h9fm5c5g47vj8f4s.cdnministry.net:8443/hls/dm4f0c0bxcxxsau-2953559340.ts

def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.iframe['src']
    # url += "|Referer=%s" %host
    
    # accept= 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
    # language = 'es-ES,es;q=0.9,en;q=0.8'
    # encoding = 'gzip,deflate,br'
    # used =  'r9m7epmwi5ey62v.harmquantity.net'
    # 'Accept': accept, 'Accept-Language': language, 'Accept-Encoding': encoding, 'Alt-Used': used, 'Sec-Fetch-Dest': 'iframe'
    # headers={'Referer': host, 'Accept-Encoding': encoding, 'Sec-Fetch-Dest': 'iframe'}

    # , 'Cookie': 'hf1=1'
    if url.startswith("//"):
        url1 = "https:%s" % url
    headers = {'Referer': host}
    data = httptools.downloadpage(url1, headers=headers, canonical=canonical).data
    enc_data = scrapertools.find_single_match(data, ">(eval.*?)</script>")
    dec_data = jsunpack.unpack(enc_data)
    matches = scrapertools.find_multiple_matches(dec_data, 'src="([^"]+)"')
    for url in matches:
        url += "|Referer=%s" %url1
        # itemlist.append(['.m3u', url])
        itemlist.append(Item(channel=item.channel, action="play", title= url, contentTitle = item.contentTitle, url=url, ignore_response_code=True))
    return itemlist




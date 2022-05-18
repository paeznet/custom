# -*- coding: utf-8 -*-
# -*- Channel Alfa Tools Set -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import re
import sys
import os

from concurrent import futures
from core import channeltools
from core import httptools
from core import jsontools
from core import scrapertools
from core.item import Item
from platformcode import config
from platformcode import logger
from platformcode import platformtools


if sys.version_info[0] >= 3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse



query = ""

if len(sys.argv) == 2 and not query:
    query = sys.argv[1]

toolset_folder = os.path.join(config.get_data_path(), 'toolset')
if not os.path.exists(toolset_folder):
    os.makedirs(toolset_folder, exist_ok=True)

filename = os.path.join(toolset_folder, 'themes_test.json')
error = os.path.join(toolset_folder, 'error.json')
# filename = "themes_test.json"
# error = "error.json"
theme = ""
themes_dict = dict()
error_dict = dict()

themes = {'toroflix': 'data-tggl="HdTop"',
          'toroplay': 'button id="searchsubmit" type="submit"',
          'torofilm': 'i id="sl-home" class="fa-search"',
          'twentytwelve': 'input type="text" value="" name="s" id="s"',
          'psyplay': 'div class="ml-item"',
          'ultimatube': '<div class="wpst-loading">',
          'dooplay': '<article id=[A-z0-9"-]+ class="item (?:movies|tvshows)"',
          'grid theme responsive': 'div class="home_post_cont post_box"',
          'goovie theme': 'article class="Item ItemCar"',
          'vizer': 'div class="lazy inner loadingBg"',
          'allcine': 'div class="short_content"',
          'sociallyviral': 'div class="featured-thumbnail"',
          'grifus': 'div class="box_item"',
          'smoothness': 'div class="thumb-ratio"',
          'movietp': 'class="movie-item clearfix tooltip',
          'rldev': 'template/RLDev/assets/css/app.css',
          'plusrex': 'class="item-pelicula pull-left"',
          'films': '<div class="card__cover">'}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


#
# elif len(sys.argv) == 2 or query:
#     print(bcolors.WARNING+"Debes crear primero el listado, usando solo:"+bcolors.ENDC+" \npython get_themes.py")
#     exit()


def get_hosts(query=None):
    matches = list()
    alfa_site = "https://extra.alfa-addon.com/api/channels/"

    channels_page = httptools.downloadpage(alfa_site, hide_infobox=True).json
    if query:
        matches = [(urlparse(query).netloc, query)]
    else:
        channels = channels_page["channels"]
        for ch in channels:
            if ch["active"]:
                matches.append((ch["id"], ch["host"]))

    return (query, matches)


def get_info_hosts(item):

    itemlist = list()

    status_values = {"dead": "- Muerto",
                     "not_tested": "- Sin Testear",
                     "not_fv": "- Posible error en Findvideos",
                     "not_pl": "- Posible error en Play",
                     "not_fv+error": "- Posible error en Findvideos\n- Otros errores",
                     "not_pl+error": "- Posible error en Play\n- Otros errores",
                     "ok+error": "- Sin Problemas importantes",
                     "ok": "Sin Problemas"
                     }
    status_colors = {"dead": "red",
                     "not_tested": "grey",
                     "not_fv": "yellow",
                     "not_pl": "yellow",
                     "not_fv+error": "brown",
                     "not_pl+error": "brown",
                     "ok+error": "cyan",
                     "ok": "green"
                     }
    alfa_site = "https://extra.alfa-addon.com/api/channels/"
    channels_data = httptools.downloadpage(alfa_site).json["channels"]

    for ch in channels_data:

        if ch["test_score"] in item.test_score or item.test_score == [6]:
            if item.test_score == [6]:
                if ch["active"]:
                    continue
            elif not ch["active"]:
                continue

            url_channel = ch["host"]
            thumb = ch["thumbnail"]
            title = "[COLOR {}][#][/COLOR] {}".format(
                status_colors.get(ch["status"], 'grey'),
                ch["name"].capitalize()
            )
            # title = ch["name"].capitalize()
            plot = status_values.get(ch["status"], "")
            if url_channel:
                plot = '[COLOR blue]URL: %s [/COLOR]\n\n%s' % (
                    url_channel, plot)

            itemlist.append(Item(channel=ch["id"], title=title, action="mainlist",
                                 plot=plot, thumbnail=thumb, channel_name=ch["name"],
                                 inactive=False))

    return itemlist


def verify(host, site):
    global theme
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}

    try:
        data = httptools.downloadpage(site.strip(), headers=headers,
                                      timeout=15, verify=False, hide_infobox=True).data
        data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', " ", data)

        if check_cloud(data, host, site):
            return ""

        theme = scrapertools.find_single_match(data, '/themes/([^/]+)/')

        logger.debug("Verificando: %s\n" % site)

        if not theme or not theme in themes.keys():
            for key, value in themes.items():
                bing = scrapertools.find_single_match(data, value)
                # print(bcolors.HEADER + bing + bcolors.ENDC+" site="+site)
                if bing:
                    theme = key
                    break

        if not theme:
            theme = "desconocido"

        logger.debug("Theme Detectado: %s\n" % theme)
        return (theme, host, site)

    except:
        e = sys.exc_info()[0]
        error_dict.setdefault(host, []).append((site, str(e)))
        # pass


def start(query=None):
    query, matches = get_hosts(query=query)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        c_results = [executor.submit(verify, host_url, site_url)
                     for host_url, site_url in matches]
        for f in futures.as_completed(c_results):
            if f.result():
                themes_dict.setdefault(f.result()[0].lower(), []).append(
                    (f.result()[1], f.result()[2]))

    if not query:
        save_json()
        save_json(error, error_dict)
    # else:
    #     return read_json()

    matches_len = len(matches)
    msg = "Utilizando %s canal%s" % (matches_len, 'es' if matches_len > 1 else '')

    platformtools.dialog_notification("Identificador de Themes", msg)


def save_json(filename=filename, themes_dict=themes_dict):
    with open(filename, "w") as f:
        f.write(jsontools.dump(themes_dict))


def read_json():

    itemlist = list()

    with open(filename, "r") as f:
        themes_json = jsontools.load(f.read())
    theme_sites = themes_json.get(theme.lower(), "No hay coincidencias")

    logger.debug("%s canales utilizan el Theme [%s]:" % (
        len(theme_sites), theme))
    itemlist.append(Item(channel="toolset", title="Detectado Theme: %s" %
                    theme.capitalize(), action=""))
    try:
        for match in theme_sites:
            ch_param = channeltools.get_channel_parameters(match[0].lower())
            itemlist.append(Item(channel=match[0].lower(), title=ch_param["title"], action="mainlist",
                                 thumbnail=ch_param["thumbnail"], plot=match[1]))
            logger.debug("- URL: %s [%s]" % (match[1], match[0].capitalize()))
    except:
        logger.debug(
            "CHANGOS!!! no existen coincidencias para el theme: [%s] A trabajar" % theme)
        platformtools.dialog_ok("Identificador de themes",
                                "No existen coincidencias para el theme: %s" % theme)
        return

    return itemlist


def read_json_bug():
    with open(error, "r") as f:
        error_json = jsontools.load(f.read())

    # logger.debug ("%s canales utilizan el Theme [%s]:\n" % (len(theme_sites), theme))
    try:
        for key in error_json:
            value = error_json.get(key, '')
            logger.debug(
                "-[%s] URL: %s | ERROR: (%s)") % (key.capitalize(), value[0][0], value[0][1])
    except:
        logger.debug("No hay errores o algo peor")


def check_cloud(data, host, site):
    pat1 = 'cpo.src = "/cdn-cgi/challenge-platform'
    pat2 = '<title>You are being redirected...</title>'

    if pat1 in data:
        info = "Cloudflare Detected"
        error_dict.setdefault(host, []).append((site, info))
        return True
    elif pat2 in data:
        info = "CloudProxy Detected"
        error_dict.setdefault(host, []).append((site, info))
        return True

    return False


def theme_identifier(item):
    logger.info()
    global query
    global theme
    query = platformtools.dialog_input(
        "", "Url o theme a verificar [vacio para actualizar listado]:")

    if os.path.exists(filename) and not query:
        answer = platformtools.dialog_yesno(
            "Alfa Tools Set", "Actualizar el listado de themes?")
        if answer:
            os.remove(filename)
            start()
        else:
            platformtools.dialog_notification(
                "No se actualizara el listado de themes..", sound=False)
            if query:
                start(query)

    elif query and not os.path.exists(filename):
        logger.debug(bcolors.WARNING + "Debes crear primero el listado, usando solo:" +
                     bcolors.ENDC + " \npython get_themes.py")
        exit()
    # Para query normal, con url
    elif query.startswith('http'):
        start(query)
        return read_json()
    # Para consultar los errores
    elif query == 'error':
        read_json_bug()
    # Para consultar themes
    elif query:
        theme = query
        return read_json()
    else:
        start()

# def go_channel(item):
#     logger.info()
#     #Para reactivar canales desactivados(config), pregunta si se quiere reactivar,
#     # Si, lo reactiva y muestra canal, no, se queda como estaba
#     if item.inactive:
#         channel_name = "[COLOR gold]%s[/COLOR]" % item.channel_name
#         answer = platformtools.dialog_yesno("Alfa Tools Set",
#                                             "¿Realmente desea reactivar %s?" % channel_name.capitalize())
#         if answer:
#                 config.set_setting("active", True, channel=item.channel_name)
#                 item.inactive = False
#                 item.action = ''
#                 return go_channel(item)
#         else:
#             return
#     else:
#         item.title = ''
#         item.plot = ''
#         item.tumbanail = ''
#         item.action = 'mainlist'
#         item.channel = item.channel_name


#     return [item]


def mainlist(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Identificador de Themes", action="theme_identifier",
                         plot="Identifica canales con temas visuales similares para reutilizar codigo"))

    itemlist.append(Item(channel=item.channel, title="Estado de los canales", action="menu_channels_check",
                         plot="Da información del estado de los canales testeados \ny los agrupa para facilitar los fixes"))

    return itemlist


def menu_channels_check(item):
    logger.info()

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title="Atención Urgente", action="get_info_hosts",
                         text_color="red", test_score=[0, 1],
                         plot="Canales que dan fallo critico (fail)"))

    itemlist.append(Item(channel=item.channel, title="Precisan Atención", action="get_info_hosts",
                         text_color="yellow", test_score=[2, 3],
                         plot="Canales que dan varios errores"))

    itemlist.append(Item(channel=item.channel, title="No reviste gravedad", action="get_info_hosts",
                         text_color="turquoise", test_score=[4],
                         plot="Canales que dan algún error leve"))

    itemlist.append(Item(channel=item.channel, title="Vegetal", action="get_info_hosts",
                         test_score=[6],
                         plot="Canales desactivados"))

    itemlist.append(Item(channel=item.channel, title="En Buen Estado", action="get_info_hosts",
                         text_color="green", test_score=[5],
                         plot="Canales que no muestran errores"))

    return itemlist

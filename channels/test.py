# -*- coding: utf-8 -*-
# ------------------------------------------------------------

# TESTING DE CANALES Y SERVIDORES
# ===============================

# Este canal virtual permite la ejecución de tests para comprobar el funcionamiento de canales y servidores.
# Los resultados de los tests se pueden enviar a la web extra.alfa-addon.com para consultarlos más cómodamente.
# ¡¡¡¡No publicar este canal, ya que contiene los datos de acceso a la web!!!!

# Test del funcionamiento de un canal:
# - Desde el mainlist() del canal, recorre recursivamente todos los enlaces
# - Para cada enlace se apunta en un log lo que devuelve
# - Si se encuentran enlaces parecidos solo se analiza el primero de ellos
#   (Por ejemplo, enlaces a cada género, a cada letra del abecedario)
#   (Parecido equivale a que llama al mismo action pasándole una url diferente)
#   (Los parecidos se descartan en cualquier submenú pero no en el menú principal)
# - La información del test se graba en un fichero de log en .kodi/userdata/addon_data/plugin.video.alfa/test_logs/channels/
# - El proceso para algunos canales con muchos enlaces puede tardar un rato.

# Test del funcionamiento de un servidor:
# - Se buscan enlaces al servidor entre todos los logs de los canales
# - Si se encuentran demasiados (parámetro configurable) se hace un muestreo aleatorio
# - Para cada uno de ellos se intenta resolver con el play del canal o llamando a servertools si no hay play
# - La información del test se graba en un fichero de log en .kodi/userdata/addon_data/plugin.video.alfa/test_logs/servers/

# A modo de ejemplo, duración de un testeo masivo:
# v2.5.19 : 
# 151 canales activos => 1841 segundos (30 minutos)
# 105 servidores activos => 434 segundos (7 minutos)
# Subir todos los tests a la web => 3 minutos (+/- 6,2 mb, 256 ficheros)
#
# v2.6.3 : 
# 117 canales (sin adultos) => 2330 segundos (39 minutos)
# 107 servidores => 676 segundos (11 minutos)
#
# v2.7.5 : 
# 118 canales (sin adultos) => 2218 segundos (37 minutos)
#  28 canales (adultos) => 206 segundos (3 minutos)
#  85 servidores => 409 segundos (7 minutos)

# ------------------------------------------------------------

from __future__ import division
from builtins import map
from builtins import range
from past.utils import old_div
#from builtins import str
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import os, time, random, xbmc, inspect

from core.item import Item
from core import httptools
from core import filetools
from core import scrapertools
from core import servertools
from core import channeltools

from platformcode import config, logger
from platformcode import platformtools

import channelselector

VFS = True
if VFS:
    LF = '\r\n'
    LF_ = '\n'
else:
    LF = '\n'
    LF_ = '\r\n'


# ============================
# AJUSTES PARA TODO EL PROCESO
# ============================

# Desactivar las llamadas a tmdb ya que no son necesarias para los tests
# ----------------------------------------------------------------------
from core import tmdb
def disabled_set_infoLabels(source, seekTmdb=True, idioma_busqueda='es', **kwargs):
    return 0
def disabled_set_infoLabels_itemlist(item_list, seekTmdb=False, idioma_busqueda='es', **kwargs):
    return 0
def disabled_set_infoLabels_item(item, seekTmdb=True, idioma_busqueda='es', lock=None, **kwargs):
    return 0
tmdb.set_infoLabels = disabled_set_infoLabels
tmdb.set_infoLabels_itemlist = disabled_set_infoLabels_itemlist
tmdb.set_infoLabels_item = disabled_set_infoLabels_item

# Desactivar las llamadas a autoplay para evitar que salten los vídeos
# --------------------------------------------------------------------
from channels import autoplay
def disabled_autoplay_init(channel, list_servers, list_quality, reset=False):
    return False
def disabled_autoplay_show_option(channel, itemlist, text_color='yellow', thumbnail=None, fanart=None):
    return False
def disabled_autoplay_start(itemlist, item):
    return False
autoplay.init = disabled_autoplay_init
autoplay.show_option = disabled_autoplay_show_option
autoplay.start = disabled_autoplay_start

# Desactivar las llamadas a logger para evitar que llene el log
# --------------------------------------------------------------------
def disable_logger_info(texto="", force=False, max_size=0):
    #function = inspect.currentframe().f_back.f_back.f_code.co_name
    txt = logger.get_caller(logger.encode_log(texto))
    if '[' not in txt or '[run]' in txt or 'URL: ' in texto or 'Response code: ' in texto:
        max_size = 200
    if max_size:
        if PY3:
            xbmc.log(logger.get_caller(str(logger.encode_log(texto)[:max_size])), xbmc.LOGINFO)
        else:
            xbmc.log(logger.get_caller(str(logger.encode_log(texto)[:max_size])), xbmc.LOGNOTICE)
    return False
def disable_logger_debug(texto="", force=False, max_size=200):
    if max_size:
        texto = "    [" + logger.get_caller() + "] " + logger.encode_log(texto)
        if PY3:
            xbmc.log("######## DEBUG #########", xbmc.LOGINFO)
            xbmc.log(str(texto)[:max_size], xbmc.LOGINFO)
        else:
            xbmc.log("######## DEBUG #########", xbmc.LOGNOTICE)
            xbmc.log(str(texto)[:max_size], xbmc.LOGNOTICE)
    return False
def disable_logger_error(texto="", force=False, max_size=200):
    if max_size:
        texto = "    [" + logger.get_caller() + "] " + logger.encode_log(texto)
        xbmc.log("######## ERROR #########", xbmc.LOGERROR)
        xbmc.log(str(texto)[:max_size], xbmc.LOGERROR)
    return False
logger.info = disable_logger_info
logger.debug = disable_logger_debug
logger.error = disable_logger_error

# Desactivar las llamadas a Generictools.get_torrent_size para evitar que salten los vídeos
# --------------------------------------------------------------------
from lib import generictools
def disabled_get_torrent_size(url, **kwargs):
    torrent_params = {}
    torrent_params['url'] = url
    torrent_params['torrents_path'] = ''
    torrent_params['local_torr'] = 'TEST'
    torrent_params['lookup'] = True
    torrent_params['force'] = False
    torrent_params['data_torrent'] = False
    torrent_params['subtitles'] = False
    torrent_params['file_list'] = False
    torrent_params['channel'] = ''
    torrent_params['torrent_alt'] = ''
    torrent_params['find_alt_link_option'] = False
    torrent_params['find_alt_link_result_save'] = []
    torrent_params['domain_alt'] = ''
    torrent_params['size'] = 'TEST'
    torrent_params['torrent_f'] = {}
    torrent_params['files'] = {}
    torrent_params['subtitles_list'] = []
    torrent_params['cached'] = False
    torrent_params['size_lista'] = []
    torrent_params['size_amount'] = []
    torrent_params['torrent_cached_list'] = []
    torrent_params['time_elapsed'] = 0
    torrent_params['find_alt_link_result'] = []
    torrent_params['find_alt_link_found'] = 0
    torrent_params['find_alt_link_next'] = 0
    
    return torrent_params

generictools.get_torrent_size = disabled_get_torrent_size

# Limitar tiempo de descarga y desactivar debug
# ---------------------------------------------
httptools.HTTPTOOLS_DEFAULT_DOWNLOAD_TIMEOUT = 10
httptools.TEST_ON_AIR = True

# ~ logger.log_enable(False)


# ====================
# PARÁMETROS GENERALES
# ====================

# Para descartar algunos action que no hay que analizar en los tests de canales
# (por ejemplo, menús que piden interacción del usuario como las búsquedas, o acciones como añadir a videoteca, abrir la configuración, ...)
ACTION_DISCARD = [
    '', 'add_pelicula_to_library', 'add_serie_to_library', 'download_all_episodes', 
    'search', 'local_search', 'filtro', 'autoplay_config', 'actualizar_titulos', 'year',
    'infosinopsis', 'configuracion', 'settingCanal', 'setting_channel', 'openconfig', 'settings',
    'anno', 'genero_rec', 'calidad_rec', 'categories', 'login', 'logout', 'items_usuario', 
    'set_status__', 'get_page_num'
]

# Para descartar algunos canales que no hay que analizar en los tests de canales
CHANNEL_DISCARD = [
    'tvmoviedb', 'ecarteleratrailers', 'help' # pq no contienen videos
    #,'seriesmeme' , 'gmobi', # pq no respondían cuando lo he probado
    #,'kbagi' ,'plusdede', 'pordede'  # pq requieren usuario/clave
]

# Para descartar algunos servidores que no hay que analizar en los tests de servidores
SERVER_DISCARD = [
    #'cloudy', 'gvideo', 'userscloud' # pq tardan demasiado en responder o no lo hacen!
]

# Número máximo de enlaces findvideos a comprobar para cada canal en los tests de canales
MAX_MUESTRAS_FINDVIDEOS = 10

# Número máximo de enlaces a comprobar para cada servidor en los tests de servidores
MAX_LINKS_PLAY = 5


# Carpetas dónde se guardan los logs
# ----------------------------------
RUTA_TEST_LOGS = filetools.join(config.get_data_path(), 'test_logs')
if not filetools.exists(RUTA_TEST_LOGS): filetools.mkdir(RUTA_TEST_LOGS)

RUTA_CHANNEL_LOGS = filetools.join(RUTA_TEST_LOGS, 'channels')
if not filetools.exists(RUTA_CHANNEL_LOGS): filetools.mkdir(RUTA_CHANNEL_LOGS)

RUTA_SERVER_LOGS = filetools.join(RUTA_TEST_LOGS, 'servers')
if not filetools.exists(RUTA_SERVER_LOGS): filetools.mkdir(RUTA_SERVER_LOGS)


# ====================
# NAVEGACIÓN
# ====================

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(action='', title="[COLOR blue]INFO TESTS[/COLOR]", plot="El proceso habitual para un testeo completo es: 1-Eliminar todos logs. 2-Testear canales (todos). 3-Testear servidores (todos). 4-Subir a la web (todo).\n\nNota: Al subir los tests a la web, se hace el upload de todos los logs existentes en local. Por esta razón es preferible eliminar los anteriores antes de testear, así sólo se subirán los nuevos que se realizen.\n\nNota: Para poder testear servidores es necesario que antes se haya hecho el testeo de canales ya que es de allí de dónde se extraen ejemplos para comprobar.")) 

    itemlist.append(item.clone(action='', title="[COLOR yellow]Logs de tests en local :[/COLOR]")) 
    itemlist.append(Item(channel=item.channel, action="clean_local_logs_all", title="Eliminar todos los logs locales"))
    itemlist.append(Item(channel=item.channel, action="clean_local_logs_channels", title="Eliminar logs de canales locales"))
    itemlist.append(Item(channel=item.channel, action="clean_local_logs_servers", title="Eliminar logs de servidores locales"))

    itemlist.append(item.clone(action='', title="[COLOR yellow]Ejecución de tests :[/COLOR]")) 
    itemlist.append(Item(channel=item.channel, action="channel_test_selected", title="Testear canales ..."))
    itemlist.append(Item(channel=item.channel, action="server_test_selected", title="Testear servidores ..."))

    itemlist.append(item.clone(action='', title="[COLOR yellow]Subir tests a la web :[/COLOR]")) 
    itemlist.append(Item(channel=item.channel, action="upload_web_tests_all", title="Upload all tests to web"))
    itemlist.append(Item(channel=item.channel, action="upload_web_tests_channels", title="Upload channel tests to web"))
    itemlist.append(Item(channel=item.channel, action="upload_web_tests_servers", title="Upload server tests to web"))

    return itemlist


# Eliminar logs anteriores
# ------------------------
def clean_local_logs_all(item):
    clean_local_logs_channels(item)
    clean_local_logs_servers(item)
    return False

def clean_local_logs_channels(item):
    list(map( os.unlink, (filetools.join(RUTA_CHANNEL_LOGS,f) for f in filetools.listdir(RUTA_CHANNEL_LOGS)) ))
    platformtools.dialog_notification('Eliminar tests', 'channel tests deleted')
    return False

def clean_local_logs_servers(item):
    list(map( os.unlink, (filetools.join(RUTA_SERVER_LOGS,f) for f in filetools.listdir(RUTA_SERVER_LOGS)) ))
    platformtools.dialog_notification('Eliminar tests', 'server tests deleted')
    return False


# Subir los tests a la web
# ------------------------
def upload_web_tests_all(item):
    upload_web_tests_channels(item)
    upload_web_tests_servers(item)
    return False

def upload_web_tests_channels(item):
    upload_web_tests(RUTA_CHANNEL_LOGS, 'channels')
    return False
    
def upload_web_tests_servers(item):
    upload_web_tests(RUTA_SERVER_LOGS, 'servers')
    return False


# Seleccionar y testear canales/servidores
# ----------------------------------------
def channel_test_selected(item):
    selected = select_items('canales')
    if len(selected) > 0:
        test_selected_channels(selected)
    return False

def server_test_selected(item):
    selected = select_items('servidores')
    if len(selected) > 0:
        test_selected_servers(selected)
    return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ====================
# DIÁLOGO DE SELECCIÓN
# ====================

# Seleccionar los canales/servidores a testear
# --------------------------------------------
def select_items(item_type):
    incluir_adultos = True
    
    kodi_INCLUDED = ''
    kodi_EXCLUDED = ''
    alfa_channels = filetools.join(config.get_runtime_path(), 'channels')
    if filetools.exists(filetools.join(alfa_channels, 'kodi_INCLUDED.txt')):
        kodi_INCLUDED = filetools.read(filetools.join(alfa_channels, 'kodi_INCLUDED.txt'))
    if filetools.exists(filetools.join(alfa_channels, 'kodi_EXCLUDED.txt')):
        kodi_EXCLUDED = filetools.read(filetools.join(alfa_channels, 'kodi_EXCLUDED.txt'))

    # Cargar lista de opciones
    # ------------------------
    lista = []
    if item_type == 'canales':
        # filterchannels('all') tiene en cuenta la configuración del usuario! (adult, language y si está el canal deshabilitado)
        # filterchannels('allchannelstatus') tiene en cuenta la configuración del usuario! (adult y language, pero no si el canal está deshabilitado)
        # filterchannels('all_channels') tiene en cuenta todos los canales, sin tener en cuenta la configuración
        channels_list = channelselector.filterchannels('all_channels')
        for channel in channels_list:
            if kodi_INCLUDED and channel.channel not in kodi_INCLUDED: continue
            if kodi_EXCLUDED and channel.channel in kodi_EXCLUDED: continue
            
            channel_parameters = channeltools.get_channel_parameters(channel.channel)
            
            lbl = '[B]'+channel_parameters['title']+'[/B]'
            lbl += ' %s' % channel_parameters['language']
            lbl += ' %s' % channel_parameters['categories']
            lista.append({'id': channel.channel, 'label': lbl, 'language': channel_parameters['language'], 'categories': channel_parameters['categories']})

    else:
        server_list = servertools.get_servers_list()
        for i, server in enumerate(sorted(server_list.keys())):
            server_parameters = server_list[server]
            if not server_parameters.get('active', False):
                continue
            lista.append({'id': server, 'label': server_parameters['name']})


    # Diálogo para pre-seleccionar (todos, ninguno, cast, lat, categorías, ...)
    # ----------------------------
    if item_type == 'canales':
        preselecciones = ['Ninguno', 'Todos', 'Castellano', 'Latino', 'movie', 'tvshow', 'documentary', 'anime', 'vos', 'direct', 'torrent']
        if incluir_adultos: preselecciones.append('adult')
    else:
        preselecciones = ['Ninguno', 'Todos']

    ret = platformtools.dialog_select("Pre-selección de %s" % item_type, preselecciones)
    if ret == -1: return []

    preselect = []
    if preselecciones[ret] == 'Ninguno': preselect = []
    elif preselecciones[ret] == 'Todos': preselect = list(range(len(lista)))
    elif preselecciones[ret] in ['Castellano','Latino']:
        busca = 'cast' if preselecciones[ret] == 'Castellano' else 'lat'
        preselect = []
        for i, elem in enumerate(lista):
            if busca in elem['language'] or '*' in elem['language']:
                preselect.append(i)
    else:
        busca = preselecciones[ret]
        preselect = []
        for i, elem in enumerate(lista):
            if busca in elem['categories']:
                preselect.append(i)


    # Diálogo para seleccionar
    # ------------------------
    ret = platformtools.dialog_multiselect("Escoger %s a testear:" % item_type, [c['label'] for c in lista], preselect=preselect)
    seleccionados = [] if ret == None else [lista[i]['id'] for i in ret]

    return seleccionados


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ====================
# TESTS DE CANALES
# ====================

# Testeos masivos en bucle
# ------------------------
def test_selected_channels(channels_list):
    total_time = 0
    for ind, channel in enumerate(channels_list):
        total_time += test_channel(channel, ind+1, len(channels_list))

    platformtools.dialog_ok('Alfa', 'Tests finalizados en %d canales' % len(channels_list), 'Duración : %d segundos' % total_time)

# Test de un canal
# ----------------
def test_channel(channel, ind=1, total=1):
    global test_filelog, test_canal, muestras_findvideos, TEST_ACTIVE
    TEST_ACTIVE = True
    
    logfilename = filetools.join(RUTA_CHANNEL_LOGS, '%s.txt' % channel)
    test_filelog = filetools.file_open(logfilename, 'w', vfs=VFS)
    
    t_ini = time.time()
    acumula_log_text('INICIO TEST %s versión %s' % (time.strftime("%Y-%m-%d"), config.__settings__.getAddonInfo('version')))

    progreso = platformtools.dialog_progress('Testeando %s - [%s/%s] ' % (channel, ind, total), 'Iniciando tests')

    if channel in CHANNEL_DISCARD:
        acumula_log_text(LF + 'Este canal se ha descartado para testear')
    else:
        try:
            muestras_findvideos = [] # para guardar algunos ejemplos de llamadas a findvideos y comprobar si resuelven

            test_canal = __import__('channels.' + channel, fromlist=[''])
            itemlist = test_canal.mainlist(Item(channel=channel, title=channel))

            acumula_log_text(LF + 'Seguimiento desde mainlist:')
            n = len(itemlist)
            for cnt, it in enumerate(itemlist):
                progreso.update(old_div(((cnt + 1) * 100), n), 'Seguimiento desde mainlist...')

                if it.channel == channel and it.action not in ACTION_DISCARD:
                    analyze_item(it, level=0)
                else:
                    acumula_log_item(LF + '*', '(not analyzed)', it)

            acumula_log_text(LF + 'Comprobación de findvideos:')
            n = len(muestras_findvideos)
            done = []
            for cnt, it in enumerate(muestras_findvideos):
                progreso.update(old_div(((cnt + 1) * 100), n), 'Comprobando findvideos...')

                if it.url not in done and len(done) < MAX_MUESTRAS_FINDVIDEOS: # máximo de 10 y sin repetir
                    done.append(it.url)
                    analyze_findvideos(it)

        except:
            acumula_log_text(LF + 'Error en el test')

    t_fin = time.time()
    elapsed = (t_fin - t_ini)
    acumula_log_text(LF + 'FINAL TEST duración: %f segundos.' % elapsed)

    test_filelog.close()

    platformtools.dialog_notification('Log generado', '%s.txt' % channel)

    return elapsed


# Seguimiento recursivo de enlaces
# --------------------------------
def analyze_item(item, level=0):
    global muestras_findvideos

    hay_findvideos = 0
    actions_done = []
    salto = LF if level == 0 else ''

    try:
        func = getattr(test_canal, item.action)
        itemlist = func(item.clone())
        acumula_log_item(salto+'*' * (level + 1), '(%d enlaces)' % len(itemlist), item)
    except:
        itemlist = []
        acumula_log_item(salto+'*' * (level + 1), '(ERROR!)', item)
    
    for it in itemlist:

        if it.action == 'findvideos' or it.action == 'play':
            acumula_log_item_ampliado('*' * (level + 2), '', it)
            if hay_findvideos < 2: muestras_findvideos.append(it.clone()) # apuntar los dos primeros para comprobar después
            hay_findvideos += 1

        # hay_findvideos == 0: Si ya hay un findvideos en la lista, no entrar a analizar siguientes items (paginaciones, etc)
        # it.channel == item.channel : solo analizar llamadas al propio canal
        # it.action != item.action : para descartar posibles paginaciones si no se han encontrado findvideos
        elif hay_findvideos == 0 and it.channel == item.channel and it.action not in ACTION_DISCARD and it.action != item.action:
            if it.action in actions_done: # no repetir mismas actions (ej: por cada letra, por cada género)
                acumula_log_item('*' * (level + 2), '(not analyzed, similar)', it)
            else:
                if level < 10:
                    analyze_item(it, level + 1)
                else:
                    acumula_log_item('*' * (level + 2), '(not analyzed, too far)', it)
                actions_done.append(it.action)

        else:
            acumula_log_item('*' * (level + 2), '(not analyzed)', it)


# Comprobación de muestras findvideos
# -----------------------------------
def analyze_findvideos(item):
    try:
        itemlist = test_canal.findvideos(item)
    except:
        itemlist = servertools.find_video_items(item)

    acumula_log_item_ampliado(LF + '*', '(%d enlaces)' % len(itemlist), item)

    for it in itemlist:
        acumula_log_findvideos('**', it)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ====================
# TESTS DE SERVIDORES
# ====================

# Testeos masivos en bucle
# ------------------------
def test_selected_servers(servers_list):
    total_time = 0
    for ind, server in enumerate(servers_list):
        total_time += test_server(server, ind+1, len(servers_list))

    platformtools.dialog_ok ('Alfa', 'Tests finalizados en %d servidores' % len(servers_list), 'Duración %d segundos' % total_time)


# Test de un servidor
# -------------------
def test_server(server, ind=1, total=1):
    global test_filelog

    logfilename = filetools.join(RUTA_SERVER_LOGS, '%s.txt' % server)
    test_filelog = filetools.file_open(logfilename, 'w', vfs=VFS)
    
    t_ini = time.time()
    acumula_log_text('INICIO TEST %s versión %s' % (time.strftime("%Y-%m-%d"), config.__settings__.getAddonInfo('version')))

    if server in SERVER_DISCARD:
        acumula_log_text(LF + 'Este servidor se ha descartado para testear')
    else:
        do_test_server(server, ind, total)

    t_fin = time.time()
    elapsed= (t_fin - t_ini)
    acumula_log_text(LF + 'FINAL TEST duración: %f segundos.' % elapsed)

    test_filelog.close()

    platformtools.dialog_notification('Log generado', '%s.txt' % server)

    return elapsed


# Realiza el test del servidor
# ----------------------------
def do_test_server(server, ind, total):
    n_ok = 0; n_ko = 0
    
    itemlist = obtener_plays_a_testear(server)

    progreso = platformtools.dialog_progress('Testeando %s - [%s/%s] ' % (server, ind, total), 'Iniciando tests')
    cnt = 0
    n = len(itemlist)

    for enlace, canal in itemlist:
        cnt += 1
        progreso.update(old_div((cnt * 100), n), 'Comprobando enlaces...')

        acumula_log_text(LF + 'Play en el canal %s con url %s' % (canal, enlace))
        try:
            test_canal = __import__('channels.' + canal, fromlist=[''])
            itemlist = test_canal.play(Item(channel=canal, server=server, url=enlace, title='Test'))

            # Play should return a list of playable URLS
            if len(itemlist) > 0 and isinstance(itemlist[0], Item):
                vitem = itemlist[0]
            # Permitir varias calidades desde play en el canal
            elif len(itemlist) > 0 and isinstance(itemlist[0], list):
                vitem = Item(channel=canal, server=server, url=enlace, title='Test')
                vitem.video_urls = itemlist
            # If not, shows user an error message
            else:
                vitem = None
        except:
            vitem = Item(channel=canal, server=server, url=enlace, title='Test')

        if vitem == None:
            acumula_log_text('* No hay enlaces a videos!')
            n_ko += 1

        elif vitem.video_urls:
            acumula_log_text('* %d enlaces encontrados:' % len(vitem.video_urls))
            acumula_log_video_urls(vitem.video_urls)
            n_ok += 1

        else:
            video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(vitem.server, vitem.url)
            if puedes:
                acumula_log_text('* %d enlaces resueltos:' % len(video_urls))
                acumula_log_video_urls(video_urls)
                n_ok += 1
            else:
                acumula_log_text('* No se puede, motivo : %s' % limpiar_campo(motivo))
                n_ko += 1

    acumula_log_text(LF + 'Total de enlaces verificados: %d  OK: %d  FAIL: %d' % (n_ok+n_ko, n_ok, n_ko))


# Busca enlaces a un servidor en los logs de canales
# --------------------------------------------------
def obtener_plays_a_testear(server):
    itemlist = []
    canales = []

    cerca = ' ~ play ~ %s ~ (.*?) ~ (.*?) ~ ' % server
    files = [f for f in filetools.listdir(RUTA_CHANNEL_LOGS) if filetools.isfile(filetools.join(RUTA_CHANNEL_LOGS, f))]
    for f in files:
        #with open(filetools.join(RUTA_CHANNEL_LOGS, f), 'r') as fit: data=fit.read(); fit.close()
        data = filetools.read(filetools.join(RUTA_CHANNEL_LOGS, f), vfs=VFS)
        canal = f.replace('.txt','')

        matches = scrapertools.find_multiple_matches(data, cerca)
        if len(matches) > 0:
            canales.append(canal)
            for titulo, enlace in matches:
                if enlace not in [it[0] for it in itemlist]:
                    itemlist.append([enlace, canal])
            

    acumula_log_text(LF + 'Hay %d canales con enlaces a %s : %s' % (len(canales), server, sorted(canales)))

    if len(itemlist) > MAX_LINKS_PLAY: # reducir el número de enlaces aleatoriamente
        acumula_log_text(LF + 'Obtenidos %d enlaces a %s. Muestreo de %d aleatorios:' % (len(itemlist), server, MAX_LINKS_PLAY))
        random.shuffle(itemlist)
        return itemlist[:MAX_LINKS_PLAY]
    else:
        acumula_log_text(LF + 'Obtenidos %d enlaces a %s. Muestreo de todos ellos:' % (len(itemlist), server))
        return itemlist



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ====================
# FUNCIONES AUXILIARES
# ====================

# Para ir grabando en el fichero de log en curso
# ----------------------------------------------

# Genérico para canales y servidores
def acumula_log_text(txt):
    test_filelog.write(txt+LF)

# Para canales
def acumula_log_item(nivel, notas, it):
    infos = [nivel, notas, it.channel, it.action, limpiar_campo(it.title), limpiar_campo(it.url)]
    test_filelog.write(' ~ '.join(infos)+LF)

def acumula_log_item_ampliado(nivel, notas, it):
    infos = [nivel, notas, it.channel, it.action, limpiar_campo(it.title), limpiar_campo(it.url), limpiar_campo(it.language), limpiar_campo(it.quality)]
    test_filelog.write(' ~ '.join(infos)+LF)

def acumula_log_findvideos(nivel, it):
    infos = [nivel, it.channel, it.action, it.server, limpiar_campo(it.title), limpiar_campo(it.url), limpiar_campo(it.language), limpiar_campo(it.quality)]
    test_filelog.write(' ~ '.join(infos)+LF)

# Para servidores
def acumula_log_video_urls(video_urls):
    ret = ''
    for v in video_urls:
        ret += ' ~ '.join(limpiar_campo(x) for x in v) + LF
    test_filelog.write(ret)


# Para corregir titles demasiado largos y urls mal resueltas con html
# -------------------------------------------------------------------
def limpiar_campo(txt):
    txt = str(txt).replace(LF, ' ')
    txt = str(txt).replace(LF_, ' ')
    txt = txt.replace(' ~ ', ' - ') # por si el texto contiene el separador de campos usado
    tam = len(txt)
    if tam > 300: txt = txt[:300] + ' (... continua %d caracteres más)' % (tam - 300)
    return txt



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# =========================
# FUNCIONES COMPLEMENTARIAS
# =========================

# Subir los logs al ftp de la web y procesarlos
# ---------------------------------------------

def upload_web_tests(ruta, destino):
    import ftplib

    # Parámetros ftp y update web
    # ---------------------------
    ftp_host = '1a.ncomputers.org'
    ftp_user = 'luispp2006_extra1'
    ftp_pass = 'pdcLnw@LHHA2'
    ftp_folder = '/web/data/test_logs/%s/' % destino

    url_update  = 'https://extra.alfa-addon.com/updates/index.php?op=%s_tests' % destino
    url_headers = {'Cookie': 'alfapalbal7=1'}
    url_post = 'login=alfa&passw=4nT7J@3r'

    # Subir ficheros por ftp
    # ----------------------
    session = ftplib.FTP(ftp_host, ftp_user, ftp_pass)

    files = [f for f in filetools.listdir(ruta) if filetools.isfile(filetools.join(ruta, f))]
    for f in files:
        fit = open(filetools.join(ruta, f),'rb')
        session.storbinary('STOR '+ftp_folder+f, fit)
        fit.close()

    session.quit()
    
    # Provocar update en la web para procesar los tests
    # -------------------------------------------------
    data = httptools.downloadpage(url_update, headers=url_headers, post=url_post, cookies=False).data


    platformtools.dialog_notification('Web Upload', '%s tests updated' % destino)


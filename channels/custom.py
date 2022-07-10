# -*- coding: utf-8 -*-
# ------------------------------------------------------------

# CANAL PERSONALIZADO
# ===================

# ¡¡¡¡IMPORTANTE!!!!
# AL GENERAR el custom.py para testers dejar solo uno de los UPDATE_LOGIN
# ****¡y borrar los de nivel superior!****
# Y para los testers sería viable eliminar el enlace a los tests dentro de mainlist

from platformcode import config, logger
from platformcode import platformtools
from core.item import Item
from core import httptools
from core import jsontools
from core import downloadtools
from core import ziptools
from core import filetools
import time
import traceback
import re
import os
import sys

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    unicode = str
    unichr = chr
    long = int
from past.utils import old_div


URL_ADDON_UPDATES = 'https://extra.alfa-addon.com/addon_updates/'

UPDATE_HEADERS = {'user': 'al-admin-fa', 'pass': 'justworking7'}

# UPDATE_LOGIN = 'user=kodi&passw=alfa'
# UPDATE_LOGIN = 'user=koditester&passw=betatester'
# UPDATE_LOGIN = 'user=al-admin-fa&passw=justworking7'

ADDON_RUNTIME_PATH = config.get_runtime_path()
ADDON_DATA_PATH = config.get_data_path()
ADDON_CURRENT_VERSION = {
    'version_full': config.get_addon_version(),
    'version': config.get_addon_version(with_fix=False),
    'fix': config.get_addon_version_fix(),
}
last_custom_json_path = filetools.join(ADDON_DATA_PATH, 'last_custom.json')

patron_domain = '(?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?([\w|\-]+\.\w+)(?:\/|\?|$)'
patron_host = '((?:http.*\:)?\/\/(?:.*ww[^\.]*)?\.?(?:[^\.]+\.)?[\w|\-]+\.\w+)(?:\/|\?|$)'


def get_installed_fixes(return_updated=True):
    """
    Carga datos de custom fixes instalados por el usuario
    @param return_updated: Si retornar un booleano que informe un cambio de versión
    @type return_updated: bool
    @return: Los fixes instalados en un dict + un booleano que informe cambio de versión
    @rtype: tuple(dict, bool) | dict
    """
    version_update = False
    lastcustom_default = {
        'installed_fixes': {},
        'version': '0.0.0',
        'zbase64': ''
    }
    lastcustom = lastcustom_default

    try:
        if filetools.exists(last_custom_json_path):
            lastcustom.update(jsontools.load(
                filetools.read(last_custom_json_path)))
            logger.info(lastcustom)

            # Si hubo un cambio de versión del addon, limpiamos la lista de custom fixes instalados
            if lastcustom['version'] != ADDON_CURRENT_VERSION['version']:
                version_update = True

                for key, fix in list(lastcustom['installed_fixes'].items()):
                    if not fix.get('persistent'):
                        # Esto es innecesario (uninstall) dado que el punto
                        # de los fixes no persistentes es que se eliminen entre
                        # cambios de versión, sin embargo, si no se eliminan,
                        # habría que eliminarlos a mano desde aquí
                        # uninstall(key=key)
                        del lastcustom['installed_fixes'][key]
                        del lastcustom[key]

                filetools.write(last_custom_json_path,
                                jsontools.dump(lastcustom))

    except Exception:
        filetools.remove(last_custom_json_path)
        logger.info('¡Error al cargar custom json! Lo borramos')
        logger.error(traceback.format_exc())

    return lastcustom, version_update if return_updated else lastcustom


lastcustom, version_update = get_installed_fixes()


def mainlist(item):
    """Menú principal"""
    logger.info()

    itemlist = []
    
    # Enlace a los tests si existe channels/test.py
    # ---------------------------------------------
    if filetools.exists(filetools.join(ADDON_RUNTIME_PATH, "channels/test.py")):
        plot = 'Realiza tests a canales y servidores %s' % ADDON_CURRENT_VERSION['version_full']
        itemlist.append(
            Item(
                title='Testear canales y servidores ...',
                channel="test",
                plot=plot,
                action="mainlist",
                viewType="files"
            )
        )

    # Enlace para verificar quick-fixes
    # ---------------------------------
    plot = 'Llama al actualizador para verificar los quick-fixes en este momento %s' % ADDON_CURRENT_VERSION['version_full']
    itemlist.append(
        Item(
            action="check_quickfixes",
            channel=item.channel,
            plot=plot,
            title='Verificar quick-fixes'
        )
    )

    itemlist.append(
        Item(
            action='submenu',
            channel=item.channel,
            title='Otras Utilidades',
            viewType=item.viewType
        )
    )

    # Lista de descargas
    # ------------------
    plot = ''.join(['Los siguientes módulos con [COLOR cyan][#][/COLOR] deberían estar TODOS descargados y actualizados.\n',
                    '    Las descargas se realizan tanto en las carpetas estándar de Alfa como en las carpetas ',
                    '[B]./userdata/ addon_data/ plugin.video.alfa/ [COLOR yellow]custom_code[/COLOR][/B] (si es [COLOR cyan][#][/COLOR]).\n',
                    '    Custom_code es una réplica de las carpetas estándar de Alfa, y se vuelcan sobre éstas ',
                    'después de cada actualización de Alfa.\n',
                    '    Custom_code puede almacenar cualquier tipo de archivo, bien sean particulares del usuario ',
                    'o módulos alternativos a los estándares de Alfa.'
                    ])
    itemlist.append(
        item.clone(
            title="[COLOR yellow]Descargas disponibles:[/COLOR]",
            plot=plot,
            folder=False
        )
    )

    available_fixes = get_addon_updates()

    if not available_fixes:
        itemlist.append(item.clone(
            title="No hay ninguna descarga extra disponible"))

    else:
        for fix in available_fixes:
            title = fix['title']

            # ¿Es el fix persistente?
            if fix['persistent']:
                persistent = True
                title = "[COLOR cyan][#][/COLOR] {}".format(title)
            else:
                persistent = False

            # Aplicamos colores a notas de estado
            if not fix['id'] in lastcustom:
                title += ' [COLOR grey][-no instalado-][/COLOR]'
                install_status = 'not_installed'
            else:
                if fix['updated'] != lastcustom[fix['id']]:
                    title += ' [COLOR yellow][-no actualizado-][/COLOR]'
                    install_status = 'not_updated'
                else:
                    title += ' [COLOR limegreen][-ok-][/COLOR]'
                    install_status = 'installed'

            context = [{
                'action': 'uninstall',
                'channel': 'custom',
                'title': 'Desinstalar fix'
            }] if install_status != 'not_installed' else []

            title += ' [COLOR cyan]({})[/COLOR]'.format(fix['allowed_users'])
            plot = '[I][COLOR yellow]'
            plot += 'Creado por {}'.format(fix['author'])
            plot += ', actualizado por {}'.format(
                fix['coauthors']) if fix['coauthors'] else ''
            plot += '[/COLOR][/I]'
            plot += '\n\n{}'.format(fix['description'])
            plot += '\nFicheros:'

            for fil in fix['files']:
                plot += '\n{}/{}'.format(fil[0], fil[1])

            itemlist.append(
                Item(
                    action="install",
                    channel=item.channel,
                    context=context,
                    fix_title=fix['title'],
                    id=fix['id'],
                    persistent=persistent,
                    plot=plot,
                    title=title,
                    updated=fix['updated'],
                    url=fix['download_url']
                )
            )

    return itemlist


def submenu(item):
    logger.info()

    itemlist = []

    # Enlace a los tests si existe channels/test.py
    # ---------------------------------------------
    if filetools.exists(filetools.join(ADDON_RUNTIME_PATH, "channels/test.py")):
        plot = 'Realiza tests a canales y servidores %s' % ADDON_CURRENT_VERSION['version_full']
        itemlist.append(
            Item(
                title='Testear canales y servidores ...',
                channel="test",
                plot=plot,
                action="mainlist",
                viewType="files"
            )
        )

    # Enlace para verificar quick-fixes
    # ---------------------------------
    plot = 'Llama al actualizador para verificar los quick-fixes en este momento %s' % ADDON_CURRENT_VERSION['version_full']
    itemlist.append(
        Item(
            action="check_quickfixes",
            channel=item.channel,
            plot=plot,
            title='Verificar quick-fixes'
        )
    )

    # Enlace para verificar el estado del "host" de los canales NO adultos
    # --------------------------------------------------------------------
    plot = 'Muestra en el log la lista de canales (NO adultos) cuyo "host" no responde'
    itemlist.append(
        Item(
            title='Listar Canales que no responden (NO adultos)',
            channel=item.channel,
            action="channel_host_verification",
            adult=False, 
            plot=plot
        )
    )

    # Enlace para verificar el estado del "host" de los canales, CON Adultos
    # ----------------------------------------------------------------------
    plot = 'Muestra en el log la lista de canales cuyo (CON adultos) "host" no responde'
    itemlist.append(
        Item(
            title='Listar Canales que no responden, CON Adultos',
            channel=item.channel,
            action="channel_host_verification",
            adult=True, 
            plot=plot
        )
    )

    # Enlace para mostrar las variables de Entorno
    # --------------------------------------------
    plot = 'Muestra las principales variables del sistema, Kodi y Alfa, y las guarda en el log'
    itemlist.append(
        Item(
            title='Mostrar Variables de Entorno',
            channel=item.channel,
            action="envtal_variables",
            plot=plot
        )
    )

    # Enlace para mostrar las variables Proxy
    # --------------------------------------------
    plot = 'Muestra las principales variables y tablas de Proxytools, y las guarda en el log'
    itemlist.append(
        Item(
            title='Mostrar Variables Proxy',
            channel=item.channel,
            action="proxy_variables",
            plot=plot
        )
    )
    
    # Enlace para validar servidores del ProxyWeb 'croxyproxy.com'
    # ------------------------------------------------------------
    plot = 'Valida los servidores del ProxyWeb "croxyproxy.com"'
    itemlist.append(
        Item(
            title='Valida los servidores del ProxyWeb "croxyproxy.com"',
            channel=item.channel,
            action="verify_croxyproxy",
            plot=plot
        )
    )

    # Enlaces para reinicar el servico de Proxies
    # -------------------------------------------
    plot = ''.join(['Reinicia Proxytools y realiza una búsqueda de direcciones proxy de cada tipo ',
                    'hasta que encuentra una buena, y para.'])
    itemlist.append(
        Item(
            title='Reiniciar Servicio Proxy',
            channel=item.channel,
            action="proxy_init",
            extra=False,
            plot=plot
        )
    )
    plot = ''.join([
        'Reinicia Proxytools y realiza una búsqueda TOTAL de direcciones proxy de cada tipo. ',
        'Revisa tanto las direcciónes que tiene en los pools como las que obtiene de webs especializadas. ',
        'El proceso puede tardar varios minutos. \n\n',
        '    El objetivo final de este proceso es copiar desde el log las nuevas tablas de direcciones ',
        'proxy a sus correpondientes en [B]./core/proxytools_source.py[/B], y así actualizarlo con ',
        'nuevas direcciones verificadas actualmente. \n\n',
        '    Después se ofusca ./core/proxytools_source.py y se sube [B]./core/proxytools.py[/B]'
    ])
    itemlist.append(
        Item(
            title='Reiniciar Servicio Proxy, Test de todas direcciones',
            channel=item.channel,
            action="proxy_init",
            extra=True,
            plot=plot
        )
    )

    # Enlaces para ofuscar los servicos de Proxytools y Alfaresolver
    # --------------------------------------------------------------
    plot = 'Ofusca Proxytools con la utilidad ./lib/proteccion_proxytools.py y deja el resultado en ./core'
    itemlist.append(
        Item(
            title='Ofuscar Proxytools',
            channel=item.channel,
            action="proxytools_ofuscar",
            plot=plot
        )
    )
    plot = 'Ofusca Alfaresolver con la utilidad lib/proteccion_alfaresolver.py y deja el resultado en ./lib'
    itemlist.append(
        Item(
            title='Ofuscar Alfaresolver',
            channel=item.channel,
            action="alfaresolver_ofuscar",
            plot=plot
        )
    )

    if config.get_system_platform() == "android":
        # Descarga, Instala y ejecuta/actualiza Alfa Assistant
        # ----------------------------------------------------
        plot = 'Descarga, Instala y ejecuta Alfa Assistant'
        itemlist.append(
            Item(
                title='Descarga, Instala y ejecuta Alfa Assistant',
                update=False,
                channel=item.channel,
                action="assistant_install",
                plot=plot
            )
        )

        plot = 'Actualiza Alfa Assistant'
        itemlist.append(
            Item(
                title='Actualiza Alfa Assistant',
                update=True,
                channel=item.channel,
                action="assistant_install",
                plot=plot
            )
        )
    else:
        # Descarga y copia Alfa Assistant al servidor remoto FTP o SMB
        # ------------------------------------------------------------
        plot = "".join(['Descarga y copia Alfa Assistant al servidor remoto FTP o SMB \n\n',
                        'Formato de la url: ftp://user:password@192.168.1.250:21/'])
        itemlist.append(
            Item(
                title='Descarga y copia Alfa Assistant al servidor remoto FTP o SMB',
                update=False,
                channel=item.channel,
                action="assistant_install",
                plot=plot
            )
        )

        plot = "".join(['Actualiza APK de Alfa Assistant al servidor remoto FTP o SMB \n\n',
                        'Formato de la url: ftp://user:password@192.168.1.250:21/'])
        itemlist.append(
            Item(
                title='Actualiza APK de Alfa Assistant al servidor remoto FTP o SMB',
                update=True,
                channel=item.channel,
                action="assistant_install",
                plot=plot
            )
        )

    # Enlace para Desofuscar un string
    # --------------------------------
    plot = ''.join(['Desofusca un string o archivo copiado a la variable [COLOR yellow]zbase64[/COLOR] del archivo ',
                    '[B]./userdata/ addon_data/ plugin.video.alfa/ [COLOR yellow]last_custom.json[/COLOR][/B]. \n\n',
                    'Esta operación la realiza hasta 10 veces sobre el resultado obtenido, hasta encontrar ',
                    'la string totalmente desofuscada.  El resultado de las iteraciones lo va escribiendo en el log. \n\n',
                    'Además de una string se puede poner el path de un .py encriptado (Alfaresolver, Proxytools) ',
                    'para ver como queda la encriptación, o el path de un .pyc/.pyo para descompilarlo. ',
                    'Instalar [COLOR yellow]Uncompyle6 o Pycdc[/COLOR] para descompilar'])
    itemlist.append(
        Item(
            title='Desofuscar .pyo/.pyc y string en Base64 (last_custom.json)',
            channel=item.channel,
            action="base64_desofuscar",
            plot=plot
        )
    )

    # Ofuscar el json de funciones llamadas desde menú de Ajustes
    # -----------------------------------------------------------
    plot = 'Ofuscar el json de funciones llamadas desde menú de Ajustes'
    itemlist.append(
        Item(
            title='Ofuscar el json de funciones llamadas desde menú de Ajustes',
            channel=item.channel,
            action="funciones_ofuscar",
            plot=plot
        )
    )

    # Enlace para testar Filesystems con XbmcVFS de Kodi
    # --------------------------------------------------
    plot = 'Comprueba la funcionalidad de un Filesystems con XbmcVFS de Kodi y guarda los resultados en el log'
    itemlist.append(
        Item(
            title='Testing XbmcVFS',
            channel=item.channel,
            action="testing_xbmcvfs",
            plot=plot
        )
    )
    return itemlist


def get_addon_updates():
    """Devuelve las descargas disponibles en la web"""
    logger.info()
    try:
        return httptools.downloadpage(URL_ADDON_UPDATES, headers=UPDATE_HEADERS, cookies=False).json
    except Exception:
        logger.info('¡Error al comprobar actualizaciones del addon!')
        logger.error(traceback.format_exc())
        return []


def install(item):
    """Descarga un custom fix determinado (item.id) y lo extrae sobre el directorio del add-on"""
    logger.info()

    try:
        # Descargar ZIP del fix
        # -------------------------------------
        localfilename = filetools.join(ADDON_DATA_PATH, 'temp_updates.zip')

        if filetools.exists(localfilename):
            filetools.remove(localfilename)

        downloadtools.downloadfile(
            item.url, localfilename, title="Descargando fix")

        # Hacemos un respaldo
        # -------------------
        import zipfile
        unzipper = zipfile.ZipFile(localfilename, 'r')
        files = unzipper.namelist()
        unzipper.close()
        del unzipper

        # Hacemos respaldo solo si no hay ya uno
        if lastcustom['installed_fixes'].get(item.id):
            fix = lastcustom['installed_fixes'][item.id]
            backup = fix.get('backup', False)
            backup_zip_filename = fix.get('backup_path', '')
            backup_zip_version = fix.get('backup_version', '0.0.0')
        else:
            backup = False
            backup_zip_folder = filetools.join(ADDON_DATA_PATH, "backups")
            backup_zip_filename = ''
            backup_zip_version = '0.0.0'
            existing_files = []

            for file in files:
                file = file[1:] if str(file).startswith("/") else file
                addon_file = filetools.join(ADDON_RUNTIME_PATH, file)

                if filetools.exists(addon_file):
                    existing_files.append(addon_file)

            if existing_files:
                backup = True
                backup_zip_filename = filetools.join(
                    backup_zip_folder, "{}.zip".format(item.id))

                fix_addon_version = lastcustom['installed_fixes'].get(
                    item.id, {}).get('version')

                # TODO: Si se cambia de versión y se quiere obtener un respaldo de la
                # última versión de x fichero que ha sido parchado con un custom fix
                # ¡se estaría respaldando el fichero del fix y no el de la nueva versión!
                # Hay que implementar el sistema de respaldo en custom code, posiblemente
                # ponerlo allá y llamarlo aquí

                # Creamos el ZIP SOLO si no existe aún
                if not filetools.exists(backup_zip_filename):
                    if not filetools.exists(backup_zip_folder):
                        os.makedirs(backup_zip_folder)

                    try:
                        backup_zip = zipfile.ZipFile(backup_zip_filename, 'w')

                        for file in existing_files:
                            backup_zip.write(file, file.replace(
                                ADDON_RUNTIME_PATH, ""))

                        backup_zip.close()
                        backup_zip_version = ADDON_CURRENT_VERSION['version_full']

                    except Exception:
                        logger.error("¡ERROR al crear el respaldo!")
                        logger.info(traceback.format_exc())

        # Descomprimir zip dentro del addon y de Custom_code (si aplica)
        # --------------------------------------------------------------
        try:
            unzipper = ziptools.ziptools()
            unzipper.extract(localfilename, ADDON_RUNTIME_PATH)
            if item.persistent:
                unzipper.extract(localfilename, filetools.join(
                    ADDON_DATA_PATH, 'custom_code'))
        except Exception:
            import xbmc
            xbmc.executebuiltin('Extract("{}", "{}")'.format(localfilename,
                                                             ADDON_RUNTIME_PATH))
            if item.persistent:
                xbmc.executebuiltin('Extract("{}", "{}")'.format(localfilename,
                                                                 filetools.join(ADDON_RUNTIME_PATH, 'custom_code')))
            time.sleep(1)

        # Borrar el zip descargado
        # ------------------------
        filetools.remove(localfilename)

        # Guardar información del fix instalado
        # -------------------------------------
        lastcustom[item.id] = item.updated
        lastcustom['installed_fixes'][item.id] = {
            'backup': backup,
            'backup_path': backup_zip_filename,
            'backup_version': backup_zip_version,
            'description': item.plot,
            'files': files,
            'persistent': item.persistent,
            'title': item.fix_title,
            'updated': item.updated,
        }

        filetools.write(last_custom_json_path, jsontools.dump(lastcustom))

        msg_title = 'Instalación de fix correcta'
        msg = "{} instalado[CR]Id: {}".format(
            item.fix_title, item.id)
    except Exception:
        msg_title = 'Error instalando fix'
        msg = "Error al instalar {}[CR]Id: {}".format(
            item.title, item.id)
        logger.error(traceback.format_exc())

    platformtools.dialog_ok(msg_title, msg)
    platformtools.itemlist_refresh()


# TODO: Implementar "sanidad" de archivos en custom_code.
# De esta manera, antes de modificar cualquier archivo en el addon,
# se realizaría una copia de seguridad automáticamente,
# permitiendo que el usuario "restaure" archivos que haya
# modificado en cualquier momento, con la posbilidad de eliminar
# las modificaciones permanentemente, es decir, borrarlas de
# tanto del addon como de custom_code, si así quisieran.
def uninstall(item=None, key=None):
    """Desinstala un fix instalado y restaura los archivos originales (si aplica)"""
    # TODO Habría que guardar copias de los originales antes de instalar para poder hacerlo...
    # De momento si se quieren eliminar todos los fixes, reinstalar la última versión del addon.
    logger.info()
    progress = platformtools.dialog_progress(
        "Desinstalando fix",
        "Desinstalando fix {}, por favor espere".format(item.id))

    try:
        # Descargar ZIP del fix
        # -------------------------------------
        if item.id in list(lastcustom['installed_fixes'].keys()):
            fix = lastcustom['installed_fixes'][item.id]

            # Borramos archivos del fix
            # -------------------------
            for file in fix['files']:
                runtime_file = filetools.join(ADDON_RUNTIME_PATH, file)
                filetools.remove(runtime_file)

            # Borramos de custom code (si aplica)
            # -----------------------------------
            if fix['persistent']:
                for file in fix['files']:
                    persistent_file = filetools.join(
                        ADDON_DATA_PATH, 'custom_code', file)
                    filetools.remove(persistent_file)

            # Restauramos el respaldo (si hay)
            # --------------------------------
            if fix['backup']:
                backup_zip_filename = fix['backup_path']

                try:
                    unzipper = ziptools.ziptools()
                    unzipper.extract(backup_zip_filename, ADDON_RUNTIME_PATH)

                except Exception:
                    import xbmc
                    xbmc.executebuiltin('Extract("{}", "{}")'.format(backup_zip_filename,
                                                                     ADDON_RUNTIME_PATH))
                    time.sleep(1)

                # Borramos el zip de respaldo
                # ---------------------------
                filetools.remove(backup_zip_filename)

            # Borramos la información del fix
            # -------------------------------
            del lastcustom[item.id]
            del lastcustom['installed_fixes'][item.id]

            filetools.write(last_custom_json_path,
                            jsontools.dump(lastcustom))

            msg_title = 'Desinstalación de fix correcta'
            msg = "{} ha sido desinstalado[CR]Id: {}".format(
                item.fix_title, item.id)
            progress.close()
    except Exception:
        msg_title = 'Error desinstalando fix'
        msg = "Error al intentar desinstalar {}[CR]Id: {}".format(
            item.title, item.id)
        progress.close()
        logger.error(traceback.format_exc())

    platformtools.dialog_ok(msg_title, msg)
    platformtools.itemlist_refresh()


def check_quickfixes(item):
    """Verificar quick-fixes a petición"""
    logger.info()

    from platformcode import updater
    return updater.check_addon_updates(verbose=True)


def channel_host_verification(item):
    """Muestra en el log la lista de canales cuyo "host" no responde"""
    logger.info()
    import xbmc
    from channels.test import select_items
    from core import scrapertools, channeltools
    from lib.generictools import js2py_conversion
    
    channels_tested = 0
    channels_no_host = 0
    channels_no_canonical = 0
    channels_new_host = 0
    channels_no_response = 0
    channels_failed = []
    canonical = {}

    channels_list_total = select_items('canales')
    channels_list = []
    for channel in channels_list_total:
        if not item.adult and channeltools.is_adult(channel): continue
        channels_list += [channel]
    n = len(channels_list)
    
    if channels_list:
        xbmc.log('### Verificando Host de %s canales' % len(channels_list), xbmc.LOGERROR)
        progreso = platformtools.dialog_progress('Verificando Host de %s canales' % len(channels_list), 'Iniciando tests')
        for cnt, channel in enumerate(channels_list):
            canonical_dict = ' - Canonical INACTIVE'
            CF = False
            CF_test = False
            patterns = []
            channel_c = ''
            host_alt = []
            host_black_list = []
            status = ''
            channels_tested += 1
            try:
                obj = __import__('channels.%s' % channel, fromlist=["channels.%s" % channel])
                channel_host = ''
                if obj.host and isinstance(obj.host, str):
                    channel_host = obj.host
                else:
                    channels_no_host += 1
                    channels_failed += [channel.capitalize()]
                    xbmc.log('*** Canal sin varible Host: %s' % channel, xbmc.LOGERROR)
                    progreso.update(old_div(((cnt + 1) * 100), n), 'Verificando canal %s: %s - Estado: NO HOST' \
                            % (channels_tested, channel.upper()))
                    if progreso.iscanceled(): break
                    continue
            except:
                channels_no_host += 1
                channels_failed += [channel.capitalize()]
                xbmc.log('*** Canal sin varible Host: %s' % channel, xbmc.LOGERROR)
                progreso.update(old_div(((cnt + 1) * 100), n), 'Verificando canal %s: %s - Estado: NO HOST' \
                            % (channels_tested, channel.upper()))
                if progreso.iscanceled(): break
                continue
            
            try:
                if obj.canonical:
                    canonical = obj.canonical
                    if canonical.get('CF', False):
                        CF = canonical['CF']
                    if canonical.get('CF_test', False):
                        CF_test = canonical['CF_test']
                    if canonical.get('pattern', False):
                        if isinstance(canonical['pattern'], list):
                            patterns += canonical['pattern']
                        else:
                            patterns += [canonical['pattern']]
                    if canonical.get('pattern_forced', False):
                        if isinstance(canonical['pattern'], list):
                            patterns += canonical['pattern_forced']
                        else:
                            patterns += [canonical['pattern_forced']]
                    if canonical.get('channel', False):
                        channel_c = canonical['channel']
                    if canonical.get('host_alt', []):
                        host_alt = canonical['host_alt']
                    if canonical.get('host_black_list', []):
                        host_black_list = canonical['host_black_list']
                    if canonical.get('status', False):
                        canonical_dict = ' - Canonical %s' % canonical['status']
                    else:
                        canonical_dict = ''
            except:
                canonical_dict = ' - Canonical NO Instalado'
            
            page = httptools.downloadpage(channel_host, ignore_response_code=True, timeout=5, alfa_s=True, CF=CF, CF_test=CF_test)
            data = re.sub(r"\n|\r|\t|(<!--.*?-->)", "", page.data).replace("'", '"')
            if 'Javascript is required' in data:
                domain = scrapertools.find_single_match(data, patron_domain)
                data = js2py_conversion(data, channel_host, domain_name=domain, channel=channel_c, canonical=canonical)
                if obj.host != channel_host:
                    channel_host = page.canonical = obj.host
            
            if not page.sucess:
                channels_no_response += 1
                channels_failed += [channel.capitalize()]
                xbmc.log('*** Canal %s no responde, Host: %s, Error: %s%s' % (channel, channel_host, page.code, canonical_dict), xbmc.LOGERROR)
                progreso.update(old_div(((cnt + 1) * 100), n), 'Verificando canal %s: %s - Estado: NO RESPONDE' \
                            % (channels_tested, channel.upper()))
                if progreso.iscanceled(): break
            else:
                canonical_stat = page.canonical
                if canonical_stat and not channel_host.endswith('/') and canonical_stat.endswith('/'):
                    canonical_stat = canonical_stat.rstrip('/')
                if canonical_stat and channel_host not in canonical_stat and canonical_stat not in host_alt \
                                  and canonical_stat not in host_black_list:
                    channels_new_host += 1
                    channels_failed += [channel.capitalize()]
                    canonical_stat = 'NUEVO Host: %s' % canonical_stat
                    xbmc.log('*** Canal %s con OTRO Host: %s / %s%s' % (channel, channel_host, canonical_stat, canonical_dict), xbmc.LOGERROR)
                elif 'retry' in page.proxy__:
                    canonical_stat = page.proxy__.replace(':retry', '')
                    channels_new_host += 1
                    channels_failed += ['%s(%s)' % (channel.capitalize(), canonical_stat)]
                    xbmc.log('*** Canal %s con PROXY temporal: %s / %s%s' % \
                            (channel, channel_host, canonical_stat, canonical_dict), xbmc.LOGERROR)
                elif not canonical_stat:
                    canonical_stat = 'NONE'
                    for pattern in patterns:
                        if not pattern: continue
                        if scrapertools.find_single_match(data, pattern):
                            canonical_stat = 'OK'
                            break
                    else:
                        canonical_stat = 'PATTERN'
                    if canonical_dict:
                        canonical_stat = 'INACTIVE'
                    if canonical_stat in ['NONE', 'PATTERN', 'INACTIVE']:
                        channels_no_canonical += 1
                        channels_failed += ['%s(%s)' % (channel.capitalize(), canonical_stat)]
                        xbmc.log('*** Canal %s falta CANONICAL: %s / %s%s' % (channel, channel_host, canonical_stat, canonical_dict), xbmc.LOGERROR)
                elif canonical_dict:
                    canonical_stat = 'INACTIVE'
                    channels_no_canonical += 1
                    channels_failed += ['%s(%s)' % (channel.capitalize(), canonical_stat)]
                    xbmc.log('*** Canal %s status CANONICAL INACTIVO: %s%s' % (channel, canonical_stat, canonical_dict), xbmc.LOGERROR)
                else:
                    canonical_stat = 'OK%s' % canonical_dict
                progreso.update(old_div(((cnt + 1) * 100), n), 'Verificando canal %s: %s - Estado: %s' \
                            % (channels_tested, channel.upper(), canonical_stat))
                if progreso.iscanceled(): break

    xbmc.log(
                '### Canales verificados: %s; Canales SIN Host: %s; Canales falta CANONICAL: %s; Canales NUEVO/PROXY Host: %s; Canales Host NO responde: %s; Canales con ACCIÓN: %s %s' \
                % (channels_tested, channels_no_host, channels_no_canonical, channels_new_host, channels_no_response, \
                str(channels_no_host+channels_no_canonical+channels_new_host+channels_no_response), str(channels_failed)), xbmc.LOGERROR)
    platformtools.dialog_ok('Log de canales cuyo "host" no responde', \
                'Canales verificados: %s; Canales SIN Host: %s; Canales falta CANONICAL: %s; Canales NUEVO/PROXY Host: %s; Canales Host NO responde: %s;\r\nCanales con ACCIÓN: %s %s' \
                % (channels_tested, channels_no_host, channels_no_canonical, channels_new_host, channels_no_response, \
                str(channels_no_host+channels_no_canonical+channels_new_host+channels_no_response), str(channels_failed)))
    
    return 


def envtal_variables(item):
    """Muestra las variables de Entorno"""
    logger.info()

    from platformcode import envtal
    itemlist, environment = envtal.paint_env(item)

    return itemlist


def proxy_variables(item):
    """Muestra las variables Proxy"""
    logger.info()

    from channelselector import get_thumb

    thumb = get_thumb("setting_0.png")
    itemlist = []
    proxy_plot = {
        'proxy_header': """Existen dos tipos de proxies gratuitos:
            - Proxy Web
            - Proxy “directo”.  Dentro de este grupo hay direcciones que soportar CloudFlare.
    Cada tipo de proxy tiene su lista de direcciones para verificar.  Se verifican contra direcciones de canales con sus regex.
    Desde cualquier Canal se pueden hacer llamadas a Httptools para que sean filtradas \
    por algún tipo de Proxy.  Las llamadas deben incluir los parámetros 'proxy=True o proxy_web=True' y \ 'forced_proxy=Total|ProxyDirect| ProxyCF|ProxyWeb'.  Con la opción 'Total' asumirá 'ProxyDirect'""",
        'proxy__active': """Indica si Proxytools se ha activado automáticamente debido a algún canal \
    bloqueado en la geografía del usuario""",
        'proxy__alter': """Indica si el usuario ha activado manualmente Proxytools, \
    forzando a que realicen actualizaciones periódicas de las tablas de direcciones proxy""",
        'proxy__channel__country': """Lista de webs bloqueadas con la lista de países en \
    donde están bloqueadas.  Si es ALL en alguna web, esa web está bloqueada en todos los países. \
        
        También lista las operadoras, países y canales/servidores que están bloqueados""",
        'proxy__channel_bloqued': """Lista de webs bloqueadas a ser tratadas por Proxytools.  
            
    Si está en ON es porque está bloqueada en esa geografía y/o operadora.""",
        'proxy__channel_white_list': """Lista de webs bloqueadas donde se dice con qué tipo \
    de proxy especifico se quiere tratar.  Si la web bloqueada no está en esta lista, \
    se trata con los proxies por defecto.""",
        'proxy_cf_addr': """El Proxy “directo CF”, es totalmente transparente para el canal, permitiendo usar \
    Post.  El problema que tienen estos Proxies es su extremada volatilidad en la disponibilidad y tiempo \
    de respuesta.""",
        'proxy_cf_list': """Se ha confeccionado una lista inicial de Proxies CloudFlare, \
    principalmente de Singapur y Hong Kong, que han sido probados y que suelen funcionar \
    con regularidad.

    Esta lista se verifica semiautomáticamente cada varias semanas y se añaden \
    direcciones validadas en ese momento. Se verifican con *Reiniciar Servicio Proxy, Test de todas direcciones* \
    contra el canal Gnula.nu

    Las nuevas direcciones se pegan en la variable *proxies_cloudflare_list* de Proxytools.py""",
        'proxy_cf_rep': """Cuando se usa *Reiniciar Servicio Proxy, Test de todas direcciones*, \
    nos dice que direcciones repiten con respecto al pool de direcciones anterior""",
        'proxy_cf_salen': """Cuando se usa *Reiniciar Servicio Proxy, Test de todas direcciones*, \
    nos dice que direcciones salen con respecto al pool de direcciones anterior""",
        'proxy_normal_addr': """El Proxy “directo”, es totalmente transparente para el canal, permitiendo usar \
    Post.  El problema que tienen estos Proxies es su extremada volatilidad en la disponibilidad y tiempo \
    de respuesta.

    Se ha optado por usar por defecto los Proxies “directos”, dejando los Proxy Webs \
    como alternativa automática para el caso de indisponibilidad de Proxies “directos”.""",
        'proxy_normal_list': """Se ha confeccionado una lista inicial de Proxies directos, \
    principalmente de Singapur y Hong Kong, que han sido probados y que suelen funcionar \
    con regularidad.  A esta lista inicial se añaden dinámicamente otros de web(s) que \
    listan estos proxy gratuitos, con algunos criterios de búsqueda exigentes de \
    disponibilidad y tiempo de respuesta.  

    Verificados tanto para http como para https contra el canal Mejortorrent1""",
        'proxy_normal_rep': """Cuando se usa *Reiniciar Servicio Proxy, Test de todas direcciones*, \
    nos dice que direcciones repiten con respecto al pool de direcciones anterior""",
        'proxy_normal_salen': """Cuando se usa *Reiniciar Servicio Proxy, Test de todas direcciones*, \
    nos dice que direcciones salen con respecto al pool de direcciones anterior""",
        'proxy_web__addr': """Es el nombre de la ProxyWeb en uso.
        En el Proxy Web, se llama a una web Proxy donde se le pasa como Post la url de la \
    web de destino, así como los parámetros que indican que NO encripte la url o los datos, y que sí \
    use cookies.  No soporta Cloudflare.
        En los datos de respuesta hay que suprimir de las urls una cabecera y una cola, \
    que varían según la web Proxy.  El resultado es una página bastante parecida a \
    la que se obtendría sin usar el proxy, aunque en el canal que lo use se \
    debe verificar que las expresiones regex funcionan sin problemas.
        Probado contra Mejortorrent1""",
        'proxy_web__list': """Se ha creado un Diccionario con las entradas verificadas de Proxy Webs.  En esas \
    entradas se encuentran los parámetros necesarios para enviar la url de la web de \
    destino, así como para convertir los datos de retorno a algo transparente para el \
    canal.""",
        'proxy_web__post': """Nombre del ProxyWeb que soporta llamadas con *post*
            
        Si no hay ninguno disponible, hay que usar ProxyDirect para la llamada""",
        'proxy_zip': """Datos de geolocalización del usuario.  Necesarios para activar \
    los proxies en los canales bloqueados en la geografía del usuario:
    - Country: país del usuario.  En caso de error, se asume *ES*
    - Operadora de Internet
    - R. Code: código de respuesta de la web_ip
    - Data: string de respuesta de la web (sólo en Debugging)"""
    }

    if not PY3:
        from core import proxytools

    else:
        from core import proxytools_py3 as proxytools

    proxy_var = proxytools.logger_disp(test=True)
    proxy_plot_keys = sorted(proxy_plot)

    for vari, value in list(proxy_var.items()):
        if vari not in proxy_plot_keys:
            proxy_plot[vari] = ''

    itemlist.append(
        Item(
            channel=item.channel,
            title="[COLOR orange][B]Variables " + "Proxy:[/B][/COLOR]",
            action="",
            plot=proxy_plot['proxy_header'],
            thumbnail=thumb,
            folder=False
        )
    )

    for label_a, proxy_ind in list(proxy_var.items()):
        if proxy_ind:
            title = '[COLOR yellow]{}{}[/COLOR]: '.format(label_a,
                                                          str(proxy_ind))
            itemlist.append(
                Item(
                    title=title,
                    channel=item.channel,
                    action="",
                    plot=proxy_plot[lable_a],
                    thumbnail=thumb,
                    folder=False
                )
            )

    itemlist = sorted(itemlist, key=lambda it: it.title)

    return itemlist


def verify_croxyproxy(item):
    import base64
    if PY3:
        import urllib.parse as urllib
    else:
        import urllib 
    
    proxy_web_list = {
    'croxyproxy.com': ('%ssuggest/?__cpo=%s', 
                '%s/%s/?__cpo=%s', '', '', '', '', '', 'https://www.croxyproxy.com/requests?fso=', 
                {'Content-type': 'application/x-www-form-urlencoded', 'Referer': 'https://www.croxyproxy.com/servers'}, 
                'url=%s&proxyServerId=%s&demo=0')
                 }
    proxy_web_name = 'croxyproxy.com'
    url_base = 'https://hdfull.stream/'
    host = url_base
    host_encrypt = base64.b64encode(host.encode('utf-8')).decode('utf-8')
    host_quoted = urllib.quote_plus(url_base)
    server_list = []
    
    #server_list = [23, 24, 28, 31]
    for server_id in range(15, 60):
        url = url_base
        proxy_site_init_post = proxy_web_list[proxy_web_name][9] % (host_quoted, server_id)
        req = httptools.downloadpage(proxy_web_list[proxy_web_name][7], post=proxy_site_init_post, 
                    headers=proxy_web_list[proxy_web_name][8], timeout=3, alfa_s=True, ignore_response_code=True, 
                    proxy=False, proxy_web=False, proxy_retries=0, count_retries_tot=1)
        if req.code not in [200]:
            logger.info('server_id: %s ERROR code %s' % (server_id, req.code))
            continue

        if req.headers.get('access-control-allow-origin', ''):
            proxy_web_name_JSON_url = req.headers['access-control-allow-origin']
            if proxy_web_name_JSON_url:
                separator = '?' if not '?' in url else '&'
                url = url.replace(host, proxy_web_name_JSON_url) + '%s__cpo=%s' % (separator, host_encrypt)
                req = httptools.downloadpage(url, timeout=3, alfa_s=True, ignore_response_code=True, 
                    proxy_retries=0, count_retries_tot=1, CF=True)
        if req.code not in [200]:
            logger.info('server_id: %s ERROR code %s' % (server_id, req.code))
            continue
        server_list += [server_id]
    logger.error(server_list)


def proxy_init(item):
    """Reinicia el servicio de Proxies"""
    logger.info()

    if not PY3:
        from core import proxytools

    else:
        from core import proxytools_py3 as proxytools

    proxytools.get_proxy_list(
        test=item.extra, debugging=True, monitor_start=False)
    proxytools.get_proxy_list_method(test=item.extra, debugging=True)


def proxytools_ofuscar(item):
    """Ofusca el módulo de utilidades Proxy"""
    logger.info()

    from lib import proteccion_proxytools

    proteccion_proxytools.ofuscar()

    # Verificar que no hay errores
    if not PY3:
        from core.proxytools import get_proxy_list, get_proxy_list_method, logger_disp, \
            set_proxy_web, restore_after_proxy_web, channel_proxy_list, get_proxy_addr, encrypt_proxy, decrypt_proxy
    else:
        from core.proxytools_py3 import get_proxy_list, get_proxy_list_method, logger_disp, \
            set_proxy_web, restore_after_proxy_web, channel_proxy_list, get_proxy_addr, encrypt_proxy, decrypt_proxy


def alfaresolver_ofuscar(item):
    """Ofusca el módulo de utilidades"""
    logger.info()

    from lib import proteccion_alfaresolver

    proteccion_alfaresolver.ofuscar()

    # Verificar que no hay errores
    if not PY3:
        from lib.alfaresolver import updated, update_now, get_info, \
            get_data, frequency_count, failed_link, decsojson4, get_sources

    else:
        from lib.alfaresolver_py3 import updated, update_now, get_info, \
            get_data, frequency_count, failed_link, decsojson4, get_sources


def base64_desofuscar(item):
    """Desofusca un string en Base64 en 'last_custom.json'"""
    logger.info()
    import base64
    import marshal
    import subprocess
    import struct
    import time
    import imp

    file = ''
    file_out = filetools.join(ADDON_DATA_PATH, 'bas64_out.pyc')

    #uncompyle_path = filetools.join(ADDON_RUNTIME_PATH, 'lib', 'uncompyle6')
    uncompyle_path = filetools.join(filetools.translatePath(
        'special://xbmc/'), 'system', 'Python', 'Lib', 'site-packages', 'uncompyle6')

    if config.get_system_platform() == "windows":
        uncompyle_path += '.exe'

    if not filetools.exists(uncompyle_path):
        uncompyle_path = filetools.join(
            ADDON_RUNTIME_PATH, 'lib', 'pycdc')

        if config.get_system_platform() == "windows":
            uncompyle_path += '.exe'

        if not filetools.exists(uncompyle_path):
            uncompyle_path = ''

    if filetools.exists(last_custom_json_path):
        lastcustom = jsontools.load(filetools.read(last_custom_json_path))

        if 'zbase64' in lastcustom:
            data_new = lastcustom['zbase64']

            if data_new and filetools.isfile(data_new):
                file = data_new
                logger.debug('Leyendo desde archivo: {}'.format(file))
                data_new = filetools.read(file, mode='rbs')

            if not data_new:
                platformtools.dialog_notification('Decode String Base64',
                                                  '[COLOR hotpink][B]ERROR[/B][/COLOR]. Variable [COLOR yellow][B]"zbase64"[/B][/COLOR] vacía')
                return

            try:
                # Da hasta 10 pasadas o hasta que de error
                for x in range(10):
                    # Decomplicar un .pyo y .pyc
                    if file and (file.endswith('.pyo') or file.endswith('.pyc')):
                        command = [uncompyle_path, str(file)]

                        if config.get_system_platform() == "windows":
                            p = subprocess.Popen(
                                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)

                        else:
                            p = subprocess.Popen(
                                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                        output_cmd, error_cmd = p.communicate()
                        if PY3 and isinstance(output_cmd, bytes):
                            output_cmd = output_cmd.decode()

                        elif not PY3:
                            output_cmd = output_cmd.encode('utf-8', 'ignore')

                        filetools.write(file_out + '.log',
                                        output_cmd, mode='wb')

                        if error_cmd:
                            logger.error(error_cmd)

                        platformtools.dialog_notification('Decode String Base64', '[COLOR yellow]Iteración: [B]' + str(x+1) +
                                                          '[/B][/COLOR]. Busca el resultado en el LOG y en el archivo [COLOR hotpink][B]{}.pycdc[/B][/COLOR]'.format(file_out))
                        return

                    # Decomplicar Alfaresolver o Proxytools (parte 2)
                    if 'marshal.' in str(data_new):
                        data_new = re.sub(r"\n|\r", '', data_new)
                        data_new = re.sub(
                            r"import marshal.*?exec\(marshal.loads\(base64.b64decode\('", '', data_new)
                        data_new = data_new.replace("')))", '')
                        data_new = base64.b64decode(data_new)

                        magic = imp.get_magic()
                        time_string = struct.pack('<L', int(time.time()))
                        f = filetools.file_open(file_out, mode='wb')
                        f.write(magic)
                        f.write(time_string)
                        f.write(data_new)
                        f.close()

                        command = [uncompyle_path, str(file_out)]
                        if config.get_system_platform() == "windows":
                            p = subprocess.Popen(
                                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)

                        else:
                            p = subprocess.Popen(
                                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                        output_cmd, error_cmd = p.communicate()

                        if PY3 and isinstance(output_cmd, bytes):
                            output_cmd = output_cmd.decode()

                        elif not PY3:
                            output_cmd = output_cmd.encode('utf-8', 'ignore')

                        filetools.write(file_out + '.log',
                                        output_cmd, mode='wb')

                        if error_cmd:
                            logger.error(error_cmd)

                        data_new = marshal.loads(data_new)
                        logger.error('Iteración: ' + str(x+1) + ' / MARSHAL: ' +
                                     str(type(data_new)) + ' ' + str(data_new))

                    # Decomplicar Alfaresolver o Proxytools (parte 1)
                    if 'base64' in str(data_new):
                        data_new = re.sub(
                            r"import base64.*?exec\(base64.b64decode\('", '', data_new)
                        data_new = data_new.replace("'))", '')

                    data = base64.b64decode(data_new).decode('utf-8')
                    logger.error('Iteración: ' + str(x+1) +
                                 ' / DATOS: ' + str(data))
                    data_new = data

            except Exception:
                logger.error(traceback.format_exc())
                platformtools.dialog_notification('Decode String Base64',
                                                  '[COLOR yellow]Iteración: [B]' + str(x) +
                                                  '[/B][/COLOR]. Busca el resultado en el LOG')
                return

            platformtools.dialog_notification('Decode String Base64', '[COLOR yellow]Iteración: [B]' + str(x+1) +
                                              '[/B][/COLOR]. [COLOR hotpink][B]ERROR[/B][/COLOR]. Busca el resultado en el LOG')


def testing_xbmcvfs(item):
    """Comprueba la funcionalidad de un Filesystems con XbmcVFS de Kodi y guarda los resultados en el log"""
    logger.info()
    from platformcode import test_xbmcvfs

    test_xbmcvfs.test_vfs()


def funciones_ofuscar(item):
    """Ofusca el json de funciones llamadas desde menú de Ajustes"""
    logger.info()

    import base64
    file_in = filetools.join(ADDON_DATA_PATH, 'funciones_ofuscar.json')
    if not filetools.exists(file_in):
        platformtools.dialog_notification(
            "Ofuscar funciones_ofuscar.json", "Archivo no existe")
        return

    data = filetools.read(file_in)
    data = base64.b64encode(data.encode('utf8')).decode('utf8')
    logger.error(data)


def assistant_install(item):
    """Descarga, Instala y ejecuta/actualiza Alfa Assistant"""
    logger.info()

    from lib import alfa_assistant

    app_name = 'com.alfa.alfamobileassistant'
    remote = ''

    if not config.get_system_platform() == "android":
        remote = platformtools.dialog_input(
            "", "Alfa Assistant: Introduce ruta al Android remoto")

    if item.update:
        res, app_name = alfa_assistant.update_alfa_assistant(remote=remote)
        if res:
            platformtools.dialog_notification("Alfa Assistant", "Actualizado")
            alfa_assistant.check_permissions_alfa_assistant()
        else:
            platformtools.dialog_notification(
                "Alfa Assistant", "Error en actualización")
    else:
        res = alfa_assistant.is_alfa_installed(remote=remote)
        if res:
            platformtools.dialog_notification("Alfa Assistant", "Instalado")
            alfa_assistant.check_permissions_alfa_assistant()
        else:
            platformtools.dialog_notification(
                "Alfa Assistant", "Error en instalación")


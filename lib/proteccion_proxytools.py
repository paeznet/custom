# -*- coding: utf-8 -*-

# 1- Indicar las dos RUTA_* de dónde obtener el _source.py, y dónde se guarda la versión protegida
# 2- Ejecutar este script para generar la versión protegida de proxytools.py

# Idea bytecode de: https://stackoverflow.com/questions/29897480/possible-to-execute-python-bytecode-from-a-script


# FICHERO_ORIGINAL = '/home/xin/.kodi/addons/plugin.video.alfa/lib/proxytools_source.py'
# FICHERO_OFUSCADO = '/home/xin/.kodi/addons/plugin.video.alfa/lib/proxytools.py'
import os
import platform
import sys
import re
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from platformcode import config, logger

p_version = str(platform.python_version()).replace('.', '_')
FICHERO_ORIGINAL = os.path.join(config.get_runtime_path(), 'core', 'proxytools_source.py')
if not PY3: FICHERO_OFUSCADO = os.path.join(config.get_runtime_path(), 'core', 'proxytools.py')
else: FICHERO_OFUSCADO = os.path.join(config.get_runtime_path(), 'core', 'proxytools_py3_%s.py' % p_version)

# Si Container.PluginName no es ninguno de la lista, no se decodificará la url
LISTA_PLUGINNAME_OK = ['', 'plugin.video.alfa']

TEST = False

# Lista de variables y funciones a esconder (ojo, no poner por ejemplo 'url' pq tb modificaría incorrectamente en 'urllib'!)

OFUSCAR_VARS_DEFS = ['channel_bloqued_list', 'operator_bloqued_list', 'proxies_list', 'proxies_cloudflare_list',
                     'proxy_web_name_POST', 'proxy_CF_url_test',  'proxy_web_list', 
                     'proxy_geoloc', 'proxies_save', 'proxy_table', 
                     'proxy_site_url_post', 'proxy_site_url_get', 'proxy_site_referer',
                     'proxy_site_header', 'proxy_site_tail', 'proxy_site_post', 'proxy_t', 
                     'proxy_white_list_init', 'country_list', 'patron', 
                     'randomize_lists', 'test_proxy_addr']

import marshal, base64, os, random

# Genera un .py con el código original más los parámetros necesarios y lo ofusca guardando los bytecode
def codificar_proteccion():

    # Convertir los strings de base64 a números para que no se vea haciendo sólo un b64decode
    lista1modif = [[ord(y) for y in base64.b64encode(x.encode('utf8')).decode('utf8')] for x in LISTA_PLUGINNAME_OK]
    
    codigo = ''

    # Añadir el código original
    with open(FICHERO_ORIGINAL, 'rb') as f: data=f.read(); f.close()
    if PY3: data = data.decode('utf8')
    codigo += data

    # Ofuscar variables y funciones
    vars_defs = []
    for nom in OFUSCAR_VARS_DEFS:
        while True:
            newnom = ''.join(random.choice('MWNV') for _ in range(500, 1000))
            if newnom not in vars_defs:
                vars_defs.append(newnom)
                break
        codigo = codigo.replace(nom, newnom)
        codigo = re.sub(r"\s?(=|!|\+|%|,)\s", r"\1", codigo)

    # Añadir parámetros
    codigo += "\n"
    codigo += "l1 = " + str(lista1modif) + "\n"

    if TEST:
        return codigo
    
    # Generar los bytecodes a ejecutar
    # --------------------------------
    compiled = compile(codigo, '<string>', 'exec')
    bytecodes = marshal.dumps(compiled)
    bytecodes64 = base64.b64encode(bytecodes).decode('utf8')
    # ~ print bytecodes  # Esto es lo que se verá si hacen un b64decode
    # ~ print ''

    # ~ import dis
    # ~ #print dis.dis(compiled)
    # ~ print dis.dis(marshal.loads(bytecodes))  # Esto es lo que se verá si descompilan
    # ~ print ''

    # Empaquetar código de desempaquetar
    # ----------------------------------
    code = "import marshal\nexec(marshal.loads(base64.b64decode('" + bytecodes64 + "')))"
    return base64.b64encode(code.encode('utf8')).decode('utf8')


# MAIN
# ====
def ofuscar():
    global FICHERO_OFUSCADO
    if not os.path.exists(FICHERO_ORIGINAL):
        logger.error('Archivo original no existe: ' + str(FICHERO_ORIGINAL))
        return
    encoded = codificar_proteccion()
    if TEST:
        final_code = encoded
    else:
        final_code = "import base64; exec(base64.b64decode('%s'))" % encoded

    # ~ print final_code

    with open(FICHERO_OFUSCADO, 'w') as f: f.write(final_code); f.close()
    if PY3:
        FICHERO_OFUSCADO = FICHERO_OFUSCADO.replace('_' + p_version, '')
        with open(FICHERO_OFUSCADO, 'w') as f: f.write(final_code); f.close()
    logger.debug('Ok, creado el fichero ofuscado: ' + FICHERO_OFUSCADO)


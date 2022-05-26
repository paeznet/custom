# -*- coding: utf-8 -*-

# 1- Indicar las dos RUTA_* de dónde obtener el _source.py, y dónde se guarda la versión protegida
# 2- Ejecutar este script para generar la versión protegida de alfaresolver.py

# Idea bytecode de: https://stackoverflow.com/questions/29897480/possible-to-execute-python-bytecode-from-a-script

import os
import platform
import sys
import re

PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from platformcode import config, logger

p_version = str(platform.python_version()).replace('.', '_')
FICHERO_ORIGINAL = os.path.join(config.get_runtime_path(), 'lib', 'alfaresolver_source.py')
if not PY3: FICHERO_OFUSCADO = os.path.join(config.get_runtime_path(), 'lib', 'alfaresolver.py')
else: FICHERO_OFUSCADO = os.path.join(config.get_runtime_path(), 'lib', 'alfaresolver_py3_%s.py' % p_version)

# Si Container.PluginName no es ninguno de la lista, no se decodificará la url
LISTA_PLUGINNAME_OK = ['', 'plugin.video.alfa']

TEST = False
# Lista de variables y funciones a esconder (ojo, no poner por ejemplo 'url' pq tb modificaría incorrectamente en 'urllib'!)
OFUSCAR_VARS_DEFS = [
    'check_played', 'value_c', 'unmix', 'get_word', 'val_0', 'val_1', 'val_3', 'patched',
    'info_d', 'j_day', 'j_month', 'j_year', 'real_text', 'new_text', 'actual_date', 'received_url', 'result_url',
    'old_url', 'temp_url', 'change', 'page_url', 'new_headers', 'g_data', 'success', 'retries', 'systems_path',
    'set_ver', 'set_word', 'f_systems', 'channel_name', 'old_frequency', 'value1', 'value2', 'value3', 'value4',
    'dia_hoy', 'fecha_actual', 'cursor_alfa', 'sql_alfa', 'result_a', 'result_b', 'val_x', 'addon_author',
    'addon_path', 'file_path', 'auto_val', 'unMixed', 'alfa_assistant_pwd', 'app_name', 'addonid', 'respuesta',
    'command', 'upk_install_path', 'apk_install_SD', 'assistant_rar', 'apk_path', 'video_urls', 'base_url', 'g_data',
    'packed', 'unpackd', 'cipher_data', 'js_code', 'so_json', 'pwd', 'sourcs', 'listed', 'v_data', 'j_data', 'g_url',
    'g_session', 'g_headers', 't_session', 'u0', 'g_ck', 'UA', 'so_data', 'j_args', 'so_x', 'decoded', 'src_data',
    'passphrase', 'encrypted_text', 'encryptd_text_bytes', 'g_salt', 'g_resp', 'g_key', 'g_iv', 'g_aes',
    'decrypted_text', 'encoder', 'unpad_text', 'js_dec', 'g_v', 'obfs_ene', 'obfs_data', 'obfs_keY', 'obfs_jsCode',
    'var_chars', 'var_ce', 'var_number', 'var_te', 'var_erre', 'var_ache', 'var_ce', 'var_efe', 'list1', 'list2', 'list3']

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
    #logger.debug(codigo)
    # ~ print codigo
    # Añadir parámetros
    codigo += "\n"
    codigo += "l1 = " + str(lista1modif) + "\n"
    if TEST:
        #print codigo
        return codigo
    # Generar los bytecodes a ejecutar
    # --------------------------------
    compiled = compile(codigo, '<string>', 'exec')
    bytecodes = marshal.dumps(compiled)
    bytecodes64 = base64.b64encode(bytecodes).decode('utf8')

    # ~ print bytecodes  # Esto es lo que se verá si hacen un b64decode
    # ~ print ''

    # import dis
    # #print dis.dis(compiled)
    # print dis.dis(marshal.loads(bytecodes))  # Esto es lo que se verá si descompilan
    # print ''

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
        #print ('Archivo original no existe: ' + str(FICHERO_ORIGINAL))
        return
    encoded = codificar_proteccion()
    if TEST:
        final_code = encoded
    else:
        final_code = "import base64; exec(base64.b64decode('%s'))" % encoded

    #print final_code

    with open(FICHERO_OFUSCADO, 'w') as f: f.write(final_code); f.close()
    if PY3:
        FICHERO_OFUSCADO = FICHERO_OFUSCADO.replace('_' + p_version, '')
        with open(FICHERO_OFUSCADO, 'w') as f: f.write(final_code); f.close()
    logger.debug('Ok, creado el fichero ofuscado: ' + FICHERO_OFUSCADO)
    #print ('Ok, creado el fichero ofuscado: ' + FICHERO_OFUSCADO)

#ofuscar()
# -*- coding: utf-8 -*-
__author__ = "Chirag Rathod (Srce Cde)"
__license__ = "MIT"
__email__ = "chiragr83@gmail.com"
__maintainer__ = "Andrés Galaz (Srce Cde)"
__version__ = "v1.0"

import base64
import email
from datetime import datetime, date

from cmp.appError import AppError
import cmp.glUtil as u


def multipart(event):
    # decodifica form-data en bytes
    post_data = base64.b64decode(event["body"])

    # recupera content-type (case sensitive)
    try:
        content_type = event["headers"]["Content-Type"]
    except:
        content_type = event["headers"]["content-type"]
    ct = "Content-Type: " + content_type + "\n"

    # Utiliza biblioteca 'email' para analizar los datos del body
    msg = email.message_from_bytes(ct.encode() + post_data)

    # verifica si es multipart
    print("Multipart check : ", msg.is_multipart())
    if msg.is_multipart():
        multipart_content = {}
        # recupera pares nombre y valor de los campos de form-data
        for part in msg.get_payload():
            nombre = part.get_param("name", header="content-disposition")
            # Si existe filename se agrega a la salida
            if part.get_filename():
                bytes = part.get_payload(decode=True)
                charset = part.get_content_charset("iso-8859-1")
                valor = bytes.decode(charset, "replace")
                # Elimina caracter <feff>
                if valor[0:3] == "ï»¿":
                    valor = valor[3:]
                # fetching the filename
                multipart_content[nombre] = {
                    "contenido": valor,
                    "file_name": part.get_filename(),
                }
            else:
                bytes = part.get_payload(decode=True)
                charset = part.get_content_charset("utf-8")
                valor = bytes.decode(charset, "replace")
                # print(nombre,':',valor)
                multipart_content[nombre] = valor

        # Upload OK
        return multipart_content
    # Si no es multipart, no retorna nada
    pass


def getParam(event, cParamName, obligatorio=False, tipo=None):
    if cParamName == "body" and "body" in event:
        return event["body"]

    if "queryStringParameters" in event:
        params = event["queryStringParameters"]
    else:
        params = event

    # Verifica existencia parámetro
    if not cParamName in params:
        if obligatorio:
            raise AppError("Falta parámetro: " + cParamName)
        return None

    if tipo is int or tipo is float:
        n = u.str2number(params[cParamName])
        if n == None:
            raise AppError("Parámetro '{}' debe ser numérico".format(cParamName))
        return n

    if tipo is datetime or tipo is date:
        d = u.str2date(params[cParamName])
        if not d:
            raise AppError("Parámetro '{}' debe ser una fecha".format(cParamName))
        return d

    if tipo is u.periodo:
        d = u.str2periodo(params[cParamName])
        if not d:
            raise AppError("Parámetro '{}' debe ser una fecha".format(cParamName))
        return d

    if tipo is bool:
        return u.str2bool(params[cParamName])

    return params[cParamName]

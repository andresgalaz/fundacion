# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.2"

import json
import logging
import traceback

from cmp.appError import AppError
import cmp.glUtil as u

import archivo
import banco
import ctaBanco
import ctaContab
import institucion
import movim
import resumen
import usuario


PATH_ARCHIVO = "/archivo"
PATH_ARCHIVO_DEL = "/archivo_del"
PATH_BANCO = "/banco"
PATH_CTA_BANCO = "/cta_banco"
PATH_CTA_BANCO_UPD = "/cta_banco_upd"
PATH_CTA_BANCO_DEL = "/cta_banco_del"
PATH_CTA_CONTAB = "/cta_contab"
PATH_CTA_CONTAB_UPD = "/cta_contab_upd"
PATH_CTA_CONTAB_DEL = "/cta_contab_del"
PATH_INSTITUCION = "/institucion"
PATH_INSTITUCION_UPD = "/institucion_upd"
PATH_INSTITUCION_DEL = "/institucion_del"
PATH_MOVIM = "/movim"
PATH_MOVIM_ASIGNA = "/movim_asigna"
PATH_PERIODOS = "/periodos"
PATH_SALDO_CTABANCO = "/saldo_cta_banco"
PATH_TOTAL_CTACONTAB = "/total_cta_contab"
PATH_UPLOAD = "/upload"
PATH_USUARIO_ASIGNA = "/usuario_asigna"
PATH_USUARIO_DESASIGNA = "/usuario_desasigna"
PATH_USUARIO_LOAD = "/usuario_load"


def convertResp(x):
    if type(x) == dict:
        if not "success" in x:
            x["success"] = True
        return x

    resp = dict(success=True)
    if type(x) == str:
        resp["message"] = x
    elif type(x) == int:
        resp["registros_procesados"] = x
    else:
        resp["records"] = x
    return resp


def lambda_handler(event, context):
    log = logging.getLogger("lambda_handler")
    log.debug("Fundaciones " + __version__)
    log.debug("lambda_handler:Inicio")
    print(event)

    try:
        cRuta = event["rawPath"]

        data = None
        if cRuta == PATH_ARCHIVO:
            data = archivo.lista(event)
        elif cRuta == PATH_ARCHIVO_DEL:
            data = archivo.delete(event)
        elif cRuta == PATH_BANCO:
            data = banco.lista(event)
        elif cRuta == PATH_CTA_BANCO:
            data = ctaBanco.lista(event)
        elif cRuta == PATH_CTA_BANCO_DEL:
            data = ctaBanco.delete(event)
        elif cRuta == PATH_CTA_BANCO_UPD:
            data = ctaBanco.update(event)

        elif cRuta == PATH_CTA_CONTAB:
            data = ctaContab.lista(event)
        elif cRuta == PATH_CTA_CONTAB_DEL:
            data = ctaContab.delete(event)
        elif cRuta == PATH_CTA_CONTAB_UPD:
            data = ctaContab.update(event)

        elif cRuta == PATH_INSTITUCION:
            data = institucion.lista(event)
        elif cRuta == PATH_INSTITUCION_DEL:
            data = institucion.delete(event)
        elif cRuta == PATH_INSTITUCION_UPD:
            data = institucion.update(event)

        elif cRuta == PATH_MOVIM:
            data = movim.lista(event)
        elif cRuta == PATH_MOVIM_ASIGNA:
            data = movim.asigna(event)

        elif cRuta == PATH_PERIODOS:
            data = movim.periodos(event)

        elif cRuta == PATH_SALDO_CTABANCO:
            data = ctaBanco.saldo(event)
        elif cRuta == PATH_TOTAL_CTACONTAB:
            data = ctaContab.total(event)

        elif cRuta == PATH_UPLOAD:
            data = resumen.upload(event)

        elif cRuta == PATH_USUARIO_ASIGNA:
            data = usuario.asigna(event)
        elif cRuta == PATH_USUARIO_DESASIGNA:
            data = usuario.desasigna(event)
        elif cRuta == PATH_USUARIO_LOAD:
            data = usuario.load(event)
        else:
            raise AppError("No existe la ruta: " + cRuta)

        resp = convertResp(data)

    except AppError as e:
        resp = dict(success=False, message=str(e))

    except Exception as e:
        log.error(e)
        log.error(traceback.format_exc())
        resp = dict(success=False, message="Error inesperado:" + str(e))

    log.debug("lambda_handler:Término", resp)
    return json.dumps(resp, default=u.object2json)

# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import json
import logging
import traceback

from cmp.appError import AppError
import cmp.glUtil as u

import banco
import ctaBanco
import ctaContab
import institucion
import movim
import resumen


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
PATH_SALDO_CTABANCO = "/saldo_cta_banco"
PATH_TOTAL_CTACONTAB = "/total_cta_contab"
PATH_UPLOAD = "/upload"


def lambda_handler(event, context):
    log = logging.getLogger("lambda_handler")
    log.debug("Fundaciones " + __version__)
    log.debug("lambda_handler:Inicio")
    print(event)

    try:
        cRuta = event["rawPath"]

        if cRuta == PATH_BANCO:
            resp = {"records": banco.lista(event)}

        elif cRuta == PATH_CTA_BANCO:
            resp = {"records": ctaBanco.lista(event)}
        elif cRuta == PATH_CTA_BANCO_DEL:
            resp = {"records": ctaBanco.delete(event)}
        elif cRuta == PATH_CTA_BANCO_UPD:
            resp = {"records": ctaBanco.update(event)}

        elif cRuta == PATH_CTA_CONTAB:
            resp = {"records": ctaContab.lista(event)}
        elif cRuta == PATH_CTA_CONTAB_DEL:
            resp = {"records": ctaContab.delete(event)}
        elif cRuta == PATH_CTA_CONTAB_UPD:
            resp = {"records": ctaContab.update(event)}

        elif cRuta == PATH_INSTITUCION:
            resp = {"records": institucion.lista(event)}
        elif cRuta == PATH_INSTITUCION_DEL:
            resp = {"message": institucion.delete(event)}
        elif cRuta == PATH_INSTITUCION_UPD:
            resp = {"message": institucion.update(event)}

        elif cRuta == PATH_MOVIM:
            resp = {"records": movim.lista(event)}
        elif cRuta == PATH_SALDO_CTABANCO:
            resp = {"records": ctaBanco.saldo(event)}
        elif cRuta == PATH_TOTAL_CTACONTAB:
            resp = {"records": ctaContab.total(event)}
        elif cRuta == PATH_UPLOAD:
            movimList = resumen.upload(event)
            resp = {"records": movimList}
        else:
            raise AppError("No existe la ruta: " + cRuta)

        if not "success" in resp:
            resp["success"] = True

    except AppError as e:
        resp = {"success": False, "message": str(e)}

    except Exception as e:
        log.error(e)
        log.error(traceback.format_exc())
        resp = {"success": False, "message": "Error inesperado:" + str(e)}

    log.debug("lambda_handler:Término", resp)
    return json.dumps(resp, default=u.object2json)

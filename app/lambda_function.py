# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import json

import globalUtil as u

import banco
import ctaBanco
import ctaContab
import movim
import resumen

print("Cargando rutas " + __version__)
PATH_BANCO = "/banco"
PATH_CTA_CONTAB = "/cta_contab"
PATH_MOVIM = "/movim"
PATH_SALDO_CTABANCO = "/saldo_cta_banco"
PATH_TOTAL_CTACONTAB = "/total_cta_contab"
PATH_UPLOAD = "/upload"


def lambda_handler(event, context):
    print("lambda_handler:Inicio")
    print(event)
    try:
        cRuta = event["rawPath"]

        if cRuta == PATH_BANCO:
            resp = {"records": banco.lista(event)}
        elif cRuta == PATH_CTA_CONTAB:
            resp = {"records": ctaContab.lista(event)}
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
            raise AssertionError("No existe la ruta: " + cRuta)

        if not "success" in resp:
            resp["success"] = True

    except Exception as e:
        resp = {"success": False, "message": str(e)}

    print("lambda_handler:Término", resp)

    return json.dumps(resp, default=u.object2json)

# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import json

import globalUtil as u
import resumen

print("Cargando rutas " + __version__)
PATH_UPLOAD = "/upload"


def lambda_handler(event, context):
    print("lambda_handler:Inicio")
    resp = resumen.upload(event)
    print(event)
    try:
        if False:
            pass
        elif event["rawPath"] == PATH_UPLOAD:
            movim = resumen.upload(event)
            print(resp)
            resp = json.dumps(
                {"success": True, "records": movim}, default=u.object2json
            )
    except Exception as e:
        resp = {"success": False, "message": str(e)}

    print("lambda_handler:Término")
    return resp

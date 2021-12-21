# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import json

# Bibliorecas propias
from cmp.appError import AppError
import cmp.db as db
import cmp.glUtil as u
from cmp.requestHlp import getParam

import config
import dataMng as dm


def asigna(event):
    cBody = getParam(event, "body", obligatorio=True)
    # Dentro de body viene un JSON que se convirte en parámetros
    arrInstitUsr = json.loads(cBody)

    cnxDb = db.conecta()
    nCount = 0
    for regAsigna in arrInstitUsr:
        pUsuario = getParam(regAsigna, "pUsuario", obligatorio=True, tipo=int)
        pInstitucion = getParam(regAsigna, "pInstitucion", obligatorio=True, tipo=int)
        dm.updInstitucionUsuario(
            cnxDb=cnxDb, pInstitucion=pInstitucion, pUsuario=pUsuario
        )
        nCount += 1

    cnxDb.commit()
    cnxDb.close()

    return nCount


def lista(event):
    nInstitucion = getParam(event, "institucion", tipo=int)
    cUsuario = getParam(event, "usuario")

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lis = dm.leeUsuarioInstitucion(cnxDb, nInstitucion, cUsuario)
    cnxDb.commit()
    cnxDb.close()

    if not lis:
        lis = []

    return lis


def desasigna(event):
    cBody = getParam(event, "body", obligatorio=True)
    # Dentro de body viene un JSON que se convirte en parámetros
    arrInstitUsr = json.loads(cBody)

    cnxDb = db.conecta()
    nCount = 0
    for regAsigna in arrInstitUsr:
        pUsuario = getParam(regAsigna, "pUsuario", obligatorio=True, tipo=int)
        pInstitucion = getParam(regAsigna, "pInstitucion", obligatorio=True, tipo=int)
        dm.delInstitucionUsuario(
            cnxDb=cnxDb, pInstitucion=pInstitucion, pUsuario=pUsuario
        )
        nCount += 1

    cnxDb.commit()
    cnxDb.close()

    return nCount


def load(event):
    try:
        arrUsers = u.getUsersCognito(config.USER_POOL_COGNITO)
    except Exception as e:
        raise AppError("No se pudo leer lista de usuarios desde COGNITO:" + str(e))

    cnxDb = db.conecta()
    for usr in arrUsers:
        dm.updUsuario(cnxDb, **usr)
    cnxDb.commit()
    lisUsr = dm.leeUsuarioInstitucion(cnxDb)
    cnxDb.close()

    return lisUsr

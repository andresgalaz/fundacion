# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

# Bibliorecas propias
import cmp.dataMng as dm
import cmp.db as db
from cmp.requestHlp import getParam
from cmp.glUtil import periodo


def delete(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    n = dm.delInstitucion(cnxDb, nInstitucion)
    cnxDb.commit()
    cnxDb.close()

    if n == 0:
        return "Registro no existe"
    return "Registro eliminado correctamente"


def lista(event):
    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    listInst = dm.leeInstitucion(cnxDb)
    cnxDb.commit()
    cnxDb.close()

    if not listInst:
        listInst = []

    return listInst


def update(event):
    nInstitucion = getParam(event, "institucion", tipo=int)
    cNombre = getParam(event, "nombre", obligatorio=True)

    cnxDb = db.conecta()
    try:
        dm.updInstitucion(cnxDb, nInstitucion, cNombre)
        cnxDb.commit()
    except Exception as e:
        cnxDb.rollback()
        return str(e)

    cnxDb.close()

    if nInstitucion:
        return "Registro actualizado correctamente"
    return "Registro ingresado correctamente"

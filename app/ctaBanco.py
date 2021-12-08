# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

# Bibliorecas propias
from cmp.appError import AppError
import cmp.db as db
from cmp.glUtil import periodo
from cmp.requestHlp import getParam

import dataMng as dm


def delete(event):
    nctaBanco = getParam(event, "cta_banco", obligatorio=True, tipo=int)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    n = dm.delCtaBanco(cnxDb, nctaBanco)
    cnxDb.commit()
    cnxDb.close()

    if n == 0:
        return "Registro no existe"
    return "Registro eliminado correctamente"


def lista(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lisCta = dm.leeCtaBanco(cnxDb, fInstitucion=nInstitucion)
    cnxDb.commit()
    cnxDb.close()

    if not lisCta:
        lisCta = []

    return lisCta


def saldo(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    dPeriodo = getParam(event, "periodo", obligatorio=True, tipo=periodo)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lisSaldo = dm.saldoCtaBanco(cnxDb, nInstitucion, dPeriodo=dPeriodo)
    cnxDb.commit()
    cnxDb.close()

    if not lisSaldo:
        lisSaldo = []

    return lisSaldo


def update(event):
    nctaBanco = getParam(event, "cta_banco", tipo=int)
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    nBanco = getParam(event, "banco", obligatorio=True, tipo=int)
    cCuenta = getParam(event, "cuenta", obligatorio=True)
    cNombre = getParam(event, "nombre", obligatorio=True)

    cnxDb = db.conecta()
    if not dm.leeInstitucion(cnxDb, bUno=True, pInstitucion=nInstitucion):
        raise AppError("No existe institución con ID={}".format(nInstitucion))
    if not dm.leeBanco(cnxDb, bUno=True, pBanco=nBanco):
        raise AppError("No existe banco con ID={}".format(nBanco))

    try:
        dm.updCtaBanco(cnxDb, nctaBanco, nInstitucion, nBanco, cCuenta, cNombre)
        cnxDb.commit()
    except Exception as e:
        cnxDb.rollback()
        return str(e)

    cnxDb.close()

    if nctaBanco:
        return "Registro actualizado correctamente"
    return "Registro ingresado correctamente"

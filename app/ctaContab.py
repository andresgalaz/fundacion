# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

# Bibliorecas propias
from cmp.appError import AppError
import cmp.db as db
from cmp.requestHlp import getParam
from cmp.glUtil import periodo

import dataMng as dm


def delete(event):
    nCtaContab = getParam(event, "cta_contab", obligatorio=True, tipo=int)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    n = dm.delCtaContab(cnxDb, nCtaContab)
    cnxDb.commit()
    cnxDb.close()

    if n == 0:
        return "Registro no existe"
    return "Registro eliminado correctamente"


def lista(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lisCta = dm.leeCtaContab(cnxDb, fInstitucion=nInstitucion)
    cnxDb.commit()
    cnxDb.close()

    if not lisCta:
        lisCta = []

    return lisCta


def total(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    dPeriodo = getParam(event, "periodo", tipo=periodo)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lisTotal = dm.totalCtaContab(cnxDb, nInstitucion, dPeriodo=dPeriodo)
    cnxDb.commit()
    cnxDb.close()

    if not lisTotal:
        lisTotal = []

    return lisTotal


def update(event):
    nCtaContab = getParam(event, "cta_contab", tipo=int)
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    cCodigo = getParam(event, "codigo", obligatorio=True)
    cNombre = getParam(event, "nombre", obligatorio=True)
    bCargo = getParam(event, "acepta_cargos", obligatorio=True, tipo=bool)
    bAbono = getParam(event, "acepta_abonos", obligatorio=True, tipo=bool)

    cnxDb = db.conecta()
    if not dm.leeInstitucion(cnxDb, bUno=True, pInstitucion=nInstitucion):
        raise AppError("No existe institución con ID={}".format(nInstitucion))

    try:
        dm.updCtaContab(
            cnxDb, nCtaContab, nInstitucion, cCodigo, cNombre, bAbono, bCargo
        )
        cnxDb.commit()
    except Exception as e:
        cnxDb.rollback()
        return str(e)

    cnxDb.close()

    if nCtaContab:
        return "Registro actualizado correctamente"
    return "Registro ingresado correctamente"

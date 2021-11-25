# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

# Bibliorecas propias
import dataMng as dm
import db
from request_helper import getParam
from globalUtil import periodo


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

# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

# Bibliorecas propias
from datetime import date
import dataMng as dm
import db
from globalUtil import periodo
from request_helper import getParam


def saldo(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    dPeriodo = getParam(event, "periodo", tipo=periodo)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lisSaldo = dm.saldoCtaBanco(cnxDb, nInstitucion, dPeriodo=dPeriodo)
    cnxDb.commit()
    cnxDb.close()

    if not lisSaldo:
        lisSaldo = []

    return lisSaldo

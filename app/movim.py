# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import json
from datetime import date

# Bibliorecas propias
from cmp.appError import AppError
import cmp.db as db
import cmp.glUtil as u
from cmp.requestHlp import getParam

import dataMng as dm


def asigna(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    cBody = getParam(event, "body", obligatorio=True)
    # Dentro de body viene un JSON que se convirte en parámetros
    arrMovContab = json.loads(cBody)
    # print(arrMovContab)

    cnxDb = db.conecta()
    nCount = 0
    for regAsigna in arrMovContab:
        pMovim = getParam(regAsigna, "pMovim", obligatorio=True, tipo=int)
        fCtaContab = getParam(regAsigna, "fCtaContab", obligatorio=True, tipo=int)
        regCta = dm.leeCtaContab(
            cnxDb, bUno=True, fInstitucion=nInstitucion, pCtaContab=fCtaContab
        )
        if not regCta:
            raise AppError(
                "No existe cuenta contable PK'{}' asociada a la institución".format(
                    fCtaContab
                )
            )
        dm.updMovimAsigna(
            cnxDb=cnxDb, pMovim=pMovim, fCtaContab=fCtaContab, fInstitucion=nInstitucion
        )
        nCount += 1

    cnxDb.commit()
    cnxDb.close()
    return nCount


def lista(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    nCtaContab = getParam(event, "cuenta_contab", tipo=int)
    # Filtra movimientos con la cuenta contable asignada o no
    bAsignadas = getParam(event, "asignadas", tipo=bool)
    # Rango fechas o Periodo
    dPeriodo = getParam(event, "periodo", tipo=u.periodo)
    fechaIni = getParam(event, "fecha_inicio", tipo=date)
    fechaFin = getParam(event, "fecha_fin", tipo=date)

    cnxDb = db.conecta()

    # se puede propocionar la id o el nombre de la cuenta contable
    # nCtaContab = None
    # if cCtaContab:
    #     arr = dm.leeCtaContab(
    #         cnxDb,
    #         bUno=True,
    #         fInstitucion=nInstitucion,
    #         cCodigo=cCtaContab,
    #     )
    #     if not arr:
    #         cnxDb.close()
    #         raise AppError(
    #             "No existe cuenta contable '{}' asociada a la institución".format(
    #                 cCtaContab
    #             )
    #         )
    #     nCtaContab = arr["pCtaContab"]

    lisMovim = dm.leeMovim(
        cnxDb,
        fInstitucion=nInstitucion,
        fCtaContab=nCtaContab,
        dPeriodo=dPeriodo,
        dMovinIni=fechaIni,
        dMovinFin=fechaFin,
        bAsignadas=bAsignadas,
    )
    cnxDb.close()

    if not lisMovim:
        lisMovim = []

    return lisMovim


def periodos(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)

    cnxDb = db.conecta()
    lisPer = dm.leePeriodos(cnxDb, nInstitucion)
    cnxDb.close()

    if not lisPer:
        lisPer = []

    return lisPer

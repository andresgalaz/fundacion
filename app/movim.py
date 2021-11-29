# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

from datetime import date

# Bibliorecas propias
from cmp.appError import AppError
import cmp.dataMng as dm
import cmp.db as db
import cmp.glUtil as u
from cmp.requestHlp import getParam


def lista(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    cCtaContab = getParam(event, "cuenta_contab")
    # Filtra movimientos con la cuenta contable asignada o no
    bAsignadas = getParam(event, "asignadas", tipo=bool)
    # Rango fechas o Periodo
    dPeriodo = getParam(event, "periodo", tipo=u.periodo)
    fechaIni = getParam(event, "fecha_inicio", tipo=date)
    fechaFin = getParam(event, "fecha_fin", tipo=date)

    cnxDb = db.conecta()

    # se puede propocionar la id o el nombre de la cuenta contable
    nCtaContab = None
    if cCtaContab:
        arr = dm.leeCtaContab(
            cnxDb,
            bUno=True,
            fInstitucion=nInstitucion,
            cCodigo=cCtaContab,
        )
        if not arr:
            cnxDb.close()
            raise AppError(
                "No existe cuenta contable '{}' asociada a la institución".format(
                    cCtaContab
                )
            )
        nCtaContab = arr["pCtaContab"]

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

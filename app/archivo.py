# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"


from datetime import date

# Bibliorecas propias
import cmp.db as db
import cmp.glUtil as u
from cmp.requestHlp import getParam

import dataMng as dm


def delete(event):
    nArchivo = getParam(event, "archivo", obligatorio=True, tipo=int)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    n = dm.delArchivo(cnxDb, nArchivo)
    cnxDb.commit()
    cnxDb.close()

    if n == 0:
        return "Registro no existe"
    return "Registro eliminado correctamente"


def lista(event):
    nInstitucion = getParam(event, "institucion", obligatorio=True, tipo=int)
    nArchivo = getParam(event, "archivo", tipo=int)
    nCtaBanco = getParam(event, "cta_banco", tipo=int)

    cNombre = getParam(event, "nombre")
    dCorte = getParam(event, "fecha_movim", tipo=date)

    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lisArch = dm.leeArchivo(
        cnxDb,
        pArchivo=nArchivo,
        fInstitucion=nInstitucion,
        fCtaBanco=nCtaBanco,
        cNombre=cNombre,
        dMovim=dCorte,
    )
    cnxDb.commit()
    cnxDb.close()

    if not lisArch:
        lisArch = []

    return lisArch

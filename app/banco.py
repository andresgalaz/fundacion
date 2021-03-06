# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

# Bibliorecas propias
import cmp.db as db
import cmp.glUtil as u

import dataMng as dm


def lista(event):
    cnxDb = db.conecta()
    # se puede propocionar la id o el nombre de la cuenta contable
    lisBco = dm.leeBanco(cnxDb)
    cnxDb.commit()
    cnxDb.close()

    if not lisBco:
        lisBco = []

    return lisBco

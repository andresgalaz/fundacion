# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import db
from globalUtil import periodo


def insArchivo(
    cnxDb, fInstitucion, cNombre, cNombreS3, cUsuario, dInicio=None, dTermino=None
):
    (n, nId) = db.sqlExec(
        "INSERT INTO tArchivo( fInstitucion, cNombre, cNombreS3,  cUsuario,  dInicio,  dTermino ) VALUES ( %s, %s, %s, %s, %s, %s )",
        cnxDb=cnxDb,
        params=(fInstitucion, cNombre, cNombreS3, cUsuario, dInicio, dTermino),
    )
    return nId


def insCtaBanco(cnxDb, fInstitucion, fBanco, cNombre, cCuenta):
    (n, nId) = db.sqlExec(
        "INSERT INTO tCtaBanco( fInstitucion, fBanco, cNombre, cCuenta ) VALUES ( %s, %s, %s, %s )",
        cnxDb=cnxDb,
        params=(fInstitucion, fBanco, cNombre, cCuenta),
    )
    return nId


def insMovim(
    cnxDb,
    fArchivo,
    fInstitucion,
    fCtaBanco,
    dMovim,
    cSucursal,
    cOperacion,
    cDescripcion,
    nAbono,
    nCargo,
    nSaldo,
):
    cSql = """INSERT INTO tMovim
                ( fArchivo, fInstitucion, fCtaBanco,   
                    dMovim, cSucursal, cOperacion, cDescripcion,
                    nAbono, nCargo, nSaldo ) 
                VALUES ( %s, %s, %s,   
                    %s, %s, %s, %s,
                    %s, %s, %s )"""
    db.sqlExec(
        cSql,
        cnxDb=cnxDb,
        params=(
            fArchivo,
            fInstitucion,
            fCtaBanco,
            dMovim,
            cSucursal,
            cOperacion,
            cDescripcion,
            nAbono,
            nCargo,
            nSaldo,
        ),
    )


def leeBanco(cnxDb, bUno=False, pBanco=None, cNombre=None):
    if pBanco:
        cWhe = " pBanco = %s "
        params = (pBanco,)
    elif cNombre:
        cWhe = " cNombre = %s "
        params = (cNombre,)
    else:
        if bUno:
            raise AssertionError("No se indico ID ni Nombre para leer Banco")
        cWhe = " 1=1 "
        params = None

    arr = db.sqlQuery(
        "SELECT pBanco, cNombre, tCreacion from tBanco WHERE " + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    if bUno == False:
        return arr
    if len(arr) > 1:
        raise AssertionError("Se esperaba un solo registro al leer banco")
    return arr[0]


def leeCtaBanco(cnxDb, pCtaBanco=None, cCuenta=None):
    if pCtaBanco:
        cWhe = " pCtaBanco = %s "
        params = (pCtaBanco,)
    elif cCuenta:
        cWhe = " cCuenta = %s "
        params = (cCuenta,)
    else:
        raise AssertionError("No se indico ID ni Cuenta para leer Cuenta Bancaria")

    arr = db.sqlQuery(
        "SELECT pCtaBanco, fInstitucion, fBanco, cNombre, cCuenta, tCreacion from tCtaBanco WHERE "
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    return arr[0]


def leeCtaContab(
    cnxDb, bUno=False, pCtaContab=None, fInstitucion=None, cNombre=None, cCodigo=None
):
    cWhe = " 1=1 "
    params = ()
    if pCtaContab:
        cWhe += " AND pCtaContab = %s "
        params += (pCtaContab,)
    if fInstitucion:
        cWhe += " AND fInstitucion = %s "
        params += (fInstitucion,)
    if cNombre:
        cWhe += " AND cNombre like %s "
        params += ("%" + cNombre + "%",)
    if cCodigo:
        cWhe += " AND cCodigo = %s "
        params += (cCodigo,)

    arr = db.sqlQuery(
        "SELECT pCtaContab, fInstitucion, cCodigo, cNombre, tCreacion from tCtaContab WHERE "
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    if bUno == False:
        return arr
    if len(arr) > 1:
        raise AssertionError("Se esperaba un solo registro al leer cuenta contable")
    return arr[0]


def leeInstitucion(cnxDb, pInstitucion=None, cNombre=None):
    if pInstitucion:
        cWhe = " pInstitucion = %s "
        params = (pInstitucion,)
    elif cNombre:
        cWhe = " cNombre = %s "
        params = (cNombre,)
    else:
        raise AssertionError("No se indico ID ni Nombre para leer Institución")

    arr = db.sqlQuery(
        "SELECT  pInstitucion, cNombre, tCreacion from tInstitucion WHERE " + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    return arr[0]


def leeMovim(
    cnxDb,
    fArchivo=None,
    fInstitucion=None,
    fCtaContab=None,
    dPeriodo=None,
    dMovinIni=None,
    dMovinFin=None,
    bAsignadas=None,
):
    params = ()
    cWhe = "1=1"
    if fArchivo:
        cWhe += " AND fArchivo = %s "
        params += (fArchivo,)
    if fInstitucion:
        cWhe += " AND fInstitucion = %s "
        params += (fInstitucion,)
    if fCtaContab:
        cWhe += " AND fCtaContab = %s "
        params += (fCtaContab,)
    if dPeriodo:
        cWhe += " AND dMovim >= %s AND dMovim <= %s "
        params += (dPeriodo.inicio(), dPeriodo.termino())
    if dMovinIni:
        cWhe += " AND dMovim >= %s "
        params += (dMovinIni,)
    if dMovinFin:
        cWhe += " AND dMovim < %s "
        params += (dMovinFin,)
    if bAsignadas != None:
        if bAsignadas:
            cWhe += " AND fCtaContab IS NOT NULL"
        elif bAsignadas:
            cWhe += " AND fCtaContab IS NULL"

    return db.sqlQuery(
        """SELECT pMovim, fArchivo, fInstitucion, fCtaBanco, fCtaContab, dMovim
                , cSucursal, cOperacion, cDescripcion, nAbono, nCargo, nSaldo, tCreacion
           FROM tMovim
           WHERE """
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )


def saldoCtaBanco(cnxDb, fInstitucion, dPeriodo=None, fCtaBanco=None):
    params = (fInstitucion,)
    cWhe = " c.fInstitucion = %s "

    if fCtaBanco:
        cWhe += " AND c.fCtaBanco = %s "
        params += (fCtaBanco,)
    if dPeriodo:
        cWhe += " AND m.dMovim >= %s AND m.dMovim <= %s "
        params += (dPeriodo.inicio(), dPeriodo.termino())

    arr = db.sqlQuery(
        """SELECT c.pCtaBanco, c.fInstitucion, c.fBanco, c.cNombre, c.cCuenta
                , m.pMovim, m.dMovim, m.nSaldo
            FROM  tCtaBanco c
                  INNER JOIN tMovim m ON m.fCtaBanco = c.pCtaBanco 
            WHERE """
        + cWhe
        + "ORDER BY c.pCtaBanco, m.dMovim DESC, m.pMovim DESC",
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None

    if len(arr) == 1:
        return arr

    arrSaldo = []
    i = 0
    while i < len(arr):
        reg1 = arr[i]
        # Asigna el primer registro que es el último saldo porque está
        # ordenado descendente
        reg0 = reg1
        periodoYear = reg1["dMovim"].year
        periodoMonth = reg1["dMovim"].month
        arrSaldo.append(reg0)
        i += 1
        while (
            i < len(arr)
            and reg0["pCtaBanco"] == reg1["pCtaBanco"]
            and periodoYear == reg1["dMovim"].year
            and periodoMonth == reg1["dMovim"].month
        ):
            reg1 = arr[i]
            i += 1

    for reg in arrSaldo:
        dp = periodo(reg["dMovim"].year, reg["dMovim"].month, 1)
        del reg["pMovim"]
        del reg["dMovim"]
        reg["dPeriodo"] = dp.strftime("%Y-%m")
    return arrSaldo


def totalCtaContab(cnxDb, fInstitucion, pCtaContab=None, dPeriodo=None):
    cWhe = " WHERE c.fInstitucion = %s "
    params = (fInstitucion,)

    if pCtaContab:
        cWhe += " AND pCtaContab = %s "
        params += (pCtaContab,)
    if dPeriodo:
        cWhe += " AND m.dMovim >= %s AND m.dMovim <= %s "
        params += (dPeriodo.inicio(), dPeriodo.termino())

    arr = db.sqlQuery(
        """
        SELECT c.pCtaContab, c.fInstitucion, c.cCodigo, c.cNombre
             , SUBSTR( m.dMovim,1,7) dPeriodo, SUM(m.nAbono) nAbono, SUM(m.nCargo) nCargo
        FROM tCtaContab c
            INNER JOIN tMovim m ON m.fCtaContab = c.pCtaContab 
        """
        + cWhe
        + " GROUP BY c.pCtaContab, c.fInstitucion, c.cCodigo, c.cNombre, SUBSTR( m.dMovim,1,7) ",
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    return arr

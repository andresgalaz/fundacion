# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"


def insArchivo(
    cnxDb, fInstitucion, cNombre, cNombreS3, cUsuario, dInicio=None, dTermino=None
):
    (n, nId) = sqlExec(
        "INSERT INTO tArchivo( fInstitucion, cNombre, cNombreS3,  cUsuario,  dInicio,  dTermino ) VALUES ( %s, %s, %s, %s, %s, %s )",
        cnxDb=cnxDb,
        params=(fInstitucion, cNombre, cNombreS3, cUsuario, dInicio, dTermino),
    )
    return nId


def insCtaBanco(cnxDb, fInstitucion, fBanco, cNombre, cCuenta):
    (n, nId) = sqlExec(
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
    sqlExec(
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


def leeBanco(cnxDb, pBanco=None, cNombre=None):
    if pBanco:
        cWhe = " pBanco = %s "
        params = (pBanco,)
    elif cNombre:
        cWhe = " cNombre = %s "
        params = (cNombre,)
    else:
        raise AssertionError("No se indico ID ni Nombre para leer Banco")

    arr = sqlQuery(
        "SELECT pBanco, cNombre, tCreacion from tBanco WHERE " + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
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

    arr = sqlQuery(
        "SELECT pCtaBanco, fInstitucion, fBanco, cNombre, cCuenta, tCreacion from tCtaBanco WHERE "
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
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

    arr = sqlQuery(
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
    dMovinIni=None,
    dMovinFin=None,
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
    if dMovinIni:
        cWhe += " AND dMovin >= %s "
        params += (dMovinIni,)
    if dMovinFin:
        cWhe += " AND dMovin <= %s "
        params += (dMovinFin,)

    return sqlQuery(
        """SELECT pMovim, fArchivo, fInstitucion, fCtaBanco, fCtaContab, dMovim
                , cSucursal, cOperacion, cDescripcion, nAbono, nCargo, nSaldo, tCreacion
           FROM tMovim
           WHERE """
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )


def sqlQuery(cSql, cnxDb=None, cursor=None, params=None):
    bCloseCursor = False
    if not cursor:
        cursor = cnxDb.cursor()
        bCloseCursor = True

    cursor.execute(cSql, params)

    cols = cursor.description
    data = cursor.fetchall()
    if not data:
        if bCloseCursor:
            cursor.close()
        return None

    arr = []
    for reg in data:
        tmp = {}
        # Crea el array de salida con nomrbe de campos
        for idx, col in enumerate(reg):
            tmp[cols[idx][0]] = col
        arr.append(tmp)

    if bCloseCursor:
        cursor.close()

    return arr


def sqlExec(cSql, cnxDb=None, cursor=None, params=None):
    bCloseCursor = False
    if not cursor:
        cursor = cnxDb.cursor()
        bCloseCursor = True

    nCount = cursor.execute(cSql, params)
    nLastId = cursor.lastrowid

    if bCloseCursor:
        cursor.close()

    return (nCount, nLastId)

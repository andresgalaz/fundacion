# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

from cmp.appError import AppError
import cmp.db as db
import cmp.glUtil as u

import config


def delArchivo(cnxDb, pArchivo):
    regArch = leeArchivo(cnxDb, bUno=True, pArchivo=pArchivo)
    if not regArch:
        raise AppError("No existe archivo con ID {}".format(pArchivo))

    # Busca lo archivos que coincidan con Institución y Cuenta Bancaria para el pArchivo,
    # pero con fecha posterior
    if db.sqlQuery(
        """
        SELECT '1'
        FROM   tArchivo arc
        INNER JOIN ( SELECT fInstitucion, fCtaBanco, dInicio, dTermino
                    FROM   tArchivo
                    WHERE  pArchivo = %s ) sub ON sub.fInstitucion = arc.fInstitucion
                                            AND sub.fCtaBanco    = arc.fCtaBanco
        WHERE   arc.dInicio > sub.dInicio
        """,
        cnxDb=cnxDb,
        params=(pArchivo,),
    ):
        # Si hay archivos posteriores, primero se deben borrar los archivos posteriores
        raise AppError("Hay archivos posteriores, no se puede borrar")

    db.sqlExec(
        "DELETE FROM tMovim WHERE fArchivo=%s",
        cnxDb=cnxDb,
        params=(pArchivo,),
    )

    (n, nId) = db.sqlExec(
        "DELETE FROM tArchivo WHERE pArchivo=%s",
        cnxDb=cnxDb,
        params=(pArchivo,),
    )
    u.deleteFromS3(config.BUCKET_S3, regArch["cNombreS3"])

    # Cantidad registros eliminados
    return n


def delCtaBanco(cnxDb, pCtaBanco):
    db.sqlExec(
        "DELETE FROM tMovim WHERE fCtaBanco=%s",
        cnxDb=cnxDb,
        params=(pCtaBanco,),
    )

    (n, nId) = db.sqlExec(
        "DELETE FROM tCtaBanco WHERE pCtaBanco=%s",
        cnxDb=cnxDb,
        params=(pCtaBanco,),
    )
    # Cantidad registros eliminados
    return n


def delCtaContab(cnxDb, pCtaContab):
    db.sqlExec(
        "UPDATE tMovim SET fCtaContab = NULL WHERE fCtaContab=%s",
        cnxDb=cnxDb,
        params=(pCtaContab,),
    )

    (n, nId) = db.sqlExec(
        "DELETE FROM tCtaContab WHERE pCtaContab=%s",
        cnxDb=cnxDb,
        params=(pCtaContab,),
    )
    # Cantidad registros eliminados
    return n


def delInstitucion(cnxDb, pInstitucion):
    (n, nId) = db.sqlExec(
        "UPDATE tInstitucion SET bEnable='0' WHERE pInstitucion=%s",
        cnxDb=cnxDb,
        params=(pInstitucion,),
    )
    # Cantidad registros update
    return n


def delInstitucionUsuario(cnxDb, pInstitucion, pUsuario):
    (n, nId) = db.sqlExec(
        "DELETE FROM tInstitucionUsuario WHERE pInstitucion=%s AND pUsuario=%s",
        cnxDb=cnxDb,
        params=(pInstitucion, pUsuario),
    )
    return n


def insArchivo(
    cnxDb,
    fInstitucion,
    fCtaBanco,
    cNombre,
    cNombreS3,
    cUsuario,
    dInicio=None,
    dTermino=None,
    nSaldoInicio=None,
    nSaldoTermino=None,
):
    (n, nId) = db.sqlExec(
        """INSERT INTO tArchivo ( fInstitucion, fCtaBanco, cNombre, cNombreS3,  cUsuario
                               ,  dInicio,  dTermino, nSaldoInicio, nSaldoTermino )
           VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )""",
        cnxDb=cnxDb,
        params=(
            fInstitucion,
            fCtaBanco,
            cNombre,
            cNombreS3,
            cUsuario,
            dInicio,
            dTermino,
            nSaldoInicio,
            nSaldoTermino,
        ),
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


def leeArchivo(
    cnxDb,
    bUno=False,
    pArchivo=None,
    fInstitucion=None,
    fCtaBanco=None,
    cNombre=None,
    dMovim=None,
):
    cWhe = " 1=1 "
    params = ()

    if pArchivo:
        cWhe += " AND a.pArchivo = %s "
        params += (pArchivo,)
    if fInstitucion:
        cWhe += " AND a.fInstitucion = %s "
        params += (fInstitucion,)
    if fCtaBanco:
        cWhe += " AND a.fCtaBanco = %s "
        params += (fCtaBanco,)
    if cNombre:
        cWhe += " AND upper(a.cNombre) like %s "
        params += ("%" + cNombre + "%",)
    if dMovim:
        # dMovim debe estar entre la fecha de Inicio y termino del archivo
        cWhe += " AND %s BETWEEN a.dInicio AND a.dTermino "
        params += (dMovim,)

    arr = db.sqlQuery(
        """
        SELECT a.pArchivo     , a.fInstitucion, a.cNombre  , a.cNombreS3
             , a.cUsuario     , a.dInicio     , a.dTermino , a.nSaldoInicio
             , a.nSaldoTermino, a.tCreacion   
             , a.fCtaBanco    , c.cNombre     cNombreCuenta, c.cCuenta
             , b.cNombre cBanco
        FROM   tArchivo a
        INNER JOIN tCtaBanco c ON c.pCtaBanco = a.fCtaBanco
        INNER JOIN tBanco    b ON b.pBanco = c.fBanco
        WHERE
        """
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    if bUno == False:
        return arr
    if len(arr) > 1:
        raise AppError("Se esperaba un solo registro al leer archivo")
    return arr[0]


def leeBanco(cnxDb, bUno=False, pBanco=None, cNombre=None):
    if pBanco:
        cWhe = " pBanco = %s "
        params = (pBanco,)
    elif cNombre:
        cWhe = " cNombre = %s "
        params = (cNombre,)
    else:
        if bUno:
            raise AppError("No se indico ID ni Nombre para leer Banco")
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
        raise AppError("Se esperaba un solo registro al leer banco")
    return arr[0]


def leeCtaBanco(
    cnxDb, bUno=False, pCtaBanco=None, fBanco=None, cCuenta=None, fInstitucion=None
):
    cWhe = " 1=1 "
    params = ()

    if pCtaBanco:
        cWhe += " AND pCtaBanco = %s "
        params += (pCtaBanco,)
    if cCuenta:
        cWhe += " AND cCuenta = %s "
        params += (cCuenta,)
    if fInstitucion:
        cWhe += " AND fInstitucion = %s "
        params += (fInstitucion,)
    if fBanco:
        cWhe += " AND fBanco = %s "
        params += (fBanco,)

    arr = db.sqlQuery(
        """SELECT cta.pCtaBanco, cta.fInstitucion
                , cta.fBanco, bco.cNombre cBanco
                , cta.cNombre, cta.cCuenta, cta.tCreacion 
                
           FROM   tCtaBanco cta 
           INNER JOIN tBanco bco ON bco.pBanco = cta.fBanco
           WHERE {} """.format(
            cWhe
        ),
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    if bUno == False:
        return arr
    if len(arr) > 1:
        raise AppError("Se esperaba un solo registro al leer cuenta contable")
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
        "SELECT pCtaContab, fInstitucion, cCodigo, cNombre, bAbono, bCargo, tCreacion from tCtaContab WHERE "
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    if bUno == False:
        return arr
    if len(arr) > 1:
        raise AppError("Se esperaba un solo registro al leer cuenta contable")
    return arr[0]


def leeInstitucion(cnxDb, bUno=False, pInstitucion=None, cNombre=None):
    cWhe = " bEnable='1' "
    params = ()
    if pInstitucion:
        cWhe += " AND pInstitucion = %s "
        params += (pInstitucion,)
    elif cNombre:
        cWhe += " AND cNombre = %s "
        params += (cNombre,)

    arr = db.sqlQuery(
        "SELECT  pInstitucion, cNombre, tCreacion from tInstitucion WHERE " + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    if bUno:
        if len(arr) > 1:
            raise AppError("No se indico ID ni Nombre para leer Institución")
        return arr[0]

    return arr


def leeMovim(
    cnxDb,
    fArchivo=None,
    fInstitucion=None,
    fCtaBanco=None,
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
    if fCtaBanco:
        cWhe += " AND fCtaBanco = %s "
        params += (fCtaBanco,)
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
        else:
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


def leePeriodos(cnxDb, fInstitucion):
    return db.sqlQuery(
        """SELECT SUBSTR( m.dMovim,1,7) dPeriodo, m.nSaldo, t.nCantidadMovim 
           FROM   tMovim m 
                  INNER JOIN ( SELECT max(pMovim) pMovimLast,  COUNT(*) nCantidadMovim 
                               FROM   tMovim 
                               WHERE  fInstitucion = %s
                               GROUP BY SUBSTR( dMovim,1,7)
                              ) as t ON t.pMovimLast = m.pMovim        
           WHERE  m.fInstitucion = %s
           ORDER BY 1 DESC""",
        cnxDb=cnxDb,
        params=(fInstitucion, fInstitucion),
    )


def leeUsuario(
    cnxDb,
    bUno=False,
    pUsuario=None,
    cUsuario=None,
    cNombre=None,
    cEmail=None,
    bEnable=None,
    cEstado=None,
    pInstitucion=None,
):
    cWhe = " 1=1 "
    params = ()
    if pUsuario:
        cWhe += " AND pUsuario = %s "
        params += (pUsuario,)
    if cUsuario:
        cWhe += " AND cUsuario = %s "
        params += (cUsuario,)
    if cNombre:
        cWhe += " AND cNombre = %s "
        params += (cNombre,)
    if cEmail:
        cWhe += " AND cEmail = %s "
        params += (cEmail,)
    if bEnable != None:
        cWhe += " AND bEnable = %s "
        params += (bEnable,)
    if cEstado:
        cWhe += " AND cEmail = %s "
        params += (cEmail,)
    if pInstitucion:
        cWhe += """ AND EXISTS 
                    ( SELECT 1 
                      FROM  tInstitucionUsuario 
                      WHERE pInstitucion=%s 
                      AND   tInstitucionUsuario.pUsuario = tUsuario.pUsuario
                    ) """
        params += (cEmaipInstitucion,)

    arr = db.sqlQuery(
        "SELECT  pUsuario, cUsuario, cNombre, cEmail, bEnable, cEstado, tCreacion from tUsuario WHERE "
        + cWhe,
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    if bUno:
        if len(arr) > 1:
            raise AppError("Se esperaba leer un solo usuario")
        return arr[0]

    return arr


def leeUsuarioInstitucion(cnxDb, pInstitucion=None, cUsuario=None):
    lisUsr = leeUsuario(cnxDb, cUsuario=cUsuario)

    cWhe = " iu.pUsuario = %s "
    if pInstitucion:
        cWhe += " AND iu.pInstitucion = %s "

    cSql = """
    SELECT  i.pInstitucion, i.cNombre, i.bEnable
    FROM    tInstitucionUsuario iu 
            INNER JOIN tInstitucion i ON i.pInstitucion = iu.pInstitucion
    WHERE   {}""".format(
        cWhe
    )
    for usr in lisUsr:
        params = (usr["pUsuario"],)
        if pInstitucion:
            params += (pInstitucion,)

        lisInst = db.sqlQuery(cSql, cnxDb=cnxDb, params=params)
        if not lisInst:
            lisInst = []
        usr["instituciones"] = lisInst

    return lisUsr


def getSaldoAnterior(cnxDb, fCtaBanco, dFecCorte=None):
    cWhe = ""
    params = (fCtaBanco,)
    if dFecCorte:
        cWhe = " AND dMovim < %s "
        params += (dFecCorte,)

    arr = db.sqlQuery(
        """SELECT dMovim, nSaldo 
            FROM   tMovim
            WHERE  fCtaBanco = %s
            {}
            ORDER BY dMovim DESC, pMovim DESC
            LIMIT 1
            """.format(
            cWhe
        ),
        cnxDb=cnxDb,
        params=params,
    )
    if arr:
        return (arr[0]["dMovim"], float(arr[0]["nSaldo"]))
    return (None, 0)


def saldoCtaBanco(cnxDb, fInstitucion, dPeriodo=None, fCtaBanco=None):
    if not dPeriodo:
        raise AppError("Falta parámetro periodo")

    cWhe = " fInstitucion = %s "
    params = (fInstitucion,)
    if fCtaBanco:
        cWhe += " AND fCtaBanco = %s "
        params += (fCtaBanco,)

    arrSaldo = db.sqlQuery(
        """SELECT pCtaBanco, fInstitucion, fBanco, cNombre, cCuenta
           FROM   tCtaBanco 
           WHERE  {}
           ORDER  BY pCtaBanco
        """.format(
            cWhe
        ),
        cnxDb=cnxDb,
        params=params,
    )
    if not arrSaldo:
        return None

    for i, cta in enumerate(arrSaldo):
        mov = db.sqlQuery(
            """SELECT count(*) nCantidadMovim, count(fCtaContab) nMovimNoAsignados
           FROM   tMovim
           WHERE  fCtaBanco = %s
           AND    dMovim >= %s AND dMovim < %s
        """,
            cnxDb=cnxDb,
            params=(cta["pCtaBanco"], dPeriodo.inicio(), dPeriodo.termino()),
        )
        arrSaldo[i] = {**cta, **mov[0]}

    return arrSaldo


def totalCtaContab(cnxDb, fInstitucion, pCtaContab=None, dPeriodo=None):
    params = ()
    cWheOn = ""
    if dPeriodo:
        cWheOn += " AND m.dMovim >= %s AND m.dMovim <= %s "
        params += (dPeriodo.inicio(), dPeriodo.termino())

    cWhe = " WHERE c.fInstitucion = %s "
    params += (fInstitucion,)
    if pCtaContab:
        cWhe += " AND c.pCtaContab = %s "
        params += (pCtaContab,)

    arr = db.sqlQuery(
        """
        SELECT c.pCtaContab, c.fInstitucion, c.cCodigo, c.cNombre
             , SUBSTR( m.dMovim,1,7) dPeriodo, SUM(m.nAbono) nAbono, SUM(m.nCargo) nCargo
             , count(*) nCantidadMovim
        FROM tCtaContab c
            LEFT OUTER JOIN tMovim m ON m.fCtaContab = c.pCtaContab 
        """
        + cWheOn
        + cWhe
        + " GROUP BY c.pCtaContab, c.fInstitucion, c.cCodigo, c.cNombre, SUBSTR( m.dMovim,1,7) ",
        cnxDb=cnxDb,
        params=params,
    )
    if not arr:
        return None
    for reg in arr:
        if reg["nAbono"] == None:
            reg["nCantidadMovim"] = 0
            reg["nAbono"] = 0
            reg["nCargo"] = 0
            if dPeriodo:
                reg["dPeriodo"] = dPeriodo.strftime("%Y-%m")
    return arr


def updCtaBanco(cnxDb, pCtaBanco, fInstitucion, fBanco, cCuenta, cNombre):
    if pCtaBanco == None or pCtaBanco <= 0:
        arr = leeCtaBanco(
            cnxDb=cnxDb, fInstitucion=fInstitucion, fBanco=fBanco, cCuenta=cCuenta
        )
        if arr:
            raise AppError("Ya existe esta cuenta bancaria: " + cCuenta)
        # Si no existe se crea
        (n, nId) = db.sqlExec(
            "INSERT INTO tCtaBanco( fInstitucion, fBanco, cCuenta, cNombre ) VALUES ( %s, %s, %s, %s )",
            cnxDb=cnxDb,
            params=(fInstitucion, fBanco, cCuenta, cNombre),
        )
        return nId

    (n, nId) = db.sqlExec(
        "UPDATE tCtaBanco set fBanco = %s, cCuenta = %s, cNombre = %s WHERE pCtaBanco = %s",
        cnxDb=cnxDb,
        params=(fBanco, cCuenta, cNombre, pCtaBanco),
    )
    arr = leeCtaBanco(
        cnxDb=cnxDb, fInstitucion=fInstitucion, fBanco=fBanco, cCuenta=cCuenta
    )
    if len(arr) > 1:
        raise AppError("Ya existe esta cuenta bancaria: " + cCuenta)

    return n


def updCtaContab(cnxDb, pCtaContab, fInstitucion, cCodigo, cNombre, bAbono, bCargo):
    if pCtaContab == None or pCtaContab <= 0:
        arr = leeCtaContab(cnxDb=cnxDb, fInstitucion=fInstitucion, cCodigo=cCodigo)
        if arr:
            raise AppError("Ya existe una cuenta contable con el código: " + cCodigo)
        # Si no existe se crea
        (n, nId) = db.sqlExec(
            "INSERT INTO tCtaContab( fInstitucion, cCodigo, cNombre, bAbono, bCargo ) VALUES ( %s, %s, %s, %s, %s )",
            cnxDb=cnxDb,
            params=(fInstitucion, cCodigo, cNombre, bAbono, bCargo),
        )
        return nId

    (n, nId) = db.sqlExec(
        "UPDATE tCtaContab set cCodigo = %s, cNombre = %s, bAbono = %s, bCargo = %s WHERE pCtaContab = %s",
        cnxDb=cnxDb,
        params=(cCodigo, cNombre, bAbono, bCargo, pCtaContab),
    )
    arr = leeCtaContab(cnxDb=cnxDb, fInstitucion=fInstitucion, cCodigo=cCodigo)
    if len(arr) > 1:
        raise AppError("Ya existe una cuenta contable con el código: " + cCodigo)

    return n


def updInstitucion(cnxDb, fInstitucion, cNombre):
    if fInstitucion == None or fInstitucion <= 0:
        arr = leeInstitucion(cnxDb=cnxDb, cNombre=cNombre)
        if arr:
            raise AppError("Ya existe una institucion con el nombre: " + cNombre)
        # Si no existe se crea
        (n, nId) = db.sqlExec(
            "INSERT INTO tInstitucion( cNombre ) VALUES ( %s )",
            cnxDb=cnxDb,
            params=(cNombre),
        )
        return nId

    (n, nId) = db.sqlExec(
        "UPDATE tInstitucion set cNombre = %s WHERE pInstitucion = %s",
        cnxDb=cnxDb,
        params=(cNombre, fInstitucion),
    )
    arr = leeInstitucion(cnxDb=cnxDb, cNombre=cNombre)
    if arr and len(arr) > 1:
        raise AppError("Ya existe una institucion con el nombre: " + cNombre)

    return n


def updInstitucionUsuario(cnxDb, pInstitucion, pUsuario):
    if db.sqlQuery(
        "SELECT 1 FROM tInstitucionUsuario WHERE pInstitucion=%s AND pUsuario=%s",
        cnxDb=cnxDb,
        params=(pInstitucion, pUsuario),
    ):
        # Ya existe la relación
        return

    db.sqlExec(
        "INSERT INTO tInstitucionUsuario( pInstitucion, pUsuario ) VALUES ( %s, %s )",
        cnxDb=cnxDb,
        params=(pInstitucion, pUsuario),
    )


def updMovimAsigna(cnxDb, pMovim, fCtaContab, fInstitucion):
    (n, nId) = db.sqlExec(
        "UPDATE tMovim set fCtaContab = %s WHERE pMovim = %s and fInstitucion=%s",
        cnxDb=cnxDb,
        params=(fCtaContab, pMovim, fInstitucion),
    )
    return n


def updUsuario(
    cnxDb, cNombre, cUsuario, cEmail, bEnable=True, cEstado="CONFIRMED", **_
):
    arr = leeUsuario(cnxDb=cnxDb, bUno=True, cUsuario=cUsuario)
    if arr:
        # SI existe se actuliza el resto de los campos
        pUsuario = arr["pUsuario"]
        (n, nId) = db.sqlExec(
            "UPDATE tUsuario set cNombre=%s, cEmail=%s, bEnable=%s, cEstado=%s WHERE pUsuario = %s",
            cnxDb=cnxDb,
            params=(cNombre, cEmail, bEnable, cEstado, pUsuario),
        )
        return n

    (n, nId) = db.sqlExec(
        "INSERT INTO tUsuario( cNombre, cUsuario, cEmail, bEnable, cEstado ) VALUES ( %s, %s, %s, %s, %s )",
        cnxDb=cnxDb,
        params=(cNombre, cUsuario, cEmail, bEnable, cEstado),
    )
    return nId

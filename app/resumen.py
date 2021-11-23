# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import re
from request_helper import multipart
from unicodedata import normalize

# Bibliorecas propias
import dataMng as dm
import db
import globalUtil as u

BUCKET_S3 = "fundaciones"

# La función upload es la principal, que recibe el evento
# desde la WEB


def buscaCelda(data, key, addKey=""):
    for i, r in enumerate(data):
        for j, c in enumerate(r):
            if not type(c) is str or c == "":
                continue
            # Elimina acentos y tildes
            c = normalize("NFKD", c).encode("ascii", "ignore").decode("ascii").upper()
            if key == c or key + addKey == c:
                # print(r[j])
                return i, j
    return -1, -1


def buscaFila(data, keys):
    fila = -1
    cols = {}
    for key in keys:
        if type(key) is str:
            cols[key] = -1
        else:
            cols[key[0]] = -1

    # recorre filas
    for i, r in enumerate(data):
        # Limpia cols
        for k in cols.keys():
            cols[k] = -1
        # Recorre colmunas
        for j, c in enumerate(r):
            if not type(c) is str or c == "":
                continue
            # Elimina acentos y tildes
            c = normalize("NFKD", c).encode("ascii", "ignore").decode("ascii").upper()

            # Busca en lista de claves
            for key in keys:
                if type(key) is str:
                    # Busca claves string
                    if key in c:
                        fila = i
                        cols[key] = j
                        break
                else:
                    # Busca claves tuplas
                    for subKey in key:
                        if subKey in c:
                            fila = i
                            cols[key[0]] = j
                            break

        # No se encontró ninguna de las columnas buscadas
        if fila == -1:
            continue

        # Verifica que todas las claves hayan sido encontradas en la fila
        maxCol = -1
        for k in cols.keys():
            if cols[k] == -1:
                # La fila no está completa con todas las claves
                fila = -1
                break
            if maxCol < cols[k]:
                maxCol = cols[k]
        # Se encontró una fila con todas las claves
        if fila >= 0:
            break

    return {"fila": fila, "max_col": maxCol, "columnas": cols}


def grabaResumen(cnxDb, cUsuario, nInstitucion, nBanco, nArchivo, cArchivoS3):
    if u.isExcelS3(BUCKET_S3, cArchivoS3):
        m = u.parseExcel(BUCKET_S3, cArchivoS3)
    else:
        m = u.parseCsv(BUCKET_S3, cArchivoS3)
    # print(m)
    cFundacion = None
    cCuenta = None
    idCuenta = m[0][0]
    if re.search("[\\(\\)]| cta:+", idCuenta):
        arr = re.split("[\\(\\)]| cta:+", idCuenta)
        cFundacion = arr[0]
        cCuenta = arr[3]
    else:
        (i, j) = buscaCelda(m, "RAZON SOCIAL", ":")
        if i >= 0 and j >= 0:
            cFundacion = m[i][j + 1]
        (i, j) = buscaCelda(m, "CUENTA", ":")
        if i >= 0 and j >= 0:
            cCuenta = m[i][j + 1]

    if not cFundacion or not cCuenta:
        raise AssertionError("No se encontró en el archivo Razón Social y/o Cuenta")

    resp = buscaFila(
        m,
        [
            "FECHA",
            "SUCURSAL",
            ("OPERACION", "NOPERACION", "DOCTO"),
            ("DESCRIPCION", "DETALLE"),
            ("CARGO", "CHEQUE"),
            ("ABONO", "DEPOSITO"),
            "SALDO",
        ],
    )

    if resp["fila"] < 0:
        raise AssertionError("No se encontró encabezado de movimientos")

    ctaBanco = dm.leeCtaBanco(cnxDb, cCuenta=cCuenta)
    if ctaBanco:
        fCtaBanco = ctaBanco["pCtaBanco"]
    else:
        fCtaBanco = dm.insCtaBanco(cnxDb, nInstitucion, nBanco, None, cCuenta)

    for i in range(resp["fila"] + 1, len(m)):
        # print(m[i])
        if len(m[i]) < resp["max_col"]:
            continue
        fecha = u.str2date(m[i][resp["columnas"]["FECHA"]])
        if not fecha:
            continue
        sucursal = m[i][resp["columnas"]["SUCURSAL"]]
        nroOperacion = m[i][resp["columnas"]["OPERACION"]]
        descripcion = m[i][resp["columnas"]["DESCRIPCION"]]
        cargo = u.str2number(m[i][resp["columnas"]["CARGO"]])
        abono = u.str2number(m[i][resp["columnas"]["ABONO"]])
        saldo = u.str2number(m[i][resp["columnas"]["SALDO"]])

        dm.insMovim(
            cnxDb,
            fInstitucion=nInstitucion,
            fArchivo=nArchivo,
            fCtaBanco=fCtaBanco,
            dMovim=fecha,
            cSucursal=sucursal,
            cOperacion=nroOperacion,
            cDescripcion=descripcion,
            nAbono=abono,
            nCargo=cargo,
            nSaldo=saldo,
        )


def upload(event):
    cnxDb = db.conecta()
    if not cnxDb:
        raise AssertionError("Error al conectar a la base de datos")

    params = multipart(event)
    # Institucion
    if not "institucion" in params:
        raise AssertionError("Falta parámetro: institucion")
    nInstitucion = u.str2number(params["institucion"])
    if not nInstitucion:
        raise AssertionError("Parámetro 'institucion' debe ser numérico")
    if not "usuario" in params:
        raise AssertionError("Falta parámetro: usuario")

    # Banco
    if not "banco" in params:
        raise AssertionError("Falta parámetro: banco")
    nBanco = u.str2number(params["banco"])
    if not nBanco:
        raise AssertionError("Parámetro 'banco' debe ser numérico")

    # Usuario
    if not "usuario" in params:
        raise AssertionError("Falta parámetro: usuario")

    cUsuario = params["usuario"]
    if not "archivo" in params:
        raise AssertionError("Falta upload 'archivo'")

    contenido = params["archivo"]["contenido"]
    fileName = params["archivo"]["file_name"]
    cArchivoS3 = "{}/{}/{}_{}_{}".format(
        "upload", nInstitucion, u.fechaIso(), cUsuario, fileName
    )
    # Graba archivo en S3
    u.strToS3(BUCKET_S3, cArchivoS3, contenido.encode("iso-8859-1"))

    # Crea un registro asociado en la BD
    fArchivo = dm.insArchivo(
        cnxDb,
        fInstitucion=nInstitucion,
        cNombre=fileName,
        cNombreS3=cArchivoS3,
        cUsuario=cUsuario,
    )
    grabaResumen(cnxDb, cUsuario, nInstitucion, nBanco, fArchivo, cArchivoS3)
    lisMovim = dm.leeMovim(cnxDb, fArchivo=fArchivo)
    cnxDb.commit()
    cnxDb.close()

    return lisMovim
# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import re
from unicodedata import normalize

# Bibliorecas propias
import config

from cmp.appError import AppError
import cmp.db as db
import cmp.glUtil as u
from cmp.requestHlp import multipart, getParam


import dataMng as dm

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


def fila2movim(fila, colName):
    mov = dict(
        dMovim=u.str2date(fila[colName["FECHA"]]),
        cSucursal=fila[colName["SUCURSAL"]],
        cOperacion=fila[colName["OPERACION"]],
        cDescripcion=fila[colName["DESCRIPCION"]],
        nCargo=u.str2number(fila[colName["CARGO"]]),
        nAbono=u.str2number(fila[colName["ABONO"]]),
        nSaldo=u.str2number(fila[colName["SALDO"]]),
    )
    if (
        mov["dMovim"] == None
        or mov["nCargo"] == None
        or mov["nAbono"] == None
        or mov["nSaldo"] == None
    ):
        return None
    return mov


def grabaResumen(cnxDb, cUsuario, nInstitucion, nBanco, cArchivo, contenido):
    try:
        contenido = contenido.encode("iso-8859-1")
    except:
        pass

    # Es necesario esperar unos milisegundos para que el archivo esté presente
    if u.isExcel(contenido):  # .encode("iso-8859-1")):
        # m = u.parseExcel(config.BUCKET_S3, cArchivoS3)
        m = u.parseExcel(contenido)
    else:
        # m = u.parseCsv(config.BUCKET_S3, cArchivoS3)
        m = u.parseCsv(contenido)  # .encode("iso-8859-1"))
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
        raise AppError("No se encontró en el archivo Razón Social y/o Cuenta")

    # Valida cuenta bancaria
    ctaBanco = dm.leeCtaBanco(
        cnxDb, bUno=True, fInstitucion=nInstitucion, fBanco=nBanco, cCuenta=cCuenta
    )
    if ctaBanco:
        fCtaBanco = ctaBanco["pCtaBanco"]
    else:
        raise AppError(
            "No existe cuenta bancaria número {}, para el banco seleccionado".format(
                cCuenta
            )
        )

    # Busca area de la matriz donde están los movimientos
    infoMovim = buscaFila(
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

    if infoMovim["fila"] < 0:
        raise AppError("No se encontró encabezado de movimientos")

    # Transfiere a una arreglo de dict de movimientos
    arrMovim = []
    for i in range(infoMovim["fila"] + 1, len(m)):
        if len(m[i]) < infoMovim["max_col"]:
            continue
        mov = fila2movim(m[i], infoMovim["columnas"])
        if not mov:
            continue
        arrMovim.append(mov)

    # Archivo vacío
    if len(arrMovim) == 0:
        raise AppError("No se puedo leer registros de movimientos dentro del archivo")

    # Valida fecha y saldo inicial contra el último saldo de la cuenta bancaria
    (dMovimAnterior, nSaldoAnterior) = dm.getSaldoAnterior(cnxDb, fCtaBanco)
    if dMovimAnterior:
        if dMovimAnterior > arrMovim[0]["dMovim"]:
            raise AppError(
                "Ya existen movimientos posteriores ingresados. Fecha último movimiento={}".format(
                    dMovimAnterior.strftime("%d/%m/%Y")
                )
            )
        nSaldoControl = nSaldoAnterior
        nSaldoAnterior += arrMovim[0]["nAbono"] - arrMovim[0]["nCargo"]
        if nSaldoAnterior != arrMovim[0]["nSaldo"]:
            raise AppError(
                "Saldo anterior no coincide con el del archivo. Saldo Anterior={}".format(
                    nSaldoAnterior
                )
            )
    else:
        # No hay saldo anterior, se constuyr a partir del primer registro
        nSaldoControl = (
            arrMovim[0]["nSaldo"] - arrMovim[0]["nAbono"] + arrMovim[0]["nCargo"]
        )

    # Valida consistencia de saldos dentro del archivo mismo
    for mov in arrMovim:
        nSaldoControl += mov["nAbono"] - mov["nCargo"]
        if nSaldoControl != mov["nSaldo"]:
            raise AppError(
                "Los movmientos no son consistentes con el saldo. Ver movimiento fecha {}, decripcion {}, abono {}, cargo {}, saldo {} ".format(
                    mov["dMovim"].strftime("%d/%m/%Y"),
                    mov["cDescripcion"],
                    mov["nAbono"],
                    mov["nCargo"],
                    mov["nSaldo"],
                )
            )
    # Esta todo OK, se graba archivo y movimientos
    cArchivoS3 = "{}/{}/{}_{}_{}".format(
        "upload", nInstitucion, u.fechaIso(), cUsuario, cArchivo
    )
    # Graba archivo en S3
    u.strToS3(config.BUCKET_S3, cArchivoS3, contenido)  # .encode("iso-8859-1"))

    # Crea un registro asociado en la BD
    fArchivo = dm.insArchivo(
        cnxDb,
        fInstitucion=nInstitucion,
        fCtaBanco=fCtaBanco,
        cNombre=cArchivo,
        cNombreS3=cArchivoS3,
        cUsuario=cUsuario,
        dInicio=arrMovim[0]["dMovim"],
        nSaldoInicio=arrMovim[0]["nSaldo"],
        dTermino=arrMovim[-1:][0]["dMovim"],
        nSaldoTermino=arrMovim[-1:][0]["nSaldo"],
    )

    # Inserta los movimientos
    for mov in arrMovim:
        dm.insMovim(
            cnxDb,
            fInstitucion=nInstitucion,
            fArchivo=fArchivo,
            fCtaBanco=fCtaBanco,
            **mov
        )


def upload(event):
    params = multipart(event)

    nInstitucion = getParam(params, "institucion", obligatorio=True, tipo=int)
    cUsuario = getParam(params, "usuario", obligatorio=True, tipo=str)
    nBanco = getParam(params, "banco", obligatorio=True, tipo=int)

    contenido = params["archivo"]["contenido"]
    fileName = params["archivo"]["file_name"]

    cnxDb = db.conecta()
    pArchivo = grabaResumen(cnxDb, cUsuario, nInstitucion, nBanco, fileName, contenido)
    cnxDb.commit()

    lisMovim = dm.leeMovim(cnxDb, fArchivo=pArchivo)
    cnxDb.close()

    return lisMovim

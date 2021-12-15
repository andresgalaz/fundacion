# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.1"

import boto3
import csv
from datetime import datetime, date, timedelta
from decimal import Decimal
import io
import json
import numpy
import pandas
import re

from cmp.appError import AppError


class periodo(date):
    pass

    def inicio(self):
        return date(self.year, self.month, 1)

    def termino(self):
        m = self.month + 1
        y = self.year
        if m > 12:
            m = 1
            y += 1
        d = date(y, m, 1) - timedelta(days=1)
        return d


def addMonth(fecha, delta):
    m, y = (fecha.month + delta) % 12, fecha.year + ((fecha.month) + delta - 1) // 12
    if not m:
        m = 12
    d = min(
        fecha.day,
        [
            31,
            29 if y % 4 == 0 and (not y % 100 == 0 or y % 400 == 0) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][m - 1],
    )
    return fecha.replace(day=d, month=m, year=y)


def archivoToLinesArray(cArchivo):
    source = open(cArchivo, "r", encoding="iso8859-1")
    lines = []
    line = source.readline()
    while line:
        lines.append(line)
        line = source.readline()
    return lines


def csvLinesToMatriz(lines):
    # recorre los registros y analisa CSV
    csvIter = csv.reader(lines, delimiter=";")
    ln = 0
    matriz = []
    for row in csvIter:
        # Elimina celdas vacías del final
        i = len(row) - 1
        while i >= 0 and row[i] == "":
            del row[i]
            i -= 1
        matriz.append(row)
    return matriz


def fechaIso(fecha=datetime.today(), formato="%Y%m%d_%H%M%S"):
    return datetime.strftime(fecha, formato)


def fmtDate(dFecha):
    if isinstance(dFecha, str):
        dFecha = str2date(dFecha)
    if dFecha:
        return datetime.strftime(dFecha, "%d/%m/%Y")
    return None


def isCero(v):
    if v == None:
        return True
    return v == 0


def isEmpty(v):
    if v == None:
        return True
    if not type(v) is str:
        v = str(v)
    return v.strip() == ""


def matrizToCsvString(matriz):
    csvfile = io.StringIO()
    spamwriter = csv.writer(csvfile, delimiter=";")
    spamwriter.writerows(matriz)
    return csvfile.getvalue()


def object2json(o):
    if isinstance(o, date) or isinstance(o, datetime):
        return o.__str__()
    if isinstance(o, Decimal):
        return float(o)
    return o


def objet2str(o):
    if o == None:
        return ""
    if isinstance(o, int) or isinstance(o, float):
        return str(o)
    if isinstance(o, date) or isinstance(o, datetime):
        return datetime.strftime(o, "%d/%m/%Y")
    return o


def str2bool(o):
    if o == None:
        return False
    if type(o) == int or type(o) == float:
        return bool(o)
    if type(o) == str:
        o = o.upper()
        if (
            o == "1"
            or o == "Y"
            or o == "S"
            or o == "YES"
            or o == "SI"
            or o == "VERDADERO"
            or o == "TRUE"
        ):
            return True
        return False
    return bool(o)


def str2date(cFecha):
    try:
        cFecha = cFecha.replace(".", "-").replace("/", "-")
        if re.search(
            "^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])",
            cFecha,
        ):
            return datetime.strptime(cFecha[:10], "%d-%m-%Y").date()
        elif re.search(
            "^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])",
            cFecha,
        ):
            return datetime.strptime(cFecha[:10], "%Y-%m-%d").date()
    except:
        pass


def str2datetime(cFecha):
    try:
        cFecha = cFecha.replace(".", "-").replace("/", "-").replace("T", " ")
        if re.search(
            "^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(T| )([0-2][0-9])(:)([0-5][0-9])(:)([0-5][0-9])",
            cFecha,
        ):
            return datetime.strptime(cFecha[:19], "%d-%m-%Y %H:%M:%S")
        elif re.search(
            "^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(T| )([0-2][0-9])(:)([0-5][0-9])(:)([0-5][0-9])",
            cFecha,
        ):
            return datetime.strptime(cFecha[:19], "%Y-%m-%d %H:%M:%S")
    except:
        pass


def str2number(cNum):
    if type(cNum) is int or type(cNum) is float:
        return cNum
    cNum = cNum.replace(".", "")
    try:
        if cNum.find(",") >= 0:
            cNum = cNum.replace(",", ".")
            return float(cNum)
        return int(cNum)
    except:
        return None


def str2periodo(cFecha):
    try:
        dt = None
        cFecha = cFecha.replace(".", "-").replace("/", "-")
        if re.search(
            "^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$",
            cFecha,
        ):
            dt = datetime.strptime(cFecha, "%d-%m-%Y")
        elif re.search(
            "^([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$",
            cFecha,
        ):
            dt = datetime.strptime(cFecha, "%m-%Y")
        elif re.search(
            "^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$",
            cFecha,
        ):
            dt = datetime.strptime(cFecha, "%Y-%m-%d")
        elif re.search(
            "^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])$",
            cFecha,
        ):
            dt = datetime.strptime(cFecha, "%Y-%m")
        if dt:
            return periodo(dt.year, dt.month, 1)
    except:
        pass


def strToS3(bucketS3, filename, contenido):
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucketS3, Key=filename, Body=contenido)


def deleteFromS3(bucketS3, filename):
    s3 = boto3.client("s3")
    s3.delete_object(Bucket=bucketS3, Key=filename)


def isExcel(contenido):
    excelSigs = [
        ("xlsx", b"\x50\x4B\x05\x06", -22, 4),
        # Saved from Excel
        ("xls", b"\x09\x08\x10\x00\x00\x06\x05\x00", 512, 8),
        # Saved from LibreOffice Calc
        (
            "xls",
            b"\x09\x08\x10\x00\x00\x06\x05\x00",
            1536,
            8,
        ),
        # Saved from Excel then saved from Calc
        (
            "xls",
            b"\x09\x08\x10\x00\x00\x06\x05\x00",
            2048,
            8,
        ),
    ]
    # Prueba todas las firmas de Excel
    for sigType, sig, offset, size in excelSigs:
        bytes = contenido[offset : (size + offset)]
        if bytes == sig:
            return True

    return False


def isExcelS3(cBucketName, cFileName):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=cBucketName, Key=cFileName)
    return isExcel(response["Body"].read())


def parseExcel(contenido):
    df = pandas.read_excel(io.BytesIO(contenido), header=None)
    data = json.loads(df.to_json(orient="table"))["data"]
    # Convierte a Matriz
    M = []
    for r in data:
        R = []
        # Identidica la filas vacias y no las agrega
        bVacio = True
        for j, c in enumerate(r):
            if j == 0:
                continue
            v = r[c]
            if v is None:
                v = ""
            elif type(v) is str:
                v = v.strip().replace("\xa0", "")
                bVacio = False
            else:
                bVacio = False
            if not bVacio:
                R.append(v)
        M.append(R)
    return M


def parseCsv(contenido):
    sAnalisis = str(contenido)
    lineas = sAnalisis.count("\\n")
    if sAnalisis.count(";") >= lineas:
        separador = ";"
    elif sAnalisis.count("\\t") >= lineas:
        separador = "\t"
    else:
        raise AppError("Separador de columnas desconocido en este archivo")

    df = pandas.read_csv(io.BytesIO(contenido), sep=separador, header=None)
    # return df
    M = []
    for i in df:
        R = []
        for c in df[i]:
            if type(c) is float:
                if c != c:
                    c = ""
            R.append(c.strip())
        M.append(R)
    return numpy.array(M).transpose().tolist()


def getUsersCognito(idUserPoolCognito):
    cognito = boto3.client("cognito-idp")

    users = []
    next_page = None
    kwargs = {"UserPoolId": idUserPoolCognito}

    users_remain = True
    while users_remain:
        if next_page:
            kwargs["PaginationToken"] = next_page
        response = cognito.list_users(**kwargs)
        users.extend(response["Users"])
        next_page = response.get("PaginationToken", None)
        users_remain = next_page is not None

    resp = []
    for reg in users:
        att = reg["Attributes"]
        nameVal = [x for x in att if x["Name"] == "name"][0]["Value"]
        emailVal = [x for x in att if x["Name"] == "email"][0]["Value"]
        resp.append(
            {
                "cUsuario": reg["Username"],
                "cNombre": nameVal,
                "cEmail": emailVal,
                "bEnable": reg["Enabled"],
                "cEstado": reg["UserStatus"],
            }
        )
    return resp

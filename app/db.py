# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import pymysql


def conecta():
    try:
        cnxDb = pymysql.connect(
            host="dev-erp.cluster-cgarkdoeof64.us-east-1.rds.amazonaws.com",
            user="admin",
            password="xtroMile",
            database="db_fundacion",
        )
        if not cnxDb:
            raise AssertionError("Error al conectar a la base de datos")

        print("conecta DB")
        return cnxDb
    except pymysql.Error as e:
        print(e)
        raise AssertionError("Error inesperado al conectar: ") + str(e)


def close(cnxDb):
    print("Desconecta DB")
    try:
        if cnxDb:
            cnxDb.close()
    except pymysql.Error as e:
        pass


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

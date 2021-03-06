# -*- coding: utf-8 -*-
__author__ = "Andrés Galaz"
__license__ = "LGPL"
__email__ = "andres.galaz@gmail.com"
__version__ = "v1.0"

import pymysql

import config
from cmp.appError import AppError


def conecta():
    try:
        cnxDb = pymysql.connect(
            host=config.DB["host"],
            user=config.DB["user"],
            password=config.DB["password"],
            database=config.DB["database"],
        )
        if not cnxDb:
            raise AppError("Error al conectar a la base de datos")

        return cnxDb
    except pymysql.Error as e:
        print("No se puedo concetar a la DB", str(e))
        raise AppError("Error inesperado al conectar: ") + str(e)


def close(cnxDb):
    try:
        if cnxDb:
            cnxDb.close()
    except pymysql.Error as e:
        pass


def sqlQuerySingle(cSql, cnxDb=None, cursor=None, params=None):
    bCloseCursor = False
    if not cursor:
        cursor = cnxDb.cursor()
        bCloseCursor = True

    cursor.execute(cSql, params)
    data = cursor.fetchall()
    if not data:
        if bCloseCursor:
            cursor.close()
        return None

    if bCloseCursor:
        cursor.close()

    return data[0][0]


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

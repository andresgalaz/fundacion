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
        # cnxDb.ping(reconnect=True)
        print("conecta DB")
        return cnxDb
    except pymysql.Error as e:
        print(e)


def close(cnxDb):
    print("Desconecta DB")
    try:
        if cnxDb:
            cnxDb.close()
    except pymysql.Error as e:
        pass

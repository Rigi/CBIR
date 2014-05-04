import os
from os.path import isfile

__author__ = 'Rigi'

import happybase


class HBase:
    # "Constants"
    CF_FEATURE = "feature"
    CF_SEPARATOR = ":"
    TABLE_NAME = "cbir"

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None
        self.initConnection()

    def initConnection(self):
        self.closeConnection()
        self.connection = happybase.Connection(self.host, int(self.port))
        # Create table if necessary
        # self.deleteTable()
        # self.removeInvalidImages()
        self.createTable()

    def closeConnection(self):
        if self.connection:
            self.connection.close()

    def listTable(self):
        return self.connection.tables()

    def createTable(self):
        if HBase.TABLE_NAME not in self.listTable():
            self.connection.create_table(HBase.TABLE_NAME, {HBase.CF_FEATURE: dict()})

    def deleteTable(self):
        self.connection.delete_table(HBase.TABLE_NAME, True)

    def putValue(self, row, col, value):
        t = self.connection.table(HBase.TABLE_NAME)
        t.put(row, {col: value})

    def putValues(self, col, features):
        t = self.connection.table(HBase.TABLE_NAME)
        b = t.batch()
        for row, value in features:
            b.put(row, {col: value})
        b.send()

    def getRow(self, row, col=None):
        t = self.connection.table(HBase.TABLE_NAME)
        return t.row(row, col)

    def scanTable(self, cols):
        t = self.connection.table(HBase.TABLE_NAME)
        return t.scan(columns=cols)

    def removeInvalidImages(self):
        b = self.connection.table(HBase.TABLE_NAME).batch()
        for key, value in self.scanTable(None):
            if not isfile(key):
                b.delete(key)
        b.send()

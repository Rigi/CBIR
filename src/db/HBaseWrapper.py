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
        self.connection = happybase.Connection(self.host, self.port)

    def listTable(self):
        return self.connection.tables()

    def createTable(self, table, families):
        if table not in self.listTable():
            self.connection.create_table(table, families)

    def deleteTable(self, table=TABLE_NAME):
        self.connection.delete_table(table, True)

    def putValue(self, table, row, col, value):
        t = self.connection.table(table)
        t.put(row, {col: value})

    def putValues(self, table, col, features):
        t = self.connection.table(table)
        b = t.batch()
        for row, value in features:
            b.put(row, {col: value})
        b.send()

    def getRow(self, table, row, col=None):
        t = self.connection.table(table)
        return t.row(row, col)

    def scanTable(self, table, cols):
        t = self.connection.table(table)
        return t.scan(columns=cols)

    def removeInvalidImages(self, table=TABLE_NAME):
        b = self.connection.table(table).batch()
        for key, value in self.scanTable(table, None):
            if not isfile(key):
                b.delete(key)
        b.send()


__author__ = 'Rigi'

import happybase


class HBase:
    def __init__(self, url):
        self.url = url
        self.connection = happybase.Connection(self.url)

    def listTable(self):
        return self.connection.tables()

    def createTable(self, table, families):
        return self.connection.create_table(table, families)

    def deleteTable(self, table):
        self.connection.delete_table(table, True)

    def putValue(self, table, row, col, value):
        t = self.connection.table(table)
        t.put(row, {col: value})

    def getRow(self, table, row, col=None):
        t = self.connection.table(table)
        return t.row(row, col)

    def scanTable(self, table, cols):
        t = self.connection.table(table)
        return t.scan(columns=cols)

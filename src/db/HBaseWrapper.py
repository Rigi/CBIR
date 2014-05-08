from numpy import ndarray, uint8
from os import path
from hashlib import md5
from src.readers.ImageReader import ImageReader

__author__ = 'Rigi'

import happybase


class HBase:
    # "Constants"
    CF_SEPARATOR = ":"

    TABLE_NAME = "cbir"
    CF_FEATURE = "feature"

    IMAGES_TABLE = "img"
    CF_IMAGE = "im"
    CQ_IMAGE_DATA = CF_IMAGE + CF_SEPARATOR + "data"
    CQ_IMAGE_SHAPE = CF_IMAGE + CF_SEPARATOR + "shape"
    CQ_IMAGE_SIZE = CF_IMAGE + CF_SEPARATOR + "size"
    CQ_IMAGE_PATH = CF_IMAGE + CF_SEPARATOR + "path"

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
        if HBase.IMAGES_TABLE not in self.listTable():
            self.connection.create_table(HBase.IMAGES_TABLE, {HBase.CF_IMAGE: dict()})

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
            if not path.isfile(key):
                b.delete(key)
        b.send()

    def uploadImages(self, paths):
        t = self.connection.table(HBase.IMAGES_TABLE)
        b = t.batch()
        for path, img in ImageReader(paths):
            tmp = path.split(path)
            m = md5(img.data)
            row = m.hexdigest() + tmp[1]
            b.put(row, {HBase.CQ_IMAGE_DATA: img.data})
            b.put(row, {HBase.CQ_IMAGE_SHAPE: "%s %s %s" % img.shape})
            b.put(row, {HBase.CQ_IMAGE_PATH: tmp[0]})
        b.send()

    def scanImages(self):
        t = self.connection.table(HBase.IMAGES_TABLE)
        s = t.scan()
        for row, cvalues in s:
            path = path.join(cvalues[HBase.CQ_IMAGE_PATH], row[32:])
            shape = [int(x) for x in str.split(cvalues[HBase.CQ_IMAGE_SHAPE])]
            img = ndarray(shape, uint8, cvalues[HBase.CQ_IMAGE_DATA])
            m = md5(img.data)
            assert m.hexdigest() == row[:32]
            yield path, img

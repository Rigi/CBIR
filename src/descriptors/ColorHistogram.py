import cv2
from numpy import *
from numpy.numarray.functions import reshape
from abstractdesc import AbstractDescriptor
from src.db.HBaseWrapper import HBase

__author__ = 'Rigi'


class ColorHistogram(AbstractDescriptor):
    CQ_COLOR_HIST = HBase.CF_FEATURE + HBase.CF_SEPARATOR + "color_hist"

    def __init__(self, i_source=None):
        super(ColorHistogram, self).__init__(i_source)

    def extract(self):
        for path, img in self.source:
            b = cv2.calcHist([img], [0], None, [64], [0, 256])
            g = cv2.calcHist([img], [1], None, [64], [0, 256])
            r = cv2.calcHist([img], [2], None, [64], [0, 256])
            h = array([r, g, b])
            cv2.normalize(h, h, 0, 255, cv2.NORM_MINMAX)
            self.features[path] = h

        return self.features

    def tostring(self):
        for k, v in self.features.items():
            yield k, v.data

    def fromstring(self, ival):
        src, val = ival
        buff = val.values()[0]
        arr = ndarray((3, 64, 1), float32, buff)
        self.features[src] = arr

    @classmethod
    def init_from_db(cls, scan):
        c = ColorHistogram()
        for k, v in scan:
            c.fromstring((k, v))
        c.source = c.features.keys()
        return c
import pickle
from os.path import isfile
from src.db.HBaseWrapper import HBase

__author__ = 'Rigi'


class SimpleQuery():

    def __init__(self, query_image=None, descriptor_cls=None, comparator_cls=None, database=None, reference_images=None):
        """
        @param query_image
        @param descriptor_cls
        @param database
        @param comparator_cls
        """
        self.query_image = query_image
        self.descriptor_cls = descriptor_cls
        self.comparator_cls = comparator_cls
        self.database = database
        self.reference_images = reference_images
        self.distance_list = None
        self.path = None

    def execute(self):
        ref_hist = None
        if self.reference_images:
            ref_hist = self.descriptor_cls(self.reference_images)
            ref_hist.extract()

        query_hist = self.descriptor_cls(self.query_image)
        query_hist.extract()

        if self.database:
            if ref_hist:
                self.database.putValues(self.descriptor_cls.column_qualifier(), ref_hist.tostring())
            scan = self.database.scanTable([self.descriptor_cls.column_qualifier()])
            ref_hist = self.descriptor_cls.init_from_db(scan)

        comp = self.comparator_cls()
        d = comp.get_distance(query_hist, ref_hist)
        self.distance_list = sorted(d.items(), key=lambda t: t[1], reverse=True)

    def best_matches(self, n):
        return self.distance_list[:n]

    def set_database(self, (host, port)):
        self.database = HBase(host, port)

    def get_database(self):
        return (self.database.host, self.database.port) if self.database else (None, None)

    def issaved(self):
        return self.path is not None

    def save(self, path=None):
        if path:
            self.path = path
        if self.path:
            f = open(self.path, 'wb')
            pickle.dump(self.descriptor_cls, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.comparator_cls, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.query_image, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.reference_images, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.get_database(), f, pickle.HIGHEST_PROTOCOL)
            f.close()

    def open(self, path):
        if path and isfile(path):
            f = open(path, 'rb')
            self.descriptor_cls = pickle.load(f)
            self.comparator_cls = pickle.load(f)
            self.query_image = pickle.load(f)
            self.reference_images = pickle.load(f)
            self.set_database(pickle.load(f))
            f.close()

    def kill(self):
        if self.database:
            self.database.closeConnection()

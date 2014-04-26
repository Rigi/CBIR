__author__ = 'Rigi'


class SimpleQuery():
    def __init__(self, query_image=None, descriptor_cls=None, comparator_cls=None, database=None, table_name=None):
        """
        @param query_image
        @param descriptor_cls
        @param database
        @param comparator_cls
        """
        self.query_image = query_image
        self.descriptor_cls = descriptor_cls
        self.database = database
        self.table_name = table_name
        self.comparator_cls = comparator_cls
        self.distance_list = None

    def execute(self):
        query_hist = self.descriptor_cls(self.query_image)
        scan = self.database.scanTable(self.table_name, [self.descriptor_cls.get_column_qualifier()])
        db_hist = self.descriptor_cls.init_from_db(scan)
        comp = self.comparator_cls()

        query_hist.extract()

        d = comp.get_distance(query_hist, db_hist)
        self.distance_list = sorted(d.items(), key=lambda t: t[1], reverse=True)

    def best_matches(self, n):
        return self.distance_list[:n]

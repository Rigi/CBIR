import abc

__author__ = 'Rigi'


class AbstractDescriptor():
    __metaclass__ = abc.ABCMeta

    def __init__(self, i_source):
        self.source = i_source
        self.features = dict()

    @abc.abstractmethod
    def extract(self):
        """ Extract the feature descriptor """

    @abc.abstractmethod
    def tostring(self):
        """ Deserialize """

    @abc.abstractmethod
    def fromstring(self, ival):
        """ Serialize """

    @classmethod
    @abc.abstractproperty
    def column_qualifier(cls):
        """ Get the column qualifier of descriptor  """

    @classmethod
    @abc.abstractmethod
    def init_from_db(cls, scan):
        """  """
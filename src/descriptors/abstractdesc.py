import abc

__author__ = 'Rigi'


class AbstractDescriptor:
    __metaclass__ = abc.ABCMeta

    def __init__(self, i_source):
        self.source = i_source

    @abc.abstractmethod
    def extract(self):
        """ Extract the feature descriptor """

    @abc.abstractmethod
    def tostring(self):
        """ Deserialize """

    @abc.abstractmethod
    def fromstring(self, i_str):
        """ Serialize """

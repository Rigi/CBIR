
__author__ = 'Rigi'

import json
import requests

class HBase:
    def __init__(self, url):
        self.url = url

    def getVersion(self):
        r = requests.get(self.url + "/version/cluster")
        return r.content

    def listTable(self):
        return requests.get(self.url)

    def putValue(self, table, row, col, value):
        return requests.put(self.url + "/" + table + "/" + row + "/" + col, "{'Row':{'@key':'" + row + "','Cell':{'@column':'" + col + "', '':'" + value + "'}}}")

    def createTable(self, table, column):
        schema = {'@name': table, 'ColumnSchema': [{'name': column}]}
        headers = {'content-type': 'application/json'}
        return requests.put(self.url + "/" + table + "/schema", data=json.dumps(schema), headers=headers)
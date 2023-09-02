# -*- coding: utf-8 -*-

import os, re
import json
import inspect
import rdflib, SPARQLWrapper

class SPARQLy:
    def __init__(self):
        self.sparql_endpoints = {}

    # query sparql_endpoint or local file
    #
    # query  : sparql query string
    # source : URL or local file
    #
    def query(self, source, query):
        if re.match(r'^(https?://)[^\s/$.?#].[^\s]*$', source[0]):
            return self.remote_query(sparql_endpoint=source[0], query=query)
        else:
            return self.local_query(rdf_files=source, query=query)

    # query local file
    #
    # rdf_files : list of rdf_file
    # query     : sparql query string
    #
    @classmethod
    def local_query(cls, rdf_files, query):
        graph = rdflib.Graph()
        for rdf_file in rdf_files:
            graph.parse(rdf_file)
        results = graph.query(query)
        serialize = results.serialize(format='json')
        return json.loads(serialize.decode('utf-8'))

    # query remote URL
    #
    # sparql_endpoint : URL
    # query           : sparql query string
    #
    def remote_query(self, sparql_endpoint, query):
        sparql = self.sparql_endpoints.get(sparql_endpoint, self.get_sparql_endpoint(sparql_endpoint))
        sparql.setQuery(query)
        sparql.setReturnFormat(SPARQLWrapper.JSON)
        return sparql.query().convert()

    # store sparql_endpoint in self.sparl_endpoints then return SPARQLWrapper instance
    #
    # sparql_endpoint : URL
    #
    def get_sparql_endpoint(self, sparql_endpoint):
        if sparql_endpoint not in self.sparql_endpoints:
            self.sparql_endpoints[sparql_endpoint] = SPARQLWrapper.SPARQLWrapper(sparql_endpoint)
        return self.sparql_endpoints[sparql_endpoint]

    # print self.query()['results']['bindings'] in table format
    #
    # data : self.query()['results']['bindings']
    #
    @classmethod
    def print_table(cls, data):
        # gather all unique column
        columns = list(set(key for record in data for key in record.keys()))

        table_data = []
        for record in data:
            row = [record[col]['value'] if col in record else '' for col in columns]
            table_data.append(row)

        # calculate the max widths for each column
        max_widths = [max([len(str(cell)) for cell in column] + [len(column)]) for column in zip(*table_data, columns)]

        # print column
        print(' ' + ' | '.join([column.center(width) for column, width in zip(columns, max_widths)]))

        # print horizontal line
        print("-" + "-+-".join(['-' * width for width in max_widths]) + "-")

        # align left for string, otherwise align right
        alignments = []
        for col in columns:
            # check if any entry in a column is of type 'typed-literal' and only contains digits (possibly including a decimal point)
            has_pure_number = any(
                record[col]['type'] == 'typed-literal' and re.match(r"^\d+(\.\d+)?$", record[col]['value'])
                for record in data if col in record
            )
            # if the column contains any pure numerical values, align right; else, align left
            alignments.append('r' if has_pure_number else 'l')

        # print row
        for row in table_data:
            print(' ' + ' | '.join([(str(cell).ljust(width) if alignment == 'l' else str(cell).rjust(width)) for cell, width, alignment in zip(row, max_widths, alignments)]))

    # return caller method name
    #
    @classmethod
    def method_name(cls):
        return inspect.currentframe().f_back.f_code.co_name

if __name__ == '__main__':
    pass

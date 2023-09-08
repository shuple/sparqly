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
    # query  : sparql string
    # source : URL or local file
    #
    def query(self, source, query):
        if re.match(r'^(https?://)[^\s/$.?#].[^\s]*$', source[0]):
            data = self.remote_query(sparql_endpoint=source[0], query=query)
        else:
            data = self.local_query(rdf_files=source, query=query)

        prefixes = self.get_prefixes(query)
        data['results']['bindings'] = self.substitute_uri_with_prefix(data['results']['bindings'], prefixes)
        return data

    # query local file
    #
    # rdf_files : list of rdf_file
    # query     : sparql string
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
    # query           : sparql string
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

    # extract PREFIX in query and store it in { PREFIX: URI } format
    #
    # query : sparql string
    #
    @classmethod
    def get_prefixes(cls, query):
        prefix_pattern = r'PREFIX\s+([a-z0-9_#-]+):\s+<([^>]+)>'
        if matches := re.findall(prefix_pattern, query, re.IGNORECASE | re.MULTILINE):
            return { match[0]: match[1] for match in matches }
        else:
            return {}

    # substitute URI with PREFIX
    #
    # bindings : cls.query()['results']['bindings']
    # prefixes : cls.get_prefixes()
    #
    @classmethod
    def substitute_uri_with_prefix(cls, bindings, prefixes):
        for binding in bindings:
            for key, item in binding.items():
                for field in ['value', 'datatype']:
                    item = cls.substitute_in_field(item, field, prefixes)
        return bindings

    # substitute the URI in a given field of the item with its corresponding PREFIX
    #
    # item     : bindings[i][key]
    # field    : 'value' or 'datatype'
    # prefixes : cls.get_prefixes()
    #
    @classmethod
    def substitute_in_field(cls, item, field, prefixes):
        for prefix, uri in prefixes.items():
            if field in item and item[field].startswith(uri):
                item[field] = item[field].replace(uri, f'{prefix}:')
        return item

    # print return value of cls.query()
    #
    # data   : cls.query()
    # format : 'json' or 'table'
    #
    @classmethod
    def print(cls, data, method):
        method = f'print_{method}'
        if hasattr(cls, method) and callable(getattr(cls, method)):
            return getattr(cls, method)(data)
        else:
            # default method
            print(json.dumps(data, indent=2, default=str))

    # print return value of cls.query() in table format
    #
    # data : cls.query()
    #
    @classmethod
    def print_table(cls, data):
        columns, bindings = data['head']['vars'], data['results']['bindings']
        if len(bindings) == 0:
            return

        table_data = []
        for record in bindings:
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
                for record in bindings if col in record
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

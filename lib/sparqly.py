# -*- coding: utf-8 -*-

import os, re
import json
import inspect
import rdflib, SPARQLWrapper

class SPARQLy:
    """ Provides an interface for interacting with SPARQL endpoints """

    def __init__(self):
        self.sparql_endpoints = {}

    def query(self, source, query):
        """
        Executes a SPARQL query against the RDF files or the remote endpoint.

        Args:
            source (str): The source file or the SPARQL remote endpoint.
            query (str): The SPARQL query string to be executed.

        Returns:
            dict: The result of the query as returned by rdflib or SPARQLWrapper.
        """
        if re.match(r'^(https?://)[^\s/$.?#].[^\s]*$', source[0]):
            data = self.remote_query(sparql_endpoint=source[0], query=query)
        else:
            data = self.local_query(rdf_files=source, query=query)

        prefixes = self.get_prefixes(query)
        data['results']['bindings'] = self.substitute_uri_with_prefix(data['results']['bindings'], prefixes)
        return data

    @classmethod
    def local_query(cls, rdf_files, query):
        """
        Executes a SPARQL query against the RDF files.

        Args:
            rdf_files (list): List of the RDF files.
            query (str): The SPARQL query string to be executed.

        Returns:
            dict: The result of the query as returned by rdflib.
        """
        dataset = rdflib.ConjunctiveGraph()

        # pass rdf_files argument into the default graph
        for rdf_file in rdf_files:
            if os.path.exists(rdf_file):
                dataset.parse(rdf_file)

        # extract all file paths from the FROM clauses and parse them into the default graph
        default_graph_files = re.findall(r'FROM\s*<([^>]+)>', query, re.IGNORECASE)
        for rdf_file in default_graph_files:
            dataset.parse(rdf_file)

        # Extract all file paths from the FROM NAMED clauses and parse them into named graphs
        named_graph_files = re.findall(r'FROM NAMED\s*<([^>]+)>', query, re.IGNORECASE)
        for rdf_file in named_graph_files:
            named_graph = rdflib.Graph(store=dataset.store, identifier=rdflib.URIRef(rdf_file))
            named_graph.parse(rdf_file)

        results = dataset.query(query)
        serialize = results.serialize(format='json')
        return json.loads(serialize.decode('utf-8'))

    def remote_query(self, sparql_endpoint, query):
        """
        Executes a SPARQL query against the remote endpoint.

        Args:
            sparl_endpoint (str): The SPARQL remote endpoint.
            query (str): The SPARQL query string to be executed.

        Returns:
            dict: The result of the query as returned by SPARQLWrapper.
        """
        sparql = self.sparql_endpoints.get(sparql_endpoint, self.get_sparql_endpoint(sparql_endpoint))
        sparql.setQuery(query)
        sparql.setReturnFormat(SPARQLWrapper.JSON)
        return sparql.query().convert()

    def get_sparql_endpoint(self, sparql_endpoint):
        """
        Retrieves or initializes a SPARQLWrapper instance for a given endpoint.

        Args:
            endpoint (str): The URL of the SPARQL endpoint.

        Returns:
            SPARQLWrapper.SPARQLWrapper: An instance of SPARQLWrapper configured for the specified endpoint.
        """
        if sparql_endpoint not in self.sparql_endpoints:
            self.sparql_endpoints[sparql_endpoint] = SPARQLWrapper.SPARQLWrapper(sparql_endpoint)
        return self.sparql_endpoints[sparql_endpoint]

    @classmethod
    def get_prefixes(cls, query):
        prefix_pattern = r'PREFIX\s+([a-z0-9_#-]+):\s+<([^>]+)>'
        """
        Extract PREFIX in the query and return it in { PREFIX: URI } format.

        Args:
            query (str): The SPARQL query string.

        Returns:
            dict: { PREFIX: URI }
        """
        if matches := re.findall(prefix_pattern, query, re.IGNORECASE | re.MULTILINE):
            return { match[0]: match[1] for match in matches }
        else:
            return {}

    @classmethod
    def substitute_uri_with_prefix(cls, bindings, prefixes):
        """
        Substitute URI with PREFIX in the bindings.

        Args:
            bindings (list): ['results']['bindings']
            prefixes (dict): Prefixes in the query.

        Returns:
            list: Bindings with URI substituted with provided prefixes.
        """
        for binding in bindings:
            for key, item in binding.items():
                for field in ['value', 'datatype']:
                    item = cls.substitute_in_field(item, field, prefixes)
        return bindings

    #
    #
    @classmethod
    def substitute_in_field(cls, item, field, prefixes):
        """
        Substitute the URI in a given field of the item with its corresponding PREFIX.

        Args:
            item     (str): An element from bindings.
            field    (str): 'value' or 'datatype'.
            prefixes (dict): Prefixes in the query.

        Returns:
            dict: Item with URI substituted with provided prefixes.
        """
        for prefix, uri in prefixes.items():
            if field in item and item[field].startswith(uri):
                item[field] = item[field].replace(uri, f'{prefix}:')
        return item

    @classmethod
    def print(cls, data, method):
        """
        Print data using callback.

        Args:
            data (list): Data to be printed
            method (str): Callback method name
        """
        method = f'print_{method}'
        if hasattr(cls, method) and callable(getattr(cls, method)):
            return getattr(cls, method)(data)
        else:
            # default method
            print(json.dumps(data, indent=2, default=str))

    @classmethod
    def print_table(cls, data):
        """
        Print data in table format.

        Args:
            data (dict): Data to be printed
        """
        columns, bindings = data['head']['vars'], data['results']['bindings']
        if len(bindings) == 0:
            return

        table_data = []
        for record in bindings:
            row = [record[col]['value'] if col in record else '' for col in columns]
            table_data.append(row)

        # calculate the max widths for each column
        data_widths = [max([len(str(cell)) for cell in column]) for column in zip(*table_data)]
        column_names_widths = [len(column) for column in columns]
        max_widths = [max(data, col_name) for data, col_name in zip(data_widths, column_names_widths)]

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

    @classmethod
    def method_name(cls):
        """ Return (str) caller method name """
        return inspect.currentframe().f_back.f_code.co_name

if __name__ == '__main__':
    pass

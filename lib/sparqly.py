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

    # return caller method name
    #
    @classmethod
    def method_name(cls):
        return inspect.currentframe().f_back.f_code.co_name

if __name__ == '__main__':
    pass

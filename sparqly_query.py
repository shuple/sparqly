# -*- coding: utf-8 -*-

import os, sys
import argparse, json

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{root_path}/lib')
import sparqly
import logging_wrapper as logging

# return example usage and exit program
#
def example():
    filename = os.path.basename(__file__)
    print(f'''   # {filename} - SPARQL query driver

    # default endpoint https://dbpedia.org/sparql and use query file dbpedia/sample.rq
    python3 {filename} dbpedia/sample.rq

    # custom endpoint or file and query from stdin
    python3 {filename} -s https://dbpedia.org/sparql 'query_string'
    ''')
    sys.exit(1)

# return command line arguments in dict
#
def parse_args():
    # application option
    parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    parser.add_argument('query', nargs='?', help='query string or file')
    parser.add_argument('-s', '--source', action='append', help='sparql endpoint or RDF file')
    parser.add_argument('-a', '--append-query', default='', help='append text to the end of the query')

    # example
    parser.add_argument('-e', '--example', action='store_true', default=False, help='print example then exit')

    # log option
    parser.add_argument('-l', '--log-file', default='', help='log to file')
    parser.add_argument(      '--log-level', default='info', help='debug, info, warn, error, critical')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='suppress stdout')

    # convert to dict
    args = vars(parser.parse_args())

    if args['example']:
        example()
    if args['query'] is None:
        parser.print_usage()
        sys.exit(1)

    # sparql_endpoint or rdf_file
    args['source'] = args['source'] or [ os.environ.get('source', 'https://dbpedia.org/sparql') ]

    return args

if __name__ == '__main__':
    args = parse_args()
    logging.init(args)

    if os.path.exists(args['query']):
        with open(args['query'], 'r') as fp:
            query = fp.read()
    else:
        query = args['query']

    graph = sparqly.SPARQLy()
    result = graph.query(args['source'], query + f" {args['append_query']}")
    print(json.dumps(result['results']['bindings'], indent=2, default=str))

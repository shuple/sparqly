# SPARQLy

SPARQLy is a Python CLI companion for effortless SPARQL endpoint and RDF file interactions.\
Send queries from stdin or files, access remote endpoints like DBpedia, and kickstart exploration with a sample DBpedia query.

## Requirement
The script requires Python3.

```bash
ptyhon3 --version
```

## Installation
Clone the repository.
```bash
git clone https://github.com/shuple/sparqly
```

Install ptyhon dependency packages.
```bash
pip3 install rdflib
pip3 install SPARQLWrapper
```

## Usage
Interact with the SPARQL endpoint at https://dbpedia.org/sparql execute a query retrieved from stdin.
```bash
python3 sparqly_query.py -s https://dbpedia.org/sparql '
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?bandMember
WHERE {
  dbr:The_Offspring dbo:bandMember ?bandMember .
}
'
```

Execute a query retrieved from a file.
```bash
python3 sparqly_query.py --source https://dbpedia.org/sparql sample.rq
```

Same as above, the default endpoint is https://dbpedia.org/sparql.
```bash
python3 sparqly_query.py sample.rq
```

The endpoint can also be a file. Utilize the --source flag to indicate multiple files in a chain.
```bash
python3 sparqly_query.py -s foaf_index.rdf -s sample.ttl sample.rq
```

## Changelog
##### 0.1a (2023-08-30)
- Initial Alpha Release.

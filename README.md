# SPARQLy

SPARQLy is a Python CLI companion for effortless SPARQL endpoint and RDF file interactions.\
Send queries from stdin or files, access remote endpoints like DBpedia, and kickstart exploration with a sample query.

## Requirement
The script requires Python 3.8 or above.

```bash
ptyhon3 --version
```
<pre>
Python 3.8.0
</pre>

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
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?bandMember ?givenName
WHERE {
  dbr:The_Offspring dbo:bandMember ?bandMember .
  ?bandMember rdf:type foaf:Person .
  ?bandMember foaf:givenName ?givenName
}
'
```
<pre>
       bandMember       |      givenName
------------------------+----------------------
 dbr:Noodles_(musician) | Kevin John Wasserman
 dbr:Dexter_Holland     | Bryan Keith Holland
</pre>

Execute a query retrieved from a file.
```bash
python3 sparqly_query.py -s https://dbpedia.org/sparql sample.rq
```

Same as above, the default endpoint is https://dbpedia.org/sparql.
```bash
python3 sparqly_query.py sample.rq
```

Change the default endpoint by assigning $sparqly_endpoint environment variable.
```bash
export sparqly_endpoint='https://dbpedia.org/sparql'
```

Append text to the end of the query.
```bash
python3 sparqly_query.py sample.rq --append 'LIMIT 10'
```

The endpoint can also be a file. Utilize the -s flag to indicate multiple files in a chain.
```bash
python3 sparqly_query.py -s foaf_index.rdf -s sample.ttl sample.rq
```

## Changelog
##### 0.1a (2023-08-30)
- Initial Alpha Release.

# from wikidata.client import Client
# client = Client()  # doctest: +SKIP
# entity = client.get('Q20145', load=True)
# image_prop = client.get('P18')
# image = entity[image_prop]

# import wikipedia2
#
# for i in range(10):
#     ny = wikipedia2.page("market share")
# print(ny.links)

# with open('page_links_en.ttl') as file:
#     for line in file:
#         print(line)
from pprint import pprint

from SPARQLWrapper import SPARQLWrapper, JSON, DIGEST

sparql = SPARQLWrapper("http://localhost:8890/DAV")  # http://dbpedia.org/sparql
sparql.setHTTPAuth(DIGEST)
sparql.setCredentials('dba', 'dba')
for i in range(100):
    sparql.setQuery("""
        SELECT * WHERE { 
            <http://dbpedia.org/resource/Asturias> <http://dbpedia.org/ontology/wikiPageWikiLink> ?o
        }    
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
# pprint(results)
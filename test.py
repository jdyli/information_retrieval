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
# from pprint import pprint
#
# from SPARQLWrapper import SPARQLWrapper, JSON, DIGEST
#
# sparql = SPARQLWrapper("http://localhost:8890/DAV")  # http://dbpedia.org/sparql
# sparql.setHTTPAuth(DIGEST)
# sparql.setCredentials('dba', 'dba')
# for i in range(100):
#     sparql.setQuery("""
#         SELECT * WHERE {
#             <http://dbpedia.org/resource/Asturias> <http://dbpedia.org/ontology/wikiPageWikiLink> ?o
#         }
#     """)
#
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
# pprint(results)

import sqlite3
from collections import namedtuple

from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
porter_stemmer = PorterStemmer()

Entry = namedtuple('Entry', 'a b')
stop_words = set(stopwords.words('english'))


def cleanup(a):
    sentence = a.lower().replace("_", " ")
    sentence = word_tokenize(sentence)
    sentence = [w for w in sentence if not w in stop_words and w.isalpha()]  # remove stopwords
    for i in range(len(sentence)):
        sentence[i] = porter_stemmer.stem(sentence[i])
    return " ".join(sentence)


def get_entries(path):
    with open(path, encoding="utf-8") as file:
        # an entry starts with `#@` line and ends with a blank line
        i = 0
        for line in file:
            i += 1
            if i == 1:
                continue
            if i > 100:
                break
            if i % 10000 == 0:
                print(i)
            split = line.split(" ")
            a = split[0].split('/')[-1].replace('>', '')
            b = split[2].split('/')[-1].replace('>', '')
            yield Entry(cleanup(a), cleanup(b))


with sqlite3.connect('example.db') as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS entries
             (a text, b text)''')
    conn.executemany('INSERT INTO entries VALUES (?,?)',
                     get_entries('../page_links_en.ttl'))
    conn.commit()
# conn.execute("INSERT INTO entries VALUES ('a', 'b')")
# conn.execute("SELECT * FROM entries").fetchall()

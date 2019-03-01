#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json as js
import os
import os.path

from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import scoring

class BM25model:
    def __init__(self, index):
        self.index = index

    # Parses a list of queries. Assuming the queries are in AND-form
    def query_parser(self, querylist, index):
        w = scoring.BM25F(B=0.75, content_B=1.0, K1=1.5)

        parsed_list = []
        parser = MultifieldParser(["table_ID", "page_title", "col_title", "body", "sec_title", "caption"], 
            schema=index.schema)

        with open(querylist, 'r') as file:
            list_of_queries = file.readlines()[1:]
            #for query in list_of_queries:
                #parsed_query_name = parser.parse(query.split(",",1)[1])
            parsed_query_name = parser.parse("world interest rates table")

            # Search parsed query
            with index.searcher(weighting=w) as s:
                results = s.search(parsed_query_name, limit=20, terms=True)
                print(results[1], "\n")
            
            """if results.has_matched_terms():
                # What terms matched in the results?
                print(results.matched_terms(), "\n")
                # What terms matched in each hit?
                for hit in results:
                    print(hit.matched_terms(), " hits ", "\n")
            """

            parsed_list.append(parsed_query_name)
        
        return parsed_list

def create_index(archive_name_path, archive_data_path, target_dir):
        with open(archive_name_path, 'r') as file:
            table_names = file.readlines()

        iter_tables = iter(table_names)
        next(iter_tables)
        table_names = [x.strip().split(",")[2] for x in iter_tables]
        table_location = [i.split("-")[1:3] for i in table_names]

        schema = Schema(table_ID=TEXT(stored=True),
                        page_title=TEXT(analyzer=StemmingAnalyzer()),
                        col_title=TEXT(analyzer=StemmingAnalyzer()),
                        body=TEXT(analyzer=StemmingAnalyzer()),
                        sec_title=TEXT(analyzer=StemmingAnalyzer()),
                        caption=TEXT(analyzer=StemmingAnalyzer()))

        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        ix = index.create_in(target_dir, schema)
        not_found = []
        for location in table_location[:15]:
            with open(archive_data_path + "re_tables-" + location[0] + ".json") as f:
                data = js.load(f)
                table_id = "table-" + location[0] + "-" + location[1]
                print(table_id)

                if table_id in data:
                    data = data[table_id]
                    data_pt = data["pgTitle"]
                    data_ct = " ".join(data["title"])
                    data_b = " ".join([" ".join(i) for i in data["data"]])
                    data_sect = data["secondTitle"]
                    data_cap = data["caption"]

                    writer = ix.writer()
                    writer.add_document(table_ID=table_id,
                                        page_title=data_pt,
                                        col_title=data_ct,
                                        body=data_b,
                                        sec_title=data_sect,
                                        caption=data_cap)
                    writer.commit()
                else:
                    not_found.append(table_id)
        print(not_found)
        return ix
        
archive_name_path = "qrels.csv"
archive_data_path = "tables/"
archive_query_path = "queries.csv"
target_dir = "index"
ix = create_index(archive_name_path, archive_data_path, target_dir)

# to do:
# - incorporting BM 25 scores in index (or TF or DF into the postings of each
# term)

model = BM25model(ix)

parsed_list = model.query_parser(archive_query_path, ix)
print(parsed_list[0])




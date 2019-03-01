#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import json as js
import os
import os.path
from collections import defaultdict

from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser


def create_index(archive_name_path, archive_data_path, target_dir):
    num_lines = sum(1 for line in open(archive_name_path))
    with open(archive_name_path, 'r') as file:
        table_names = file.readlines()

    iter_tables = iter(table_names)
    next(iter_tables)
    table_names = [x.strip().split(",")[2] for x in iter_tables]
    table_location = [i.split("-")[1:3] for i in table_names]

    schema = Schema(table_ID=TEXT(),
                    page_title=TEXT(analyzer=StemmingAnalyzer()),
                    col_title=TEXT(analyzer=StemmingAnalyzer()),
                    body=TEXT(analyzer=StemmingAnalyzer()),
                    sec_title=TEXT(analyzer=StemmingAnalyzer()),
                    caption=TEXT(analyzer=StemmingAnalyzer()))

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    ix = index.create_in(target_dir, schema)
    not_found = []
    count = 0
    for location in table_location:
        with open(archive_data_path + "re_tables-" + location[0] + ".json") as f:
            data = js.load(f)
            table_id = "table-" + location[0] + "-" + location[1]
            print(str(float(count) / float(num_lines)))
            count += 1
            if count > 62:
                break

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


def parse_queries():
    pass


def parse_qrels():
    results = defaultdict(lambda: defaultdict(int))
    with open("qrels.csv", newline="") as file:
        reader = csv.reader(file)
        iter_reader = iter(reader)
        next(iter_reader)
        for line in iter_reader:
            results[line[0]][line[2]] = int(line[3])
    return results


def main():
    archive_name_path = "qrels.csv"
    archive_data_path = "tables/"
    target_dir = "index"
    ix = create_index(archive_name_path, archive_data_path, target_dir)
    queries = parse_queries()
    qrels = parse_qrels()

    queries = [[1, "world interest rates table\n"],
               [2, "2008 beijing olympics\n"],
               [3, "fast cars\n"]]

    results = get_results(ix, queries, qrels)

    # to do:
    # - incorporting BM 25 scores in index (or TF or DF into the postings of each
    # term)


def get_results(ix, queries, qrels):
    results = defaultdict()
    for query in queries:
        with ix.searcher() as searcher:
            parser = QueryParser("content", ix.schema)
            myquery = parser.parse(queries[0][1])
            results[query] = searcher.search(myquery)


if __name__ == "__main__":
    main()

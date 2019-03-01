#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import json as js
import math
import os
import os.path
from collections import defaultdict

from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT
from whoosh.qparser import MultifieldParser

archive_name_path = "qrels.csv"
archive_data_path = "tables/"
target_dir = "index"


def parse_queries():
    results = []
    with open("queries.csv", newline="") as file:
        reader = csv.reader(file)
        iter_reader = iter(reader)
        next(iter_reader)
        for line in iter_reader:
            results.append(line)
    return results


def parse_qrels():
    results = defaultdict(lambda: defaultdict(int))
    with open("qrels.csv", newline="") as file:
        reader = csv.reader(file)
        iter_reader = iter(reader)
        next(iter_reader)
        for line in iter_reader:
            results[line[0]][line[2]] = int(line[3])
    return results


def create_index(query):
    with open(archive_name_path, 'r') as file:
        table_names = file.readlines()

    iter_tables = iter(table_names)
    next(iter_tables)
    queries = [x.strip().split(",")[0] for x in iter_tables]

    iter_tables = iter(table_names)
    next(iter_tables)
    table_names = [x.strip().split(",")[2] for x in iter_tables]
    table_location = [i.split("-")[1:3] for i in table_names]

    schema = Schema(title=TEXT(stored=True),
                    page_title=TEXT(analyzer=StemmingAnalyzer()),
                    col_title=TEXT(analyzer=StemmingAnalyzer()),
                    body=TEXT(analyzer=StemmingAnalyzer()),
                    sec_title=TEXT(analyzer=StemmingAnalyzer()),
                    caption=TEXT(analyzer=StemmingAnalyzer()))

    if not os.path.exists(target_dir + query):
        os.mkdir(target_dir + query)
    ix = index.create_in(target_dir + query, schema)
    not_found = []
    for table_query, location in zip(queries, table_location):
        if table_query != query:
            continue

        with open(archive_data_path + "re_tables-" + location[0] + ".json") as f:
            data = js.load(f)
            table_id = "table-" + location[0] + "-" + location[1]

            if table_id in data:
                data = data[table_id]
                data_pt = data["pgTitle"]
                data_ct = " ".join(data["title"])
                data_b = " ".join([" ".join(i) for i in data["data"]])
                data_sect = data["secondTitle"]
                data_cap = data["caption"]

                writer = ix.writer()
                writer.add_document(title=table_id,
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


def get_results(searcher, schema, query):
    parser = MultifieldParser(["title", "page_title", "col_title", "body", "sec_title", "caption"], schema)
    myquery = parser.parse(query[1])
    return searcher.search(myquery, limit=20)


def evaluate_results(query, results, qrels):
    score = 0
    for i in range(len(results.top_n)):
        score += float(qrels[query][results[i]["title"]]) / math.log(i + 2, 2)
    return score


def main():
    queries = parse_queries()
    qrels = parse_qrels()
    scores = []
    for query in queries:
        ix = create_index(query[0])
        with ix.searcher() as searcher:
            results = get_results(searcher, ix.schema, query)
            score = evaluate_results(query[0], results, qrels)
            print(str(query) + " - " + str(score))
            scores.append((query, score))
    with open("lexical.csv", "w+") as file:
        csv_writer = csv.writer(file)
        for score in scores:
            csv_writer.writerow([int(score[0][0]), score[1]])


if __name__ == "__main__":
    main()

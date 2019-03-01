#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json as js
import os
import os.path

from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT


def create_index(archive_name_path, archive_data_path, target_dir):
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
    for location in table_location:
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


def main():
    archive_name_path = "qrels.csv"
    archive_data_path = "tables/"
    target_dir = "index"
    index = create_index(archive_name_path, archive_data_path, target_dir)
    queries = parse_queries()


    # to do:
    # - incorporting BM 25 scores in index (or TF or DF into the postings of each
    # term)


if __name__ == "__main__":
    main()

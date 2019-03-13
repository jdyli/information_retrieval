import json
import os

from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT

from util import archive_name_path, target_dir, archive_data_path, parse_queries

"""
This file should be run before running lexical_single_field or lexical_multi_field. It builds for every query a separate
index containing the tables that were assessed by human judges for their relevance to the query.
"""


def create_index(query):
    with open(archive_name_path, 'r') as file:
        table_names = file.readlines()

    iter_tables = iter(table_names)
    next(iter_tables)
    queries = [int(x.strip().split(",")[0]) - 1 for x in iter_tables]

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

    if not os.path.exists(target_dir + str(query)):
        os.mkdir(target_dir + str(query))
    ix = index.create_in(target_dir + str(query), schema)
    not_found = []
    for table_query, location in zip(queries, table_location):
        if table_query != query:
            continue

        with open(archive_data_path + "re_tables-" + location[0] + ".json") as f:
            data = json.load(f)
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
    return ix


if __name__ == "__main__":
    queries = parse_queries()
    for query in queries:
        create_index(query[0])

import csv
import math
from functools import reduce

from whoosh import index
from whoosh.qparser import MultifieldParser

from util import parse_queries, parse_qrels, target_dir, evaluate_results


def get_results(searcher, schema, query):
    parser = MultifieldParser(["title", "page_title", "col_title", "body", "sec_title", "caption"], schema)
    myquery = parser.parse(query[1])
    return searcher.search(myquery, limit=20)


def main():
    queries = parse_queries()
    qrels = parse_qrels()
    scores = []
    normalized_scores = []
    for query in queries:
        ix = index.open_dir(target_dir + query[0])
        with ix.searcher() as searcher:
            results = get_results(searcher, ix.schema, query)
            score = evaluate_results(query[0], results, qrels)
            normalized_scores.append((query, score))
            print(str(query) + " - " + str(score))
    with open("lexical.csv", "w+") as file:
        csv_writer = csv.writer(file)
        for score in scores:
            csv_writer.writerow([int(score[0][0]), score[1]])
    with open("lexical_normalized.csv", "w+") as file:
        csv_writer = csv.writer(file)
        for score in normalized_scores:
            csv_writer.writerow([int(score[0][0]), score[1]])
    print("Average normalized score = " + str(
        reduce(lambda x, y: (0, x[1] + y[1]), normalized_scores)[1] / len(normalized_scores)))


if __name__ == "__main__":
    main()

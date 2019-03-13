from functools import reduce

from whoosh import index
from whoosh.qparser import MultifieldParser

from CoordinateAscent import CoordinateAscent
from util import evaluate_results, parse_queries, parse_qrels

"""
Implementation of Multi-field Document Ranking. Uses the indices built by index_creation.py and uses Coordinate Ascent
to find a local optimum for the parameters. It shows the average normalized NDCG score of all queries and also the set
of locally optimal parameters.
"""


archive_name_path = "qrels.csv"
archive_data_path = "tables/"
target_dir = "index"
k = 20


class Holder:
    queries, qrels = None, None


def get_results(searcher, schema, query, weights):
    parser = MultifieldParser(["title", "page_title", "col_title", "body", "sec_title", "caption"], schema, weights)
    myquery = parser.parse(query[1].replace(" ", " OR "))
    return searcher.search(myquery, limit=k)


def run(weights):
    scores = []
    for query in Holder.queries:
        ix = index.open_dir(target_dir + str(query[0]))
        with ix.searcher() as searcher:
            results = get_results(searcher, ix.schema, query, weights)
            score = evaluate_results(query[0], results, Holder.qrels)
            scores.append((query, score))
    return reduce(lambda x, y: (0, x[1] + y[1]), scores)[1] / len(scores)


def main():
    Holder.queries = parse_queries()
    Holder.qrels = parse_qrels()
    initial_weights = {
        "page_title": 1. / 5,
        "col_title": 1. / 5,
        "body": 1. / 5,
        "sec_title": 1. / 5,
        "caption": 1. / 5
    }
    best_params = CoordinateAscent(run).learn(initial_weights)
    print(best_params)
    print("Average normalized score = " + str(run(best_params)))


if __name__ == "__main__":
    main()

import csv
import math
from collections import defaultdict
from functools import reduce

from whoosh import index
from whoosh.qparser import MultifieldParser

from CoorAscent import CoorAscent

archive_name_path = "qrels.csv"
archive_data_path = "tables/"
target_dir = "index"


class Holder:
    queries = None
    qrels = None


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


def get_results(searcher, schema, query):
    results = {}
    for field in ["page_title", "col_title", "body", "sec_title", "caption"]:
        parser = MultifieldParser(["title", field], schema)
        myquery = parser.parse(query[1])
        results[field] = searcher.search(myquery, limit=20)
    return results


def evaluate_results(query, results, qrels, weights):
    score = 0
    for field, search_results in results.items():
        _score = 0
        for i in range(len(search_results.top_n)):
            _score += float(qrels[query][search_results[i]["title"]]) / math.log(i + 2, 2)
        score += _score * weights[field]
    return score


def get_max_score(results):
    score = 0
    for _, search_results in results.items():
        for i in range(len(search_results)):
            score += 2.0 / math.log(i + 2, 2)
    return score


def run(initial_weights):
    scores = []
    normalized_scores = []
    for query in Holder.queries:
        ix = index.open_dir(target_dir + query[0])
        with ix.searcher() as searcher:
            results = get_results(searcher, ix.schema, query)
            score = evaluate_results(query[0], results, Holder.qrels, initial_weights)
            scores.append((query, score))
            normalized_score = score / max(0.0000001, get_max_score(results))
            normalized_scores.append((query, normalized_score))
    print("tmp score: " + str(reduce(lambda x, y: (0, x[1] + y[1]), normalized_scores)[1] / len(normalized_scores)))
    return reduce(lambda x, y: (0, x[1] + y[1]), normalized_scores)[1] / len(normalized_scores)


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
    best_params = CoorAscent(run).learn(initial_weights)
    print(best_params)
    print("Average normalized score = " + str(run(best_params)))


if __name__ == "__main__":
    main()

import csv
import math
from collections import defaultdict

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
            results[int(line[0]) - 1][line[2]] = int(line[3])
    return results


def get_max_score(query, qrels):
    score = 0
    i = 1
    for table, assessment in qrels[query].items():
        score += (2.0 ** assessment - 1) / math.log(i + 1, 2)
        i += 1
    return score


def evaluate_results(query, results, qrels):
    score = 0
    for i in range(len(results.top_n)):
        score += (2 ** (float(qrels[query][results[i]["title"]])) - 1) / math.log(i + 2, 2)
    return score / max(0.0000001, get_max_score(query, qrels))

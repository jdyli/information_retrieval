import csv
from functools import reduce
from math import log

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold

from util import parse_queries, parse_qrels


def parse_features():
    results = []
    for i in range(60):
        results.append([])
    with open("features.csv", newline="") as file:
        reader = csv.DictReader(file)
        for line in reader:
            results[int(line["query_id"]) - 1].append({
                "qlen": int(line["query_l"]),
                "idf": float(line["idf1"]) + float(line["idf2"]) + float(line["idf3"]) + float(
                    line["idf4"]) + float(line["idf5"]) + float(line["idf6"]),
                "numRows": int(line["row"]),
                "numCols": int(line["col"]),
                "numNulls": int(line["nul"]),
                "PMI": float(line["PMI"]),
                "inLinks": int(line["in_link"]),
                "outLinks": int(line["out_link"]),
                "pageViews": int(line["pgcount"]),
                "tableImportance": float(line["tImp"]),
                "tablePageFraction": float(line["tPF"]),
                "numHitsLC": int(line["leftColhits"]),
                "numHitsSLC": int(line["SecColhits"]),
                "numHitsB": int(line["bodyhits"]),
                "qInPgTable": float(line["qInPgTitle"]),
                "qInTableTitle": float(line["qInTableTitle"]),
                "yRank": int(line["yRank"])
            })
    return results


def evaluate_results(predictions, values):
    score = 0
    # for i in range(len(predictions)):
    #     score += (2 ** (float(qrels[query][results[i]["title"]])) - 1) / math.log(i + 2, 2)
    # return score / max(0.0000001, get_max_score(query, qrels))


def main():
    queries = parse_queries()
    qrels = parse_qrels()
    features = parse_features()
    fold_scores = []
    for fold in range(5):
        clf = RandomForestRegressor(n_estimators=1000, max_features=3)
        X = []
        y = []
        for i in range(0, fold):
            for j in range(int(len(queries) / 5)):
                X.extend([[xx for xx in x.values()] for x in features[i * int(len(queries) / 5) + j]])
                y.extend([yy for yy in qrels[i * int(len(queries) / 5) + j].values()])
        for i in range(fold + 1, 5):
            for j in range(int(len(queries) / 5)):
                X.extend([[xx for xx in x.values()] for x in features[i * int(len(queries) / 5) + j]])
                y.extend([yy for yy in qrels[i * int(len(queries) / 5) + j].values()])
        clf.fit(X, y)
        scores = []
        for i in range(int(len(queries) / 5)):
            results = clf.predict([[xx for xx in table_features.values()] for table_features in features[fold * int(len(queries) / 5) + i]])
            results_with_score = list(zip(results, [yy for yy in qrels[fold * int(len(queries) / 5) + i].values()]))

            results_with_score_sorted_on_prediction = results_with_score.copy()
            results_with_score_sorted_on_prediction.sort(key=lambda x: x[0], reverse=True)
            score = 0
            for j in range(20):
                score += (2 ** round(results_with_score[j][1]) - 1) / log(i + 2, 2)

            results_with_score_sorted_on_value = results_with_score.copy()
            results_with_score_sorted_on_value.sort(key=lambda x: x[1], reverse=True)
            max_score = 0
            for j in range(20):
                max_score += results_with_score_sorted_on_value[j][1]
            scores.append(score / max(0.0000001, max_score))
        total_score = sum(scores) / len(scores)
        print(total_score)
        fold_scores.append(total_score)
    total_score = sum(fold_scores) / len(fold_scores)
    print(total_score)


if __name__ == "__main__":
    main()

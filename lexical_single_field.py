import csv
from functools import reduce

from whoosh import index
from whoosh.qparser import MultifieldParser

from util import parse_queries, parse_qrels, target_dir, evaluate_results


def get_results(searcher, schema, query):
    parser = MultifieldParser(["title", "page_title", "col_title", "body", "sec_title", "caption"], schema)
    myquery = parser.parse(query[1].replace(" ", " OR "))
    return searcher.search(myquery, limit=20)


def main():
    queries = parse_queries()
    qrels = parse_qrels()
    scores = []
    for query in queries:
        ix = index.open_dir(target_dir + str(query[0]))
        with ix.searcher() as searcher:
            results = get_results(searcher, ix.schema, query)
            score = evaluate_results(query[0], results, qrels)
            scores.append((query, score))
            print(str(query) + " - " + str(score))
    with open("lexical.csv", "w+") as file:
        csv_writer = csv.writer(file)
        for score in scores:
            csv_writer.writerow([int(score[0][0]), score[1]])
    print("Average normalized score = " + str(
        reduce(lambda x, y: (0, x[1] + y[1]), scores)[1] / len(scores)))


if __name__ == "__main__":
    main()

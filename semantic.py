"""Example of Python client calling Knowledge Graph Search API."""
import json
import urllib.parse
import urllib.request

from lexical import parse_queries, parse_qrels
#
#
# def main():
#     queries = parse_queries()
#     qrels = parse_qrels()
#     scores = []
#     normalized_scores = []
#     for query in queries:
#         ix = create_index(query[0])
#         with ix.searcher() as searcher:
#             results = get_results(searcher, ix.schema, query)
#             score = evaluate_results(query[0], results, qrels)
#             print(str(query) + " - " + str(score))
#             scores.append((query, score))
#             normalized_score = score / max(0.0000001, get_max_score(len(results.top_n)))
#             normalized_scores.append((query, normalized_score))
#             print(str(query) + " - " + str(normalized_score))
#     with open("lexical.csv", "w+") as file:
#         csv_writer = csv.writer(file)
#         for score in scores:
#             csv_writer.writerow([int(score[0][0]), score[1]])
#     with open("lexical_normalized.csv", "w+") as file:
#         csv_writer = csv.writer(file)
#         for score in normalized_scores:
#             csv_writer.writerow([int(score[0][0]), score[1]])
#     print("Average normalized score = " + str(reduce(lambda x, y: (0, x[1] + y[1]), normalized_scores)[1] / len(normalized_scores)))
#
#
# if __name__ == "__main__":
#     main()


api_key = "AIzaSyCXsINFAQY2cBdeDUyPRaVnMXbcb5-tU_k"
query = 'world'
service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
params = {
    'query': query,
    'limit': 100,
    'indent': True,
    'key': api_key,
}
url = service_url + '?' + urllib.parse.urlencode(params)
response = json.loads(urllib.request.urlopen(url).read())
for element in response['itemListElement']:
    print(element['result']['name'] + ' (' + str(element['resultScore']) + ')')

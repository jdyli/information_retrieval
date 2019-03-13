import os 
import logging
import math
import csv

from gensim.test.utils import datapath, get_tmpfile
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.similarities import Similarity, WmdSimilarity
from gensim.corpora import Dictionary
from gensim.models import Word2Vec, WordEmbeddingSimilarityIndex
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix
from pyemd import emd_with_flow
from util import parse_qrels
from collections import defaultdict
from functools import reduce

"""
The implementation of Word Embeddings with the use of the Gensim library and the pre-trained Word2Vec model of GloVe.

Note: Prior to this code, you first need to create the required index tables and queries. For this task, use the 'semantic_index_creation.py'
file. Moreover, the file 'glove.6B.300d.txt' is not included in this project due to a large file size. However, this file
can be found at (https://nlp.stanford.edu/projects/glove/) and can be placed inside the 'semantic_data' folder.
"""

def load_pretrained_glove_model():
    path = os.path.abspath(os.path.curdir)
    glove_file = datapath(path + '/semantic_data/glove.6B.300d.txt')
    tmp_file = get_tmpfile(path + "/semantic_data/glove.word2vec.txt")
    _ = glove2word2vec(glove_file, tmp_file)
    return KeyedVectors.load_word2vec_format(tmp_file, binary=False)

def get_query_table(query):
    path = os.path.abspath(os.path.curdir)
    #change folder name if you want to use another table collection
    archive_name_path = path + "/semantic_data/index_semantic/" + str(query) + ".txt" 
    tables = [line.rstrip('\n').split() for line in open(archive_name_path)]
    return tables

def get_queries():
    path = os.path.abspath(os.path.curdir)
    lines = [line.rstrip('\n').split(",") for line in open(path + "/semantic_data/cleaned_queries.txt")]
    lines = [[int(line[0])-1, line[1]] for line in lines]
    return lines

def get_max_score(query, qrels, k):
    score = 0
    i = 0
    for table, assessment in qrels[query].items():
        i += 1
        if i > k:
            break
        score += (2.0 ** assessment - 1) / math.log(i + 1, 2)
    return score

def evaluate_results(query, results, qrels, k):
    score = 0
    for i in range(0, k-1):
        score += (2 ** (float(qrels[query][results[i]["title"]])) - 1) / math.log(i + 2, 2)
    return score / max(0.0000001, get_max_score(query, qrels, k))

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    k = 20 # parameter
    scores = []
    qrels = parse_qrels()
    path = os.path.abspath(os.path.curdir)
    model = load_pretrained_glove_model()
    termsim_index = WordEmbeddingSimilarityIndex(model.wv) 

    # compute the top k tables based on a query
    list_of_queries = get_queries()
    for query in list_of_queries:
        table_corpus = get_query_table(query[0])
        dictionary = Dictionary(table_corpus) 
        bow_corpus = [dictionary.doc2bow(table) for table in table_corpus] 
        similarity_matrix = SparseTermSimilarityMatrix(termsim_index, dictionary)  
        instance = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=k)
        sims = instance[dictionary.doc2bow(query[1].split())]
        results = defaultdict(lambda: defaultdict(int))
        print('Query: ', query)
        for i in range(len(sims)):
            print()
            print('sim = %.4f' % sims[i][1])
            print(table_corpus[sims[i][0]][0])
            line = table_corpus[sims[i][0]][0]
            results[i]['title'] = line
        ndcg_score = evaluate_results(query[0], results, qrels, k)
        scores.append((query[0], ndcg_score))

        # Save results in csv file
        with open(path + "/semantic_data/semantic_nobody_score" + str(k) + ".csv", "w+") as file:
            csv_writer = csv.writer(file)
            for score in scores:
                csv_writer.writerow([score[0], score[1]])
        print("Average normalized score = " + str(
            reduce(lambda x, y: (0, x[1] + y[1]), scores)[1] / len(scores)))
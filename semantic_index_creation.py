import json
import os
import csv

from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from util import archive_name_path, target_dir, archive_data_path, parse_queries

"""
Performs the preprocessing of the raw query data and the table data by using the nltk library. 
Moreover, after the data is cleaned up the files are saved as text files 
"""

porter_stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def clean_up(sentence):
    sentence = sentence.lower()
    sentence = word_tokenize(sentence)
    sentence = [w for w in sentence if not w in stop_words]
    sentence = [w for w in sentence if w.isalpha()]
    stem_sentence = []
    for word in sentence:
        stem_sentence.append(porter_stemmer.stem(word))
    return " ".join(stem_sentence)

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
    not_found = []
    filewriter = open("semantic_data/index_body/" + str(query) + ".txt", "a+")
    for table_query, location in zip(queries, table_location):
        if table_query != query:
            continue
        table_stem = "table-" + location[0] + "-"
        with open(archive_data_path + "re_tables-" + location[0] + ".json") as f:
            data = json.load(f)
            table_id = table_stem + location[1]
            if table_id in data:
                data = data[table_id]
                data_pt = data["pgTitle"]
                data_ct = " ".join(data["title"])
                data_b = " ".join([" ".join(i) for i in data["data"]])
                data_sect = data["secondTitle"]
                data_cap = data["caption"]
                query_line = "%s %s %s %s %s" % (str(data_b), str(data_pt), str(data_ct), str(data_sect), str(data_cap))
                cleaned_query_line = clean_up(query_line)
                query_line = "%s %s" % (str(table_id), 
                                 str(cleaned_query_line))
                filewriter.write(query_line + "\n")
            else:
                not_found.append(table_id)
    filewriter.close()
    print(not_found)

def create_query():
    with open("queries.csv", newline="") as file:
        reader = csv.reader(file)
        iter_reader = iter(reader)
        next(iter_reader)
        filewriter = open("semantic_data/cleaned_queries.txt", "+a")
        for line in iter_reader:
            cleaned_line = clean_up(line[1])
            filewriter.write(line[0] + "," + cleaned_line + "\n")
        filewriter.close()

if __name__ == "__main__":
    #create_query() # use when you want to create queries
    queries = parse_queries() # use when you want to create the tables
    for query in queries:
        create_index(query[0])

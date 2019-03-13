import json
import os
import csv

from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from util import archive_name_path, target_dir, archive_data_path, parse_queries

porter_stemmer = PorterStemmer()


def clean_up(sentence):
    sentence = sentence.lower()
    sentence = word_tokenize(sentence)
    stop_words = set(stopwords.words('english'))
    sentence = [w for w in sentence if not w in stop_words] # remove stopwords
    sentence = [w for w in sentence if w.isalpha()] # remove numbers and punctuation
    stem_sentence = []
    for word in sentence:
        stem_sentence.append(porter_stemmer.stem(word))
        stem_sentence.append(" ")
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
                
                query_line = "%s %s %s %s %s" % (str(data_b), str(data_pt), str(data_ct), str(data_sect), str(data_cap))
                cleaned_query_line = clean_up(query_line)
                query_line = "%s %s" % (str(table_id), 
                                 str(cleaned_query_line))

                filewriter = open("semantic_data/index_all/" + str(query) + ".txt", "a+")
                filewriter.write(query_line + "\n")
                filewriter.close()
            else:
                not_found.append(table_id)
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

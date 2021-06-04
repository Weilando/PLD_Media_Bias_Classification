import csv
import os

from helpers import print_log

# Helper

def generate_tweets_path(rel_path):
    """ Generates a relative path for a CSV-file with fetched tweets.
    'rel_path' refers to a CSV-file with names of PLDs. """
    assert is_valid_pld_path(rel_path)
    return rel_path.replace('_train.csv', '_tweets.csv')

def is_valid_pld_path(rel_path):
    """ Checks if 'rel_path' exists and if its suffix is '-_train.csv'. """
    abs_path = os.path.join(os.getcwd(), rel_path)
    return os.path.exists(abs_path) and abs_path.endswith('_train.csv')

# Reader

def read_pld_list(rel_path, verbose=False):
    """ Reads PLDs from a CSV-file referred to by 'rel_path'. Assumes that the
    CSV-file contains the name of one PLD per line. """
    assert is_valid_pld_path(rel_path)

    pld_list, pld_counter = [], 0
    csv.register_dialect('skip_space', skipinitialspace=True)
    with open(rel_path, 'r') as file:
        reader = csv.reader(file, dialect='skip_space')

        for line in reader:
            assert len(line)==1
            pld_list.append(line[0])
            pld_counter += 1

    print_log(f"Read {pld_counter} PLDs from '{rel_path}'.", verbose)
    return pld_list

def read_tweets_from_csv(rel_path, verbose=False):
    """ Reads data from a CSV-file referred to by 'rel_path'. Returns lists of
    strings as fetched from SPARQL-endpoint. """
    pld_ls, tweet_cnt_ls = [], []
    emos_pos_ls, emos_neg_ls, tags_ls, tweet_ids_ls = [], [], [], []

    csv.register_dialect('skip_space', skipinitialspace=True)
    csv.field_size_limit(250000)
    with open(rel_path, 'r') as f:
        reader = csv.DictReader(f , delimiter=',', dialect='skip_space')

        for row in reader:
            d_row = dict(row)
            pld_ls.append(d_row['pld'])
            tweet_cnt_ls.append(d_row['tweet_count'])
            emos_pos_ls.append(d_row['emos_pos'])
            emos_neg_ls.append(d_row['emos_neg'])
            tags_ls.append(d_row['tags'])
            #tweet_ids_ls.append(d_row['tweet_ids'])

    print_log(f"Read {len(pld_ls)} rows from '{rel_path}'.", verbose)
    return pld_ls, tweet_cnt_ls, emos_pos_ls, emos_neg_ls, tags_ls, tweet_ids_ls

# Writer

def write_tweets_to_csv(rel_path, tweets, header=False):
    """ Writes 'tweets' into a CSV-file with the same relative path prefix as
    the CSV-file which is referenced by 'rel_path'. If 'header' is True, a new
    file is created with a header line. Otherwise, 'tweets' is appended. """
    assert is_valid_pld_path(rel_path)

    tweets_path = generate_tweets_path(rel_path)
    with open(tweets_path, ('w' if header else 'a'), encoding='utf-8') as file:
        fw = csv.writer(file, delimiter=',', quotechar='|',
                        quoting=csv.QUOTE_MINIMAL)

        if header:
            fw.writerow(tweets["head"]["vars"])
        for tweet in tweets["results"]["bindings"]:
            fw.writerow([tweet[k]["value"] for k in tweet.keys()])

def write_results_to_csv(plds, class_ls, confidenc_ls, rel_path_l, rel_path_r):
    """ Writes names from 'plds' and the corresponding confidences from
    'confidence_ls' to CSV-files whose relative paths are given by 'rel_path_l'
    and 'rel_path_r'. PLDs from class 0 are written into 'rel_path_l', those
    with class 1 are written to 'rel_path_r'. """
    with open(rel_path_l, 'w', encoding='utf-8') as file_l, \
        open(rel_path_r, 'w', encoding='utf-8') as file_r:
        fw_l = csv.writer(file_l, delimiter=',', quotechar='|',
                          quoting=csv.QUOTE_MINIMAL)
        fw_r = csv.writer(file_r, delimiter=',', quotechar='|',
                          quoting=csv.QUOTE_MINIMAL)

        for pld, cls, cnf in zip(plds, class_ls, confidenc_ls):
            (fw_l if (cls==0) else fw_r).writerow([pld, cnf])

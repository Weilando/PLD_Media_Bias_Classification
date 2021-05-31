"""
Retrieves tweets from the TweetsCOV19 dataset.
Example call: python -m data_retriever '../../../input_data/left_train.csv'
"""

import csv
import os
import sys
from argparse import ArgumentParser
from SPARQLWrapper import SPARQLWrapper, JSON

SPARQL_URL = 'https://data.gesis.org/tweetscov19/sparql'

# Helpers

def print_log(message, verbose):
    """ Prints 'message' if the 'verbose' is True. """
    if verbose:
        print(message)

def is_valid_pld_path(rel_path):
    """ Check if the given relative path exists and if the file ends with
    '-_train.csv'. """
    abs_path = os.path.join(os.getcwd(), rel_path)
    return os.path.exists(abs_path) and abs_path.endswith('_train.csv')

def generate_tweets_path(rel_path):
    """ Generate a relative path for a CSV-file with fetched tweets.
    'rel_path' refers to a CSV-file with PLDs. """
    assert is_valid_pld_path(rel_path)
    return rel_path.replace('_train.csv', '_tweets.csv')

def write_tweets_to_csv(rel_path, tweets, verbose=False):
    """ Write 'tweets' into a CSV-file with the same relative path prefix as
    the CSV-file which is referenced by 'rel_path'. """
    assert is_valid_pld_path(rel_path)

    tweets_path = generate_tweets_path(rel_path)
    print_log(f"Write tweets to '{tweets_path}'.", verbose)
    with open(tweets_path, 'w', encoding='utf-8') as tweets_file:
        fw = csv.writer(tweets_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        fw.writerow(tweets["head"]["vars"])
        for tweet in tweets["results"]["bindings"]:
            fw.writerow([tweet[k]["value"] for k in tweet.keys()])

# Data Retrieval

def read_pld_list(rel_path, verbose=False):
    """ Reads PLDs from a CSV-file referred to by rel_path.
    Assumes that the CSV-file contains one PLD per line. """
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

def retrieve_tweets(rel_path, pld_list, verbose=False):
    """ Retrieves training data from the SPARQL endpoint of TweetsCOV19.
    All tweets related to the PLDs in pld_list are taken into account.
    Returns the dataset as dict. """
    print_log("Retrieve training data.", verbose)

    sparql = SPARQLWrapper(SPARQL_URL)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(f"""
        PREFIX onyx: <http://www.gsi.dit.upm.es/ontologies/onyx/ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
        PREFIX sioc: <http://rdfs.org/sioc/ns#>
        PREFIX sioc_t: <http://rdfs.org/sioc/types#>
        PREFIX wna: <http://www.gsi.dit.upm.es/ontologies/wnaffect/ns#>

        SELECT DISTINCT ?tweet,
                        (GROUP_CONCAT(DISTINCT ?pld ; separator='+') AS ?plds),
                        (GROUP_CONCAT(DISTINCT ?tag ; separator='+') AS ?tags),
                        ?emotion_pos, ?emotion_neg
        WHERE {{
            ?tweet a sioc:Post ;
                schema:citation ?url ;
                schema:mentions ?mention ;
                onyx:hasEmotionSet ?emotion_set .
            BIND(REPLACE( REPLACE(STR(?url), "https?://(www.)?", ""),
                          "/.*", "") as ?pld) .
            FILTER(?pld IN (\"{'", "'.join(pld_list)}\")) .

            ?mention a sioc_t:Tag ;
                rdfs:label ?tag .

            ?emotion_set a onyx:EmotionSet ;
                onyx:hasEmotion ?emotion1 ;
                onyx:hasEmotion ?emotion2 .
            ?emotion1 onyx:hasEmotionCategory wna:negative-emotion ;
                onyx:hasEmotionIntensity ?emotion_neg .
            ?emotion2 onyx:hasEmotionCategory wna:positive-emotion ;
                onyx:hasEmotionIntensity ?emotion_pos .
        }}
        ORDER BY ?tweet
    """)
    # FILTER(?pld IN ("telegraaf.nl", "newbostonpost.com")).

    return sparql.queryAndConvert()

# Main

def parse_arguments(args):
    """ Creates an ArgumentParser with help messages. """
    info =  """ Retriever for the TweetsCOV19 dataset.
                Fetches tweets related to PLDs which are read from the CSV-file
                which is referenced by 'rel_path' and writes them into a
                JSON-file in the same directory. """
    parser = ArgumentParser(description=info)
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="activate output")
    parser.add_argument('rel_path', help="relative path to training data, i.e., a CSV with PLDs")

    if len(args) < 1:  # show help, if no arguments are given
        parser.print_help(sys.stderr)
        sys.exit()
    return parser.parse_args(args)

def main(args):
    parsed_args = parse_arguments(args)

    pld_list = read_pld_list(parsed_args.rel_path, parsed_args.verbose)
    tweets = retrieve_tweets(parsed_args.rel_path, pld_list,
                             parsed_args.verbose)
    write_tweets_to_csv(parsed_args.rel_path, tweets, parsed_args.verbose)

if __name__ == '__main__':
    main(sys.argv[1:])

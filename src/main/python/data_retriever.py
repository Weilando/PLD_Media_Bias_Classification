"""
Retrieves training data from the SPARQL-endpoint of TweetsCOV19.
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
    """ Checks if 'rel_path' exists and if its suffix is '-_train.csv'. """
    abs_path = os.path.join(os.getcwd(), rel_path)
    return os.path.exists(abs_path) and abs_path.endswith('_train.csv')

def generate_tweets_path(rel_path):
    """ Generates a relative path for a CSV-file with fetched tweets.
    'rel_path' refers to a CSV-file with names of PLDs. """
    assert is_valid_pld_path(rel_path)
    return rel_path.replace('_train.csv', '_tweets.csv')

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

# Data Retrieval

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

def retrieve_tweets(pld):
    """ Retrieves aggregated training data from the TweetsCOV19 SPARQL-endpoint
    and returnes a dict. All tweets related to 'pld' are taken into account. """
    sparql = SPARQLWrapper(SPARQL_URL)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(f"""
        PREFIX onyx: <http://www.gsi.dit.upm.es/ontologies/onyx/ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
        PREFIX sioc: <http://rdfs.org/sioc/ns#>
        PREFIX sioc_t: <http://rdfs.org/sioc/types#>
        PREFIX wna: <http://www.gsi.dit.upm.es/ontologies/wnaffect/ns#>

        SELECT DISTINCT ?pld,
            (GROUP_CONCAT(?tmp_tags ; separator='+') AS ?tags),
            (AVG(?emotion_pos) AS ?emotion_pos_avg),
            (AVG(?emotion_neg) AS ?emotion_neg_avg),
            (COUNT(DISTINCT ?tweet) AS ?tweet_count),
            (GROUP_CONCAT(DISTINCT ?tweet ; separator='+') AS ?tweet_ids)
        WHERE {{
            SELECT ?tweet, ?pld,
                (GROUP_CONCAT(DISTINCT ?tag ; separator='+') AS ?tmp_tags),
                ?emotion_pos, ?emotion_neg
            WHERE {{
                ?tweet a sioc:Post ;
                    schema:citation ?url ;
                    schema:mentions ?mention ;
                    onyx:hasEmotionSet ?emotion_set .
                BIND(REPLACE( REPLACE(STR(?url), "https?://(www.)?", ""),
                    "/.*", "") as ?pld) .
                FILTER(?pld=\"{pld}\") .

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
            GROUP BY ?pld ?tweet ?emotion_pos ?emotion_neg
        }}
        GROUP BY ?pld
        ORDER BY ?pld
    """)
    return sparql.queryAndConvert()

# Main

def parse_arguments(args):
    """ Creates an ArgumentParser with help messages. """
    info =  """ Retriever for the TweetsCOV19 dataset. Fetches tweets related
                to classified PLDs whose names are read from the CSV-file which
                is referenced by 'rel_path'. It writes aggregated results per
                PLD into a JSON-file in the same directory. """
    parser = ArgumentParser(description=info)
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="activate output")
    parser.add_argument('rel_path',
                        help="relative path to CSV-file with PLD names")

    if len(args) < 1:  # show help, if no arguments are given
        parser.print_help(sys.stderr)
        sys.exit()
    return parser.parse_args(args)

def main(args):
    parsed_args = parse_arguments(args)

    pld_list = read_pld_list(parsed_args.rel_path, parsed_args.verbose)
    for n, pld in enumerate(pld_list, start=1):
        print_log(f"{n:3d} Retrieve data for '{pld}'.", parsed_args.verbose)
        tweets = retrieve_tweets(pld)
        write_tweets_to_csv(parsed_args.rel_path, tweets, (n==1))

if __name__ == '__main__':
    main(sys.argv[1:])

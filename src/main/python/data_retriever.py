"""
Retrieves training data from the SPARQL-endpoint of TweetsCOV19.
Example call: python -m data_retriever '../../../input_data/left_train.csv'
"""

import sys
from argparse import ArgumentParser
from SPARQLWrapper import SPARQLWrapper, JSON

from data_file_handler import generate_tweets_path, is_valid_pld_path, \
                              read_pld_list, write_tweets_to_csv
from helpers import print_log

SPARQL_URL = 'https://data.gesis.org/tweetscov19/sparql'

# Data Retrieval

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
            (COUNT(DISTINCT ?tweet) AS ?tweet_count),
            (GROUP_CONCAT(?emotion_pos ; separator='+') AS ?emos_pos),
            (GROUP_CONCAT(?emotion_neg ; separator='+') AS ?emos_neg),
            (GROUP_CONCAT(?tmp_tags ; separator='+') AS ?tags),
            (GROUP_CONCAT(DISTINCT ?tweet ; separator='+') AS ?tweet_ids)
        WHERE {{
            SELECT ?pld, ?tweet, ?emotion_pos, ?emotion_neg,
                (GROUP_CONCAT(DISTINCT ?tag ; separator='+') AS ?tmp_tags)
            WHERE {{
                ?tweet a sioc:Post ;
                    schema:citation ?url ;
                    onyx:hasEmotionSet ?emotion_set .
                BIND(REPLACE( REPLACE(STR(?url), "https?://(www.)?", ""),
                    "/.*", "") as ?pld) .
                FILTER(?pld=\"{pld}\") .

                OPTIONAL {{
                    ?tweet schema:mentions ?mention .
                    ?mention a sioc_t:Tag ;
                        rdfs:label ?tag }} .

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

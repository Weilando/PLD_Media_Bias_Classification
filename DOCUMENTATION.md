# DOCUMENTATION

## Data Retrieval

`data_retriever.py` can be used to retrieve tweets which mention PLDs from a given CSV-file.
It offers a command line interface and saves its results into a CSV-file in the same directory as the input file.

## Features

`data_retriever.py` retrieves the following features, mainly focusing on sentiments and hashtags:

Name | Value
--- | ---
tweet | nodeId of tweet
pld | PLD mentioned in the tweet
tag | Hashtag used in the tweet, omits #
emotion_intensity | Float between 0 (weak) and 1 (strong)
emotion_category | Either `wna:positive-emotion` or `wna:negative-emotion`

The knowledge base stores an emotion set containing both categories for each tweet.
This results in twice as many rows, but might be useful to learn certain features.
Please notice `PREFIX wna: <http://www.gsi.dit.upm.es/ontologies/wnaffect/ns#>`.

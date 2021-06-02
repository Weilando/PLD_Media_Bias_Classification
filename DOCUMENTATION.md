# DOCUMENTATION

## Data Retrieval

`data_retriever.py` can be used to retrieve tweets which mention PLDs from a given CSV-file.
It offers a command line interface and saves aggregated features per PLD into a CSV-file in the same directory as the input file.

## Features

`data_retriever.py` retrieves the following features, mainly focusing on sentiments and hashtags:

Name | Value
--- | ---
pld | Name of PLD
tags | Hashtags used in related tweets, omits leading #
emotion_pos_avg | Average positive emotion score for related tweets
emotion_neg_avg | Average negative emotion score for related tweets
tweet_count | Number of aggregated related tweets
tweet_ids | nodeIds of aggregated related tweets

`tags` and `tweet_ids` represent used hashtags and nodeIds respectively.
They are stored as strings using `+` as separator, which is not allowed in valid hashtags and nodeIds.
The nodeIds might be used to hydrate the tweets.

The knowledge base stores an emotion set containing negative and positive scores for each tweet.
`emotion_pos_avg` and `emotion_pos_avg` are floats between 0 (weak) and 1 (strong).
Please notice that both values are greater than zero for some tweets.

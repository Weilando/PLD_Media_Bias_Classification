# DOCUMENTATION

## Data Retrieval

`data_retriever.py` retrieves aggregated tweets which mention PLDs from a given CSV-file, mainly focusing on sentiments and hashtags.
It offers a command line interface and saves aggregated features per PLD into a CSV-file in the same directory as the input file.

Name | Value
--- | ---
pld | Name of PLD
tweet_count | Number of aggregated related tweets
emos_pos | Positive emotion scores for related tweets
emos_neg | Negative emotion scores for related tweets
tags | Hashtags used in related tweets, omits leading #
tweet_ids | nodeIds of aggregated related tweets

`emos_pos`, `emos_neg`, `tags` and `tweet_ids` are stored as strings using `+` as separator, which is not allowed in valid emotion scores, hashtags and nodeIds.
The nodeIds might be used to hydrate the tweets.
Hashtags are not distinct, i.e., they are listed as often as they occur in the corresponding tweets.

The knowledge base stores an emotion set containing negative and positive scores for each tweet.
`emotion_pos_avg` and `emotion_pos_avg` are floats between 0 (weak) and 1 (strong).
Please notice that both values are greater than zero for some tweets.

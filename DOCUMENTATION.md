# DOCUMENTATION

## Data Retrieval

`data_retriever.py` can be used to retrieve tweets which mention PLDs from a given CSV-file.
It offers a command line interface and saves its results into a CSV-file in the same directory as the input file.

## Features

`data_retriever.py` retrieves the following features, mainly focusing on sentiments and hashtags:

Name | Value
--- | ---
tweet | nodeId of tweet
plds | PLDs cited in the tweet
tags | Hashtags used in the tweet, omits leading #
emotion_pos | Float between 0 (weak) and 1 (strong)
emotion_neg | Float between 0 (weak) and 1 (strong)

The knowledge base stores an emotion set containing negative and positive scores for each tweet.
Please notice that for some tweets both values are greater than zero.

`plds` and `tags` represent cited PLDs and used hashtags respectively.
They are stored as strings using `+` as separator, which is not allowed in valid domain names and hashtags.

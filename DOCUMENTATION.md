# DOCUMENTATION

[Data Retrieval](#data) describes how the training data can be generated using `data_retriever.py`.
[Machine Learning Algorithm](#algo) describes applied features, the algorithm itself, as well as its [Training](#train) and [Application](#app).
`pld_classifier_trainer.py` trains a new instance, whereas `evaluation.py` performs an evaluation using unlabeled data.

## <a id="data">Data Retrieval</a>

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

## <a id="algo">Machine Learning Algorithm</a>

### Features

The algorithm considers two classes of features per PLD.
On the one hand, it uses positive and negative emotion scores by taking one average for each over all relevant tweets.
The averages are represented as floats in one tensor `emos`.
On the other hand, all hashtags from related tweets are taken into account to approximate the PLDs main topics.
The hashtags `tags` are concatenated strings and need to be transformed into word vectors for training.

### Algorithm

A linear classifier in PyTorch is used to learn the classification of PLDs into left and right leaning.
Therefore, hashtags are embedded using pretrained FastText vectors, which are stacked with the emotion scores after passing the embedding layer.
The architecture comes with one fully-connected hidden layer and one fully-connected output layer to perform the classification.

Please notice that the implementation uses an `torch.nn.EmbeddingBag`, which takes a row-tensor with a concatenation of all word vectors as first input, and a tensor with offsets as second input.
As there is one offset per sample from the batch, there is no need for zero padding.
This layer has some additional features regarding efficiency.

#### <a id="train">Training</a>

Two batches from the training data are reserved for validation.
`pld_classifier_trainer.py` can be used to train a classifier with the Adam optimizer and previously retrieved training data.
It saves the `state_dict` final classifier and the applied `Vocab` as PyTorch files.

#### <a id="app">Application</a>

The classifier can be called like a python function and accepts either a single sample or a complete batch.
Thus, the input data needs to be have the same form as the training data and needs to use the same `Vocab` object to produce word vectors.
A call might be `pld_classifier(emos, tags_vec, offsets)`, where `emos` holds both emotion values, `tags_vec` is an encoded vector for all hashtags and `offsets` contains the offsets of hashtags from single tweets.

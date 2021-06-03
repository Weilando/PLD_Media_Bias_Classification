"""
Trains a classifier for the PLDs of referenced URLs according to their
political leaning, i.e., left or right.

Example call: python -m pld_classifier_trainer '../../../input_data/left_tweets.csv' '../../../input_data/right_tweets.csv'
"""

import csv
import numpy as np
import sys
import torch
from argparse import ArgumentParser
from collections import Counter
from torchtext.data.utils import get_tokenizer
from torch.utils.data import DataLoader
from torchtext.vocab import Vocab
from pld_dataset import PLDDataset
from helpers import print_log

# Helpers

def read_tweets_file(rel_path, verbose=False):
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

def build_vocab(l_tag_str_arr, r_tag_str_arr):
    """ Builds vocab for all tokens in 'l_tag_str_arr' and 'r_tag_str_arr'. """
    tokenizer = get_tokenizer('basic_english')
    counter = Counter()

    for tag_str in l_tag_str_arr:
        counter.update(tokenizer(tag_str))
    for tag_str in r_tag_str_arr:
        counter.update(tokenizer(tag_str))

    return Vocab(counter, min_freq=1, vectors='fasttext.simple.300d'), tokenizer

def build_dataloader(pld_dataset, batch_size, vocab, tokenizer):
    """ Builds dataloader for 'pld_dataset' and transforms 'tags_str' into word
    vectors as tensors. Each batch contains 'batch_size' samples. """
    tags_pipeline = lambda x: [vocab[token] for token in tokenizer(x)]

    def collate_batch(batch):
        """ Transforms 'tags_str' into word vectors using 'tags_pipeline'. """
        label_ls, emos_ls, tags_vec_ls, offsets = [], [], [], [0]
        for sample in batch:
            label, emos, tags_str = sample.values()
            label_ls.append(label)
            emos_ls.append(emos)
            tags_vec = torch.tensor(tags_pipeline(tags_str), dtype=torch.int64)
            tags_vec_ls.append(tags_vec)
            offsets.append(tags_vec.size(0))

        label_ts = torch.tensor(label_ls, dtype=torch.int64)
        emos_ts = torch.tensor(emos_ls, dtype=torch.int64)
        tags_ts = torch.cat(tags_vec_ls)
        offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
        return label_ts, emos_ts, tags_ts, offsets

    return DataLoader(pld_dataset, batch_size=batch_size, num_workers=0,
                      shuffle=False, drop_last=False, collate_fn=collate_batch)

def concatenate_arrays(left_arr, right_arr):
    """ Concatenate 'left_arr' and 'right_arr' to get one feature array. """
    return np.concatenate((left_arr, right_arr), axis=0)

def generate_labels(num, left=True):
    """ Generates 'num' labels. If 'left' is True, each label is 0, else 1. """
    return np.zeros(num, dtype=int) if left else np.ones(num, dtype=int)

def preprocess_emos(emos_pos_str_ls, emos_neg_str_ls):
    """ Parses lists of floats from strings in 'emos_pos_str_ls' and
    'emos_neg_str_ls', calculates an average per list and returns them as
    np.array. """
    parse_emos_str = lambda emos_str: list(map(float, emos_str.split('+')))

    emos_pos_ls_ls = [parse_emos_str(emos_str) for emos_str in emos_pos_str_ls]
    emos_neg_ls_ls = [parse_emos_str(emos_str) for emos_str in emos_neg_str_ls]

    emos_pos_avg_ls = [np.mean(emos_ls) for emos_ls in emos_pos_ls_ls]
    emos_neg_avg_ls = [np.mean(emos_ls) for emos_ls in emos_neg_ls_ls]

    return np.array([emos_pos_avg_ls, emos_neg_avg_ls]).T

def preprocess_tags(tags):
    """ Replaces separator '+' with spaces in and lower cases strings from
    'tags'. Returns a np.array with one string per PLD. """
    return np.array([tag_str.replace('+', ' ').lower() for tag_str in tags])

# Main

def parse_arguments(args):
    """ Creates an ArgumentParser with help messages. """
    info =  """ Trainer for a classifier for PLD media bias classification.
            Uses tweets from CSV-files generated by 'data_retriever.py'. """
    parser = ArgumentParser(description=info)
    parser.add_argument('data_l',
                        help="specify relative path to left training data")
    parser.add_argument('data_r',
                        help="specify relative path to right training data")
    parser.add_argument('-b', '--batch', type=int, default=43, metavar='N',
                        help="specify number of samples per batch")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="activate output")

    if len(args) < 1:  # show help, if no arguments are given
        parser.print_help(sys.stderr)
        sys.exit()
    return parser.parse_args(args)

def main(args):
    parsed_args = parse_arguments(args)

    l_pld_ls, l_tweet_cnt_ls, l_emos_pos_ls, l_emos_neg_ls, l_tags_ls, _ \
        = read_tweets_file(parsed_args.data_l, parsed_args.verbose)
    r_pld_ls, r_tweet_cnt_ls, r_emos_pos_ls, r_emos_neg_ls, r_tags_ls, _ \
        = read_tweets_file(parsed_args.data_r, parsed_args.verbose)

    l_label_arr = generate_labels(len(l_pld_ls), left=True)
    r_label_arr = generate_labels(len(r_pld_ls), left=False)
    l_emos_arr = preprocess_emos(l_emos_pos_ls, l_emos_neg_ls)
    r_emos_arr = preprocess_emos(r_emos_pos_ls, r_emos_neg_ls)
    l_tag_str_arr = preprocess_tags(l_tags_ls)
    r_tag_str_arr = preprocess_tags(r_tags_ls)

    label_arr = concatenate_arrays(l_label_arr, r_label_arr)
    emos_arr = concatenate_arrays(l_emos_arr, r_emos_arr)
    tags_str_arr = concatenate_arrays(l_tag_str_arr, r_tag_str_arr)
    pld_dataset = PLDDataset(label_arr, emos_arr, tags_str_arr)

    vocab, tokenizer = build_vocab(l_tag_str_arr, r_tag_str_arr)
    dataloader = build_dataloader(pld_dataset, parsed_args.batch, vocab,
                                  tokenizer)

    print_log("Pre-processing done.", parsed_args.verbose)


if __name__ == '__main__':
    main(sys.argv[1:])

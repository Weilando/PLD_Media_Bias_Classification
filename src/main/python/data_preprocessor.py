import numpy as np
import torch
from collections import Counter
from torchtext.data.utils import get_tokenizer
from torch.utils.data import DataLoader
from torchtext.vocab import Vocab

def append_cnts_to_emos(emos_arr, cnts_arr):
    """ Appends 'cnts_arr' as new column to 'emos_arr'. """
    return np.hstack((emos_arr, cnts_arr.reshape(-1, 1))) # concat rows

def build_vocab(tags_str_arr):
    """ Builds vocab for all tokens in 'tags_str_arr'. """
    tokenizer = get_tokenizer('basic_english')
    counter = Counter()

    for tags_str in tags_str_arr:
        counter.update(tokenizer(tags_str))

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

def concatenate_colums(left_arr, right_arr):
    """ Concatenates 'left_arr' and 'right_arr' to get one feature array. """
    return np.concatenate((left_arr, right_arr), axis=0)

def generate_labels(num, left=True):
    """ Generates 'num' labels. If 'left' is True, each label is 0, else 1. """
    return np.zeros(num, dtype=int) if left else np.ones(num, dtype=int)

def preprocess_cnts(cnts_str_ls):
    """ Parses ints from strings in 'cnts_str_ls' and normalizes the whole list.
    Returns a np.array with one normalized float per PLD. """
    cnts_ls = np.array([int(cnts_str) for cnts_str in cnts_str_ls])
    max = np.max(cnts_ls)
    min = np.min(cnts_ls)
    return (cnts_ls - min) / (max - min) # normalization using broadcasting

def preprocess_emos(emos_pos_str_ls, emos_neg_str_ls):
    """ Parses lists of floats from strings in 'emos_pos_str_ls' and
    'emos_neg_str_ls', calculates the arithmetic mean and standard deviation
    per list and returns them as np.array. """
    parse_emos_str = lambda emos_str: list(map(float, emos_str.split('+')))

    emos_pos_ls_ls = [parse_emos_str(emos_str) for emos_str in emos_pos_str_ls]
    emos_neg_ls_ls = [parse_emos_str(emos_str) for emos_str in emos_neg_str_ls]

    emos_pos_avg_ls = [np.mean(emos_ls) for emos_ls in emos_pos_ls_ls]
    emos_neg_avg_ls = [np.mean(emos_ls) for emos_ls in emos_neg_ls_ls]
    emos_pos_std_ls = [np.std(emos_ls) for emos_ls in emos_pos_ls_ls]
    emos_neg_std_ls = [np.std(emos_ls) for emos_ls in emos_neg_ls_ls]

    return np.array([emos_pos_avg_ls, emos_neg_avg_ls, emos_pos_std_ls,
                     emos_neg_std_ls]).T

def preprocess_tags(tags):
    """ Replaces separator '+' with spaces in and lower cases strings from
    'tags'. Returns a np.array with one string per PLD. """
    return np.array([tag_str.replace('+', ' ').lower() for tag_str in tags])

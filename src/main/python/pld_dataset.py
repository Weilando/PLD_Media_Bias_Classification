from torch import is_tensor
from torch.utils.data import Dataset, random_split

from data_preprocessor import append_cnts_to_emos, concatenate_colums, \
                              generate_labels, preprocess_cnts, \
                              preprocess_emos, preprocess_tags
from helpers import print_log

class PLDDataset(Dataset):
    """ PLD dataset. """

    def __init__(self, labels, emos_feat, tags_feat):
        """ Expects preprocessed 'labels', 'emos_feat' and 'tags_feat'. """
        self.labels = labels
        self.emos_feat = emos_feat
        self.tags_feat = tags_feat

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        if is_tensor(idx):
            idx = idx.tolist()

        return {'label': self.labels[idx],
                'emos': self.emos_feat[idx],
                'tags': self.tags_feat[idx],}

def build_emos_arr(l_emos_pos_ls, l_emos_neg_ls, r_emos_pos_ls, r_emos_neg_ls,
                   l_cnts_ls, r_cnts_ls):
    """ Preprocesses the input lists from a CSV-file and builds one array
    [pos_avg, neg_avg, pos_std, neg_std, cnt] with one arithmetic mean and
    standard deviation for all left and right emotion scores per PLD. 'cnt'
    holds normalized counters of aggregated tweets. """
    l_emos_arr = preprocess_emos(l_emos_pos_ls, l_emos_neg_ls)
    r_emos_arr = preprocess_emos(r_emos_pos_ls, r_emos_neg_ls)
    l_cnts_arr = preprocess_cnts(l_cnts_ls)
    r_cnts_arr = preprocess_cnts(r_cnts_ls)

    emos_arr = concatenate_colums(l_emos_arr, r_emos_arr)
    cnts_arr = concatenate_colums(l_cnts_arr, r_cnts_arr)
    return append_cnts_to_emos(emos_arr, cnts_arr)

def build_label_arr(l_len, r_len):
    """ Generates a label array with 'l_len' zeros and 'r_len' ones. """
    l_label_arr = generate_labels(l_len, left=True)
    r_label_arr = generate_labels(r_len, left=False)
    return concatenate_colums(l_label_arr, r_label_arr)

def build_tags_str_arr(l_tags_ls, r_tags_ls):
    """ Preprocesses the input lists which are read from a CSV-file and
    concatenates the results, i.e., one string with Hashtags per PLD. """
    l_tag_str_arr = preprocess_tags(l_tags_ls)
    r_tag_str_arr = preprocess_tags(r_tags_ls)
    return concatenate_colums(l_tag_str_arr, r_tag_str_arr)

def split_dataset(pld_dataset, batch_size=43, val_batches=2, verbose=False):
    """ Randomly splits 'pld_dataset' into training and validation sets. Takes
    'val_batches' batches for validation. """
    val_len = batch_size * val_batches
    trn_len = len(pld_dataset) - val_len
    assert val_len < trn_len
    print_log(f"{trn_len} trn-samples, {val_len} val-samples", verbose)
    return random_split(pld_dataset, [trn_len, val_len])

import torch
from torch.utils.data import Dataset

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
        if torch.is_tensor(idx):
            idx = idx.tolist()

        return {'label': self.labels[idx],
                'emos': self.emos_feat[idx],
                'tags': self.tags_feat[idx],}

from torch import cat
from torch.nn import CrossEntropyLoss, EmbeddingBag, Linear, Module
from torch.nn.functional import relu

class PLDClassifierParam(object):
    """ Defines parameters for the initialization of a PLDClassifier. """
    def __init__(self, param_dict: dict = dict()):
        self.emb_dim = param_dict.get('emb_dim', 300) # embedding dimension
        self.hid_dim = param_dict.get('hid_dim', 150) # hidden layer size
        self.num_classes = param_dict.get('num_classes', 2) # number of classes

class PLDClassifier(Module):
    """ Classifier which predicts the leaning of PLDs. """
    def __init__(self, params: PLDClassifierParam, embedding_weight):
        super().__init__()

        self.emb = EmbeddingBag.from_pretrained(embedding_weight)
        self.hid = Linear(params.emb_dim + 2, params.hid_dim) # +2 for emos
        self.out = Linear(params.hid_dim, params.num_classes)

        self.loss_fct = CrossEntropyLoss()

    def forward(self, emos, tags_vec, offsets):
        """ Performs a forward pass through the classifier. """
        # BS = batch size, ES = number of emotion scores
        tags_feats = self.emb(tags_vec, offsets)    # (BS, emb_dim)
        tags_feats = relu(tags_feats)               # (BS, emb_dim)
        concat_feats = cat((tags_feats, emos), 1)   # (BS, emb_dim + ES)
        concat_feats = self.hid(concat_feats)       # (BS, hid_dim)
        concat_feats = relu(concat_feats)           # (BS, hid_dim)
        return self.out(concat_feats)               # (num_classes)

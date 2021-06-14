import matplotlib.pyplot as plt
import numpy as np

def gen_stat_msg(epoch, trn_hist, val_hist):
    """ Builds a status message for int 'epoch' and lists 'trn_hist' and
    'val_hist', whose elements are tuples (accuracy, loss). """
    return (f"Epoch {epoch:2d}: "
            f"trn-loss={trn_hist[-1][1]:.3f}, trn-acc={trn_hist[-1][0]:.3f}, "
            f"val-loss={val_hist[-1][1]:.3f}, val-acc={val_hist[-1][0]:.3f}")

def plot_acc_and_loss(trn_hist, val_hist):
    """ Plots accuracies and losses per epoch from 'trn_hist' 'val_hist'. """
    assert isinstance(trn_hist, np.ndarray) and isinstance(val_hist, np.ndarray)
    fig, (ax_acc, ax_loss) = plt.subplots(1, 2, figsize=(10, 4))
    plot_on_ax(ax_acc, trn_hist[:,0], val_hist[:,0], "Accuracy")
    plot_on_ax(ax_loss, trn_hist[:,1], val_hist[:,1], "Loss")
    plt.show()

def plot_on_ax(ax, trn_ls, val_ls, ylabel="Accuracy"):
    """ Plots data from 'trn_ls' and 'val_ls' per epoch on 'ax'. """
    ax.plot(trn_ls, 'o-', label='Training')
    ax.plot(val_ls, 'x-', label='Validation')
    ax.set_xlabel('Epochs')
    ax.set_ylabel(ylabel)
    ax.legend()

def print_log(message, verbose):
    """ Prints 'message' if the 'verbose' is True. """
    if verbose:
        print(message)

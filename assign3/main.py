"""
Author: Wilhelm Ågren, wagren@kth.se
Last edited: 19/04/2021
"""

import numpy as np
import matplotlib.pyplot as plt


# ======================================================================================================================
def parse_data(dset, verbose=False):
    print('<| Parse data from batch:')
    """
    reformat the given dataset such that it returns the data, the one-hot encoded labels,
    and the labels.
    output:
            X := d x n size which contains the image pixel data.
                 n is number of images, d is dimensionality of each image
            Y := one hot encoded labels, K x n matrix
            y := vector length n containing label for each image.
    """
    y = np.array(dset[b'labels'])
    X = dset[b'data'].T
    K = len(np.unique(y))
    n = len(X[0])
    Y = np.zeros((K, n))
    for idx, num in enumerate(y):
        Y[num, idx] = 1

    if verbose:
        print('\tthe shape of X:', X.shape)
        print('\tthe shape of Y:', Y.shape)
        print('\tthe shape of y:', y.shape)

    return X, Y, y


def load_batch(filename):
    import pickle
    with open('Dataset/' + filename, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict


def preprocess_data(x):
    print('<| Preprocess X data :')
    normalized = (x - x.mean(axis=0)) / x.std(axis=0)
    return normalized


def softmax(x):
    """ Standard definition of the softmax function """
    return np.exp(x) / np.sum(np.exp(x), axis=0)
# ======================================================================================================================


# noinspection PyTypeChecker
class KNN:

    def __init__(self, X=None, Y=None, y=None,
                 X_eval=None, Y_eval=None, y_eval=None,
                 X_test=None, Y_test=None, y_test=None,
                 batch_size=0, n_epochs=1, eta=0, lamda=0,
                 num_layers=0, num_nodes=None, verbose=False):
        if num_nodes is None:
            num_nodes = []
        self.X = X
        self.Y = Y
        self.y = y
        self.X_eval = X_eval
        self.Y_eval = Y_eval
        self.y_eval = y_eval
        self.X_test = X_test
        self.Y_test = Y_test
        self.y_test = y_test
        # We need a weight matrix and bias vector for each layer of the neural network
        self.W = [np.zeros((1, 1)) for _ in range(num_layers)]
        self.b = [np.zeros((1, 1)) for _ in range(num_layers)]
        self.batch_size = batch_size
        self.n_epochs = n_epochs
        self.eta = eta
        self.lamda = lamda
        self.num_layers = num_layers
        self.num_nodes = num_nodes
        self.k = len(num_nodes)
        self.verbose = verbose

    def parse_full_data(self, val_split=5000):
        dataX, dataY, datay = parse_data(load_batch('data_batch_1'))
        dataX2, dataY2, datay2 = parse_data(load_batch('data_batch_2'))
        dataX3, dataY3, datay3 = parse_data(load_batch('data_batch_3'))
        dataX4, dataY4, datay4 = parse_data(load_batch('data_batch_4'))
        dataX5, dataY5, datay5 = parse_data(load_batch('data_batch_5'))
        X, Y, y = np.concatenate((dataX, dataX2, dataX3, dataX4, dataX5[:, :val_split]), axis=1), \
                  np.concatenate((dataY, dataY2, dataY3, dataY4, dataY5[:, :val_split]), axis=1), \
                  np.concatenate((datay, datay2, datay3, datay4, datay5[:val_split]))
        eval_X, eval_Y, eval_y = dataX5[:, val_split:], dataY5[:, val_split:], datay5[val_split:]
        self.X = preprocess_data(X)
        self.Y = Y
        self.y = y
        self.X_eval = preprocess_data(eval_X)
        self.Y_eval = eval_Y
        self.y_eval = eval_y

        if self.verbose:
            print('<| Parsing all of the batches...')

    def initialize_params(self):
        assert self.num_layers == len(self.num_nodes) + 1, print(f'<| ERROR: num_layers={self.num_layers} '
                                                                 f'and we got {len(self.num_nodes)} hidden nodes...' )
        #  K = Y.shape[0], d = X.shape[0], m = hid_nodes

        # The first weight matrix will always have size (m, d). Where m = num_nodes[0]
        # We will always have a first weight matrix, since this class requires k-layer network where k >= 2
        self.W[0] = np.random.normal(0, 1 / np.sqrt(self.X.shape[0]), size=(self.num_nodes[0], self.X.shape[0]))
        for num_node in range(1, len(self.num_nodes)):
            self.W[num_node] = np.random.normal(0, 1 / np.sqrt(self.num_nodes[num_node]),
                                                size=(self.num_nodes[num_node], self.num_nodes[num_node - 1]))

        self.W[self.num_layers - 1] = np.random.normal(0, 1 / np.sqrt(self.num_nodes[-1]),
                                                       size=(self.Y.shape[0], self.num_nodes[-1]))

        for idx, num_node in enumerate(self.num_nodes):
            self.b[idx] = np.zeros(shape=(num_node, 1))
        self.b[-1] = np.zeros(shape=(self.Y.shape[0], 1))

        if self.verbose:
            print('<| Initializing the network parameters...')
            for idx, w in enumerate(self.W):
                print(f'\tthe shape of W{idx + 1}: {w.shape}')
            for idx, b in enumerate(self.b):
                print(f'\tthe shape of b{idx + 1}: {b.shape}')
        return

    def forward_pass(self):
        # assign a temporary variable which holds the propagated input
        X_tmp = self.X
        S = 0
        for i in range(self.num_layers):
            S= self.W[i] @ X_tmp + self.b[i]
            X_tmp = np.maximum(0, S)
        # Apply the final linear transformation
        S = self.W[self.k] @ X_tmp + self.b[self.k]
        # Apply softmax operation to turn final scores into probabilties
        P = softmax(S)
        return P

    def compute_cost(self):
        reg_sum = 0
        for w in self.W:
            reg_sum += self.lamda * np.sum(w**2)
            pass


def main():
    knn = KNN(X=None, Y=None, y=None,
                 X_eval=None, Y_eval=None, y_eval=None,
                 X_test=None, Y_test=None, y_test=None,
                 batch_size=0, n_epochs=1, eta=0, lamda=0,
                num_layers=4, num_nodes=[50, 30, 20], verbose=True)
    knn.parse_full_data(val_split=5000)
    knn.initialize_params()


if __name__ == '__main__':
    main()
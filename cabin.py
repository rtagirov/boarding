import numpy as np

import random

from itertools import product

import math

def Prob(E, T, i0 = 0):

    Nrow = len(E[:, 0])

    Ncol = len(E[0, :])

    p = np.zeros((Nrow, Ncol))

    Z = 0; p[:, :] = 0.0e+0

    for i, j in product(range(i0, Nrow), range(Ncol)): Z += math.exp(-E[i, j] / T)

    for i, j in product(range(i0, Nrow), range(Ncol)): p[i, j] = math.exp(-E[i, j] / T) / Z

    return p

def Image(cab):

    Nrow = len(cab)

    Ncol = len(cab[0])

    cabimg = [[0] * Ncol for i in range(Nrow)]
    
    for i, j in product(range(Nrow), range(Ncol)):

        if cab[i][j] > 0: cabimg[i][j] = 1

    return cabimg

def ChooseSeat(p):

    r = random.uniform(0, 1)

    s = 0.0; i = 0; j = 0

    while s <= r:

        s += p[i, j]

        i_seat = i; j_seat = j

        if j < 6:

            j += 1

        else:

            i += 1; j = 0

    return [i_seat, j_seat]

def Aisle(cab):

    a = []

    for i in range(len(cab)): a.append(cab[i][3])

    return a

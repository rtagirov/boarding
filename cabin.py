import numpy as np
import random
import math

from itertools import product

# Nrow, Ncol --- number of rows and columns in the airplane cabin
# alpha --- the linear slope of the seat energies along the aisle
# mean_llt --- mean luggage loading time
# T --- temperature of the passengers 
# (measure of their apathy towards the seat choice)
# higher temperature ---> higher apathy
# stat --- possible passenger statuses
def initiate(Nrow, Ncol, Nempty, mean_llt, alpha, T, stat):

#   number of passengers
#   Nepmty --- number of seats that will remain empty 
#   after the boarding is complete (this parameter needed for
#   the case of partially filled aircraft)
    Npsg = Nrow * (Ncol - 1) - Nempty

#   creating a dictionary with information about passengers
    psg = {}

    for i in range(1, Npsg + 1):

#       dest --- destination, list of length 2 giving the coordinates of the chosen seat,
#                unless the passenger is out of the aircraft, in which case
#                'dest' is string 'tbd' (to be determined)
#       loc ---  location of the passenger along the cabin aisle, integer equal to the row number,
#                unless the passenger is out of the aircraft, in which case it is equal to -1
#       llt ---  luggage loading time
#       stat --- passenger status, string, stat[0] means out of the airplane
        psg[i] = {'dest': 'tbd', 'loc': -1, 'llt': random.uniform(0.0, 2.0 * mean_llt), 'stat': stat[0]}

#   2D integer numpy array, filled with zeros and one 1,
#   representing the initial state of the airplane cabin
#   in which the passenger number 1 enters the cabin and
#   occupies the 0th cell of the aisle
    cab = np.zeros((Nrow, Ncol), dtype = int)

    cab[0, 3] = 1

    E = np.zeros((Nrow, Ncol))

#   seat energies in the 0th row
    E[Nrow - 1, 0] = -7.0
    E[Nrow - 1, 1] = -5.0
    E[Nrow - 1, 2] = -8.0
    E[Nrow - 1, 3] = 1.0e+100
    E[Nrow - 1, 4] = -8.0
    E[Nrow - 1, 5] = -5.0
    E[Nrow - 1, 6] = -7.0

#   linear scaling of the seat energies along the airplane cabin
    for i in range(Nrow - 2, -1, -1):

        E[i, :] = E[Nrow - 1, :] + alpha * (Nrow - 1 - i)

#   initial probabilities
    p = prob(E, T)

#   first passenger chooses a seat
    psg[1]['dest'] = choose_seat(p)
    psg[1]['loc'] = 0
    psg[1]['stat'] = stat[1]

    return psg, Npsg, cab, E, p

# list all passengers that have entered the cabin
def list_cab(psg):

    for num in psg.keys():

#       passenger has entered the cabin if his destination 
#       value is a list, otherwise it is a string ('tbd')
        if type(psg[num]['dest']) == list:

            print(num, ':', psg[num])

def show(l, psg, what):

    if what == 'r':

        for num in l:

            print('Passenger ', num, ' is now headed to seat ', psg[num]['dest'])

    if what == 's':

        for num in l:

            print('Passenger ', num, ' has seated')

            del psg[num]

def prob(E, T, i0 = 0):

    Nrow = len(E[:, 0])

    Ncol = len(E[0, :])

    p = np.zeros((Nrow, Ncol))

    Z = 0.0

    p[:, :] = 0.0e+0

    for i, j in product(range(i0, Nrow), range(Ncol)):

        Z += math.exp(-E[i, j] / T)

    for i, j in product(range(i0, Nrow), range(Ncol)):

        p[i, j] = math.exp(-E[i, j] / T) / Z

    return p

# take an image of the cabin
# wherever there is a passenger the image is equal to 1
# wherever there is no passenger the image is equal to 0
def image(cab):

    Nrow = len(cab[:, 0])

    Ncol = len(cab[0, :])

    img = np.zeros((Nrow, Ncol), dtype = int)

    img[np.where(cab > 0)] = 1

    return img

def choose_seat(p):

    Ncol = len(p[0, :]) - 1

    r = random.uniform(0, 1)

    s = 0.0; i = 0; j = 0

    while s <= r:

        s += p[i, j]

        i_seat = i

        j_seat = j

        if j < Ncol:

            j += 1

        else:

            i += 1

            j = 0

    return [i_seat, j_seat]

def time_increment(time_contrib):

    tc = np.array(time_contrib)

    all_tc_lt_one = np.all(tc < 1.0)

    if all_tc_lt_one:

        dt = max(tc)

    else:

        dt = np.sum(tc[np.where(tc < 1.0)])

        if dt < 1.0:

            dt = 1.0

    return dt

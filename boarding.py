import math

import numpy as np

import sys

import importlib

import cabin; importlib.reload(cabin)

Nrow = 5; Ncol = 7; Nempty = 0

Npsg = Nrow * (Ncol - 1) - Nempty

psg_num = []; psg_dest = []; psg_loc = []

for i in range(1, Npsg + 1):

    psg_num.append(i)

    psg_dest.append('tbd')

    psg_loc.append(-1)

psg = {}

for i in range(Npsg): psg[psg_num[i]] = {'dest': psg_dest[i], 'loc': psg_loc[i]}

cab =    [[0] * Ncol for i in range(Nrow)]; cab[0][3] = 1

cabimg = cabin.Image(cab)

E = np.zeros((Nrow, Ncol))

T = 1

E[Nrow - 1, 0] = -7.0
E[Nrow - 1, 1] = -5.0
E[Nrow - 1, 2] = -8.0
E[Nrow - 1, 3] = 1.0e+100
E[Nrow - 1, 4] = -8.0
E[Nrow - 1, 5] = -5.0
E[Nrow - 1, 6] = -7.0

alpha = -0.25

for i in range(Nrow - 2, -1, -1): E[i, :] = E[Nrow - 1, :] + alpha * (Nrow - 1 - i)

p = cabin.Prob(E, T)

psg[1]['dest'] = cabin.ChooseSeat(p); psg[1]['loc'] = 0

for i in range(len(cabimg)): print(cabimg[i])

while psg:

    for num in psg.keys():

        print(num, ':', psg[num])

    seat_change = []

    for num in psg.keys():

        psg_loc = psg[num]['loc']

        psg_dest = psg[num]['dest']

        if type(psg_dest) == list:

            if cab[psg_dest[0]][psg_dest[1]] != 0:

                ahead = cabin.Prob(E, T, psg_loc)
            
                psg[num]['dest'] = cabin.ChooseSeat(ahead)

                seat_change.append(num)

    for num in seat_change:

        print('Passenger ', num, ' changed seat to ', psg[num]['dest'])

    seated_psg = []

    for num in psg.keys():

        psg_loc = psg[num]['loc']

        psg_dest = psg[num]['dest']

        if type(psg_dest) == str or psg_loc != psg_dest[0]: continue

        cab[psg_loc][3] = 0

        cab[psg_dest[0]][psg_dest[1]] = num

        seated_psg.append(num)

        E[psg_dest[0], psg_dest[1]] = 1.0e+100

        if num != Npsg: p = cabin.Prob(E, T)

        if num == Npsg: p[psg_dest[0], psg_dest[1]] = 0.0e0

        cabimg = cabin.Image(cab)

    for num in seated_psg:

        print('Passenger ', num, ' seated')

        del psg[num]

    seated_psg = []

    aisle = cabin.Aisle(cabimg)

    if psg and aisle[0] == 0 and aisle[1] == 0:

        for num in psg.keys():

            if type(psg[num]['dest']) == str:

                print('New Passenger ', num)

                psg_dest = cabin.ChooseSeat(p)

                psg[num]['dest'] = psg_dest

                psg[num]['loc'] = 0

                if psg_dest[0] == 0:

                    cab[0][psg_dest[1]] = num

                    cabimg = cabin.Image(cab)

                    E[0, psg_dest[1]] = 1.0e+100

                    p = cabin.Prob(E, T)

                    seated_psg.append(num)

                    continue

                cab[0][3] = num

                cabimg = cabin.Image(cab)

                break

        for num in seated_psg:

            print('Passenger ', num, ' seated')

            del psg[num]

    aisle = cabin.Aisle(cabimg)

    for i in range(Nrow - 2):

        if psg and aisle[i] == 1 and aisle[i + 1] == 0 and aisle[i + 2] == 0:

            psg_num = cab[i][3]

            cab[i]    [3]    = 0
            cab[i + 1][3]    = psg_num

            cabimg = cabin.Image(cab)

            psg[psg_num]['loc'] = i + 1

    for i in range(len(cabimg)): print(cab[i])

    print('\n')

    aisle = cabin.Aisle(cabimg)

    if psg and aisle[Nrow - 1] == 0 and aisle[Nrow - 2] == 1:

        psg_num = cab[Nrow - 2][3]

        if psg[psg_num]['dest'][0] == Nrow - 1:

            cab[Nrow - 2][3] = 0
            cab[Nrow - 1][3] = psg_num

            cabimg = cabin.Image(cab)

            psg[psg_num]['loc'] = Nrow - 1

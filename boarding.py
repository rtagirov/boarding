import numpy as np
import math
import sys
import random
import importlib

if not '../aux/' in sys.path: sys.path.append('../aux/')

import cabin
import auxsys

importlib.reload(cabin)
importlib.reload(auxsys)

Nrow = 20
Ncol = 7
Nempty = 0
#Nempty = 120

Npsg = Nrow * (Ncol - 1) - Nempty

psg = {}

for i in range(1, Npsg + 1):

    psg[i] = {'dest': 'tbd', 'loc': -1, 'llt': random.uniform(0, 100), 'stat': 'oo'}

#sys.exit()

cab = [[0] * Ncol for i in range(Nrow)]
cab[0][3] = 1

cabimg = cabin.image(cab)

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

for i in range(Nrow - 2, -1, -1):

    E[i, :] = E[Nrow - 1, :] + alpha * (Nrow - 1 - i)

#initial probabilities
p = cabin.prob(E, T)

#possible passenger statuses
stat = ['mf', 'ww', 'll', 'ld', 'mb']

#first passenger chooses a seat
psg[1]['dest'] = cabin.choose_seat(p)
psg[1]['loc'] = 0
psg[1]['stat'] = stat[0]

for i in range(len(cabimg)):

    print(cabimg[i])

time = 0.0

time_step = 0

while psg:

# listing all passegners that have entered the cabin
    for num in psg.keys():

        if type(psg[num]['dest']) == list:

            print(num, ':', psg[num])

#-------------------------------------------------------------------------
# first thing is to check whether any passenger needs to change their seat
# because it has been taken while they were walking to it
#-------------------------------------------------------------------------
    redirected = []

    for num in psg.keys():

        loc = psg[num]['loc']

        dest = psg[num]['dest']

# this condition means that the passenger has entered the airplane cabin
        if type(dest) == list:

# this condition means that their chosed seat has been occupied
            if cab[dest[0]][dest[1]] != 0:

                ahead = cabin.prob(E, T, loc)
            
                psg[num]['dest'] = cabin.choose_seat(ahead)

                redirected.append(num)

    for num in redirected:

        print('Passenger ', num, ' is now headed to seat ', psg[num]['dest'])

#---------------------------------------------------------------------------
# secondly we check which passengers (if any) have reached their chosen seat
#---------------------------------------------------------------------------

    time_contrib = []

    seated = []

    for num in psg.keys():

        loc = psg[num]['loc']

        dest = psg[num]['dest']

        if type(dest) == str or loc != dest[0]:

            continue

        remaining = psg[num]['llt']

        if remaining == 0.0:

            cab[loc][3] = 0

            cab[dest[0]][dest[1]] = num

            time_contrib.append(0.0)

            seated.append(num)

            E[dest[0], dest[1]] = 1.0e+100

            if len(psg) == 1:

                p[dest[0], dest[1]] = 0.0e0

            else:

                p = cabin.prob(E, T)

            cabimg = cabin.image(cab)

            continue

        if  remaining > 1.0:

            psg[num]['llt'] = remaining - 1.0

            psg[num]['stat'] = stat[2]

            time_contrib.append(1.0)

        if  remaining <= 1.0:

            psg[num]['llt'] = 0.0

            psg[num]['stat'] = stat[3]

            time_contrib.append(remaining)

    for num in seated:

        print('Passenger ', num, ' seated')

        del psg[num]

    seated = []

    a = cabin.aisle(cabimg)

    if psg and a[0] == 0 and a[1] == 0:

        for num in psg.keys():

            if type(psg[num]['dest']) == str:

                print('New Passenger ', num)

                dest = cabin.choose_seat(p)

                psg[num]['dest'] = dest

                psg[num]['loc'] = 0

                psg[num]['stat'] = stat[0]

                if dest[0] == 0:

                    remaining = psg[num]['llt']

                    if remaining == 0.0:

                        cab[0][dest[1]] = num

                        cabimg = cabin.image(cab)

                        E[0, dest[1]] = 1.0e+100

                        p = cabin.prob(E, T)

                        time_contrib.append(0.0)

                        seated.append(num)

                        continue

                    if  remaining > 1.0:

                        psg[num]['llt'] = remaining - 1.0

                        psg[num]['stat'] = stat[2]

                        time_contrib.append(1.0)

                    if  remaining <= 1.0:

                        psg[num]['llt'] = 0.0

                        psg[num]['stat'] = stat[3]

                        time_contrib.append(remaining)

                cab[0][3] = num

                cabimg = cabin.image(cab)

                break

        for num in seated:

            print('Passenger ', num, ' seated')

            del psg[num]

    a = cabin.aisle(cabimg)

#---------------------------------------------------------------------------
# Change status of passengers depending on their current status and wheather
# they can move forward
#---------------------------------------------------------------------------
    for i in range(Nrow - 2):

        num = cab[i][3]

        if num == 0:

            continue

        not_luggage = psg[num]['stat'] != stat[2] and psg[num]['stat'] != stat[3]

        if not_luggage and a[i] == 1 and a[i + 1] == 0 and a[i + 2] == 0:

            psg[num]['stat'] = stat[0]

        if not_luggage and a[i] == 1 and a[i + 1] == 0 and a[i + 2] == 1:

            psg[num]['stat'] = stat[1]

            print('Passenger ', num, 'is waiting')

        if not_luggage and a[i] == 1 and a[i + 1] == 1:

            psg[num]['stat'] = stat[1]

            print('Passenger ', num, ' is waiting')

#---------------------------------------------------------------------------
# Move passenger one cell further if there is an empty cell in front and the
# passenger is moving already
#---------------------------------------------------------------------------
    for i in range(Nrow - 1):

        if a[i] == 1 and a[i + 1] == 0:

            num = cab[i][3]

            if psg[num]['stat'] == stat[0]:

                cab[i][3] = 0
                cab[i + 1][3] = num

                cabimg = cabin.image(cab)

                psg[num]['loc'] = i + 1

                time_contrib.append(1.0)

    if not time_contrib:

        auxsys.abort('time_contrib list is somehow empty. Abort.')

    time += cabin.time_increment(time_contrib)

    time_step += 1

    for i in range(len(cabimg)):

        print(cab[i])

    print('\ntime_step = ', time_step, ' time = ', time, '\n')

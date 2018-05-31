import numpy as np
import math
import sys
import random
import importlib

import cabin
import auxsys

importlib.reload(cabin)
importlib.reload(auxsys)

# Nrow, Ncol --- number of rows and columns in the airplane cabin
# Nepmty --- number of seats that will remain empty 
# after the boarding is complete (this parameter needed for
# the case of partially filled aircraft)
# mean_llt --- mean luggage loading time
# alpha --- the linear slope of the seat energies along the aisle
Nrow = 20
Ncol = 7
Nempty = 0
mean_llt = 50.0
alpha = -0.25

# temperature of the passengers (measure of their apathy towards the seat choice)
# higher temperature ---> higher apathy
T = 1.0

# possible passenger statuses
# 0: oa --- out of the airplane
# 1: mf --- moving forward
# 2: ww --- waiting
# 3: ll --- loading luggage
# 4: ld --- luggage done (i.e. ready to sit down)
# 5: mb --- moving backward
stat = ['oa', 'mf', 'ww', 'll', 'ld', 'mb']

# create the airplane cabin and the passenger dictionary
psg, Npsg, cab, E, p = cabin.initiate(Nrow, Ncol, Nempty, mean_llt, alpha, T, stat)

print(cab)

# each cabin scan adds 1 to the time step counter
# time_step is always an integer number
time_step = 0

# each cabin scan adds a cetrain amount of time to the time counter
# see function time_increment in cabin.py for the way the
# time increment of each scan is calculated
time = 0.0

# the aisle of the cabin will be scanned until there are no passengers left
# in the passenger dictionary, i.e. until all passengers are seated
while psg:

#   list all passengers that have entered the cabin
    cabin.list_cab(psg)

#-------------------------------------------------------------------
#   first, we check whether any passenger needs to change their seat
#   because it has been taken while they were walking to it
#-------------------------------------------------------------------
    redirected = []

#   loop over passengers
    for n in psg.keys():

        loc = psg[n]['loc']

        dest = psg[n]['dest']

#       this condition means that the passenger has entered the airplane cabin
        if type(dest) == list:

#           this condition means that their chosed seat has been occupied
            if cab[dest[0], dest[1]] != 0:

#               recalculate probabilites, but using only seats ahead of the passenger, i.e.
#               starting from the passenger's current location
                ahead = cabin.prob(E, T, loc)

#               choose seat with the recalculated probabilities ahead of the passenger
                psg[n]['dest'] = cabin.choose_seat(ahead)

#               register a redirected passenger
#               the statement after this one prints out numbers of
#               all redirected passengers
                redirected.append(n)

#   print out the number of passengers who have changed their destination
    cabin.show(redirected, psg, 'r')

#--------------------------------------------------------------------------
# second, we check which passengers (if any) have reached their chosen seat
#--------------------------------------------------------------------------

#   if a passenger has reached their seat, but is in the process of
#   loading their luggage we add the corresponding time contribution to
#   the time contribution list;
#   this time contribution list is later proccessed by the function
#   time_increment in cabin.py to figure out the resulting time contribution
#   of the current cabin scan
    time_contrib = []

#   if a passenger has reached their seat and they are done with the luggage
#   they sit down and their number is added to the 'seated' list in order for
#   those passengers to be removed from the passenger dictionary
    seated = []

#   loop over passengers
    for n in psg.keys():

        loc = psg[n]['loc']

        dest = psg[n]['dest']

#       the first condition means that passenger is
#       not in the cabin, the second means that
#       they have not reached their seat
#       in these cases we just continue the loop over passengers
        if type(dest) == str or loc != dest[0]:

            continue

#       if they reached their seat we check
#       how much time they still need to
#       load their luggage
        remaining = psg[n]['llt']

#       if they are done with their luggage they sit down
        if remaining == 0.0:

#           remove from the aisle
            cab[loc, 3] = 0

#           fill the seat location in the cabin with the passenger number
            cab[dest[0], dest[1]] = n

#           we neglect the time it takes a passenger to sit down
            time_contrib.append(0.0)

#           register the seated passenger in order to remove
#           them from the passenger dictionary later
            seated.append(n)

#           the occupied seat has zero probability to be chosen again
            E[dest[0], dest[1]] = 1.0e+100

            if len(psg) == 1:

#               if we are dealing with the last passenger the probability has to be
#               put to zero directly otherwise we encounter an error
#               (division by zero partition function when recalculating the seat probabilities)
                p[dest[0], dest[1]] = 0.0e0

            else:

#               if we are not dealing with the last passenger we just recalculate the
#               probabilities with the new partition function 
#               (the occupied seat just changed its energy)
                p = cabin.prob(E, T)

            continue

#       passenger is about to finish loading luggage
#       (during the next cabin scan this passenger will sit down)
        if remaining <= 1.0:

#           put remaining luggage loading time to zero
            psg[n]['llt'] = 0.0

#           change status to luggage loading done
            psg[n]['stat'] = stat[4]

#           add the remaining luggage loading time
#           to the time contribution of the current cabin scan
            time_contrib.append(remaining)

#       passenger is still loading the luggage
        if remaining > 1.0:

#           subtract the time increment (1 second) from their remaining luggage loading time
            psg[n]['llt'] = remaining - 1.0

#           passenger status is luggage loading
            psg[n]['stat'] = stat[3]

#           add the time increment of 1 second
#           to the time contribution list of the current cabin scan;
#           this list is processed at the end of the main while loop
#           by time_increment procedure (see cabin.py) to figure out
#           the resulting time contribution corresponding to the scan
            time_contrib.append(1.0)

#   print out the numbers of seated passengers
#   and delete these passengers from the passenger dictionary
    cabin.show(seated, psg, 's')

#-----------------------------------------------------------
# third, we check if the first and second cells of the aisle 
# are free so that new passenger can enter the cabin
#-----------------------------------------------------------

#   renew the 'seated' list in case the new passenger
#   is ready to sit down right away
    seated = []

#   extracting the aisle image of the cabin
#   [:, 3] is the aisle of the cabin image
#   cabin image is a numpy array of zeros and ones
    a = cabin.image(cab)[:, 3]

#   the first part of this condition makes sure that we
#   do not perform the check if there are no passengers left
#   in the dictionary, i.e. if all passengers are seated
#   second and third parts mean that first and second cells of
#   the aisle are empty
    if psg and a[0] == 0 and a[1] == 0:

#       loop over passenger dictionary to find the first passenger
#       with 'to be determined' destination because that passenger
#       is the next one in the queue to enter the airplane cabin
        for n in psg.keys():

#           condition for the passenger with 'to be determined' destination
            if type(psg[n]['dest']) == str:

                print('New Passenger ', n)

#               new passenger chooses seat
                dest = cabin.choose_seat(p)

#               change passenger destination
                psg[n]['dest'] = dest

#               put passenger in the first cell of the aisle
                psg[n]['loc'] = 0

#               change passenger's status to 'moving forward'
                psg[n]['stat'] = stat[1]

#               check if the passenger's destination is in the first row
                if dest[0] == 0:

#                   if the passenger's destination is in the first row
#                   then check how much time they need to unload their luggage
                    llt = psg[n]['llt']

#                   if they have no luggage they sit down
                    if llt == 0.0:

#                       fill the seat location in the cabin with the passenger number
                        cab[0, dest[1]] = n

#                       the occupied seat has zero probability to be chosen again
                        E[0, dest[1]] = 1.0e+100

#                       recalculate the seat probabilities with the new partition function
#                       (the occupied seat has just changed its energy)
                        p = cabin.prob(E, T)

#                       we neglect the time it takes a passenger to sit down
                        time_contrib.append(0.0)

#                       register the seated passenger in order to remove
#                       them from the passenger dictionary later
                        seated.append(n)

#                       continue to the next passenger in the queue to enter the cabin
                        continue

#                   passenger has almost no luggage
                    if llt <= 1.0:

#                       put remaining luggage loading time to zero
                        psg[n]['llt'] = 0.0

#                       change status to luggage loading done
                        psg[n]['stat'] = stat[4]

#                       add their luggage loading time to the time
#                       contribution of the current cabin scan
                        time_contrib.append(llt)

#                   passenger has luggage and starts unloading it
                    if llt > 1.0:

#                       subtract the time increment (1 second) from their luggage loading time
                        psg[n]['llt'] = llt - 1.0

#                       passenger status is luggage loading
                        psg[n]['stat'] = stat[3]

#                       add the time increment of 1 second
#                       to the time contribution list of the current cabin scan;
#                       this list is processed at the end of the main while loop
#                       by time_increment procedure (see cabin.py) to figure out
#                       the resulting time contribution corresponding to the scan
                        time_contrib.append(1.0)

#               new passenger is in the 0-th cell of the aisle
                cab[0, 3] = n

#               no need to go further through the passenger dictionary
                break

#       print out the numbers of passengers who just sat down (if any)
        cabin.show(seated, psg, 's')

#---------------------------------------------------------------
# fourth, change status of passengers depending on their current
# status and wheather they can move forward
#---------------------------------------------------------------

#   extract the aisle image of the cabin
    a = cabin.image(cab)[:, 3]

#   loop over the aisle cells
    for i in range(Nrow - 2):

#       retrieve the number of the passenger in i-th cell
        n = cab[i, 3]

#       cell is free
        if n == 0:

            continue

#       this condition means that passenger is not in the process of loading their luggage
        if psg[n]['stat'] != stat[3] and psg[n]['stat'] != stat[4]:

#           see rule (1) in section C of free_for_all.pdf
            if a[i + 1] == 0 and a[i + 2] == 0:

#               updating passenger status to moving forward
#               (i.e. passenger starts moving)
                psg[n]['stat'] = stat[1]

#           next aisle cell is occupied
            if a[i + 1] == 1:

#               updating passenger status to waiting
                psg[n]['stat'] = stat[2]

                print('Passenger ', n, ' is waiting')

#--------------------------------------------------------------------------
# fifth, if a passenger has started moving, then they will occupy any empty
# space in front of them prior to stopping
#--------------------------------------------------------------------------

#   loop over the aisle cells
    for i in range(Nrow - 1):

#       if there is a passenger in cell i and
#       no passenger in the next cell
        if a[i] == 1 and a[i + 1] == 0:

#           retrieve passenger number
            n = cab[i, 3]

#           check that the passenger has started moving
#           and if so move them one cell further;
#           see rule (2) in section C of free_for_all.pdf
            if psg[n]['stat'] == stat[1]:

                cab[i, 3] = 0
                cab[i + 1, 3] = n

                psg[n]['loc'] = i + 1

#               walking the distance between adjacent rows takes 1 second
                time_contrib.append(1.0)

#   if time_contrib list somehow turned out to be empty
    if not time_contrib:

        auxsys.abort('time_contrib list is somehow empty.')

    time += cabin.time_increment(time_contrib)

    time_step += 1

    print(cab)

    print('\ntime_step = ', time_step, ' time = ', time, '\n')

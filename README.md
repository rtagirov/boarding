This version just walks N passengers to their seats (currently, N = 30).
Sometimes the last passenger fails to be seated because there is a bug associated with the partition function.
It happens rarely, when there are no seats left in the front of the airplane, and
therefore, since going backwards is not implemented, the probabilities of all the seats which the last
passanger chooses from equal zero, as well as the partition function.
As a result, because the probabilities are normalized by the partition function, we get division by zero.

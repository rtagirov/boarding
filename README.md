This version walks N passengers to their seats (currently, N = 120),
taking into accout the luggage loading. The time tracking associated with the luggage loading as well as the movement of passengers has been added.
The 'psg' dictionary now has an entry: 'llt' - luggage loading time.
The other entry 'stat' has been added to implement the movement rules described in the original paper in a more precise manner.
Moving back is has not been implemented yet, though the corresponding status in the 'stat' list has been introduced.
The bug mentioned in the README.md of the master branch has been fixed.

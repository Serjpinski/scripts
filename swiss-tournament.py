#!/usr/bin/python

from sys import argv
from string import split
from random import shuffle
from operator import itemgetter

if len(argv) < 2:

    print "playerlist file required"
    print "usage: python swiss-tournament.py playerlist"
    exit(1)

playerlist = [[index] + split(line[0:-1], sep = '\t') for index, line in enumerate(open(argv[1]))]

for player in playerlist:
    player[2] = float(player[2])

shuffle(playerlist)

playerlist = sorted(playerlist, key = itemgetter(2), reverse = True)
print playerlist

while len(playerlist) > 1:

    player1 = playerlist.pop(0)
    found = False

    for player2 in playerlist:

        if not found and player1[3 + player2[0]] == "-":

            print player1[1] + "\t-\t" + player2[1]
            playerlist.remove(player2)
            found = True


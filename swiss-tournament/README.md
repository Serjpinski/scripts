# swiss-tournament
Simple **ad-hoc** script that computes pairings for a [swiss-system tournament](https://en.wikipedia.org/wiki/Swiss-system_tournament).

# Pairing rules

1. Players are ordered by score. Players with the same score are ordered randomly.
1. Players are paired based on their order: #1 vs #2, #3 vs #4, etc.
1. Repeated pairings are excluded.

This algorithm does **NOT** grant valid pairings for all players. Repeated pairings may be needed. The higher the ratio rounds/players, the bigger the chance for this situation to happen.

# Usage

`$ python swiss-tournament.py inputFile`

Input files are composed of one line for each player. Lines have tab separated values:
- Player name (string containing anything but tabs)
- Score (integer or real)
- List of tab separated results versus each player (including itself). Result values can be anything, what matters is that non-played pairings are marked with `-`. Any other string is considered as an already played pairing, thus not elegible.

Sample input file:
```
Player1	0	-	0	0	-	-	-
Player2	1	1	-	-	-	-	0
Player3	2	1	-	-	-	1	-
Player4	2	-	-	-	-	1	1
Player5	0	-	-	0	0	-	-
Player6	1	-	1	-	0	-	-
```

Sample output:
```
Player4	-	Player3
Player2	-	Player5
Player6	-	Player1
```

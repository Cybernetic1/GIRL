#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

from rete.common import Has, Rule, WME, Neg, Ncc, Token
from rete.network import Network

print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

net = Network()

# Can win a vertical column:
# X($y, $x) ^ X($z, $x) ^ □($w, $x) ^ ($y != $z) => playX($w, $x)
p0 = net.add_production(Rule(
	Has('X', '$y', '$x'),
	Has('X', '$z', '$x'),
	Has('□', '$w', '$x'),
	Has('!=', '$y', '$z'),
))
p0.postcondition = Has("oldX", '$w', '$x')

# Can win a horizontal row:
# X($x, $y) ^ X($x, $z) ^ □($x, $w) ^ ($y != $z) => playX($x, $w)

# Can win a diagonal:
# X($x, $x) ^ X($y, $y) ^ □($z, $z) ^ ($x != $y) ^ ($y != $z) ^ ($z != $x) => playX($z, $z)

# Can win a backward diagonal: (0,2) (1,1) (2,0)
# X($x, $z) ^ X($y, $y) ^ □($z, $x) ^ ($x != $y) ^ ($y != $z) ^ ($z != $x) => playX($z, $z)

# If enemy can win, we need to block it:

# Must block a vertical column:
# O($y, $x) ^ O($z, $x) ^ □($w, $x) ^ ($y != $z) => playX($w, $x)

# Must block a horizontal row:
# Must block a diagonal:
# Must block a backward diagonal:

# Otherwise, prefer a tile that can lead to 'double fork'
# Otherwise, just play randomly

def show_board(board):
	for i in [0, 3, 6]:
		for j in range(3):
			x = board[i + j]
			if x == -1:
				c = '❌'
			elif x == 1:
				c = '⭕'
			else:
				c = '  '
			print(c, end='')
		print(end='\n')

board = 9 * [0]
# ⭕  ❌
# ⭕❌⭕
#   ❌⭕
wmes = [
	WME('X', 0, 2),
	WME('X', 1, 1),
	WME('X', 2, 1),
	WME('O', 0, 0),
	WME('O', 1, 0),
	WME('O', 1, 2),
	WME('O', 2, 2),
	WME('□', 0, 1),
	WME('□', 2, 0),
]
for wme in wmes:
	net.add_wme(wme)
	if wme.F0 == 'X':
		x = -1
	elif wme.F0 == 'O':
		x = 1
	else:
		x = 0
	board[ wme.F1 * 3 + wme.F2 ] = x
print("\nFacts:")
show_board(board)

print("\n# of p0 results = ", len(p0.items))
print("Results:")
for i in p0.items:
	print(i)

f = open("rete1.dot", "w+")
f.write(net.dump())
f.close()
os.system("dot -Tpng rete1.dot -orete1.png")
print("\nRete graph saved as rete1.png\n")

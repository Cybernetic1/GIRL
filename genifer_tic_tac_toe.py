#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

from rete.common import Has, Rule, WME, Neg, Ncc, Token
from rete.network import Network

print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

net = Network()

c01 = Has('X', '$y', '$x')
c02 = Has('X', '$z', '$x')
c03 = Has('□', '$w', '$x')
c04 = Has('!=', '$y', '$z')
p0 = net.add_production(Rule(c01, c02, c03, c04))

#c04 = Has('O', '$x', '$x')
#c05 = Has('□', '$y', '$z')
#c06 = Has('>', '$y', '$z')
#p1 = net.add_production(Rule(c04, c05, c06))

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
	WME('X', '0', '2'),
	WME('X', '1', '1'),
	WME('X', '2', '1'),
	WME('O', '0', '0'),
	WME('O', '1', '0'),
	WME('O', '1', '2'),
	WME('O', '2', '2'),
	WME('□', '0', '1'),
	WME('□', '2', '0'),
	#WME('!=', '1', '2'),
	#WME('!=', '2', '1'),
]
for wme in wmes:
	net.add_wme(wme)
	if wme.F1 == 'X':
		x = -1
	elif wme.F1 == 'O':
		x = 1
	else:
		x = 0
	board[ int(wme.F2) * 3 + int(wme.F3) ] = x
print("\nFacts:")
show_board(board)

print("\n# of results = ", len(p0.items))
print("Results:")
for i in p0.items:
	print(i)

f = open("rete.dot", "w+")
f.write(net.dump())
f.close()
os.system("dot -Tpng rete.dot -orete.png")
print("\nRete graph saved as rete.png\n")

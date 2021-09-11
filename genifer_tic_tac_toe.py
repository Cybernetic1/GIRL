#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TO-DO:
# * need ability to make logic assumptions (how?)
# * need fuzzy or probabilistic truth values

import sys
import os

from rete.common import DEBUG, Has, Rule, WME, Neg, Ncc, Token
from rete.network import Network

print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

net = Network()
p = []				# list of p-Nodes

# **** General strategy ****
# - if can win, play it
# - about to lose, play it
# - if center not occupied, play it
# - if able to 'double-fork', play it
# - play randomly

# row 0 win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 0),
	Has('π0', '$y', 0),
	Has('π0', '$z', 0),
)))
p[-1].postcondition = Has("row_0_win", '$x')

# row 1 win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 1),
	Has('π0', '$y', 1),
	Has('π0', '$z', 1),
)))
p[-1].postcondition = Has("row_1_win", '$x')

# row 2 win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 2),
	Has('π0', '$y', 2),
	Has('π0', '$z', 2),
)))
p[-1].postcondition = Has("row_2_win", '$x')

# column 0 win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 0),
	Has('π1', '$y', 0),
	Has('π1', '$z', 0),
)))
p[-1].postcondition = Has("column_0_win", '$x')

# column 1 win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('π1', '$x', 1),
	Has('π1', '$y', 1),
	Has('π1', '$z', 1),
	Has('!=', '$y', '$z'),
)))
p[-1].postcondition = Has("column_1_win", '$x')

# column 2 win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 2),
	Has('π1', '$y', 2),
	Has('π1', '$z', 2),
)))
p[-1].postcondition = Has("column_2_win", '$x')

# diagonal win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('diag', '$x'),
	Has('diag', '$y'),
	Has('diag', '$z'),
)))
p[-1].postcondition = Has("diag_win", '$x')

# backward diagonal win:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('back_diag', '$x'),
	Has('back_diag', '$y'),
	Has('back_diag', '$z'),
)))
p[-1].postcondition = Has("backdiag_win", '$x')

# prevent row 0 lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 0),
	Has('π0', '$y', 0),
	Has('π0', '$z', 0),
)))
p[-1].postcondition = Has("prevent_row_0_lose", '$x')

# prevent row 1 lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 1),
	Has('π0', '$y', 1),
	Has('π0', '$z', 1),
)))
p[-1].postcondition = Has("prevent_row_1_lose", '$x')

# prevent row 2 lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 2),
	Has('π0', '$y', 2),
	Has('π0', '$z', 2),
)))
p[-1].postcondition = Has("prevent_row_2_lose", '$x')

# prevent column 0 lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 0),
	Has('π1', '$y', 0),
	Has('π1', '$z', 0),
)))
p[-1].postcondition = Has("prevent_column_0_lose", '$x')

# prevent column 1 lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 1),
	Has('π1', '$y', 1),
	Has('π1', '$z', 1),
)))
p[-1].postcondition = Has("prevent_column_1_lose", '$x')

# prevent column 2 lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 2),
	Has('π1', '$y', 2),
	Has('π1', '$z', 2),
)))
p[-1].postcondition = Has("prevent_column_2_lose", '$x')

# prevent diagonal lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('diag', '$x'),
	Has('diag', '$y'),
	Has('diag', '$z'),
)))
p[-1].postcondition = Has("prevent_diag_lose", '$x')

# prevent backward diagonal lose:
p.append(net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('back_diag', '$x'),
	Has('back_diag', '$y'),
	Has('back_diag', '$z'),
)))
p[-1].postcondition = Has("prevent_backdiag_lose", '$x')

# if center not occupied, play it:
p.append(net.add_production(Rule(
	Has('□', (1,1))
)))
p[-1].postcondition = Has("center_empty", (1,1))

# If potential double-fork, play it.
# How to determine double-fork?
#   assume play $x => can-win $y,
#   assume play $x => can-win $z,
#   and $y != $z.
# => potential double-fork exists at position $x

# play randomly:
p.append(net.add_production(Rule(
	Has('□', '$x')
)))
p[-1].postcondition = Has("random_play", '$x')

# Solved: The problem here is that the π1(x,1) proposition needs to
# be checked for x != y, but it has no "Has" representation.
# Now the problem is a "None" token passed down to the Join Node.
# Why is it None? 

f = open("rete.dot", "w+")
f.write(net.dump())
f.close()
os.system("dot -Tpng rete.dot -orete.png")
DEBUG("\nRete graph saved as rete.png\n")

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
	WME('X', (0, 2)),
	WME('X', (1, 1)),
	WME('X', (2, 1)),
	WME('O', (0, 0)),
	WME('O', (1, 0)),
	WME('O', (1, 2)),
	WME('O', (2, 2)),
	WME('□', (0, 1)),
	WME('□', (2, 0)),
]
for wme in wmes:
	net.add_wme(wme)
	if wme.F0 == 'X':
		x = -1
	elif wme.F0 == 'O':
		x = 1
	else:
		x = 0
	board[ wme.F1[0] * 3 + wme.F1[1] ] = x
print("\nFacts:")
show_board(board)

for q in p:
	print(f"\n{q.postcondition} ({len(q.items)} results):")
	for i in q.items:
		print(i)

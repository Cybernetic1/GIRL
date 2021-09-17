#!/usr/bin/python3
# -*- coding: utf-8 -*-

# **** This is a third (improved) representation of the logic of Tic Tac Toe.
# We seek to find a representation that is most "natural" and close to human thinking.

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
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 0),
	Has('π0', '$y', 0),
	Has('π0', '$z', 0),
))
q.postcondition = Has("row_0_win", '$x')
q.truth=1.0
p.append(q)

# row 1 win:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 1),
	Has('π0', '$y', 1),
	Has('π0', '$z', 1),
))
q.postcondition = Has("row_1_win", '$x')
q.truth=1.0
p.append(q)

# row 2 win:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 2),
	Has('π0', '$y', 2),
	Has('π0', '$z', 2),
))
q.postcondition = Has("row_2_win", '$x')
q.truth=1.0
p.append(q)

# column 0 win:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 0),
	Has('π1', '$y', 0),
	Has('π1', '$z', 0),
))
q.postcondition = Has("column_0_win", '$x')
q.truth=1.0
p.append(q)

# column 1 win:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('π1', '$x', 1),
	Has('π1', '$y', 1),
	Has('π1', '$z', 1),
	Has('!=', '$y', '$z'),
))
q.postcondition = Has("column_1_win", '$x')
q.truth=1.0
p.append(q)

# column 2 win:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 2),
	Has('π1', '$y', 2),
	Has('π1', '$z', 2),
))
q.postcondition = Has("column_2_win", '$x')
q.truth=1.0
p.append(q)

# diagonal win:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('diag', '$x'),
	Has('diag', '$y'),
	Has('diag', '$z'),
))
q.postcondition = Has("diag_win", '$x')
q.truth=1.0
p.append(q)

# backward diagonal win:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('X', '$y'),
	Has('X', '$z'),
	Has('!=', '$y', '$z'),
	Has('back_diag', '$x'),
	Has('back_diag', '$y'),
	Has('back_diag', '$z'),
))
q.postcondition = Has("backdiag_win", '$x')
q.truth=1.0
p.append(q)

# prevent row 0 lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 0),
	Has('π0', '$y', 0),
	Has('π0', '$z', 0),
))
q.postcondition = Has("prevent_row_0_lose", '$x')
q.truth=0.8
p.append(q)

# prevent row 1 lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 1),
	Has('π0', '$y', 1),
	Has('π0', '$z', 1),
))
q.postcondition = Has("prevent_row_1_lose", '$x')
q.truth=0.8
p.append(q)

# prevent row 2 lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π0', '$x', 2),
	Has('π0', '$y', 2),
	Has('π0', '$z', 2),
))
q.postcondition = Has("prevent_row_2_lose", '$x')
q.truth=0.8
p.append(q)

# prevent column 0 lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 0),
	Has('π1', '$y', 0),
	Has('π1', '$z', 0),
))
q.postcondition = Has("prevent_column_0_lose", '$x')
q.truth=0.8
p.append(q)

# prevent column 1 lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 1),
	Has('π1', '$y', 1),
	Has('π1', '$z', 1),
))
q.postcondition = Has("prevent_column_1_lose", '$x')
q.truth=0.8
p.append(q)

# prevent column 2 lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('π1', '$x', 2),
	Has('π1', '$y', 2),
	Has('π1', '$z', 2),
))
q.postcondition = Has("prevent_column_2_lose", '$x')
q.truth=0.8
p.append(q)

# prevent diagonal lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('diag', '$x'),
	Has('diag', '$y'),
	Has('diag', '$z'),
))
q.postcondition = Has("prevent_diag_lose", '$x')
q.truth=0.8
p.append(q)

# prevent backward diagonal lose:
q = net.add_production(Rule(
	Has('□', '$x'),
	Has('O', '$y'),
	Has('O', '$z'),
	Has('!=', '$y', '$z'),
	Has('back_diag', '$x'),
	Has('back_diag', '$y'),
	Has('back_diag', '$z'),
))
q.postcondition = Has("prevent_backdiag_lose", '$x')
q.truth=0.8
p.append(q)

# if center not occupied, play it:
q = net.add_production(Rule(
	Has('□', (1,1))
))
q.postcondition = Has("center_empty", (1,1))
q.truth=0.6
p.append(q)

# If potential double-fork, play it.
# How to determine double-fork?
#    assume X plays move $a:
#        assume O plays an arbitrary (non-winning) move,
#            assume X plays move $b then X wins,
#            or, assume X plays move $c then X wins,
#        and $b != $c
#    then $a is a potential fork.

# In other words, perhaps can be expressed as conditional statements?
#    (X plays move $a =>
#        (O plays anything =>
#            (X plays $b => X wins
#            ∨ X plays $c => X wins)
#         ∧ $b != $c))
#     => $a is a potential fork.

# This can be simplied with new predicates:
# 1. (X plays $a => has_fork) => play $a
# 2. O-move can be ignored.
# 3. can_win $b ∧ can_win $c ∧ $b != $c => has_fork
# but the first state is not a proper logic formula (in our system)
# because it contains 2 =>'s.  Perhaps we can convert it to:
# 1'.  (! X plays $a ∨ has_fork) => play $a
# but still, the satisfaction of a conditional statement is not derivable
# in our current system.  Unless we have the ability to put a hypothetical
# fact into our WMEs and then derive the conclusion.

# Actually, more simply:
# 1. X plays $a => ∃$b can_win $b
# 2. X plays $a => ∃$c can_win $c
# 3. $b != $c
# ==> exists fork $a
# but still this is not expressible in our current system because 1 & 2
# are conditionals within the "outer" conditional statement.

# Let's turn it into disjunctions:
# 1. !X plays $a ∨ (∃$b can_win $b)
# 2. !X plays $a ∨ (∃$c can_win $c)
# 3. $b != $c
# ==> exists fork $a

# The above suggests the use of NCC's (negated conjunctions) supported by our Rete:
# 1. ! (X plays $a ∧ ! (∃$b can_win $b))
# 2. ! (X plays $a ∧ ! (∃$b can_win $c))
# 3. $b != $c
# ==> exists fork $a
# but this is still problematic, because $b and $c's bindings seem to be lost or
# mysterious.

# (A => B) => C
# (!A ∨ B) => C
# !(!A ∨ B) ∨ C
# (A ∧ !B) ∨ C
# (A ∨ C), (!B ∨ C)
# !A => C, B => C

# play randomly:
q = net.add_production(Rule(
	Has('□', '$x')
))
q.postcondition = Has("random_play", '$x')
q.truth=0.4
p.append(q)

# Solved: The problem here is that the π1(x,1) proposition needs to
# be checked for x != y, but it has no "Has" representation.
# Now the problem is a "None" token passed down to the Join Node.
# Why is it None? 

f = open("rete.dot", "w+")
f.write(net.dump())
f.close()
os.system("dot -Tpng rete.dot -orete.png")
DEBUG("\nRete graph saved as rete.png\n")

# **** Background knowledge ****
net.add_wme(WME('diag', (0, 0)))
net.add_wme(WME('diag', (1, 1)))
net.add_wme(WME('diag', (2, 2)))
net.add_wme(WME('back_diag', (0, 2)))
net.add_wme(WME('back_diag', (1, 1)))
net.add_wme(WME('back_diag', (2, 0)))

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

print("Setting up board...")
board = 9 * [0]
# ⭕  
#   ❌⭕
#     ❌
wmes = [
	WME('X', (1, 1)),
	WME('X', (2, 2)),
	WME('O', (0, 0)),
	WME('O', (1, 2)),
	WME('□', (0, 1)),
	WME('□', (0, 2)),
	WME('□', (1, 0)),
	WME('□', (2, 0)),
	WME('□', (2, 1)),
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

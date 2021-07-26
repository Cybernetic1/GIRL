# -*- coding: utf8 -*-

# TO-DO:
# * May need multi-step reasoning, but how?
# * rule is sometimes bodiless --- when does it arise?
# * Do all bindings lead to same production?
# * After bug fix, NC's may be nested again, or contain Neg conditions
# * Custom operators and comparisons
# * Rete: clear all memories (retain rules)
# * HTML GUI -- how would Python communicate with Javascript?

# Done:
# * Invention of new predicates
#		- see if / how Rete supports it
#		- keep a list of invented predicates
#		- predicates should only be invented in generate_postconditions
# * Removed empty NCs
# * Fixed bug: delete_token_and_descendents ---> delete_descendents_of_tokens
# * fixed a couple more bugs in Rete

# **** NOTE:  In this new version we use rules that are compatible with Rete,
# that consists only of conjunctions, negations, and negated conjunctions (NC).
# NCs can be nested to any level.  So the general form of a rule is: a conjunction,
# followed by some negated atoms, followed by a possibly nested NC.

# How the score is calculated
# ===========================	
# * moves are saved during a game
# * at game's end, moves (ie. logic rules) are added or subtracted scores
# * the "average fitness" is simply averaged over the entire population of rules

# * Objective function:
#		The KB of rules would be run many times
#		For each game, a positive/negative reward would be obtained
#		That reward would be assigned to the entire inference chain (with time-discount)
#		Over many runs, each candidate rule would accumulate some scores

# * Rule engine (minimalistic):
#		It may be based on Genifer 3 (simple rule engine)
#		This version is based on Genifer 6 (Rete)
#		1. First, evolve a set of rules, import into Rete
#		2. Run the rules for N iterations, record scores
#		3. Repeat

# **** Rete-related ideas:
#		* If Rete is used, we may want to learn the Rete network directly
#		* How to genetically encode a Rete net?
#		* Perhaps differentiable Rete is a better approach?
#		* It may be efficient enough to compile to Rete on each GA iteration 

from random import randint, uniform, choice
import operator
import sys
import math
import os

from rete.common import Has, Rule, WME, Neg, Ncc, is_var # , DEBUG
from rete.network import Network
from rete.network import PNode

# Comment out if you don't need GUI:
# from new_GUI import drawBoard
# import new_GUI

def DEBUG(*args):
	# print(*args)
	return

# ============ Global variables ==============

# Logic parameters:
numPreds = 10	# not used yet
numVars = 4
numConsts = 30
const2varRatio = 0.6      # 0.6 means 60% consts
const2varFlipRate = 0.5   # probability of "var <--> const"

# Evolution parameters:
maxGens = 50
popSize = 300
childrenSize = int(popSize * 0.4)
dropRate = 0.08			# when children size proportion = 40%, 0.1 seems a good choice
crossRate = 0.9
mutationRate = 0.1

maxDepth = 7
bouts = 5
p_repro = 0.08

cache = []			# for storing previously-learned best formulas

var_index = -1		# for creating new logic variables
pred_index = -1		# for creating new predicates

# For Tic Tac Toe:
board = [ [' ']*3 for i in range(3)]
moves = []

# For Rete:
rete_net = None		# declare as global

def export_rule_as_graph(node, fname):
	""" This function is currently not used """
	if fname == "stdout":
		f = sys.stdout
	else:
		f = open(fname + '.dot', 'w')
	f.write("digraph {\n")
	# f.write("fontname=\"times-bold\";")
	print_rule_as_graph(f, node)
	f.write("}\n")
	if fname != "stdout":
		f.close()
		os.system("dot -Tpng %s.dot -o%s.png" % (fname, fname))

def print_rule_as_graph(f, node, index = 0):
	""" This function has to be rewritten """
	op = node[0]
	# if node[0] in op_map:
		# op = op_map[node[0]]
	color = "\"];\n"
	if op == '⋀' or op == '⋁' or op == '=>':
		color = "\",color=\"red\"];\n"
		f.write("node" + str(index) + "[label=\"" + op + color)
		f.write("node" + str(index) + " -> node" + str(index + 1) + ";\n")
		count1 = print_tree_as_graph(f, node[1], index + 1)
		f.write("node" + str(index) + " -> node" + str(index + count1 + 1) + ";\n")
		count2 = print_tree_as_graph(f, node[2], index + count1 + 1)
		return count1 + count2 + 1
	elif op == '~':
		color = "\",color=\"green\"];\n"
		f.write("node" + str(index) + "[label=\"" + op + color)
		f.write("node" + str(index) + " -> node" + str(index + 1) + ";\n")
		count1 = print_tree_as_graph(f, node[1], index + 1)
		return count1 + 1
	else:									# Atoms
		color = "\",style=\"filled\",fillcolor=\"yellow\"];\n"
		label = op + '(' + str(node[1]) + ',' + str(node[2]) + ')'
		f.write("node" + str(index) + "[label=\"" + label + color)
		return 1

def print_rule(rule):
	""" Format of a rule:
		[ => pre-condition post-condition ]
		Format of a pre-condition:
		[ literals ... [NC ... [NC ...] ] ]
	(In the current version of Rete, NC's cannot be nested, but we keep
	the function anyway)
	"""
	# print("rule = ", rule)
	s = ""
	for literal in rule[0]:
		s += print_literal(literal) + ' ⋀ '
	s += print_nc(rule[1])
	if rule[2][0][0] == 'P':
		return s + " \x1b[32;1m=> " + print_literal(rule[2]) + "\x1b[0m"
	else:
		return s + " \x1b[31;1m=> " + print_literal(rule[2]) + "\x1b[0m"

def print_nc(nc):
	if len(nc) == 0:
		return "\x08\x08\x08"
	s = ''
	for atom in nc:
		s += print_literal(atom) + ' '
	return '\x1b[32m~[ ' + s + ']\x1b[0m'

def print_literal(literal):
	if literal[0] == '~':
		return '~' + ('□' if literal[1] == ' ' else literal[1]) + '(' + \
			str(literal[2]) + ',' + str(literal[3]) + ')'
	else:
		# print("litertal[0] = ", literal[0])
		return ('□' if literal[0] == ' ' else literal[0]) + '(' + \
			str(literal[1]) + ',' + str(literal[2]) + ')'

def read_tree(str):			# assume str is in prefix notation with ()'s
	""" old code, needs rewrite """
	if str[0] == '(':
		op = str[1]
		return [
			op,
			read_tree(str[2:]),
			read_tree(str),
			]
	return None

def generate_random_formula():
	global var_index
	var_index = -1
	pre_condition  = generate_random_condition()
	post_condition = generate_random_post_condition()
	return [*pre_condition, post_condition]

# Generate a random (pre-)condition in 2 stages:
# 1) a number of atoms (possibly negated)
# 2) an NC (= negated conjunction, possibly nested)
def generate_random_condition():
	cond = generate_random_conjunction()
	nc = generate_random_NC()
	# New edit: NC can contain negative literals
	# nc = generate_random_conjunction()
	if not cond and not nc:
		return generate_random_condition()
	else:
		return [cond, nc]

def generate_random_NC():
	""" In this version, NC's cannot be nested,
	nor can they contain Neg (negative) conditions. """
	nc = []
	while uniform(0.0, 1.0) < 0.7:
		nc.append(generate_random_atom())
	# if uniform(0.0, 1.0) < 0.3:
		# nc.append(generate_random_NC())
	return nc

def generate_random_conjunction():
	conjunction = []
	while uniform(0.0, 1.0) < 0.7:
		conjunction.append(generate_random_literal())
	return conjunction

def generate_random_literal():
	if uniform(0.0, 1.0) < 0.25:
		return ['~'] + generate_random_atom()
	else:
		return generate_random_atom()

def generate_random_atom():
	""" An atomic logic formula such as X(a,b).
	This function does not invent new predicates! """
	global pred_index
	# choice 0, 1, 2 = X, O, ' ' respectively
	choice = randint(0, pred_index + 3)
	if choice == 0:
		predicate = 'X'
	elif choice == 1:
		predicate = 'O'
	elif choice == 2:
		predicate = ' '
	else:
		predicate = 'P' + str(choice - 3)	# use an existing predicate
	arg1 = generate_random_var_or_const()
	arg2 = generate_random_var_or_const()
	return [predicate, arg1, arg2]

def generate_random_post_condition():
	""" An atom with possibly new predicate invention,
	but not new variable creation """
	global pred_index
	if uniform(0.0, 1.0) > 0.2:
		predicate = 'X'		# this would be an 'action'
	else:
		# infer old predicate or generate a new one:
		if pred_index >= 0 and uniform(0.0, 1.0) > 0.1:
			predicate = 'P' + str(randint(0, pred_index))
		else:
			pred_index += 1
			predicate = 'P' + str(pred_index)
	arg1 = generate_random_var_or_const(False)
	arg2 = generate_random_var_or_const(False)
	return [predicate, arg1, arg2]

def generate_random_var_or_const(create = True):
	""" Result could be old var, new var, or const """
	global var_index
	choice = uniform(0.0, 1.0)
	if create and choice > 0.9:				# new var
		var_index += 1
		return '$' + str(var_index)
	elif choice > 0.5 and var_index >= 0:	# old var
		return '$' + str(randint(0, var_index))
	else:									# constant ∈ {0, 1, 2}
		return randint(0, 2)

def generate_random_inequality(maxDepth, funcs, terms):
	""" Old code, not used yet """
	# determine maxDepth = ?
	arg1 = generate_random_formula(maxDepth, funcs, terms)
	arg2 = generate_random_formula(maxDepth, funcs, terms)
	op = operator.gt if (uniform(0.0, 1.0) > 0.5) else operator.lt
	return [op, arg1, arg2]

def length_of_rule(rule):
	""" Basically, find the length of the rule, where each unit is a point
	of possible mutation / crossover.
	In this version, NC's cannot be nested. """
	return length_of_condition(rule[0]) + length_of_condition(rule[1]) + 1

def length_of_condition(cond):
	""" Each literal is 1 unit """
	return len(cond)

def tournament_selection(pop, bouts):
	""" Select a group, fight, choose 1 winner """
	selected = []
	# print "bouts = ", bouts
	for i in range(bouts):
		selected.append(choice(pop))
	# print("len = ", len(pop))
	selected.sort(key = lambda x: x['fitness'])
	return selected[0]

# TO-DO:  prune needs to respect boolean structure
def prune(node, maxDepth, terms, depth = 0):
	""" old code """
	depth += 1
	if not isinstance(node, list):
		return node
	if is_arith(node):
		a1 = prune2(node[1], maxDepth, terms, depth)
		a2 = prune2(node[2], maxDepth, terms, depth)
		return [node[0], a1, a2]
	else:
		a1 = prune(node[1], maxDepth, terms, depth)
		a2 = prune(node[2], maxDepth, terms, depth)
		return [node[0], a1, a2]

def prune2(node, maxDepth, terms, depth = 0):
	""" old code """
	if depth >= maxDepth - 1:
		t = terms[randint(0, len(terms) - 1)]
		if t == 'R':
			return uniform(-5.0, +5.0)
		else:
			return t
	depth += 1
	if not isinstance(node, list):
		return node
	a1 = prune2(node[1], maxDepth, terms, depth)
	a2 = prune2(node[2], maxDepth, terms, depth)
	return [node[0], a1, a2]

def crossover(parent1, parent2):
	""" Find 2 crossover points, cross.
	We exploit the fact that rules have a somewhat linear structure,
	even if NCs are allowed to nest.
	This code may potentially work for nested NCs """
	rule1 = parent1['rule']
	rule2 = parent2['rule']
	if length_of_rule(rule1) == 1:
		print("cross: p1 = ", print_rule(rule1), rule1[0], rule1[1], rule1[2])
	if length_of_rule(rule2) == 1:
		print("cross: p2 = ", print_rule(rule2), rule2[0], rule2[1], rule2[2])
	pt1 = randint(1, length_of_rule(rule1) - 1)
	pt2 = randint(1, length_of_rule(rule2) - 1)
	# print("pt1 = %d, pt2 = %d" % (pt1, pt2))

	# copy head and tail
	index = 0
	head1 = []
	tail1 = []
	crossed = False
	for sublist in rule1:
		remainder = pt1 - index
		if not crossed:
			if remainder >= len(sublist):
				index += len(sublist)
				head1.append(sublist)
				tail1.append([])
			else:
				index += remainder
				head1.append(sublist[:remainder])
				tail1.append(sublist[remainder:])
			if index == pt1:
				crossed = True
		else:	# crossed (at this point, index == pt1)
			head1.append([])
			tail1.append(sublist)

	index = 0
	head2 = []
	tail2 = []
	crossed = False
	for sublist in rule2:
		remainder = pt2 - index
		if not crossed:
			if remainder >= len(sublist):
				index += len(sublist)
				head2.append(sublist)
				tail2.append([])
			else:
				index += remainder
				head2.append(sublist[:remainder])
				tail2.append(sublist[remainder:])
			if index == pt2:
				crossed = True
		else:	# crossed (at this point, index == pt2)
			head2.append([])
			tail2.append(sublist)

	# print(head1, " +++ ", tail1)
	# print(head2, " +++ ", tail2)

	# Construct children
	child1 = list(map(lambda x, y: x + y, head1, tail2))
	child2 = list(map(lambda x, y: x + y, head2, tail1))
	# child1 = prune(child1)
	# child2 = prune(child2)
	# print(print_rule(child1))
	# print(print_rule(child2))
	# print("^^^^^^^^^^^^^^^^^^^^^")
	if length_of_rule(child1) == 1:
		print("cross: p1 = ", print_rule(child1), child1[0], child1[1], child1[2])
	if length_of_rule(child2) == 1:
		print("cross: p2 = ", print_rule(child2), child2[0], child2[1], child2[2])
	return	{'rule':child1, 'fitness':0.0, 'p_node':None}, \
			{'rule':child2, 'fitness':0.0, 'p_node':None}

def get_largest_var_index(rule):
	max_index = 0
	for lit in rule[0]:
		i = get_largest_var_index2(lit)
		if i > max_index:
			max_index = i
	for lit in rule[1]:
		i = get_largest_var_index2(lit)
		if i > max_index:
			max_index = i
	i = get_largest_var_index2(rule[2])
	if i > max_index:
		max_index = i
	return max_index

def get_largest_var_index2(literal):
	max_index = 0
	if literal[0] == '~':
		for i in [1,2,3]:
			if type(literal[i]) == str and literal[i][0] == '$':
				index = int(literal[i][1:])
				if index > max_index:
					max_index = index
	else:
		for i in [0,1,2]:
			if type(literal[i]) == str and literal[i][0] == '$':
				index = int(literal[i][1:])
				if index > max_index:
					max_index = index
	return max_index

def mutate(parent):
	""" YKY's own idea: insert / delete random literal;
	This can happen in any part of the rule """
	rule = parent['rule']
	# print("+++ ", print_rule(rule), end='')
	# 'point' designates the place where mutation occurs, can be at position 0
	point = randint(0, length_of_rule(rule) - 1)
	choice = randint(1, 3)		# delete / insert / replace
	# print(' (%s %d)' % ('delete' if choice == 1 else 'insert' if choice == 2 \
		# else 'replace', point))

	# New problem: generate_random_literal uses variables that is not indexed from
	# the formula to be mutated.  The variable index should come from the range of the
	# original variables + 1.

	index = 0
	child = []
	done = False
	for i, sublist in enumerate(rule):
		global var_index
		var_index = get_largest_var_index(rule)
		# print('sublist %d = %s' % (i, sublist))
		if not done:
			remainder = point - index
			if remainder >= len(sublist):
				# if remainder = 0 then point = index and list must also be empty
				# so we can skip to next sublist and continue the operation
				index += len(sublist)
				child.append(sublist)
			else:	# designated point is inside sublist, and remainder > 0
				index += remainder
				# print('remainder=', remainder)
				# index =? point
				done = True
				if choice == 1 and i < 2:			# delete (must not be conclusion)
					# print('delete')
					child.append(sublist[:remainder] + sublist[remainder + 1:])
					# NOTE that the list[i:] notation allows index to be > list length
					index -= 1
				elif choice == 2 and i < 2:		# insert (cannot be conclusion)
					# print('insert')
					child.append(sublist[:remainder] + [generate_random_literal()] \
						+ sublist[remainder:])
					index += 1
				elif i < 2:								# replace
					# print('replace')
					child.append(sublist[:remainder] + [generate_random_literal()] \
						+ sublist[remainder + 1:])
				else:									# mutate conclusion
					child.append(generate_random_atom())
		else:	# mutated (at this point, index == point)
			# just copy whatever is left
			child.append(sublist)

	# child = prune(child)
	# print('>> ', child)
	# print('●', print_rule(child))
	return {'rule':child, 'fitness':0.0, 'p_node':None}

# Add a logic formula to Rete
def add_rule_to_Rete(rete_net, rule):
	""" Format of a rule:
		[ => pre-condition post-condition ]
		Format of a pre-condition:
		[ [ literals ... ] [ NC-atoms ... ] ]
	"""
	# print("rule[1] = ", rule[1])
	# print("rule[2] = ", rule[2])
	# print("rule[3] = ", rule[3])
	conjunction = []
	for literal in rule[0]:
		conjunction.append(get_Rete_literal(literal))
	conjunction2 = []
	for literal in rule[1]:
		conjunction2.append(get_Rete_literal(literal))
	if conjunction2 != []:
		p = rete_net.add_production(Rule(*conjunction, Ncc(*conjunction2)))
	elif conjunction != []:
		p = rete_net.add_production(Rule(*conjunction))
	else:
		return None
	p.postcondition = get_Rete_literal(rule[2])
	return p

def get_Rete_nc(nc):
	""" This is the recursive (nested) algorithm, not used anymore """
	conjunction = []
	for literal_or_NC in nc[1:]:
		if literal_or_NC[0] == 'NC':
			return conjunction.append(get_Rete_nc(literal_or_NC))
		else:
			conjunction.append(get_Rete_literal(literal_or_NC))
	return Ncc(*conjunction)

def get_Rete_literal(literal):
	if literal[0] == '~':
		if len(literal) == 4:
			return Neg(literal[1], str(literal[2]), str(literal[3]))
		else:
			return Neg(literal[1], str(literal[2]))
	else:
		if len(literal) == 3:
			return Has(literal[0], str(literal[1]), str(literal[2]))
		else:
			return Has(literal[0], str(literal[1]))

def save_Rete_graph(net, fname):
	f = open(fname + '.dot', 'w+')
	f.write(net.dump())
	f.close()
	# os.system("dot -Tpng %s.dot -o%s.png" % (fname, fname))
	print("Rete graph saved as %s.png\n" % fname)

def hasWinner():
	global board

	for player in ['X', 'O']:
		tile = player

		# check horizontal
		for i in [0, 1, 2]:
			if board[i][0] == tile and board[i][1] == tile and board[i][2] == tile:
				return player

		# check vertical
		for j in [0, 1, 2]:
			if board[0][j] == tile and board[1][j] == tile and board[2][j] == tile:
				return player

		# check diagonal
		if board[0][0] == tile and board[1][1] == tile and board[2][2] == tile:
			return player

		# check backward diagonal
		if board[0][2] == tile and board[1][1] == tile and board[2][0] == tile:
			return player

	# ' ' is for game still open
	for i in [0, 1, 2]:
		for j in [0, 1, 2]:
			if board[i][j] == ' ':
				return ' '

	# '-' is for draw match
	return '-'

def opponentPlay():
	global board

	playable2 = []
	for i in [0, 1, 2]:
		for j in [0, 1, 2]:
			if board[i][j] == ' ':
				playable2.append((i,j))
	return choice(playable2)

def printBoard():
	global board
	for i in [0, 1, 2]:
		print(' [', end='')
		for j in [0, 1, 2]:
			print(board[i][j], end='')
		print(']')

def playGames(population):
	global board, moves, rete_net
	win = draw = stall = lose = 0

	# Add rules to Rete
	rete_net = Network()
	# print("\x1b[43m-----------------------------------------------\x1b[0m")
	for candidate in population:
		p = add_rule_to_Rete(rete_net, candidate['rule'])
		if p:
			# print('●', print_rule(candidate['rule']), end='\n')
			# print(' (%d)' % length_of_rule(candidate['rule']))
			candidate['p_node'] = p
	# save_Rete_graph(rete_net, 'rete_0')

	for n in range(1000):		# play game N times
		print("\r\t\tGame ", n, end='\r')
		# Initialize board
		for i in [0, 1, 2]:
			for j in [0, 1, 2]:
				if board[i][j] != ' ':
					rete_net.remove_wme(WME(board[i][i], str(i), str(j)))
				rete_net.add_wme(WME(' ', str(i), str(j)))
				board[i][j] = ' '

		CurrentPlayer = 'X'					# In the future, may play against self
		moves = []							# for recording played moves
		for move in range(9):				# Repeat playing moves in single game
			# print("    move", move, end='; ')

			if CurrentPlayer == 'X':
				if play_1_move(population, CurrentPlayer):	# Stalled?
					stall += 1
					break						# game-over, next game

			else:			# Player = 'O'
				i,j = opponentPlay()
				board[i][j] = 'O'
				# print("Opponent move: O(%d,%d)" % (i,j))
				# remove old WME
				rete_net.remove_wme(WME(' ', str(i), str(j)))
				# add new WME
				rete_net.add_wme(WME('O', str(i), str(j)))

			# printBoard()				# this is text mode
			# new_GUI.draw_board()		# graphics mode
			# check if win / lose, assign rewards accordingly
			winner = hasWinner()
			if winner == ' ':
				# let the same set of rules play again
				# let opponent play (opponent = self? this may be implemented later)
				CurrentPlayer = 'O' if CurrentPlayer == 'X' else 'X'
			elif winner == '-':
				# increase the scores of all played moves by 3.0
				for candidate in moves:
					candidate['fitness'] += 3.0
				# print("Draw")
				draw += 1
				break			# next game
			elif winner == 'X':
				# increase the scores of all played moves by 10.0
				for candidate in moves:
					candidate['fitness'] += 10.0
				# print("X wins")
				win += 1
				break			# next game
			elif winner == 'O':
				# decrease the scores of all played moves by 8.0
				for candidate in moves:
					candidate['fitness'] -= 8.0
				# print("O wins")
				lose += 1
				break			# next game
	return win, draw, stall, lose

# ALGORITHM:
# 1) REPEAT: apply rules and collect all results
#		update RETE Working Memory
# 2) Select 1 playable result and play it
# Each rule candidate could have multiple instances
# should we add all P_i's to WM?
# 1) every rule may infer a (non-action) proposition P_i
# 2) every rule has its instantiations that should be assumed
#	-- why are instantiations different? because of substitution into rules.
#	-- but are these subsitutions mutually compatible or exclusive?
#	-- seems compatible, eg: all men are mortal => Socrates and Plato are mortal.
# 3) can we simply accept all such propositions in the same Working-Memory state?
#	-- in other words, if head[0] == P then we always add postcond to WM.
# 4) TO-DO:  we can iterate the "INFERENCE" step multiple times, before making
#		an action.
# NOTE: When a variable is unbound, we simply assign random values to it;
#		This seems reasonable, as we regard unbound predicates as STOCHASTIC.
def play_1_move(population, CurrentPlayer):
	global moves
	# **** Part A: pure INFERENCE step(s) ****
	i_infer = 0
	max_infer = 3
	while i_infer < max_infer:
		i_infer += 1
		for candidate in population:
			p0 = candidate['p_node']		# a p-node seems to be the "results" node
			if not p0:
				continue
			if p0.items:
				DEBUG(len(p0.items), "instances")
			for item in p0.items:
				# **** Previously I assumed postcond = X = action
				# **** But now postcond can be a predicate P_i
				head = p0.postcondition.F1
				DEBUG("the head=", head)
				if head[0] == 'P':

					DEBUG("production rule =", print_rule(candidate['rule']))
					DEBUG("chosen item =", item)
					DEBUG("postcond =", p0.postcondition)
					# Question: are all instances the same?
					# apply binding to rule's action (ie, post-condition)
					if is_var(p0.postcondition.F2):
						p0.postcondition.F2 = item.get_binding(p0.postcondition.F2)
						if p0.postcondition.F2 is None:
							p0.postcondition.F2 = str(randint(0,2))
					if is_var(p0.postcondition.F3):
						p0.postcondition.F3 = item.get_binding(p0.postcondition.F3)
						if p0.postcondition.F3 is None:
							p0.postcondition.F3 = str(randint(0,2))
					DEBUG("postcond =", p0.postcondition, "<-- after binding")

					# **** Add to Working Memory:
					rete_net.add_wme(WME(head, p0.postcondition.F2, p0.postcondition.F3))
					# input("added proposition to WM...")		# pause
					continue			# continue to next instantiation...

	# **** Part B: action step ****
	# 1) collect all playable rules
	playable = []
	for candidate in population:
		p0 = candidate['p_node']		# a p-node seems to be the "results" node
		if not p0:
			continue
		if p0.items:
			DEBUG(len(p0.items), "instances")
		for item in p0.items:

			head = p0.postcondition.F1
			if head[0] != 'P':
				# **** Here, the post-cond must be an ACTION ****

				DEBUG("production rule =", print_rule(candidate['rule']))
				DEBUG("chosen item =", item)
				DEBUG("postcond =", p0.postcondition)
				# item = choice(p0.items)		# choose an instantiation randomly
				# Question: are all instances the same?
				# apply binding to rule's action (ie, post-condition)
				if is_var(p0.postcondition.F2):
					p0.postcondition.F2 = item.get_binding(p0.postcondition.F2)
					if p0.postcondition.F2 is None:
						p0.postcondition.F2 = str(randint(0,2))
				if is_var(p0.postcondition.F3):
					p0.postcondition.F3 = item.get_binding(p0.postcondition.F3)
					if p0.postcondition.F3 is None:
						p0.postcondition.F3 = str(randint(0,2))
				DEBUG("postcond =", p0.postcondition, "<-- after binding")

				# Check if the square is empty
				x = int(p0.postcondition.F2)
				y = int(p0.postcondition.F3)
				if board[x][y] == ' ':
					playable.append(candidate)		# append to 'playable' list
					candidate['fitness'] += 1.0
				else:
					candidate['fitness'] -= 1.0

	# **** Randomly choose 1 playable move and play it ****
	# print(len(playable), "playable rules ", end='')
	uniques = []
	for candidate in playable:
		if not uniques:
			uniques.append(candidate)
			continue
		exists = False
		for u in uniques:
			if candidate['p_node'].postcondition == u['p_node'].postcondition:
				exists = True
		if not exists:
			uniques.append(candidate)
	# print("; unique moves =\x1b[31;1m", len(uniques), end='\x1b[0m\n')

	if not uniques:
		# print("No rules playable")
		return True		# next game

	# 2) Choose a playable rule randomly
	candidate = choice(uniques)
	p0 = candidate['p_node']

	x = int(p0.postcondition.F2)
	y = int(p0.postcondition.F3)
	board[x][y] = CurrentPlayer
	# print("    played move: X(%d,%d)" % (x,y))
	# remove old WME
	rete_net.remove_wme(WME(' ', p0.postcondition.F2, p0.postcondition.F3))
	# add new WME
	rete_net.add_wme(WME(CurrentPlayer, p0.postcondition.F2, p0.postcondition.F3))
	# **** record move: record the rule that is fired
	moves.append(candidate)
	return False

def Evolve():
	global maxGens, popSize, maxDepth, bouts, p_repro, crossRate, mutationRate, childrenSize
	population = []

	print("Generating population...")
	# for c in cache:
		# population.append(c)
	# print("Added from cache:", len(cache))

	for i in range(popSize - len(cache)):
		# print('...', i, end='\r')
		# sys.stdout.flush()
		# print "\tGenerating formula..."
		rule = generate_random_formula()
		population.append({'rule':rule, 'fitness':0.0, 'p_node':None})

	print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

	# CO-OPERATIVE EVOLUTIONARY ALGORITHM
	# ===================================
	# Randomly generate a set of rules
	# Repeat until success:
	#		Play game, evaluate candidates
	#		Select survivors
	#		Select parents via tournament; recombine, mutate

	print('Win\tLose\tDraw\tStall')
	average_fitness = 0.0
	for gen in range(maxGens):
		# if gen > 0:
			# break

		# print("Evaluating rules...")
		for candidate in population:
			candidate['fitness'] = 0.0
		# fitness values are returned in {rule.fitness}:
		win, draw, stall, lose = playGames(population)
		print('                                            ', end='\r')
		print('W %d\tL %d\tD %d\tS %d\t' % (win, lose, draw, stall), end='')
		# population = children
		population.sort(key = lambda x : x['fitness'], reverse = False)
		# plot_population(screen, population)
		fitness = 0.0
		for candidate in population:
			fitness += candidate['fitness']
		last_fitness = average_fitness
		average_fitness = fitness / popSize
		diff = average_fitness - last_fitness
		print('avg fitness %.1f' % average_fitness, end='')
		print(' %s%.1f\x1b[0m' % ('\x1b[32m▲' if diff > 0 else '\x1b[31m▼', abs(diff)))

		children = []
		# print("\nGenerating children...")
		while len(children) < childrenSize:
			# select a group, fight and find 1 winner:
			p1 = tournament_selection(population, bouts)
			operation = uniform(0.0, 1.0)
			# if operation < p_repro:			# from earlier version,
				# c1 = copy_tree(p1)			# simple reproduction / replication
			if operation < mutationRate:
				c1 = mutate(p1)
				# print "***** mutated = ", print_tree(c1)
			else:	# otherwise crossover
				p2 = tournament_selection(population, bouts)
				c1, c2 = crossover(p1, p2)
				# print "***** crossed = ", print_tree(c1)
				children.append(c2)
			if len(children) < childrenSize:
				children.append(c1)

		# Add children to population
		j = 0
		for i, rule in reversed(list(enumerate(population))):
			if uniform(0.0, 1.0) <= dropRate:
				population[i] = children[j]
				j += 1
				if j == childrenSize:
					break

		# quitting = False
		# pausing = False
		# for event in pygame.event.get():
			# if event.type == pygame.QUIT:
				# quitting = True
			# elif event.type == pygame.KEYDOWN:
				# pausing = True
			# elif event.type == pygame.KEYUP:
				# pausing = False
		# while pausing:
			# for event in pygame.event.get():
				# if event.type == pygame.QUIT:
					# quitting = True
					# pausing = False
				# elif event.type == pygame.KEYUP:
					# pausing = False

		print("Gen[", gen, "]", end=' ')
		# os.system('aplay -q /home/yky/beep.wav')
		os.system("beep -f 2000 -l 50")

		# if overall fitness == optimal:
		#	break
	# return best

if not "new_GUI" in sys.modules:
	Evolve()

# print("\x1b[36m**** This program works till here....\n\x1b[0m")
# os.system("beep -f 2000 -l 50")
# exit(0)

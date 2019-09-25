# -*- coding: utf8 -*-

# TO-DO:

#	* Rete: clear all memories (retain rules)
#	* Do all bindings lead to same production?
#	* mysterious bug still exists: negative_node right_activated;
#		jr.wme.negative_join_result.remove(jr);	jr not in list
#	* After bug fix, NC's may be nested again, or contain Neg conditions.
#	* Invention of new predicates

# Done:
#	* Removed empty NCs
#	* Fixed bug: delete_token_and_descendents ---> delete_descendents_of_tokens

# **** NOTE:  In this new version we use rules that are compatible with Rete,
# that consists only of conjunctions, negations, and negated conjunctions (NC).
# NCs can be nested to any level.  So the general form of a rule is: a conjunction,
# followed by some negated atoms, followed by a possibly nested NC.

# * Objective function:
#		The KB would be run many times
#		For each run, a positive/negative reward would be obtained
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

# STANDARD EVOLUTIONARY ALGORITHM
# ===============================
# Initialize population
# Repeat until success:
#    Select parents
#    Recombine, mutate
#    Evaluate
#    Select survivors

# STRUCTURE OF THE GENOME
# =======================
# * The genome is a set of rules, which evolve co-operatively.
# * Each candidate = just one rule.
# * Each rule = [ head => tail ]
# * Heads and tails are composed from "var" symbols and "const" symbols.
# * Rules have variable length, OK?
#   -- as long as their lengths can decrease during learning

# SCORING OF RULES
# ================
# * For each generation, rules should be allowed to fire plentifully
# * Some facts lead to rewards
# * The chains of inference can be inspected in Clara Rules

# STRUCTURE OF A RULE
# ===================
#   pre-condition => post-condition
#	pre-condition = list of positive/negative atoms, followed by an NC part
#	NC = NC[ list of atoms... ]
#	post-condition = just one positive atom
#	literal = atomic proposition optionally preceded by a negation sign

import random
import operator
import sys
import math
import os
# import pygame	# for pause key in Evolve()

from rete.common import Has, Rule, WME, Neg, Ncc, is_var, DEBUG
from rete.network import Network
from rete.network import PNode

# ============ Global variables ==============

# Logic parameters:
numPreds = 10
numVars = 4
numConsts = 30
const2varRatio = 0.6      # 0.6 means 60% consts
const2varFlipRate = 0.5   # probability of "var <--> const"

# Evolution parameters:
maxGens = 100
popSize = 100
childrenSize = int(popSize * 0.6)
dropRate = 0.1			# when children size proportion = 40%, 0.1 seems a good choice
crossRate = 0.9
mutationRate = 1.0 / 10

maxDepth = 7
bouts = 5
p_repro = 0.08

cache = []		# for storing previously-learned best formulas

var_index = -1	# keeping track of logic variables

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
	for literal in rule[1]:
		s += print_literal(literal) + ' ⋀ '
	s += print_nc(rule[2])
	return s + " \x1b[31;1m=> " + print_literal(rule[3]) + "\x1b[0m"

def print_nc(nc):
	if len(nc) == 0:
		return "\x08\x08\x08"
	s = ''
	for atom in nc:
		s += print_literal(atom) + ' '
	return '\x1b[32m~[ ' + s + ']\x1b[0m'

def print_literal(literal):
	if literal[0] == '~':
		return '~' + literal[1] + '(' + \
			str(literal[2]) + ',' + str(literal[3]) + ')'
	else:
		# print("litertal[0] = ", literal[0])
		return literal[0] + '(' + \
			str(literal[1]) + ',' + str(literal[2]) + ')'

def read_tree(str):			# assume str is in prefix notation with ()'s
	""" old code """
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
	return ['=>', *pre_condition, post_condition]

# Generate a random (pre-)condition in 2 stages:
# 1) a number of atoms (possibly negated)
# 2) an NC (= negated conjunction, possibly nested)
def generate_random_condition():
	return [ \
		generate_random_conjunction(),
		generate_random_NC() ]

def generate_random_NC():
	""" In the current version of Rete, NC's cannot be nested,
	nor can they contain Neg (negative) conditions. """
	nc = []
	while random.uniform(0.0, 1.0) < 0.7:
		nc.append(generate_random_atom())
	# if random.uniform(0.0, 1.0) < 0.3:
		# nc.append(generate_random_NC())
	return nc

def generate_random_conjunction():
	conjunction = []
	while random.uniform(0.0, 1.0) < 0.7:
		if random.uniform(0.0, 1.0) < 0.3:
			conjunction.append(['~'] + generate_random_atom())
		else:
			conjunction.append(generate_random_atom())
	return conjunction

def generate_random_atom():
	""" An atomic logic formula such as X(a,b) """
	r = random.uniform(0.0, 1.0)
	if r < 0.33333:
		predicate = 'X'
	elif r < 0.66666:
		predicate = 'O'
	else:
		predicate = ' '
	arg1 = generate_random_var_or_const()
	arg2 = generate_random_var_or_const()
	return [predicate, arg1, arg2]

def generate_random_post_condition():
	""" An atom without new variable creation """
	predicate = 'X' # if (random.uniform(0.0, 1.0) > 0.5) else 'O'
	arg1 = generate_random_var_or_const(False)
	arg2 = generate_random_var_or_const(False)
	return [predicate, arg1, arg2]

def generate_random_var_or_const(create = True):
	""" Result could be old var, new var, or const """
	global var_index
	choice = random.uniform(0.0, 1.0)
	if create and choice > 0.9:				# new var
		var_index += 1
		return '$' + str(var_index)
	elif choice > 0.5 and var_index >= 0:	# old var
		return '$' + str(random.randint(0, var_index))
	else:									# constant ∈ {0, 1, 2}
		return random.randint(0, 2)

def generate_random_inequality(maxDepth, funcs, terms):
	""" Old code, not used yet """
	# determine maxDepth = ?
	arg1 = generate_random_formula(maxDepth, funcs, terms)
	arg2 = generate_random_formula(maxDepth, funcs, terms)
	op = operator.gt if (random.uniform(0.0, 1.0) > 0.5) else operator.lt
	return [op, arg1, arg2]

def tournament_selection(pop, bouts):
	""" Select a group, fight, choose 1 winner """
	selected = []
	# print "bouts = ", bouts
	for i in range(bouts):
		selected.append(random.choice(pop))
	# print("len = ", len(pop))
	selected.sort(key = lambda x: x['fitness'])
	return selected[0]

def replace_node(node, replacement, node_num, cur_node = 0):
	if cur_node == node_num:
		return [replacement, (cur_node + 1)]
	cur_node += 1
	if not isinstance(node, list):
		return [node, cur_node]
	a1, cur_node = replace_node(node[1], replacement, node_num, cur_node)
	a2, cur_node = replace_node(node[2], replacement, node_num, cur_node)
	return [[node[0], a1, a2], cur_node]

def copy_tree(node):
	# print node
	if not isinstance(node, list):
		return node
	return [node[0], copy_tree(node[1]), copy_tree(node[2])]

def get_node(node, node_num, current_node = 0):
	if current_node == node_num:
		return node, (current_node + 1)
	current_node += 1
	if not isinstance(node, list):		# is a var or number
		return [], current_node
	a1, current_node = get_node(node[1], node_num, current_node)
	if a1:		# a1 != []
		return a1, current_node
	a2, current_node = get_node(node[2], node_num, current_node)
	if a2:		# a2 != []
		return a2, current_node
	return [], current_node		# ?? will we ever get here?

# TO-DO:  prune needs to respect boolean structure
def prune(node, maxDepth, terms, depth = 0):
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
	if depth >= maxDepth - 1:
		t = terms[random.randint(0, len(terms) - 1)]
		if t == 'R':
			return random.uniform(-5.0, +5.0)
		else:
			return t
	depth += 1
	if not isinstance(node, list):
		return node
	a1 = prune2(node[1], maxDepth, terms, depth)
	a2 = prune2(node[2], maxDepth, terms, depth)
	return [node[0], a1, a2]

def crossover(parent1, parent2):
	pt1 = random.randint(1, count_nodes(parent1) - 1)
	pt2 = random.randint(1, count_nodes(parent2) - 1)
	# print "pt 1 & 2 = ", pt1, pt2
	# c1, c2 are dummy variables
	tree1, c1 = get_node(parent1, pt1)
	tree2, c2 = get_node(parent2, pt2)
	# print "tree 1 & 2 = ", tree1, tree2
	child1, c1 = replace_node(parent1, copy_tree(tree2), pt1)
	child1 = prune(child1, maxDepth, terms)
	child2, c2 = replace_node(parent2, copy_tree(tree1), pt2)
	child2 = prune(child2, maxDepth, terms)
	return [child1, child2]

def mutate(parent):
	point = random.randint(0, count_nodes(parent) - 1)
	random_tree = generate_random_formula(maxDepth / 2, funcs, terms)
	child, count = replace_node(parent, random_tree, point)
	child = prune(child, maxDepth, terms)
	return child

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
	for literal in rule[1]:
		conjunction.append(get_Rete_literal(literal))
	conjunction2 = []
	for literal in rule[2]:
		conjunction2.append(get_Rete_literal(literal))
	if conjunction2 != []:
		p = rete_net.add_production(Rule(*conjunction, Ncc(*conjunction2)))
	elif conjunction != []:
		p = rete_net.add_production(Rule(*conjunction))
	else:
		return None
	p.postcondition = get_Rete_literal(rule[3])
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

# For Tic Tac Toe:
board = [ [' ']*3 for i in range(3)]

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
	return random.choice(playable2)

def printBoard():
	global board
	for i in [0, 1, 2]:
		print(' [', end='')
		for j in [0, 1, 2]:
			print(board[i][j], end='')
		print(']')

# TO-DO: actions could be intermediate predicates
def playGames(population):
	global board
	moves = []				# for recording played moves

	# Add rules to Rete
	rete_net = Network()
	for candidate in population:
		p = add_rule_to_Rete(rete_net, candidate['rule'])
		if p:
			print('●', print_rule(candidate['rule']))
			candidate['p_node'] = p
	# save_Rete_graph(rete_net, 'rete-0')

	for n in range(1):		# play game N times
		print("**** Game ", n)
		# Initialize board
		for i in [0, 1, 2]:
			for j in [0, 1, 2]:
				rete_net.add_wme(WME(' ', str(i), str(j)))
				board[i][j] = ' '

		CurrentPlayer = 'X'					# In the future, may play against self
		for move in range(9):				# Repeat playing moves in single game
			print("    move", move, end='; ')

			if CurrentPlayer == 'X':
				# collect all playable rules
				playable = []
				for candidate in population:
					p0 = candidate['p_node']
					if not p0:
						continue
					if p0.items:
						DEBUG(len(p0.items), " instances")
					for item in p0.items:
						# item = random.choice(p0.items)		# choose an instantiation randomly
						# Question: are all instances the same?
						# apply binding to rule's action (ie, post-condition)
						if is_var(p0.postcondition.F2):
							p0.postcondition.F2 = item.get_binding(p0.postcondition.F2)
							if p0.postcondition.F2 is None:
								p0.postcondition.F2 = str(random.randint(0,2))
						if is_var(p0.postcondition.F3):
							p0.postcondition.F3 = item.get_binding(p0.postcondition.F3)
							if p0.postcondition.F3 is None:
								p0.postcondition.F3 = str(random.randint(0,2))
						DEBUG("production rule = ", print_rule(candidate['rule']))
						DEBUG("chosen item = ", item)
						DEBUG("postcond = ", p0.postcondition)

						# Check if the square is empty
						x = int(p0.postcondition.F2)
						y = int(p0.postcondition.F3)
						if board[x][y] == ' ':
							playable.append(candidate)
							candidate['fitness'] += 1.0
						else:
							candidate['fitness'] -= 1.0

				print(len(playable), "playable rules found ", end='')
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
				print("\x1b[31;1munique moves =", len(uniques), end='\x1b[0m\n')

				if not uniques:
					print("No rules playable")
					break		# next game
				# Choose a playable rule randomly
				candidate = random.choice(uniques)
				p0 = candidate['p_node']

				x = int(p0.postcondition.F2)
				y = int(p0.postcondition.F3)
				board[x][y] = CurrentPlayer
				print("    played move: X(%d,%d)" % (x,y))
				# remove old WME
				rete_net.remove_wme(WME(' ', p0.postcondition.F2, p0.postcondition.F3))
				# add new WME
				rete_net.add_wme(WME(CurrentPlayer, p0.postcondition.F2, p0.postcondition.F3))
				# **** record move: record the rule that is fired
				moves.append(candidate)
				
			else:			# Player = 'O'
				i,j = opponentPlay()
				board[i][j] = 'O'
				print("Opponent move: O(%d,%d)" % (i,j))
				# remove old WME
				rete_net.remove_wme(WME(' ', str(i), str(j)))
				# add new WME
				rete_net.add_wme(WME('O', str(i), str(j)))

			printBoard()
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
				print("Draw")
				break			# next game
			elif winner == 'X':
				# increase the scores of all played moves by 10.0
				for candidate in moves:
					candidate['fitness'] += 10.0
				print("X wins")
				break			# next game
			elif winner == 'O':
				# decrease the scores of all played moves by 8.0
				for candidate in moves:
					candidate['fitness'] -= 8.0
				print("O wins")
				break			# next game

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

	for gen in range(maxGens):

		print("Evaluating rules...")
		playGames(population)			# fitness values are returned in {rule.fitness}
		# population = children
		population.sort(key = lambda x : x['fitness'], reverse = False)
		# plot_population(screen, population)
		fitness = 0.0
		for candidate in population:
			fitness += candidate['fitness']
		print("Average fitness = ", fitness / popSize)

		children = []
		print("\nGenerating children...")
		while len(children) < childrenSize:
			# select a group, fight and find 1 winner:
			p1 = tournament_selection(population, bouts)
			operation = random.uniform(0.0, 1.0)
			# if operation < p_repro:
				# c1 = copy_tree(p1)
			if operation < crossRate:
				p2 = tournament_selection(population, bouts)
				c1,c2 = crossover(p1, p2)
				# print "***** crossed = ", print_tree(c1)
				children.append(c2)
			elif operation < crossRate + mutationRate:
				c1 = mutate(p1)
				# print "***** mutated = ", print_tree(c1)
			if len(children) < childrenSize:
				children.append(c1)

		# Add children to population
		j = 0
		for i, rule in reversed(list(enumerate(population))):
			if random.uniform(0.0, 1.0) <= dropRate:
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

		print("[", gen, "]", end=' ')

		# if overall fitness == optimal:
		#	break
	# return best

Evolve()

print("\x1b[36m**** This program works till here....\n\x1b[0m")
os.system("beep -f 2000 -l 50")
exit(0)

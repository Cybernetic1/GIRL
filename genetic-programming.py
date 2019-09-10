# -*- coding: utf8 -*-

# TO-DO:

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
#    formula => literal
# =  pair( tree as list , literal as list )

import random
import operator
import sys
import math
import os
import pygame	# for pause key in Evolve()

from rete.common import Has, Rule, WME
from rete.network import Network

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
crossRate = 0.9
mutationRate = 1.0 / 10

maxDepth = 7
bouts = 5
p_repro = 0.08

cache = []		# for storing previously-learned best formulas

var_index = 0	# keeping track of logic variables

op_map = {
	operator.and_ : '⋀',
	operator.or_ : '⋁',
	operator.not_: '~',

	# These may not be used in the program:
	operator.add : '+',
	operator.sub : '-',
	operator.mul : '*',
	operator.truediv : '÷',
	operator.gt : '>',
	operator.lt : '<',
	}

def export_tree_as_graph(node, fname):
	if fname == "stdout":
		f = sys.stdout
	else:
		f = open(fname + '.dot', 'w')
	f.write("digraph {\n")
	# f.write("fontname=\"times-bold\";")
	print_tree_as_graph(f, node)
	f.write("}\n")
	if fname != "stdout":
		f.close()
		os.system("dot -Tpng %s.dot -o%s.png" % (fname, fname))

def print_tree_as_graph(f, node, index = 0):
	if not isinstance(node, list):
		if isinstance(node, int):
			f.write("node" + str(index) + "[label=\"" + str(node) + "\",style=\"filled\",fillcolor=\"yellow\"];\n")
		else:
			f.write("node" + str(index) + "[label=\"" + str(node) + "\"];\n")
		return 1			# This means # of tree nodes increment by 1
	op = node[0]
	if node[0] in op_map:
		op = op_map[node[0]]
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

def print_tree(node):
	if not isinstance(node, list):
		if isinstance(node, int):
			return str(node)		# consts
		else:
			return node				# vars
	if node[0] in op_map:
		op = op_map[node[0]]
	else:
		op = node[0]
	if len(node) == 3:
		return '(' + op + ' ' + \
			print_tree(node[1]) + ' ' + \
			print_tree(node[2]) + ')'
	else:
		return '(' + op + ' ' + \
			print_tree(node[1]) + ')'

def read_tree(str):			# assume str is in prefix notation with ()'s
	if str[0] == '(':
		op = str[1]
		return [
			op,
			read_tree(str[2:]),
			read_tree(str),
			]
	return None

def eval_tree(node, time):
	""" Old code """
	if not isinstance(node, list):
		if isinstance(node, float):
			return node
		# elif dict[node] is not None:
		elif node == 'label':
			return data[time - 1]
		else:
			return node
	arg1 = eval_tree(node[1], time)
	arg2 = eval_tree(node[2], time)
	if node[0] == operator.truediv and arg2 == 0.0:
		return float('nan')
	return node[0](*[arg1, arg2])

def generate_random_formula(maxDepth):
	pre_condition  = generate_random_condition(maxDepth)
	post_condition = generate_random_atom()
	return ['=>', pre_condition, post_condition]

# Generate a random (pre-)condition in 2 stages:
# 1) ⋀ and ⋁ and ~
# 2) literals
def generate_random_condition(maxDepth, depth = 0):
	if (depth >= maxDepth - 1) or (depth > 1 and random.uniform(0.0, 1.0) < 0.1):
		return generate_random_atom()
	depth += 1
	choice = random.uniform(0.0, 1.0)
	arg1 = generate_random_condition(maxDepth, depth)
	if choice < 0.1:
		return [operator.not_, arg1]
	arg2 = generate_random_condition(maxDepth, depth)
	op = operator.and_ if (choice < 0.55) else operator.or_
	return [op, arg1, arg2]

def generate_random_atom():
	""" An atomic logic formula such as X(a,b) """
	predicate = 'X' if (random.uniform(0.0, 1.0) > 0.5) else 'O'
	arg1 = generate_random_var_or_const()
	arg2 = generate_random_var_or_const()
	return [predicate, arg1, arg2]

def generate_random_var_or_const():
	""" Result could be old var, new var, or const """
	global var_index
	choice = random.uniform(0.0, 1.0)
	if choice < 0.5:					# constant ∈ {0, 1, 2}
		return random.randint(0, 2)
	elif choice < 0.8:					# old var
		return '?' + str(random.randint(0, var_index))
	else:								# new var
		var_index += 1
		return '?' + str(var_index)

def generate_random_inequality(maxDepth, funcs, terms):
	""" Old code, not used yet """
	# determine maxDepth = ?
	arg1 = generate_random_formula(maxDepth, funcs, terms)
	arg2 = generate_random_formula(maxDepth, funcs, terms)
	op = operator.gt if (random.uniform(0.0, 1.0) > 0.5) else operator.lt
	return [op, arg1, arg2]

def count_nodes(node):
	if not isinstance(node, list):
		return 1
	a1 = count_nodes(node[1])
	a2 = count_nodes(node[2])
	return a1 + a2 + 1

# ***** Calculate fitness
def fitness(formula, cond = None, num_trials = 200):
	""" This is old code from Stock Market (to be modified) """
	return 0.0
	sum_err = 0.0
	for i in range(0, num_trials):
		time = random.randint(100, datasize - 10)
		target = eval_tree(formula, time)
		# print "target = ", target
		# print "Condition = ", print_tree(cond)
		# c = eval_tree(cond, time)
		# if not c:
		#	continue
		if math.isnan(target):
			sum_err += 100000.0
			continue
		error = (target - highs[time])
		sum_err += abs(error)
		# print "Condition satisfied"
		# print "profit = ", sum_profit
		# sum_profit += profit
	return sum_err / num_trials

def tournament_selection(pop, bouts):
	selected = []
	# print "bouts = ", bouts
	for i in range(0, bouts):
		selected.append(pop[random.randint(0, len(pop) - 1)])
	return sorted(selected, key = lambda x: x['fitness'])[0]

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

def crossover(parent1, parent2, maxDepth, terms):
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

# crossover for conditions
def crossover_cond(parent1, parent2, maxDepth, terms):
	if random.uniform(0.0, 1.0) > 0.5:
		return crossover_cond1(parent1, parent2, maxDepth, terms)
	else:
		return crossover_cond2(parent1, parent2, maxDepth, terms)

def is_boolean(node):
	if not isinstance(node, list):
		return False
	else:
		op = node[0]
		return (op == operator.and_) or (op == operator.or_)

# randomly cross at boolean layer (choose 2 points in boolean layers)
def crossover_cond1(parent1, parent2, maxDepth, terms):
	# print "Crossing boolean layer"
	while True:
		pt1 = random.randint(1, count_nodes(parent1) - 1)
		tree1, c = get_node(parent1, pt1)
		if is_boolean(tree1):		# test if tree is boolean
			break

	while True:
		pt2 = random.randint(1, count_nodes(parent2) - 1)
		tree2, c = get_node(parent2, pt2)
		if is_boolean(tree2):		# test if tree is boolean
			break

	# print "tree 1 & 2 = ", tree1, tree2
	child1, c = replace_node(parent1, copy_tree(tree2), pt1)
	child1 = prune(child1, maxDepth, terms)
	child2, c = replace_node(parent2, copy_tree(tree1), pt2)
	child2 = prune(child2, maxDepth, terms)
	return [child1, child2]

def is_arith(node):
	if not isinstance(node, list):
		return True
	else:
		op = node[0]
		return \
		(op == operator.add) or \
		(op == operator.sub) or \
		(op == operator.mul) or \
		(op == operator.truediv)

# randomly cross some inequalities? (choose 2 points in inequalities)
def crossover_cond2(parent1, parent2, maxDepth, terms):
	# print "Crossing arithmetic layer"
	while True:
		pt1 = random.randint(1, count_nodes(parent1) - 1)
		tree1, c = get_node(parent1, pt1)
		if is_arith(tree1):		# test if tree is arithmetic
			break

	while True:
		pt2 = random.randint(1, count_nodes(parent2) - 1)
		tree2, c = get_node(parent2, pt2)
		if is_arith(tree2):		# test if tree is arithmetic
			break

	# print "tree 1 & 2 = ", tree1, tree2
	child1, c = replace_node(parent1, copy_tree(tree2), pt1)
	child1 = prune(child1, maxDepth, terms)
	child2, c = replace_node(parent2, copy_tree(tree1), pt2)
	child2 = prune(child2, maxDepth, terms)
	return [child1, child2]

def mutation(parent, maxDepth, funcs, terms):
	point = random.randint(0, count_nodes(parent) - 1)
	random_tree = generate_random_formula(maxDepth / 2, funcs, terms)
	child, count = replace_node(parent, random_tree, point)
	child = prune(child, maxDepth, terms)
	return child

def mutation_cond(parent, maxDepth, funcs, terms):
	point = random.randint(0, count_nodes(parent) - 1)
	# need to determine type of "replacement"
	tree, c = get_node(parent, point)
	if is_arith(tree):
		random_tree = generate_random_formula(maxDepth / 2, funcs, terms)
	elif is_boolean(tree):
		random_tree = generate_random_condition(maxDepth / 2, funcs, terms)
	else:
		random_tree = generate_random_formula(maxDepth / 2, funcs, terms)
		if random.uniform(0.0, 1.0) > 0.5:
			point += 1		# node number of left child
		else:
			point += count_nodes(tree[1])	# node number of right child

	child, count = replace_node(parent, random_tree, point)
	child = prune(child, maxDepth, terms)
	return child

# problem configuration

terms = [
		'O', 'X',		# Moves for the 2 players
		'T', 'F',		# Logical true and false
		'R']			# 'R' invokes random number generator

def add_tree_to_Rete(rete_net, rule):
	c1 = Has('O', '$x', '$x')
	c2 = Has('□', '$y', '$z')
	c3 = Has('>', '$y', '$z')
	rete_net.add_production(Rule(c1, c2, c3))

def Evolve():
	global maxGens, popSize, maxDepth, bouts, p_repro, crossRate, mutationRate
	population = []

	print("Generating population...")
	for c in cache:
		population.append({
			'target' : c['target'],
			'fitness' : fitness(c['target'])
		})
	print("Adding from cache:", len(cache))
	for i in range(0, popSize - len(cache)):
		print(i, ' ', end=' ')
		sys.stdout.flush()
		# print "\tGenerating formula..."
		target = generate_random_formula(maxDepth)
		population.append({
			'target' : target, \
			'fitness' : fitness(target)})
	print()
	pop2 = sorted(population, key = lambda x : x['fitness'], reverse = False)
	best = pop2[0]
	rule = best.get('target')
	print("\nExample logic rule:\n", print_tree(rule))
	export_tree_as_graph(rule, "logic-rule")
	print("Example rule written to file: logic-rule.png")
	# plot_population(screen, pop2)

	print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

	# Feed logic formulas into Rete
	rete_net = Network()
	add_tree_to_Rete(rete_net, rule)

	input("**** This program works till here....")

	for gen in range(0, maxGens):
		children = []
		# print "\nGenerating children..."
		while len(children) < popSize:
			operation = random.uniform(0.0, 1.0)
			p1 = tournament_selection(population, bouts)
			c1 = {}
			if operation < p_repro:
				c1['target'] = copy_tree(p1['target'])
				# c1['cond'] = copy_tree(p1['cond'])
			elif operation < p_repro + crossRate:
				p2 = tournament_selection(population, bouts)
				c2 = {}
				c1['target'],c2['target'] = crossover(p1['target'], p2['target'], maxDepth, terms)
				# c1['cond'],  c2['cond']   = crossover_cond(p1['cond'],   p2['cond'],   maxDepth, terms)
				# print "***** crossed condition = ", print_tree(c1['cond'])
				children.append(c2)
			elif operation < p_repro + crossRate + mutationRate:
				c1['target'] = mutation(p1['target'], maxDepth, arith_ops, terms)
				# c1['cond']   = mutation_cond(p1['cond'],   maxDepth, arith_ops, terms)
				# print "***** mutated condition = ", print_tree(c1['cond'])
			if len(children) < popSize:
				children.append(c1)

		# print "Evaluating children..."
		for c in children:
			# print "c's Condition = ", print_tree(c['cond'])
			c['fitness'] = fitness(c['target'])
		best['fitness'] = fitness(best['target'], None, 500)
		# population = children
		population = sorted(children, key = lambda x : x['fitness'], reverse = False)
		# plot_population(screen, population)
		quitting = False
		pausing = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quitting = True
			elif event.type == pygame.KEYDOWN:
				pausing = True
			elif event.type == pygame.KEYUP:
				pausing = False
		while pausing:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quitting = True
					pausing = False
				elif event.type == pygame.KEYUP:
					pausing = False

		print("[", gen, "]", end=' ')
		print("best in pop =", round(population[0]['fitness'],2), "\tprevious best =", round(best['fitness'],2))
		if population[0]['fitness'] <= best['fitness']:
			best = population[0]
		else:
			population = [best] + population[:-1]
		# if best['fitness'] == 0:
		#	break
	return best

Evolve()

#!/usr/bin/python2.7grep
# -*- coding: utf-8 -*-
import sys
import os

from rete.common import Has, Rule, WME, Neg, Ncc, Token
from rete.network import Network

def init_network():
	net = Network()

	c1 = Has('male', '$a')
	c2 = Has('love', '$a', '$b')
	c3 = Has('female', '$b')
	net.add_production(Rule(Ncc(c1, Ncc(c2, c3))))
	# net.add_production(Rule(c1, Ncc(c2, c3)))
	# net.add_production(Rule(c2, c3))

	# c01 = Has('O', '$x', '$x')
	# c02 = Has('□', '$y', '$z')
	# c03 = Has('>', '$y', '$z')
	# net.add_production(Rule(c01, c02, c03))
	return net

def add_wmes(net):
	wmes = [
		WME('female', 'Mary'),
		WME('female', 'Ann'),
		WME('love', 'John', 'Pete'),
		#WME('love', 'John', 'Ann'),
		WME('love', 'Pete', 'Ann'),
		WME('love', 'Pete', 'Mary'),
		#WME('love', 'Pete', 'Ann'),
		WME('male', 'John'),
		WME('male', 'Pete'),
		# WME('X', '0', '2'),
		# WME('X', '1', '1'),
		# WME('X', '2', '1'),
		# WME('O', '0', '0'),
		# WME('O', '1', '0'),
		# WME('O', '1', '2'),
		# WME('O', '2', '2'),
		# WME('□', '0', '1'),
		# WME('□', '2', '0'),
	]
	for wme in wmes:
		net.add_wme(wme)

print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

rete_net = init_network()

f = open("rete.dot", "w+")
f.write(rete_net.dump())
f.close()
os.system("dot -Tpng rete.dot -orete.png")
print("Rete graph saved as rete.png\n")

add_wmes(rete_net)

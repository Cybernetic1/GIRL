#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from rete.common import Has, Rule, WME, Neg, Ncc
from rete.network import Network

print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

net = Network()

c1 = Has('male', '$a')
c2 = Has('love', '$a', '$b')
c3 = Has('female', '$b')

# net.add_production(Rule(Ncc(c1, Ncc(c2, c3))))
# net.add_production(Rule(Ncc(c2, Ncc(c3))))
# net.add_production(Rule(c1, Ncc(c2)))
# net.add_production(Rule(c1, Ncc(c2, c3)))
# net.add_production(Rule(c2, c3))
print("rule condition: B is female and no man loves her")
p0 = net.add_production(Rule(c3, Ncc(c2, c1)))

wmes = [
	WME('female', 'Mary'),
	WME('female', 'Ann'),
	WME('love', 'John', 'Pete'),		# 基
	WME('love', 'John', 'John'),		# 自恋
	WME('love', 'Pete', 'Mary'),		# 所谓正常
	WME('love', 'Pete', 'John'),		# 互基
	WME('love', 'Mary', 'Ann'),			# Lesbian
	WME('male', 'John'),
	WME('male', 'Pete'),
]
print("\nFacts:")
for wme in wmes:
	net.add_wme(wme)
	print(wme.F1 + '(' + wme.F2, end='')
	if wme.F3:
		print(', ' + wme.F3 + ')')
	else:
		print(')')

print("\n# of results = ", len(p0.items))
print("Results:")
for i in p0.items:
	print(i)

f = open("rete.dot", "w+")
f.write(net.dump())
f.close()
os.system("dot -Tpng rete.dot -orete.png")
print("\nRete graph saved as rete.png\n")

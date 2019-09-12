#!/usr/bin/python2.7grep
# -*- coding: utf-8 -*-
import sys
import os

from rete.common import Has, Rule, WME, Neg, Ncc, Token
from rete.network import Network

net = Network()

c1 = Has('male', '$a')
c2 = Has('love', '$a', '$b')
c3 = Has('female', '$b')
# net.add_production(Rule(Ncc(c1, Ncc(c2, c3))))
# net.add_production(Rule(Ncc(c2, Ncc(c3))))
p0 = net.add_production(Rule(c3, Ncc(c1, c2)))
# net.add_production(Rule(c1, Ncc(c2)))
# net.add_production(Rule(c1, Ncc(c2, c3)))
# net.add_production(Rule(c2, c3))

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
for wme in wmes:
	net.add_wme(wme)

print("# of results = ", len(p0.items))
print("Results:")
for i in p0.items:
	print(i)

print("\n\x1b[32m——`—,—{\x1b[31;1m@\x1b[0m\n")   # Genifer logo ——`—,—{@

f = open("rete.dot", "w+")
f.write(net.dump())
f.close()
os.system("dot -Tpng rete.dot -orete.png")
print("Rete graph saved as rete.png\n")

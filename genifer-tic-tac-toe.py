#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

from rete.common import Has, Rule, WME, Neg, Ncc, Token
from rete.network import Network

net = Network()

c01 = Has('O', '$x', '$x')
c02 = Has('□', '$y', '$z')
c03 = Has('>', '$y', '$z')
net.add_production(Rule(c01, c02, c03))

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

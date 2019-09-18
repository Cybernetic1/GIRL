# -*- coding: utf-8 -*-

from rete.common import Rule, Has, Neg, WME, Token, Ncc
from rete.network import Network
from rete.pnode import PNode
import os

def test_neg():
	# setup
	net = Network()
	c0 = Has('$x', 'on', '$y')
	c1 = Has('$y', 'left-of', '$z')
	c2 = Neg('$z', 'color', 'red')
	p0 = net.add_production(Rule(c0, c1, c2))
	# end

	wmes = [
		WME('B1', 'on', 'B2'),
		WME('B1', 'on', 'B3'),
		WME('B1', 'color', 'red'),
		WME('B2', 'on', 'table'),
		WME('B2', 'left-of', 'B3'),
		WME('B2', 'color', 'blue'),
		WME('B3', 'left-of', 'B4'),
		WME('B3', 'on', 'table'),
		WME('B3', 'color', 'red'),
		# WME('B4', 'color', 'blue'),
	]
	for wme in wmes:
		net.add_wme(wme)
	assert p0.items[0].wmes == [
		WME('B1', 'on', 'B3'),
		WME('B3', 'left-of', 'B4'),
		None
	]

def save_Rete_graph(net, fname):
	f = open(fname + '.dot', 'w+')
	f.write(net.dump())
	f.close()
	os.system("dot -Tpng %s.dot -o%s.png" % (fname, fname))
	print("Rete graph saved as %s.png\n" % fname)

def test_ncc():
	net = Network()
	c0 = Has('$x', 'on', '$y')
	c1 = Has('$y', 'left-of', '$z')
	c2 = Has('$z', 'color', 'red')
	c3 = Has('$z', 'on', '$w')

	p0 = net.add_production(Rule(c0, c1, Ncc(c2, c3)))
	save_Rete_graph(net, 'rete-0')
	wmes = [
		WME('B1', 'on', 'B2'),
		WME('B1', 'on', 'B3'),
		WME('B1', 'color', 'red'),
		WME('B2', 'on', 'table'),
		WME('B2', 'left-of', 'B3'),
		WME('B2', 'color', 'blue'),
		WME('B3', 'left-of', 'B4'),
		WME('B3', 'on', 'table'),
	]
	for wme in wmes:
		net.add_wme(wme)
	assert len(p0.items) == 2
	net.add_wme(WME('B3', 'color', 'red'))
	assert len(p0.items) == 1

def test_black_white():
	net = Network()
	c1 = Has('$item', 'cat', '$cid')
	c2 = Has('$item', 'shop', '$sid')
	white = Ncc(
		Has('$item', 'cat', '100'),
		Neg('$item', 'cat', '101'),
		Neg('$item', 'cat', '102'),
	)
	n1 = Neg('$item', 'shop', '1')
	n2 = Neg('$item', 'shop', '2')
	n3 = Neg('$item', 'shop', '3')
	p0 = net.add_production(Rule(c1, c2, white, n1, n2, n3))
	wmes = [
		WME('item:1', 'cat', '101'),
		WME('item:1', 'shop', '4'),
		WME('item:2', 'cat', '100'),
		WME('item:2', 'shop', '1'),
	]
	for wme in wmes:
		net.add_wme(wme)

	assert len(p0.items) == 1
	assert p0.items[0].get_binding('$item') == 'item:1'

# test_neg()
test_ncc()
# test_black_white()

# -*- coding: utf-8 -*-

#FIELDS = ['identifier', 'attribute', 'value']
FIELDS = ['F1', 'F2', 'F3']

class BetaNode(object):

	def __init__(self, children=None, parent=None):
		self.children = children if children else []
		self.parent = parent if parent else []

	def dump(self):
		return "%s %s" % (self.__class__.__name__, id(self))


class Has:

	def __init__(self, F1=None, F2=None, F3=None):
		"""
		(<x> ^self <y>)
		repr as:
		('$x', 'self', '$y')

		:type F1, F2, F3: Var or str
		"""
		self.F1 = F1
		self.F2 = F2
		self.F3 = F3

	def __repr__(self):
		return "(%s %s %s)" % (self.F1, self.F2, self.F3)

	def __eq__(self, other):
		return self.__class__ == other.__class__ \
			   and self.F1 == other.F1 \
			   and self.F2 == other.F2 \
			   and self.F3 == other.F3

	@property
	def vars(self):
		"""
		:rtype: list
		"""
		ret = []
		for field in FIELDS:
			v = getattr(self, field)
			if is_var(v):
				ret.append((field, v))
		return ret

	def contain(self, v):
		"""
		Get the field containing value v
		:type v: Var
		:rtype: bool
		"""
		for f in FIELDS:
			_v = getattr(self, f)
			if _v == v:
				return f
		return ""

	def test(self, w):
		"""
		:type w: rete.WME
		"""
		for f in FIELDS:
			v = getattr(self, f)
			if is_var(v):
				continue
			if v != getattr(w, f):
				return False
		return True


class Neg(Has):

	def __repr__(self):
		return "~(%s %s %s)" % (self.F1, self.F2, self.F3)


class Rule(list):

	def __init__(self, *args):
		self.extend(args)

class Ncc(Rule):

	def __repr__(self):
		return "~%s" % super(Ncc, self).__repr__()

	@property
	def number_of_conditions(self):
		return len(self)


class Filter:
	def __init__(self, tmpl):
		self.tmpl = tmpl

	def __eq__(self, other):
		return isinstance(other, Filter) and self.tmpl == other.tmpl


class Bind:
	def __init__(self, tmp, to):
		self.tmpl = tmp
		self.to = to

	def __eq__(self, other):
		return isinstance(other, Bind) and \
			   self.tmpl == other.tmpl and self.to == other.to


class WME:

	def __init__(self, F1=None, F2=None, F3=None):
		self.F1 = F1
		self.F2 = F2
		self.F3 = F3
		self.amems = []  # the ones containing this WME
		self.tokens = []  # the ones containing this WME
		self.negative_join_results = []

	def __repr__(self):
		return "(%s %s %s)" % (self.F1, self.F2, self.F3)

	def __eq__(self, other):
		"""
		:type other: WME
		"""
		if not isinstance(other, WME):
			return False
		return self.F1 == other.F1 and \
			   self.F2 == other.F2 and \
			   self.F3 == other.F3


class Token:

	def __init__(self, parent, wme, node=None, binding=None):
		"""
		:type wme: WME
		:type parent: Token
		:type binding: dict
		"""
		self.parent = parent
		self.wme = wme
		self.node = node  # points to memory this token is in
		self.children = []  # the ones with parent = this token
		self.join_results = []  # used only on tokens in negative nodes
		self.ncc_results = []
		self.owner = None  # Ncc (bug?)
		self.binding = binding if binding else {}	# {"$x": "B1"}

		if self.wme:
			self.wme.tokens.append(self)
		if self.parent:
			self.parent.children.append(self)

	def __repr__(self):
		return "<%s>" % self.wmes

	def __eq__(self, other):
		return isinstance(other, Token) and \
			   self.parent == other.parent and self.wme == other.wme

	def is_root(self):
		return not self.parent and not self.wme

	@property
	def wmes(self):
		ret = [self.wme]
		t = self
		while t.parent and not t.parent.is_root():
			t = t.parent
			ret.insert(0, t.wme)
		return ret

	def get_binding(self, v):
		t = self
		ret = t.binding.get(v)
		while not ret and t.parent:
			t = t.parent
			ret = t.binding.get(v)
		return ret

	def all_binding(self):
		path = [self]
		if path[0].parent:
			path.insert(0, path[0].parent)
		binding = {}
		for t in path:
			binding.update(t.binding)
		return binding

	@classmethod
	def delete_token_and_descendents(cls, token):
		"""
		:type token: Token
		"""
		from rete.negative_node import NegativeNode
		from rete.ncc_node import NccPartnerNode, NccNode
		from rete.alpha import AlphaMemory
		from rete.beta_memory_node import BetaMemory

		DEBUG("*** delete token = ", token)
		DEBUG("token.owner = ", token.owner)
		DEBUG("token.node = ", token.node)
		DEBUG("token.wme = ", token.wme)

		while token.children:
			DEBUG("Looping...")
			child = token.children[0]
			cls.delete_token_and_descendents(child)

		if token.owner != token.parent:
			DEBUG("token.parent = ", token.parent)

		if not isinstance(token.node, NccPartnerNode):
			DEBUG("token.node.items = ", token.node.items)
			token.node.items.remove(token)
		if token.wme:
			token.wme.tokens.remove(token)
		if token.parent:
			print('token.parent.children =', token.parent.children)
			token.parent.children.remove(token)

		if isinstance(token.node, AlphaMemory) or isinstance(token.node, BetaMemory):
			# print('My code actually working')
			if not token.node.items:
				for child in token.node.children:
					print('child =', child)
					print('child.amem.successors =', child.amem.successors)
					child.amem.successors.remove(child)
		elif isinstance(token.node, NegativeNode):
			print('# token.join_results =', len(token.join_results))
			if not token.node.items:
				token.node.amem.successors.remove(token.node)
			while token.join_results:
				jr = token.join_results.pop()
				print("jr = (neg) token.join_results[0] =", jr)
				print("jr.wme =", jr.wme)
				print("jr.wme.negative_join_results =", jr.wme.negative_join_results)
				jr.wme.negative_join_results.remove(jr)
		elif isinstance(token.node, NccNode):
			print("token.ncc_results =", token.ncc_results)
			while token.ncc_results:
				result_tok = token.ncc_results.pop()
				print("result_tok =", result_tok)
				print("result_tok.wme =", result_tok.wme)
				print("result_tok.wme.tokens =", result_tok.wme.tokens)
				result_tok.wme.tokens.remove(result_tok)
				result_tok.parent.children.remove(result_tok)
		elif isinstance(token.node, NccPartnerNode):
			print('token.owner =', token.owner)
			print('token.owner.ncc_results =', token.owner.ncc_results)
			token.owner.ncc_results.remove(token)
			if not token.owner.ncc_results:			# changed from 1 to 0
				for child in token.node.ncc_node.children:
					child.left_activation(token.owner, None)
		DEBUG("Next recursion...")

	@classmethod
	def delete_descendents_of_token(cls, t):
		"""
		:type t: Token
		"""
		while t.children:
			tok = t.children[0]
			cls.delete_token_and_descendents(tok)

def is_var(v):
	return v.startswith('$') if v else False

def DEBUG(*args):
	print(*args)
	return

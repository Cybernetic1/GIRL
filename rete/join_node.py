from rete.common import DEBUG, BetaNode, Has

import io

class JoinNode(BetaNode):

	kind = 'join-node'

	def __init__(self, children, parent, amem, tests, has, custom_tests=None):
		"""
		:type children:
		:type parent: BetaNode
		:type amem: AlphaMemory
		:type tests: list of TestAtJoinNode
		:type custom_tests: list of CustomTestAtJoinNode
		:type has: Has
		"""
		super(JoinNode, self).__init__(children=children, parent=parent)
		self.amem = amem
		self.tests = tests
		self.has = has
		if custom_tests:
			self.custom_tests = custom_tests

	def right_activation(self, wme):
		"""
		:type wme: rete.WME
		"""
		# The Join Nodes with CustomTests will never be right-activated
		# Because they have no proper "conditions" (Has).
		if hasattr(self, 'custom_tests'):
			DEBUG("This should be an error")

		# DEBUG(self, "right-activation:")
		# DEBUG("wme =", wme)
		for token in self.parent.items:
			# DEBUG("token=", token)
			if self.perform_join_test(token, wme):
				binding = self.make_binding(wme)
				for child in self.children:
					child.left_activation(token, wme, binding)

	def left_activation(self, token):
		"""
		:type token: rete.Token
		"""
		# DEBUG(self, "left-activation:")
		# DEBUG("token=", token)
		if hasattr(self, 'custom_tests'):
			# DEBUG("custom_tests=", self.custom_tests)
			if self.perform_custom_join_test(token):
				# binding = self.make_binding(wme)
				for child in self.children:
					child.left_activation(token, None, None)

		if self.amem:		# added by YKY
			# DEBUG("Amem gets left-activation")
			for wme in self.amem.items:
				# DEBUG("wme =", wme)
				if self.perform_join_test(token, wme):
					binding = self.make_binding(wme)
					for child in self.children:
						child.left_activation(token, wme, binding)

	def perform_join_test(self, token, wme):
		"""
		:type token: rete.Token
		:type wme: rete.WME
		"""
		for this_test in self.tests:
			# This is for ordinary TestAtJoinNode:
			arg1 = getattr(wme, this_test.field_of_arg1)
			wme2 = token.wmes[this_test.condition_number_of_arg2]
			arg2 = getattr(wme2, this_test.field_of_arg2)
			if arg1 != arg2:
				return False
		return True

	def perform_custom_join_test(self, token):
		# This is for CustomTestAtJoinNode:
		for this_test in self.custom_tests:
			op = this_test.op
			wme1 = token.wmes[this_test.condition_number_of_arg1]
			arg1 = getattr(wme1, this_test.field_of_arg1)
			if hasattr(this_test, 'const'):
				arg2 = this_test.const
			else:
				wme2 = token.wmes[this_test.condition_number_of_arg2]
				arg2 = getattr(wme2, this_test.field_of_arg2)
			if op == '=':
				if arg1 != arg2:
					return False
			if op == '!=':
				if arg1 == arg2:
					return False
			if op == '>':
				if arg1 <= arg2:
					return False
			if op == '<':
				if arg1 >= arg2:
					return False
		return True

	def make_binding(self, wme):
		"""
		:type wme: WME
		"""
		binding = {}
		for field, v in self.has.vars:
			val = getattr(wme, field)
			binding[v] = val
		return binding

class TestAtJoinNode:
	# see "perform_join_test()" above

	def __init__(self, field_of_arg1, condition_number_of_arg2, field_of_arg2):
		self.field_of_arg1 = field_of_arg1
		self.condition_number_of_arg2 = condition_number_of_arg2
		self.field_of_arg2 = field_of_arg2

	def __repr__(self):
		return "<TestAtJoinNode WME:%s == Cond%s:%s>" % (
			self.field_of_arg1, self.condition_number_of_arg2, self.field_of_arg2)

	def dump(self):
		return "%s == %s:%s?" % (
			self.field_of_arg1, self.condition_number_of_arg2, self.field_of_arg2)

	def __eq__(self, other):
		return isinstance(other, TestAtJoinNode) and \
			self.field_of_arg1 == other.field_of_arg1 and \
			self.field_of_arg2 == other.field_of_arg2 and \
			self.condition_number_of_arg2 == other.condition_number_of_arg2

class CustomTestAtJoinNode:
	# see "perform_custom_test()" above

	def __init__(self, condition_number_of_arg1, field_of_arg1, op, condition_number_of_arg2=None, field_of_arg2=None, const=None):
		self.condition_number_of_arg1 = condition_number_of_arg1
		self.field_of_arg1 = field_of_arg1
		self.op = op
		if const:
			self.const = const
		else:
			self.condition_number_of_arg2 = condition_number_of_arg2
			self.field_of_arg2 = field_of_arg2

	def __repr__(self):
		if hasattr(self, 'const'):
			return "<CustomTestAtJoinNode %s:%s %s %s>" % (
				self.condition_number_of_arg1, self.field_of_arg1, self.op, self.const )
		else:
			return "<CustomTestAtJoinNode %s:%s %s %s:%s>" % (
				self.condition_number_of_arg1, self.field_of_arg1, self.op, self.condition_number_of_arg2, self.field_of_arg2 )

	def dump(self):
		if hasattr(self, 'const'):
			return "%s:%s %s %s?" % (
				self.condition_number_of_arg1, self.field_of_arg1, self.op, self.const )
		else:
			return "%s:%s %s %s:%s?" % (
				self.condition_number_of_arg1, self.field_of_arg1, self.op, self.condition_number_of_arg2, self.field_of_arg2 )

	def __eq__(self, other):
		if self.const:
			return isinstance(other, CustomTestAtJoinNode) and \
				self.field_of_arg1 == other.field_of_arg1 and \
				self.condition_number_of_arg1 == other.condition_number_of_arg1 and \
				self.const == other.const and \
				self.op == other.op
		else:
			return isinstance(other, CustomTestAtJoinNode) and \
				self.field_of_arg1 == other.field_of_arg1 and \
				self.field_of_arg2 == other.field_of_arg2 and \
				self.condition_number_of_arg1 == other.condition_number_of_arg1 and \
				self.condition_number_of_arg2 == other.condition_number_of_arg2 and \
				self.op == other.op

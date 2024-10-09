from ctypes import *
import os

class BuDDy:

	# choose buddy.macos for macOS (arm64), buddy.linux for Linux (x64)
	def __init__(self, var_order: list, lib="buddy.macos"):
		self._bdd = CDLL(f"./{lib}")

		self._bdd.bdd_satcountln.restype = c_double
		self._bdd.bdd_satcount.restype = c_double

		self._bdd.bdd_init(1<<26, 1<<20)
		self._bdd.bdd_setmaxincrease(1<<27)
		self._bdd.bdd_setcacheratio(32)
		self._bdd.bdd_setvarnum(c_int(len(var_order)))

		self.var_dict = dict(enumerate(var_order))
		self.name_dict = { x : k for k, x in self.var_dict.items() }
		self.var_bdds = { x : self.var2bdd(x) for x in self.name_dict.keys() }

	def __exit__(self):
		self._bdd.bdd_done()

	### Basic methods
	@property
	def false(self):
		return self._bdd.bdd_false()

	@property
	def true(self):
		return self._bdd.bdd_true()

	def var2bdd(self, x):
		if x not in self.name_dict.keys():
			print(f"WARNING! {x} variable not found")
		return self._bdd.bdd_ithvar(self.name_dict[x])

	def nvar2bdd(self, x):
		if x not in self.name_dict.keys():
			print(f"WARNING! {x} variable not found")
		return self._bdd.bdd_nithvar(self.name_dict[x])

	def var(self, u):
		x = self._bdd.bdd_var(u)
		return self.var_dict[x]

	def low(self, u):
		return self._bdd.bdd_low(u)

	def high(self, u):
		return self._bdd.bdd_high(u)

	def level(self, u):
		return self._bdd.bdd_level(u)

	def node_count(self, u):
		return self._bdd.bdd_nodecount(u)

	def satcount_int(self, u):
		scount = 0
		stack = [(u, 0)]
		vcount = len(self.var_dict)

		while stack:
			node, depth = stack.pop()
			if node == self.true:
				scount += 1 << (vcount - depth)
			elif node != self.false:
				stack.append((self.low(node),  depth +1))
				stack.append((self.high(node), depth +1))
		return scount

	def satcount(self, u):
		return self._bdd.bdd_satcount(u)

	def satcount_ln(self, u):
		return self._bdd.bdd_satcountln(u)

	def support(self, u):
		return self._bdd.bdd_support(u)
	
	### Operations
	def neg(self, u):
		return self._bdd.bdd_not(u)
		
	def apply_and(self, u, v):
		return self._bdd.bdd_and(u,v)
		
	def apply_or(self, u, v):
		return self._bdd.bdd_or(u,v)
	
	def apply_ite(self, u, v, w):
		return self._bdd.bdd_ite(u,v,w)

	def apply(self, op, u, v = None, w = None):
		if op in ('~', 'not', 'NOT', '!'):
			return self._bdd.bdd_not(u)
		elif op in ('or', 'OR', r'\/', '|', '||'):
			return self._bdd.bdd_or(u, v)
		elif op in ('and', 'AND', '/\\', '&', '&&'):
			return self._bdd.bdd_and(u, v)
		elif op in ('nand', 'NAND'):
			return self._bdd.bdd_not(self._bdd.bdd_and(u, v))
		elif op in ('xor', 'XOR', '^'):
			return self._bdd.bdd_xor(u, v)
		elif op in ('=>', '->', 'implies'):
			return self._bdd.bdd_imp(u, v)
		elif op in ('<=>', '<->', 'equiv'):
			return self._bdd.bdd_bimp(u, v)
		elif op in ('diff', '-'):
			return self.ite(u, self._bdd.bdd_not(u), self.false)
		elif op in ('ite', 'ITE'):
			return self.ite(u, v, w)
		else:
			raise Exception(f'unknown operator "{op}"')

	### reference counting and garbage collection
	def incref(self, u):
		return self._bdd.bdd_addref(u)

	def decref(self, u):
		return self._bdd.bdd_delref(u)

	def dump(self, u=None, filename="out.bdd"):
		tempf = filename+".tmp"
		if filename[-3:] == "dot":
			self._bdd.bdd_fnprintdot(c_char_p(filename.encode("UTF-8")), u)
		elif filename[-3:] == "pdf":
			self._bdd.bdd_fnprintdot(c_char_p(tempf.encode("UTF-8")), u)
			os.system(f"dot -Tpdf {tempf} > {filename}")
			os.remove(tempf)
		else:
			self._bdd.bdd_fnsave(c_char_p(filename.encode("UTF-8")), u)
			with open(filename+"v", "w") as f:
				for i in range(len(self.var_dict)):
					f.write(f"{self.var_dict[i]}\n")
				f.close()

	def load(self, filename="in.bdd"):
		root = c_int()
		self._bdd.bdd_fnload(c_char_p(filename.encode("UTF-8")), byref(root))
		# TODO: also read variable names
		self.incref(root.value)
		return root.value
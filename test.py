import sys

from gv import MODULE, STRUCT, UNION, BIT, REG, INPUT, OUTPUT
from gv import ELABORATE, stream

GLOBAL = 6

class block_t(UNION):
	def __init__(self, value=None):
		super().__init__(value)

	def impl(self):
		w = BIT(256)
		b = BIT(32)(8)

class test(MODULE):
	def impl(self):
		i = INPUT(block_t())
		o = INPUT(block_t())
		o = i | 0b1110

class top(MODULE):
	def __init__(self):
		super().__init__()

	def impl(self):
		a = INPUT(block_t())
		b = INPUT(BIT(32)(8))
		c = OUTPUT(BIT(4))
		c = a[0:1] & b[0:1]
		l = block_t()

		test_inst = test()
		test_inst.i = c
		l.w = test_inst.o

		test_inst2 = test()
		test_inst2.i = c
		l.w = test_inst2.o

		if c == BIT(2, 3):
			c = BIT(2, 1)
		elif c == BIT(2, 1):
			c = BIT(2, 0)

def main():
	a = top()
	ELABORATE.dump(stream(sys.stdout))

if __name__ == '__main__':
	main()
import sys
import argparse

from gv import MODULE, STRUCT, UNION, BIT, INPUT, OUTPUT
from gv import ELABORATE, stream

from gv import COND, EXISTS, CONNECT
GLOBAL = 6

class block_t(UNION):
	def __init__(self, value=None):
		super().__init__(value)

	def __impl__(self):
		self.w = BIT(256)
		self.b = BIT(32)(8)

class TOP(MODULE):
	def __init__(self):
		super().__init__()

	def __impl__(self):
		self.a = INPUT(block_t())
		self.b = INPUT(BIT(32))
		self.c = OUTPUT(BIT(4))
		self.c = self.a[0:1] & self.b[0:1]
		l = 5

		# self.a = BIT(block_t.width, 45)

		# EXISTS('a', locals(), globals(), None)
		if EXISTS('a', locals(), globals(), self) and isinstance(self.a, BIT):
			CONNECT(self.a, BIT(block_t(45), 45))
		else:
			self.a = 4

		# if self.c == BIT(1, 45):
		# 	pass
		# else:
		# 	pass

		def if_body():
			self.c = BIT(1, 1)
		def else_body():
			self.c = BIT(1, 0)
		COND().IF(lambda:self.c == BIT(2, 3), if_body).ELSE(else_body)

def main():
	TOP()
	ELABORATE.dump(stream(sys.stdout))

if __name__ == '__main__':
	main()
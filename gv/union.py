from . import bit
from .elaborate import ELABORATE

class union(bit):
	def __init__(self, value=None):
		self.value = value;
		# ELABORATE.union(self.__class__.__name__)
		self.__impl__()
		super().__init__(ELABORATE.bits())
from .bit import bit
from .elaborate import ELABORATE

class struct(bit):
	def __init__(self, value=None):
		self.value = value
		# ELABORATE.struct(self.__class__.__name__)
		self.__impl__()
		super().__init__(ELABORATE.bits())
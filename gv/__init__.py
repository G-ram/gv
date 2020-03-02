import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bit import bit, input, output
from reg import reg
from module import module
from Type import Struct, union
from stmt import cond, connect
from stream import stream
from elaborate import ELABORATE

def exists(name, loc1, loc2={}):
	if type(loc1) is not dict:
		return hasattr(loc1, name)
	return (name in loc1.keys()) or (name in loc2.keys())

BIT = bit
REG = reg
STRUCT = Struct
UNION = union
MODULE = module
INPUT = input
OUTPUT = output
COND = cond
EXISTS = exists
CONNECT = connect

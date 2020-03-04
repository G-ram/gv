import os
import re
import sys
import argparse

from stream import stream

def tostr(v):
	if v is None: return ''
	return v

def strip_comments(lines):
	newlines = []
	for line in lines:
		if '#' in line:
			newlines.append(line[:line.index('#')])
			if '\n' not in newlines[-1]:
				newlines[-1] = '%s\n' % newlines[-1]
		else:
			newlines.append(line)
	return newlines

def find_conditional(lines):
	newlines = []
	elif_count = 0
	max_indent = max(map(lambda x: x.count('\t'), lines))
	cmds = [None for _ in range(max_indent + 1)]
	for i, line in enumerate(lines):
		replace = False
		match = re.match(r'(\t*)(if([^:]+)):\s*\n', line)
		if match is not None:
			indent = 0 if match.group(1) is None else match.group(1).count('\t')
			cmds[indent] = '%sCOND().IF(lambda:%s, if_body)' % (
				(indent * '\t'), match.group(3))
			newlines.append('%sdef if_body():\n' % (indent * '\t'))
			replace = True

		match = re.match(r'(\t*)(elif([^:]+)):\s*\n', line)
		if match is not None:
			indent = 0 if match.group(1) is None else match.group(1).count('\t')
			cmds[indent] += '.ELIF(lambda:%s, elif_body%d)' % (
				match.group(3), elif_count)
			newlines.append('%sdef elif_body%d():\n' % (
				(indent * '\t'), elif_count))
			elif_count += 1
			replace = True

		match = re.match(r'(\t*)else:\s*\n', line)
		if match is not None:
			indent = 0 if match.group(1) is None else match.group(1).count('\t')
			cmds[indent] += '.ELSE(else_body)'
			newlines.append('%sdef else_body():\n' % (indent * '\t'))
			replace = True

		if not replace: 
			newlines.append(line)

		if i < len(lines) - 1:
			match = re.match(r'(\t*)[^\n].*', lines[i+1])
			if match is not None:
				indent = 0 if match.group(1) is None else match.group(1).count('\t')
				for j in range(len(cmds)-1, indent, -1):
					if cmds[j] is not None:
						newlines.append('%s\n' % cmds[j])
						cmds[j] = None

	for cmd in reversed(cmds):
		if cmd is not None:
			newlines.append('%s\n' % cmd)
			
	return newlines

def replace_conditionals(lines):
	newlines = []
	found_module = False
	found_impl = False
	indent_level = 0
	i = 0
	while i < len(lines):
		if 'MODULE' in lines[i]:
			found_module = True
			found_impl = False
		elif 'class' in lines[i]:
			found_module = False
			found_impl = False

		if found_module and 'impl' in lines[i]:
			indent_level = lines[i].count('\t')
			found_impl = True

		if found_module and found_impl:
			newlines.append(lines[i])
			for j, l in enumerate(lines[i+1:]):
				match = re.match(r'\s*\n\s*', l)
				if match is not None:
					continue
				if l.count('\t') <= indent_level:
					break
			found_module = False
			found_impl = False
			newlines += find_conditional(lines[i+1:i + j])
			i += j
		else:
			newlines.append(lines[i])
			i += 1

	return newlines

def replace_assignments(lines):
	newlines = []
	found_module = False
	found_impl = False
	for i, line in enumerate(lines):
		if 'MODULE' in line:
			found_module = True
			found_impl = False
		elif 'class' in line:
			found_module = False
			found_impl = False

		if found_module and 'impl' in line:
			found_impl = True

		if found_module and found_impl:
			fxn_arg_match = re.match(r'(\t*)([a-zA-Z]+[a-zA-Z\d_]*\.)*?([a-zA-Z]+[a-zA-Z\d_]*)\(.*\)', line)
			if fxn_arg_match is not None:
				newlines.append(line)
				continue
			match = re.match(r'(\t*)([a-zA-Z]+[a-zA-Z\d_]*\.)*?([a-zA-Z]+[a-zA-Z\d_]*)(\[.+\])* *=([^=][^\n]*)\n', line)
			if match is not None:
				indent = match.group(1)
				classname = 'None'
				if match.group(2) is not None:
					classname = match.group(2).replace('.', '')
				name = tostr(match.group(3))
				pre_eq = '%s%s%s' % (
					tostr(match.group(2)), 
					tostr(match.group(3)), 
					tostr(match.group(4)))
				post_eq = '%s' % (tostr(match.group(5)))
				newlines.append('%stry:\n' % indent)
				var_match = re.match(r'(\t*)([a-zA-Z]+[a-zA-Z\d_]*)', line)
				v = var_match.group(2)
				newlines.append('%s\t# nonlocal %s\n' % (indent, v))
				newlines.append('%s\tCONNECT(%s, (%s))\n' % (indent, pre_eq, post_eq))
				newlines.append('%sexcept:\n' % indent)
				newlines.append('\t%s' % line)
			else:
				newlines.append(line)
		else:
			newlines.append(line)
	return newlines

def fix_assignments(lines):
	newlines = []
	i = 0
	while i < len(lines):
		if 'else_body()' in lines[i] or 'if_body()' in lines[i]:
			indent = lines[i].count('\t')
			newlines.append(lines[i])
			i += 1
			start = i
			for j, line in enumerate(lines[start:]):
				if line.count('\t') <= indent and len(line.strip()) > 0:
					break
				if '#' in line:
					newlines.append(line.replace('# ', ''))
				else:
					newlines.append(line)
				i += 1
		else:
			newlines.append(lines[i])
			i += 1

	return newlines


def main(args):
	f = stream(sys.stdout)
	if args.dest:
		if os.path.exists(os.path.dirname(args.dest)):
			f = stream(open(args.dest, 'w+'))
		else:
			print('Not found: %s' % args.dest)
			return

	if not os.path.exists(args.top[0]):
		print('Could not find top %s' % args.top)

	with open(args.top[0], 'r') as t:
		lines = t.readlines()
		lines.insert(0, 'from gv import COND, EXISTS, CONNECT\n')
		lines = strip_comments(lines)
		lines = replace_conditionals(lines)
		lines = replace_assignments(lines)
		lines = fix_assignments(lines)

	for line in lines:
		f.write(line)
	f.blank()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--dest', 
		type=str, help='Destination')
	parser.add_argument('top', 
		nargs=1, help='top')
	args = parser.parse_args()
	main(args)

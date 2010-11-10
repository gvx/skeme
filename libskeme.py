'''Skeme

Expects on standard input:
- Node
-- Sub node (in: int blah) (out: x) (inout: y) (returns: int)
-- Sibling node
'''

import cairo
import re
import math

_descr = re.compile(r'\(([a-z]*) ([^)]*)\)')

class Node(object):
	def __init__(self, level):
		self.subnodes = []
		self.level = level
		self.text = None
		self.args = [] # ('in', 'int blah'), ('out', 'x'), ('inout', 'y')
		self.returns = None
		self.parent = None
	def stringify(self, indent=0):
		t = self.text.strip()
		chardict = {'in': '->', 'out': '<-', 'inout': '<->'}
		for arg in self.args:
			t += '  ' + chardict[arg[0]] + arg[1]
		if self.returns:
			t += '  Returns:' + self.returns
		t += '\n'
		indent += 1
		for kid in self.subnodes:
			t += '\t'*indent + kid.stringify(indent)
		return t

class ParseError(Exception):
	pass

class Tree(object):
	def __init__(self, origin):
		stack = []
		repetition_stack = []
		self.maxdepth = 0
		self.maxwidth = 1
		self.repetitions = []
		for line in origin.splitlines():
			if line == '{':
				repetition_stack.append(None)
				continue
			elif line == '}':
				self.repetitions.append((repetition_stack.pop(), stack[-1]))
				continue
			level = self.getlevel(line)
			self.maxdepth = max(self.maxdepth, level)
			if level:
				newnode = Node(level)
				if repetition_stack and repetition_stack[-1] is None:
					repetition_stack[-1] = newnode
				for i in range(len(stack)-1, -1, -1):
					if stack[i].level < level: #found parent!
						if i < len(stack)-1: #stack[i].subnodes:
							self.maxwidth += 1
						stack[i].subnodes.append(newnode)
						newnode.parent = stack[i]
						newnode.x = self.maxwidth
						stack = stack[:i+1]
						break
				stack.append(newnode)
			for match in _descr.finditer(line):
				key = match.group(1)
				if key == 'returns':
					stack[-1].returns = match.group(2)
				elif key in ('in', 'out', 'inout'):
					stack[-1].args.append(match.groups())
				else:
					raise ParseError('unrecognized key: '+key)
			line = _descr.sub('', line)
			if level:
				stack[-1].text = line.lstrip(' \t-').rstrip()
			else:
				stack[-1].text += '\n' + line.strip()
		self.toplevel = stack[0]
	def __str__(self):
		return self.toplevel.stringify()
	def getlevel(self, line):
		level = 0
		for c in line:
			if c == '-':
				level += 1
			elif c not in ' \t':
				break
		return level

class Renderer(object):
	def __init__(self, input):
		self.tree = Tree(input)
		self.item_width = 210 #80
		self.horizontal_separation = self.item_width + 10 #90
		self.item_height = 35
		self.vertical_seperation = 120
		self.x_offset = 6#5.5
		self.y_offset = 6#5.5
		self.curving_line = True
		self.arrows = True
		self.type_char = {'in': u'\u2193', 'out': u'\u2191', 'inout': u'\u2195'}
		self.font = 'Serif'
		self.font_size = 12
		self.small_font = 'Sans'
		self.small_font_size = 10
		self.fg = (0, 0, 0)
		self.bg = (1, 1, 1)

	def roundedrec(self, x, y, w, h, r = 10):
		"Draw a rounded rectangle"
		#   A****BQ
		#  H      C
		#  *      *
		#  G      D
		#   F****E
		
		context = self.context

		context.move_to(x+r,y)                      # Move to A
		context.line_to(x+w-r,y)                    # Straight line to B
		context.curve_to(x+w,y,x+w,y,x+w,y+r)       # Curve to C, Control points are both at Q
		context.line_to(x+w,y+h-r)                  # Move to D
		context.curve_to(x+w,y+h,x+w,y+h,x+w-r,y+h) # Curve to E
		context.line_to(x+r,y+h)                    # Line to F
		context.curve_to(x,y+h,x,y+h,x,y+h-r)       # Curve to G
		context.line_to(x,y+r)                      # Line to H
		context.curve_to(x,y,x,y,x+r,y)             # Curve to A

	def drawnode(self, node):
		context = self.context
		x = node.x
		level = node.level - 1
		context.set_line_width(2)
		self.roundedrec(self.x_offset + x * self.horizontal_separation, self.y_offset + self.vertical_seperation * level, self.item_width, self.item_height, 15)
		context.set_source_rgba(*self.bg)
		context.fill()
		self.roundedrec(self.x_offset + x * self.horizontal_separation, self.y_offset + self.vertical_seperation * level, self.item_width, self.item_height, 15)
		context.set_source_rgba(*self.fg)
		context.stroke()
		context.select_font_face(self.font,
				cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		context.set_font_size(self.font_size)
		lines = node.text.splitlines()
		for i, text in enumerate(lines):
			x_bearing, y_bearing, width, height = context.text_extents(text)[:4]
			if len(lines) > 1:
				ydiff = height * ((i-1)/len(lines))*.9
			else:
				ydiff = -.5 * height
			x_, y_ = round(self.x_offset + self.item_width / 2.0 + x * self.horizontal_separation - width/2 - x_bearing), round(self.y_offset + self.item_height / 2.0 +self.vertical_seperation * level + ydiff - y_bearing)
			context.move_to(x_, y_)
			if '//' in text:
				t1, t2 = text[:text.index('//')], text[text.index('//'):]
				context.show_text(t1)
				context.select_font_face(self.font,
						cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
				context.move_to(x_ + context.text_extents(t1+'.')[2], y_)
				context.show_text(t2)
			else:
				context.show_text(text)
			context.set_font_size(self.font_size - 2)
		if node.parent:
			p = node.parent
			siblings = p.subnodes
			lastinline = len(siblings) > 1 and siblings.index(node) == len(siblings) - 1
			mustcurve = lastinline and self.curving_line
			ex = siblings.index(node) + 1.0
			if node.returns:
				context.set_line_width(2)
				context.move_to(round(self.x_offset + self.item_width / 2.0 + x * self.horizontal_separation), round(self.y_offset + self.vertical_seperation * level))
				#context.line_to(round(self.x_offset + self.item_width * ex / (len(p.subnodes)+1) + p.x * self.horizontal_separation), round(self.y_offset + self.vertical_seperation * (p.level - 1) + self.item_height))
			else:
				context.set_line_width(.8)
				context.move_to(.5+round(self.x_offset + self.item_width / 2.0 + x * self.horizontal_separation), round(self.y_offset + self.vertical_seperation * level))
				#context.line_to(.5+round(self.x_offset + self.item_width * ex / (len(p.subnodes)+1) + p.x * self.horizontal_separation), round(self.y_offset + self.vertical_seperation * (p.level - 1) + self.item_height))
			context.rel_line_to(0, -round((self.vertical_seperation - self.item_height) * 4 / 5.0) + (mustcurve and 10 or 0))
			context.stroke()
			context.select_font_face(self.small_font,
				cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
			context.set_font_size(self.small_font_size)
			if node.returns:
				if self.arrows:
					context.move_to(round(self.x_offset + self.item_width / 2.0 + x * self.horizontal_separation), round(self.y_offset + self.vertical_seperation * level - (self.vertical_seperation - self.item_height) * 4 / 5.0) + (mustcurve and 10 or 0))
					context.rel_line_to(-7, 7)
					context.rel_line_to(14, 0)
					context.fill()
				x_bearing, y_bearing, width, height = context.text_extents(node.returns)[:4]
				#l = (x - p.x) * self.horizontal_separation / 10.0
				#context.move_to(round(self.x_offset + self.item_width / 2.0 + x * self.horizontal_separation - x_bearing - l - width - 4), round(self.y_offset + self.vertical_seperation * level + y_bearing/2 + 1))
				context.move_to(round(self.x_offset + x * self.horizontal_separation - x_bearing + 4), round(self.y_offset + self.vertical_seperation * level + y_bearing/2 + 1))
				context.show_text(node.returns)
			for i, arg in enumerate(node.args):
				arg = self.type_char[arg[0]] + arg[1]
				x_bearing, y_bearing, width, height = context.text_extents(arg)[:4]
				context.move_to(round(self.x_offset + self.item_width + x * self.horizontal_separation - x_bearing - width), round(self.y_offset + self.vertical_seperation * level + y_bearing/2 - i * (height + 1) + 1))
				context.show_text(arg)
			if lastinline:
				context.set_line_width(.8)
				context.move_to(.5+round(self.x_offset + self.item_width / 2.0 + siblings[0].x * self.horizontal_separation), .5+round(self.y_offset + self.vertical_seperation * level - (self.vertical_seperation - self.item_height) * 4 / 5.0))
				if self.curving_line:
					context.rel_line_to((x - siblings[0].x) * self.horizontal_separation - 10, 0)
					context.rel_curve_to(5, 0, 10, 5, 10, 10)
				else:
					context.rel_line_to((x - siblings[0].x) * self.horizontal_separation, 0)
				context.stroke()
		if node.subnodes:
			context.set_line_width(.8)
			context.move_to(.5+round(self.x_offset + self.item_width / 2.0 + x * self.horizontal_separation), round(self.y_offset + self.vertical_seperation * level + self.item_height))
			context.rel_line_to(0, round(self.vertical_seperation - self.item_height) / 2)
			context.stroke()

	def drawrepetition(self, start, end):
		context = self.context
		context.set_line_width(.8)
		context.move_to(round(self.x_offset + self.item_width / 4.0 + start.x * self.horizontal_separation), .5+round(self.y_offset + self.vertical_seperation * (start.level - 1) - (self.vertical_seperation - self.item_height) * 4 / 7.0))
		context.rel_line_to(round(self.x_offset + self.item_width / 2.0 + (end.x - start.x) * self.horizontal_separation), 0)
		context.stroke()

	def renderto(self, output):
		self.width = (self.tree.maxwidth-1) * self.horizontal_separation + self.item_width + int(self.x_offset * 2)
		self.height = (self.tree.maxdepth-1) * self.vertical_seperation + self.item_height + int(self.y_offset * 2)
		self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
		self.context = cairo.Context(self.surface)
		queue = [self.tree.toplevel]
		x = 0
		while queue:
			n = queue.pop(0)
			n.x = x
			self.drawnode(n)
			if n.subnodes:
				queue = n.subnodes + queue #depth-first search
			else:
				x += 1
		for start, end in self.tree.repetitions:
			self.drawrepetition(start, end)
		self.surface.flush()
		self.surface.write_to_png(output)

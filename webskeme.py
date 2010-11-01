#!/usr/bin/env python 
import sys
sys.path += ['/home/robin/Hacking/skeme/']
from libskeme import *
import cgi
import cgitb
cgitb.enable()#display=0, logdir='/tmp', format='')

form = cgi.FieldStorage()

def splitpairs(text):
	for i in range(0, len(text), 2):
		yield text[i:i+2]

r = Renderer(form.getfirst('content', '-'))
r.arrows = form.getfirst('arrow', False)
r.curving_line = form.getfirst('curve', False)
r.item_width = int(form.getfirst('width', False)) or r.item_width
r.item_height = int(form.getfirst('height', False)) or r.item_height
r.horizontal_separation = int(form.getfirst('hor-sep', False)) or r.horizontal_separation
r.vertical_seperation = int(form.getfirst('vert-sep', False)) or r.vertical_seperation
r.x_offset = int(form.getfirst('x-off', False)) or r.x_offset
r.y_offset = int(form.getfirst('y-off', False)) or r.y_offset
r.font = form.getfirst('font', False) or r.font
r.small_font = form.getfirst('small-font', False) or r.small_font
r.font_size = int(form.getfirst('font-size', False)) or r.font_size
r.small_font_size = int(form.getfirst('small-font-size', False)) or r.small_font_size
if form.getfirst('fg', False):
	r.fg = tuple(int(x, 16) / 255.0 for x in splitpairs(form.getfirst('fg')))
if form.getfirst('bg', False):
	r.bg = tuple(int(x, 16) / 255.0 for x in splitpairs(form.getfirst('bg')))

print("Content-Type: image/png")
print("")
r.renderto(sys.stdout)

from django import template
import random
import datetime
register = template.Library()

@register.simple_tag
def foo():
	return "Hello"

@register.simple_tag
def random_colour():
	'''
		usage: background-color: {%% foo %%};
	'''
	r,g,b = random.randint(0,255),random.randint(0,255),random.randint(0,255)
	return "rgb(%s,%s,%s)"%(r,g,b)

@register.simple_tag
def random_colour2():
	'''
		usage: background-color: rgb {%% foo %%};
	'''
	r,g,b = random.randint(0,255),random.randint(0,255),random.randint(0,255)
	return r,g,b


@register.assignment_tag
def concat(a,b,c):
	'''
		Usage:
		{%% concat 'HI' 'Hi' 'Yo' as result %%}
	'''
	return a+b+c


@register.simple_tag
def current_time(format_string):
	return datetime.datetime.now().strftime(format_string)



#TEMPLATE FILTERS

@register.filter(name='lower')
def lower(value):
	return value.lower()






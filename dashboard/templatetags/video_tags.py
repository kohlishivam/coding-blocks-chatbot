from django import template

register = template.Library()

@register.simple_tag
def foo():
    return 12

@register.filter(name='cut')
def lower(value): # Only one argument.
    """Converts a string into all lowercase"""
    return value.lower()

@register.assignment_tag
def get_result_tag(arg1, arg2, arg3):
    "----"
    return "response"
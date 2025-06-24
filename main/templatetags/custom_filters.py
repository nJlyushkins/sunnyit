from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

@register.filter(name='range')
def range_filter(number):
    return list(range(int(number)))
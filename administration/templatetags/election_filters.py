from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key), 0)  # Retourne 0 si la clé n'existe pas
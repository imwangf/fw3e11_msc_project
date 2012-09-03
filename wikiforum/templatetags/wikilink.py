from django import template
import re

wikilink = re.compile ("^[[(.*)]]$")
register = template.Library()

@register.filter
def wiki_ahref (value):
    return wikilink.sub (r"<a href='\1'>\1</a>", value)

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def cgroup(field):
    return mark_safe('<div class="pure-control-group %s">%s%s%s</div>' 
                     % (field.css_classes(),
                        field.label_tag(label_suffix=''), 
                        unicode(field),
                        field.errors))

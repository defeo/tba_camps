from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def cgroup(field):
    label = field.label
    if field.field.required:
        label += '*'
    if field.help_text:
        label += '<br><small>(%s)</small>' % field.help_text
    return mark_safe('<div class="pure-control-group %s">%s%s%s</div>'
                     % (field.css_classes(),
                        field.label_tag(mark_safe(label), label_suffix=''),
                        unicode(field),
                        field.errors))

# -:- encoding: utf-8

from django.utils.html import format_html
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django import forms
from django.utils.encoding import force_text
from .templatetags.decimal import strip_cents
from .models import Hebergement, Semaine, Formule

# The Formule-Semaine-Hebergement mess has a complicated logic and UI
# We need custom fiedls and widgets that extract more custom
# information from the mode.
#
# Django has no native system to do that, so we hack the "label" of
# the various choice fields to hold more data than it is supposed to.
#
# This usually requires cooperation between the field and its widget
# (only Hebergement is simpler), then uses the builtin django
# templates.

### Hebergement

class HebergementField(forms.ModelChoiceField):
    widget = forms.widgets.RadioSelect

    def __init__(self, *args, **kwds):
        super().__init__(queryset=Hebergement.objects.all(), *args, **kwds)
        self.empty_label = None

    def label_from_instance(self, obj):
        return format_html('''{nom} {commentaire}''',
                               nom=force_text(obj.nom),
                               commentaire=obj.md_commentaire())

### Semaines

class SemainesWidget(forms.widgets.CheckboxSelectMultiple):
    class Media:
        js = ('//code.jquery.com/jquery-1.12.4.min.js', 
              'js/inscription.js')

    def create_option(self, *args, **kwds):
        opt = super().create_option(*args, **kwds)
        opt['attrs']['data-complet'] = opt['label']['complet']
        opt['label'] = opt['label']['label']
        return opt
    
class SemainesField(forms.ModelMultipleChoiceField):
    widget = SemainesWidget

    def __init__(self, *args, **kwds):
        super().__init__(queryset=Semaine.objects.open(), *args, **kwds)

    def label_from_instance(self, obj):
        return {
            'label': str(obj),
            'complet': ','.join(str(h.pk) for h in obj.complet.iterator())
            }

### Formules

class FormuleWidget(forms.widgets.RadioSelect):
    class Media:
        js = ('//code.jquery.com/jquery-1.12.4.min.js', 
              'js/inscription.js')
            
    def create_option(self, *args, **kwds):
        opt = super().create_option(*args, **kwds)
        opt['attrs'].update(opt['label']['attrs'])
        opt['label'] = opt['label']['label']
        return opt
    
class FormuleField(forms.ModelChoiceField):
    widget = FormuleWidget
    
    def __init__(self, *args, **kwds):
        super().__init__(queryset=Formule.objects.all(), *args, **kwds)
        self.empty_label = None
        self.iterator = self

    # Too lazy to implement a separate iterator class
    def __call__(self, *args):
        return self

    def __len__(self):
        return len(self.queryset)

    # Transform a list of choices in a list of grouped choices
    def __iter__(self):
        subgroup = []
        prev_group = ''
        header = lambda g: format_html('<div class="group">{g}</div>', g=g)
        for i, choice in enumerate(self.queryset.all()):
            group = choice.groupe
            if group:
                if subgroup:
                    yield (header(prev_group), subgroup)
                subgroup = []
                prev_group = group
            subgroup.append((
                self.prepare_value(choice),
                self.label_from_instance(choice)
                ))
        if subgroup:
            yield (header(prev_group), subgroup)
    
    def label_from_instance(self, obj):
        attrs = {}
        if obj.affiche_accompagnateur:
            attrs['data-accompagnateur'] = '1'
        if obj.affiche_train:
            attrs['data-train'] = '1'
        if obj.affiche_chambre:
            attrs['data-chambre'] = '1'
        if obj.affiche_navette:
            attrs['data-navette'] = '1'
        if obj.affiche_assurance:
            attrs['data-assurance'] = '1'
        if obj.affiche_mode:
            attrs['data-mode'] = '1'
        attrs['data-hebergements'] = ','.join(str(h.pk) for h in obj.hebergements.iterator())
        for field, (val, _, _) in obj.costs().items():
            attrs['data-%s' % field.name] = val

        return {
            'label': format_html(
    '''{nom} <span class="prix">{prix}</span> <span class="description">{description}</span>''',
                nom=force_text(obj.nom),
                prix=format_html('({}€)', strip_cents(obj.prix)) * obj.publique,
                description=force_text(obj.description)),
            'attrs': attrs,
            }

### Date Picker

class DatePicker(forms.widgets.DateInput):
    class Media:
        css = { 'all' : ('css/jquery-ui.min.css',) }
        js = ('//code.jquery.com/jquery-1.12.4.min.js', 
              'js/jquery-ui.min.js',
              'js/datepicker.js')

    def __init__(self, *args, **kwds):
        super(DatePicker, self).__init__(*args, **kwds)
        if self.attrs.get('class') is None:
            self.attrs['class'] = 'datepicker'
        else:
            self.attrs['class'] += ' datepicker'


### Files

class FileInput(forms.widgets.FileInput):
    template = '%(input)s <a href="%(url)s">%(text)s</a>'

    def render(self, name, value, attrs=None):
        s = {
            'input' : super(FileInput, self).render(name, value, attrs),
            'url'   : value.url or '',
            'text'  : value.name.split('/')[-1] or '',
        }
        return mark_safe(self.template % s)

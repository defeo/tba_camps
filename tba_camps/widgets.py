# -:- encoding: utf-8

from django.utils.html import format_html
from django.forms.utils import flatatt
from django.forms.models import ModelChoiceIteratorValue
from django.utils.safestring import mark_safe
from django import forms
from django.utils.encoding import force_str
from .templatetags.decimal import strip_cents
from .models import Hebergement, Semaine, Formule, Reversible

# The Formule-Semaine-Hebergement mess has a complicated logic and UI
# We need custom fiedls and widgets that extract more custom
# information from the model.
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
                               nom=force_str(obj.nom),
                               commentaire=obj.md_commentaire())

### Semaines

class SemainesWidget(forms.widgets.CheckboxSelectMultiple):
    class Media:
        js = ('js/inscription.js',)

    def create_option(self, *args, **kwds):
        opt = super().create_option(*args, **kwds)
        if opt['label']['off']:
            opt['attrs']['disabled'] = True
            hidden = '<input type="hidden" name="{}" value="{}">'.format(opt['name'], opt['value'])
        else:
            hidden = ''
        opt['attrs']['data-formule_complet'] = opt['label']['formule_complet']
        opt['attrs']['data-hbgt_complet'] = opt['label']['hbgt_complet']
        opt['label'] = mark_safe(hidden + opt['label']['label'])
        return opt
    
class SemainesField(forms.ModelMultipleChoiceField):
    widget = SemainesWidget

    def __init__(self, locked=None, **kwds):
        super().__init__(queryset=Semaine.objects.open(), **kwds)
        self._locked = locked

    def label_from_instance(self, obj):
        return {
            'label': str(obj),
            'off': self._locked and obj in self._locked,
            'formule_complet': ','.join(str(h.pk) for h in obj.formule_complet.iterator()),
            'hbgt_complet': ','.join(str(h.pk) for h in obj.hbgt_complet.iterator()),
            }

### Formules

class FormuleWidget(forms.widgets.RadioSelect):
    class Media:
        js = ('js/inscription.js',)
            
    def create_option(self, *args, **kwds):
        opt = super().create_option(*args, **kwds)
        opt['attrs'].update(opt['label']['attrs'])
        opt['label'] = opt['label']['label']
        return opt

    def id_for_label(self, *args, **kwds):
        return ''
    
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
        if obj.affiche_chambre:
            attrs['data-chambre'] = '1'
        if obj.needs_assurance:
            attrs['data-assurance'] = '1'
        for field, (val, _) in obj.costs(1):
            attrs['data-%s' % field.name] = val

        return {
            'label': format_html(
    '''{nom} <span class="prix">{prix}</span> <span class="description">{weekend}{description}</span>''',
                nom=force_str(obj.nom),
                prix=format_html('({}€)', strip_cents(obj.prix)) * obj.publique,
                weekend=format_html('(<strong>+{}€</strong>/week-end si semaines consécutives) <br>', strip_cents(obj.weekend)) if obj.weekend > 0 else '',
                description=force_str(obj.description)),
            'attrs': attrs,
            }

### Transport

class TransportWidget(forms.widgets.Select):
    class Media:
        js = ('js/inscription.js',)
            
    def create_option(self, name, value, *args, **kwds):
        opt = super().create_option(name, value, *args, **kwds)
        if (isinstance(value, ModelChoiceIteratorValue)):
            opt['attrs']['data-formules'] = " ".join(str(f.pk) for f in value.instance.formules.all())
            opt['attrs']['disabled'] = True
        else:
            opt['attrs']['class'] = 'default'
        return opt

### Reversible

class ReversibleWidget(forms.widgets.Select):
    class Media:
        js = ('js/inscription.js',)
            
    def create_option(self, *args, **kwds):
        opt = super().create_option(*args, **kwds)
        opt['attrs'].update(opt['label']['attrs'])
        opt['label'] = opt['label']['label']
        return opt        
    
class ReversibleField(forms.ModelChoiceField):
    widget = ReversibleWidget

    def __init__(self, *args, **kwds):
        super().__init__(queryset=Reversible.objects.all(), *args, **kwds)
        self.empty_label = { 'label' : self.empty_label, 'attrs' : {
            'data-min' : 0,
            'data-max' : 0
            } }
    
    def label_from_instance(self, obj):
        return { 'label': str(obj), 'attrs': {
            'data-min' : obj.min_stature or 0,
            'data-max' : obj.max_stature or 300,
            }}

    @property
    def help_text(self):
        if self._help_text:
            return self._help_text
        else:
            return '<a>voir la grille des tailles</a>' + self.queryset.table()

    @help_text.setter
    def help_text(self, v):
        self._help_text = v
        
### Date Picker

class DatePicker(forms.widgets.DateInput):
    class Media:
        css = { 'all' : ('css/jquery-ui.min.css',) }
        js = ('js/jquery-ui.min.js',
              'js/datepicker.js')

    def __init__(self, *args, **kwds):
        super(DatePicker, self).__init__(*args, **kwds)
        if self.attrs.get('class') is None:
            self.attrs['class'] = 'datepicker'
        else:
            self.attrs['class'] += ' datepicker'


### Files

class FileInput(forms.widgets.FileInput):
    class Media:
        js = ('js/uploads.js',)
            
    template = '''
<span class="fileinput {klass}">
  <label>
    {input}
    <span class="pure-button" title="{command} fichier">{command}…</span>
  </label>
  <span class="filename">
    <span class="uploading">{msg}</span>
    <a href="{url}" target="_blank" title="télécharger {text}">{text_s}</a>
  </span>
</span>
'''

    def render(self, name, value, attrs=None, **kwds):
        t = value.name and value.name.split('/')[-1] or ''
        trunc = lambda x,l: x[:l] + '…' * (len(x) > l)
        attrs = attrs or {}
        attrs['style'] = 'display:none'
        return format_html(self.template,
            klass   = bool(value.name) * 'has-file',
            command = 'Changer' if value.name else 'Choisir',
            input   = super(FileInput, self).render(name, value, attrs),
            msg     = 'Pas de fichier sélectionné' * (not value.name),
            url     = value.url or '',
            text    = t,
            text_s  = t and trunc(t, 30),
        )

### Yes/No/specify widget

class YesNoSpecify(forms.widgets.TextInput):
    class Media:
        js = ('js/jquery-ui.min.js',
              'js/yesnospecify.js',)
        css = { 'all' : ('css/jquery-ui.min.css',
                         'css/yesnospecify.css',)}

    template_name = "widgets/yesnospecify.html"

    def format_value(self, value):
        if value == "" or value is None:
            return value
        else:
            return super().format_value(value)

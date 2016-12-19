# -:- encoding: utf-8

from django.utils.html import format_html
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django import forms
from django.utils.encoding import force_text
from .templatetags.decimal import strip_cents
from .models import Semaine

# Mixins and abstract classes for ChoiceInputs that hold a pointer
# `choice_obj` to the model object.

class FullModelMixin(object):
    def __init__(self, name, value, attrs, choice, index):
        self.choice_obj = choice[1]
        super().__init__(name, value, attrs, choice, index)
class FullModelRadioChoiceInput(FullModelMixin, forms.widgets.RadioChoiceInput):
    pass
class FullModelCheckboxChoiceInput(FullModelMixin, forms.widgets.CheckboxChoiceInput):
    pass

### Formule widget

class FormuleChoiceInput(FullModelRadioChoiceInput):
    def render(self):
        if self.choice_obj.affiche_accompagnateur:
            self.attrs['data-accompagnateur'] = '1'
        if self.choice_obj.affiche_train:
            self.attrs['data-train'] = '1'
        if self.choice_obj.affiche_chambre:
            self.attrs['data-chambre'] = '1'
        if self.choice_obj.affiche_navette:
            self.attrs['data-navette'] = '1'
        if self.choice_obj.affiche_assurance:
            self.attrs['data-assurance'] = '1'
        if self.choice_obj.affiche_mode:
            self.attrs['data-mode'] = '1'
        self.attrs['data-hebergements'] = ','.join(str(h.pk) for h in self.choice_obj.hebergements.iterator())
        for field, (val, _, _) in self.choice_obj.costs().items():
            self.attrs['data-%s' % field.name] = val
        return format_html('''<label>{input} {nom}
<span class="prix">{prix}</span>
<span class="description">{description}</span></label>''',
                           input=self.tag(),
                           nom=force_text(self.choice_obj.nom),
                           prix=format_html('({}€)', strip_cents(self.choice_obj.prix)) * self.choice_obj.publique,
                           description=force_text(self.choice_obj.description))

class FormuleRenderer(forms.widgets.ChoiceFieldRenderer):
    choice_input_class = FormuleChoiceInput

    def render(self):
        id_ = self.attrs.get('id', None)
        start_tag = format_html('<ul id="{0}">', id_) if id_ else '<ul>'
        output = [start_tag]
        prev_group = ''
        for i, choice in enumerate(self.choices):
            group = choice[1].groupe
            if group:
                if prev_group:
                    output.append('</ul></li>')
                prev_group = group
                output.append(format_html('<li><div class="group">{0}</div><ul>', group))
            w = self.choice_input_class(self.name, self.value,
                                        self.attrs.copy(), choice, i)
            output.append(format_html('<li>{0}</li>', force_text(w)))
        if prev_group:
            output.append('</ul>')
        output.append('</ul>')
        return mark_safe('\n'.join(output))


class FormuleWidget(forms.widgets.RadioSelect):
    renderer = FormuleRenderer
    
    class Media:
        js = ('//code.jquery.com/jquery-1.11.0.min.js', 
              'js/inscription.js')

    def id_for_label(self, _id):
        return None


### Hebergement widget

class HebergementChoiceInput(FullModelRadioChoiceInput):
    def render(self):
        return format_html('''<label>{input} {nom} {commentaire}</label>''',
                           input=self.tag(),
                           nom=force_text(self.choice_obj.nom),
                           commentaire=self.choice_obj.md_commentaire())

class HebergementRenderer(forms.widgets.ChoiceFieldRenderer):
    choice_input_class = HebergementChoiceInput

class HebergementWidget(forms.widgets.RadioSelect):
    renderer = HebergementRenderer

    def id_for_label(self, _id):
        return None


### Semaines widget

class SemaineChoiceInput(FullModelCheckboxChoiceInput):
    def render(self):
        self.attrs['data-complet'] = ','.join(str(h.pk)
                                                  for h in self.choice_obj.complet.iterator())
        return super().render()

class SemaineRenderer(forms.widgets.ChoiceFieldRenderer):
    choice_input_class = SemaineChoiceInput

class SemaineWidget(forms.widgets.CheckboxSelectMultiple):
    renderer = SemaineRenderer

    class Media:
        js = ('//code.jquery.com/jquery-1.11.0.min.js', 
              'js/inscription.js')

    def id_for_label(self, _id):
        return None

### Fields carrying a pointer to their model object

class SemainesField(forms.ModelMultipleChoiceField):
    widget = SemaineWidget

    def __init__(self, *args, **kwds):
        super().__init__(queryset=Semaine.objects.open(), *args, **kwds)

    def label_from_instance(self, obj):
        return obj

class FullModelField(forms.ModelChoiceField):
    widget = None

    def __init__(self, *args, **kwds):
        super(FullModelField, self).__init__(*args, **kwds)
        self.empty_label = None

    def label_from_instance(self, obj):
        return obj


### Date Picker

class DatePicker(forms.widgets.DateInput):
    class Media:
        css = { 'all' : ('css/jquery-ui.min.css',) }
        js = ('//code.jquery.com/jquery-1.11.0.min.js', 
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
            'url'   : value.url() or '',
            'text'  : value.name.split('/')[-1] or '',
        }
        return mark_safe(self.template % s)

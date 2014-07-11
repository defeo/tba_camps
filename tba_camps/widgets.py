# -:- encoding: utf-8

from django.utils.html import format_html
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django import forms
from django.utils.encoding import force_text

class FullModelChoiceInput(forms.widgets.ChoiceInput):
    input_type = 'radio'

    def __init__(self, name, value, attrs, choice, index):
        self.name = name
        self.value = value
        self.attrs = attrs
        self.choice_value = force_text(choice[0])
        self.choice_obj = choice[1]
        self.index = index
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        if self.value == self.choice_value:
            self.attrs['checked'] = 'checked'

class FormuleChoiceInput(FullModelChoiceInput):
    def render(self):
        if self.choice_obj.affiche_train:
            self.attrs['data-train'] = '1'
        if self.choice_obj.affiche_hebergement:
            self.attrs['data-hebergement'] = '1'
        self.attrs['data-prix'] = self.choice_obj.prix
        self.attrs['data-cotisation'] = self.choice_obj.cotisation
        self.attrs['data-taxe'] = self.choice_obj.taxe
        return format_html(u'''<label>
<input type="radio" name="{name}" value="{value}"{attrs}/> {nom}
<span class="prix">({prix}€)</span>
<span class="description">{description}</span></label>''',
                           name=self.name,
                           value=self.choice_value,
                           attrs=flatatt(self.attrs),
                           nom=force_text(self.choice_obj.nom),
                           prix=self.choice_obj.prix,
                           description=force_text(self.choice_obj.description))

### Formule widget

class FormuleRenderer(forms.widgets.ChoiceFieldRenderer):
    choice_input_class = FormuleChoiceInput

class FormuleWidget(forms.widgets.RendererMixin, forms.Select):
    renderer = FormuleRenderer
    
    class Media:
        js = ('//code.jquery.com/jquery-1.11.0.min.js', 
              'js/inscription.js')

    def id_for_label(self, _id):
        return _id


### Hebergement widget

class HebergementChoiceInput(FullModelChoiceInput):
    def render(self):
        return format_html(u'''<label>
<input type="radio" name="{name}" value="{value}"{attrs}/> {nom}
{commentaire}</label>''',
                           name=self.name,
                           value=self.choice_value,
                           attrs=flatatt(self.attrs),
                           nom=force_text(self.choice_obj.nom),
                           commentaire=mark_safe(self.choice_obj.commentaire.rendered))

class HebergementRenderer(forms.widgets.ChoiceFieldRenderer):
    choice_input_class = HebergementChoiceInput

class HebergementWidget(forms.widgets.RendererMixin, forms.Select):
    renderer = HebergementRenderer

    def id_for_label(self, _id):
        return _id


### Field

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

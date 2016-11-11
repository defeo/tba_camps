# -:- encoding: utf-8

from django.utils.html import format_html
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django import forms
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse
from .templatetags.decimal import strip_cents

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
        if self.choice_obj.affiche_accompagnateur:
            self.attrs['data-accompagnateur'] = '1'
        if self.choice_obj.affiche_train:
            self.attrs['data-train'] = '1'
        if self.choice_obj.affiche_hebergement:
            self.attrs['data-hebergement'] = '1'
        if self.choice_obj.affiche_chambre:
            self.attrs['data-chambre'] = '1'
        if self.choice_obj.affiche_navette:
            self.attrs['data-navette'] = '1'
        if self.choice_obj.affiche_assurance:
            self.attrs['data-assurance'] = '1'
        if self.choice_obj.affiche_mode:
            self.attrs['data-mode'] = '1'
        for field, (val, _, _) in self.choice_obj.costs().items():
            self.attrs['data-%s' % field.name] = val
        return format_html('''<label>
<input type="radio" name="{name}" value="{value}"{attrs}/> {nom}
<span class="prix">{prix}</span>
<span class="description">{description}</span></label>''',
                           name=self.name,
                           value=self.choice_value,
                           attrs=flatatt(self.attrs),
                           nom=force_text(self.choice_obj.nom),
                           prix=format_html('({}€)', strip_cents(self.choice_obj.prix)) * self.choice_obj.publique,
                           description=force_text(self.choice_obj.description))

### Formule widget

class FormuleRenderer(forms.widgets.ChoiceFieldRenderer):
    choice_input_class = FormuleChoiceInput

    def render(self):
        id_ = self.attrs.get('id', None)
        start_tag = format_html('<ul id="{0}">', id_) if id_ else '<ul>'
        output = [start_tag]
        prev_group = ''
        for i, choice in enumerate(self.choices):
            group = choice[1].groupe
            if group and group != prev_group:
                if prev_group:
                    output.append('</ul></li>')
                prev_group = group
                output.append(format_html('<li><div>{0}</div><ul>', group))
            w = self.choice_input_class(self.name, self.value,
                                        self.attrs.copy(), choice, i)
            output.append(format_html('<li>{0}</li>', force_text(w)))
        if prev_group:
            output.append('</ul>')
        output.append('</ul>')
        return mark_safe('\n'.join(output))


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
        return format_html('''<label>
<input type="radio" name="{name}" value="{value}"{attrs}/> {nom}
{commentaire}</label>''',
                           name=self.name,
                           value=self.choice_value,
                           attrs=flatatt(self.attrs),
                           nom=force_text(self.choice_obj.nom),
                           commentaire=self.choice_obj.md_commentaire())

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

from import_export import resources, fields, widgets
from django_globals import globals
from models import Inscription

class FKeyWidget(widgets.ForeignKeyWidget):
    def __init__(self, model, field='pk', *args, **kwds):
        super(FKeyWidget, self).__init__(model, *args, **kwds)
        self.field = field

    def render(self, value):
        if value is None:
            return ""
        return getattr(value, self.field)

class InscriptionResource(resources.ModelResource):
    lien = fields.Field()

    class Meta:
        model = Inscription
        exclude = ('id', 'slug')
        widgets = {
            'semaines' : { 'field' : 'debut' },
        }
        
    def dehydrate_hebergement(self, inscr):
        if inscr.hebergement is None:
            return ''
        return inscr.hebergement.nom

    def dehydrate_formule(self, inscr):
        if inscr.formule is None:
            return ''
        return inscr.formule.nom

    def dehydrate_lien(self, inscr):
        req = globals.request
        return req.build_absolute_uri(inscr.get_absolute_url())

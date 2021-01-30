from django.forms import Media

class SimpleModelFormset:
    def __init__(self, queryset, modelform_class, extra=0, prefix=''):
        self.forms = []
        self.queryset = queryset
        for o in queryset.iterator():
            self.forms.append(modelform_class(instance=o, prefix=prefix + str(o.pk)))
        for i in range(extra):
            self.forms.append(modelform_class(prefix=prefix))

    @property
    def media(self):
        if self.forms:
            return self.forms[0].media
        else:
            return Media()

    def __iter__(self):
        return iter(self.forms)
    
    def __len__(self):
        return len(self.forms)

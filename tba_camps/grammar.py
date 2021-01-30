def count(model, n):
    if n == 0:
        return "pas de %s" % model._meta.verbose_name_plural
    elif n == 1:
        return "1 %s" % model._meta.verbose_name
    else:
        return "%d %s" % (n, model._meta.verbose_name_plural)

def inflect(word, masculine=True, singular=True):
    return word + 'e' * (not masculine) + 's' * (not singular)

def determinate(word, masculine=True, singular=True):
    return (('le ' if masculine else 'la ') if singular else 'les ') + word

def indeterminate(word, masculine=True, singular=True):
    return (('un ' if masculine else 'une ') if singular else 'des ') + word

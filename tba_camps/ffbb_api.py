from django.http import JsonResponse, HttpResponseBadRequest
from urllib.request import urlopen
from urllib.parse import urlencode
import re, json

SEARCH_FORM = 'http://www.ffbb.com/jouer/recherche-avancee'
SEARCH_SERVICE = 'http://www.ffbb.com/system/ajax'

CSRF_REGEX = re.compile(rb'<input type="hidden" name="form_build_id" value="(.+)" />\s<input type="hidden" name="form_id" value="ffbb_prototype_ws_simple_form" />')
LICENSE_LIST = re.compile(r'<tr.*?>(.*?)</tr>', re.DOTALL)
LICENSE_FIELDS = re.compile(r'<td><div class="(\w+)">(?:<\w+.*?>)*(.*?)(?:</\w+>)+?</td>')

def _parse(data):
    try:
        html = next(d for d in data if d['command'] == 'insert')['data']
    except KeyError:
        raise ValueError('Cannot parse data')

    if html == '<h1 class="title">Aucun Résultat trouvé</h1>':
        raise ValueError('No results')

    match = LICENSE_LIST.finditer(html)

    licenses = []
    for l in match:
        fields = LICENSE_FIELDS.finditer(l.group(1))
        licenses.append({f.group(1): f.group(2) for f in fields})
    return licenses

def licence(req):
    if not (req.method == 'GET'
                and 'nom' in req.GET
                and 'prenom' in req.GET
                and 'sexe' in req.GET):
        return HttpResponseBadRequest()
    
    with urlopen(SEARCH_FORM) as form:
        match = CSRF_REGEX.search(form.read())
        if not match:
            return HttpResponseBadRequest('Cannot parse ffbb.com')
        token = match.group(1).decode()
        data = {
            'numLicence' : '',
            'id_license' : '',
            'nom' : req.GET['nom'],
            'prenom' : req.GET['prenom'],
            'sexe' : req.GET['sexe'],
            'dtNais[date]': req.GET.get('naissance') or '',
            'lbOrg' : '',
            'form_build_id' : token,
            'form_id' : 'ffbb_prototype_ws_simple_form',
        }

        with urlopen(SEARCH_SERVICE, urlencode(data).encode()) as results:
            try:
                licenses = _parse(json.loads(results.read().decode()))
            except ValueError as e:
                return HttpResponseBadRequest(e)
            return JsonResponse({ 'licenses': licenses })
    return HttpResponseBadRequest('Cannot connect to ffbb.com')

from django.conf.urls import url
urls = [url('^$', licence)]

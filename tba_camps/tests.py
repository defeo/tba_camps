from django.test import TestCase, Client
from django.core import mail
from django.contrib.auth.models import User
import json
from .models import Inscription, Formule, Semaine, Hebergement, VALID, PREINSCRIPTION
from .views import InscriptionForm
from decimal import Decimal

class BasicTests(TestCase):
    fixtures = ['formules.json', 'hebergements.json', 'semaines.json']
    
    def setUp(self):
        inscr = Inscription.objects.create(nom='AaA',
                                               prenom='aaa-bbb',
                                               email='email@example.com',
                                               tel='0123456789',
                                               naissance='2000-01-01',
                                               formule=Formule.objects.get(pk=1))
        self.slug = inscr.slug
        inscr.semaines.add(Semaine.objects.get(pk=4))
        inscr.save()
        u = User.objects.create_user('toto', 'toto@toto.to', 'toto')
        u.is_staff = True
        u.save()
        
    def test_static(self):
        import os
        pages = (['cherche.htm', 'date.htm', 'inscriptions.htm',
                  'inscriptions.htm/%s/' % self.slug]
                 + [f[:-1] for f in os.listdir('tba_camps/templates/tba/')])
        assert self.client.get('/tba/').status_code == 200
        for p in pages:
            assert self.client.get('/tba/%s' % p).status_code == 200

    def test_cherche(self):
        response = self.client.post('/tba/cherche.htm', follow=True,
                                    data={'email': 'email@example.com'})
        self.assertContains(response, 'Aaa-Bbb AAA, un mail de rappel')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'email@example.com')

    def test_sms(self):
        response = self.client.post('/sms/json', data={ 'semaines': 4, 'formules': [1] })
        assert response.status_code == 403
        self.client.login(username='toto', password='toto')
        response = self.client.post('/sms/json', data={ 'semaines': 4, 'formules': [1] })
        self.assertEqual(response.json(), {
            'semaine': 1,
            'formules': ['F1 Externe plein temps'],
            'nums': ['0123456789']
        })


    def test_form(self):
        response = self.client.get('/tba/inscriptions.htm')
        self.assertEqual(response.status_code, 200)
        
    def test_inscr(self):
        response = self.client.post('/tba/inscriptions.htm', data={
            'nom' : 'nom', 'prenom' : 'prenom',
            'semaines' : ['4','5'],
            'email' : 'email@email.org', 'email2' : 'email@email.org',
            'formule' : '1',
            'licencie' : 'O', 'taille' : '100', 'adresse' : 'addresse',
            'cp' : 'cp', 'ville' : 'ville', 'pays' : 'pays', 'tel' : '010101010101',
            'naissance' : '01/01/2011', 'lieu' : 'lieu', 'sexe' : 'H',
            'licence' : '10101001', 'club' : 'club', 'venu' : 'O',
            'train' : '0.000', 'navette_a' : '0.00',
            'navette_r' : '0.00', 'assurance' : '0.00',
            'caf' : 'N',
            })
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prenom NOM')
        inscr = Inscription.objects.get(nom='NOM')
        self.assertTrue(inscr.certificat_snail)
        self.assertFalse(inscr.fiche_hotel_snail)
        self.assertFalse(inscr.fiche_inscr_snail)
        self.assertFalse(inscr.fiche_sanit_snail)
        self.assertEqual(inscr.etat, PREINSCRIPTION)
        assert Semaine.objects.get(pk=4) in inscr.semaines.all()

    def test_export(self):
        self.client.login(username='toto', password='toto')
        response = self.client.post('/admin/tba_camps/inscription/export/',
                                        data={ 'file_format': '1' })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], "application/vnd.ms-excel")

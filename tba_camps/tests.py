from django.test import TestCase, Client
from django.core import mail
from django.contrib.auth.models import User
import json
from .models import Inscription, Formule, Semaine, Hebergement, VALID

class BasicTests(TestCase):
    fixtures = ['formules.json', 'hebergements.json', 'semaines.json']
    
    @classmethod
    def setUpTestData(cls):
        inscr = Inscription.objects.create(nom='AAA',
                                               prenom='aaa',
                                               email='email@example.com',
                                               tel='0123456789',
                                               naissance='2000-01-01',
                                               formule=Formule.objects.get(pk=1),
                                               slug='A'*22)
        inscr.semaines.add(Semaine.objects.get(pk=4))
        User.objects.create_user('toto', 'toto@toto.to', 'toto')
        
    def test_static(self):
        import os
        pages = (['cherche.htm', 'date.htm', 'inscriptions.htm',
                  'inscriptions.htm/%s/' % ('A'*22)]
                 + [f[:-1] for f in os.listdir('tba_camps/templates/tba/')])
        assert self.client.get('/tba/').status_code == 200
        for p in pages:
            assert self.client.get('/tba/%s' % p).status_code == 200

    def test_cherche(self):
        response = self.client.post('/tba/cherche.htm', follow=True,
                                    data={'email': 'email@example.com'})
        self.assertContains(response, 'aaa AAA, un mail de rappel')
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

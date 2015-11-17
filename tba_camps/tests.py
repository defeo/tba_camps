from django.test import TestCase, Client
from django.core import mail
from models import Inscription, Formule, Semaine, Hebergement, VALID

class BasicTests(TestCase):
    fixtures = ['formules.json', 'hebergements.json', 'semaines.json']
    
    @classmethod
    def setUpTestData(cls):
        Inscription.objects.create(nom='AAA',
                                   prenom='aaa',
                                   email='email@example.com',
                                   naissance='2000-01-01',
                                   formule=Formule.objects.get(pk=1),
                                   slug='A'*22)
        
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


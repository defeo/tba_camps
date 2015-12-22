from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from tba_camps.models import Inscription

class Command(BaseCommand):
    help = '(Backup data) and clean Inscriptions model.'

    def add_arguments(self, parser):
        parser.add_argument('--no-backup', action='store_true',
                            help='Do not call the inscriptions_backup command before cleaning.')

    def handle(self, **opts):
        if not opts['no_backup']:
            call_command('inscriptions_backup', uploads=True)
            
        self.stdout.write('Cleaning Inscriptions... ', ending='')
        entries, _ = Inscription.objects.all().delete()
        self.stdout.write('done, removed %d entries!' % entries)
        

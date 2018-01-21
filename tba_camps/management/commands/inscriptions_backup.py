from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
import tarfile, io
from datetime import datetime
from tba_camps.models import Dossier, Stagiaire, Semaine, Hebergement, Formule
from django.conf import settings

_models = [Dossier, Stagiaire, Semaine, Hebergement, Formule]

class Command(BaseCommand):
    help = 'Backup model data (and uploads directory) in a tar file.'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--uploads', action='store_true',
                            help='Add uploads directory in tarfile.')
        for model in _models:
            parser.add_argument('--no-%s' % model.__name__.lower(),
                                action='store_true', dest=model.__name__,
                                help='Do not include %s model in tarfile.' % model.__name__)
        parser.add_argument('filename', nargs='?',
                            default='%s-backup' % datetime.now().date())

    def handle(self, **opts):
        if opts['filename'][-7:] == '.tar.gz' or opts['filename'][-4:] == '.tgz':
            compression = 'gz'
        else:
            compression = 'bz2'
            if opts['filename'][-8:] != '.tar.bz2':
                opts['filename'] += '.tar.bz2'

        def serialize(serializer, model, tar):
            serializer.serialize(model.objects.all())
            tarinfo = tarfile.TarInfo('%s-%s.json' %
                                      (datetime.now().date(), model.__name__.lower()))
            data = serializer.stream.getvalue()
            tarinfo.size = len(data)
            tar.addfile(tarinfo, io.BytesIO(data.encode()))
        
        self.stdout.write('Saving models... ', ending='')
        with tarfile.open(opts['filename'], 'w:%s' % compression) as out:
            serial = serializers.get_serializer('json')()
            for model in _models:
                if not opts[model.__name__]:
                    serialize(serial, model, out)
            self.stdout.write('done!')
            if opts['uploads']:
                self.stdout.write('Compressing uploads... ', ending='')
                out.add(settings.MEDIA_ROOT)
                self.stdout.write('done!')

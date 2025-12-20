# Même si ce fichier est un script exécutable, il vaut mieux exécuter
# manuellement les lignes. Commenter la ligne ci-dessous pour exécuter
# en tant que script shell.
exit

########## CONFIGURATION DE L'ENVIRONNEMENT PYTHON

# On commence par installer quelques dépendences
apt-get install git python3 python3-venv python3-pip python3-dev libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 shared-mime-info libpq-dev libmariadb-dev libffi-dev 

# On crée un utilisateur de système pour faire tourner le serveur sans
# privilèges, et on se place dans son home
adduser --system tba
cd ~tba

# On télécharge les sources du site.  Il faut avoir accès au repo
# (privé) sur github.  Si vous lisez ce fichier, normalement vous
# savez déjà comment y avoir accès. Sinon, me demander.
git clone git@github.com:defeo/tba_camps.git

# On entre dans le dossier, on installe un environnement virtuel
# python, et les dépendances du projet
cd tba_camps
python3 -m venv ve
. ve/bin/activate
pip install -r requirements.txt

########## CONFIGURATION DE LA BASE MYSQL

# Le projet marche aussi bien avec Postgres, mais par défaut on va
# configurer MySQL.
apt-get install mariadb-server

# On crée la base de données pour le projet. Dans un hébergement
# partagé, il est probablement plus approprié de créer un utilisateur
# mysql, et de lui donner accès à cette base.
mysqladmin -p create tba

# Ce paramètre va permettre à Django de se connecter à la base de
# données. Il faut définir ce paramètre à chaque nouvelle session où
# on a besoin de lancer des commandes par manage.py.
#
# Remplacer root et PASSWORD par l'utilisateur et le mot de passe
# MySQL.
export DATABASE_URL=mysql://root:PASSWORD@localhost/tba

# D'autre paramètres pour Django, nécessaires pour manage.py
export DJANGO_SETTINGS_MODULE=tba_camps.settings_deploy
# Celui-ci n'est pas important pour le moment
export HOST_NAME=

# On crée les tables dans la base de données. Cette commande va
# demander de créer l'administrateur du site Django. Accepter et créer
# l'administrateur.
./manage.py migrate

# On charge des données par défaut dans les tables
./manage.py loaddata tba_camps/fixtures/*json

########## PRÉPARATION DU SERVEUR DJANGO

# Le serveur Django va tourner en local sur le port 8001 (configuré
# dans gunicorn_start) sous le user tba (configuré dans
# supervisor_tba_camps.conf)

# On copie les fichiers statiques dans leur emplacement définitif
./manage.py collectstatic

# On donne les droits en écriture dans le dossier uploads au serveur
chown tba:nogroup uploads

# Ouvrir le ficheir gunicorn_start et configurer la base de données et
# l'adresse du site comme indiqué dans le fichier.
edit gunicorn_start

# On va utiliser supervisord <http://supervisord.org/> pour lancer
# automatiquement le serveur. D'autres superviseurs seraient aussi
# possibles, comme indiqué ici:
# <http://gunicorn-docs.readthedocs.org/en/latest/deploy.html>
apt-get install supervisor

# Ouvrir le ficher et renseigner les chemins, comme indiqué dans le
# fichier.
edit supervisor_tba_camps.conf

# Copier le fichier là où supervisord peut le lire, et lancer le
# serveur
cp supervisor_tba_camps.conf /etc/supervisor/conf.d/tba_camps.conf
supervisorctl reread
supervisorctl update

# Lancer cette commande et vérifier que le serveur fonctionne bien
supervisorctl status tba_camps


########## PRÉPARATION DU PROXY NGINX

# Le serveur Django va être mis derrière un proxy nginx. On pourrait
# aussi utiliser Apache à la place, mais nginx est un choix
# classique. Nginx va aussi s'occuper de servir les fichiers statiques
# dans le dossier static/

apt-get install nginx-light

# Ouvrir ce fichier et éditer les chemins comme indiqué
edit nginx_tba_camps.conf

# Copier la configuration et lancer le serveur
cp nginx_tba_camps.conf /etc/nginx/sites-available/tba_camps.conf
ln -s /etc/nginx/sites-available/tba_camps.conf /etc/nginx/sites-enabled/
service nginx restart


########## CONFIGURATION DU MAIL SORTANT

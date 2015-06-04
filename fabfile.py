from fabric.api import *
from fabric.decorators import *
#from environment import env

env.hosts = ['social@roma.dennytwix.com']
env.port = '27678'
client = 'social'

@task
def deploy():
    local('git push')

    with cd('/home/social/social-server'):
        with prefix('source /home/social/social-server/.env/bin/activate'):
            run('./ctl stop')
            run('git pull')
            run('alembic upgrade head')
            # run('python manage.py db_upgrade')
            run('./ctl start')

@task
def getdb():
    run('pg_dump social > /tmp/social.sql')
    get('/tmp/social.sql', '/tmp/social.sql')
    run('rm /tmp/social.sql')

@task
def updatedb():
    local('dropdb social')
    local('createdb social')
    local('psql social < /tmp/social.sql')
    local('rm /tmp/social.sql')


@task
def syncdb():
    getdb()
    updatedb()
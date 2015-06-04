from fabric.api import *
from fabric.decorators import *
#from environment import env

env.hosts = ['45.55.197.87']
env.port = '27678'
client = 'hawkist'

@task
def deploy():
    local('git push')

    with cd('/home/hawkist/hawkist'):
        with prefix('source /home/hawkist/hawkist/.env/bin/activate'):
            run('./ctl stop')
            run('git pull')
            run('alembic upgrade head')
            # run('python manage.py db_upgrade')
            run('./ctl start')

@task
def getdb():
    run('pg_dump social > /tmp/hawkist.sql')
    get('/tmp/hawkist.sql', '/tmp/hawkist.sql')
    run('rm /tmp/social.sql')

@task
def updatedb():
    local('dropdb hawkist')
    local('createdb hawkist')
    local('psql hawkist < /tmp/hawkist.sql')
    local('rm /tmp/hawkist.sql')


@task
def syncdb():
    getdb()
    updatedb()
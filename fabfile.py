"""
To see the list of available commands use:
    fab --list

"""

from fabric.api import env
from fabric.api import cd, run, execute, task
from fabric.contrib.files import exists
from fabric.operations import sudo
from fabric.contrib.project import rsync_project
from fabtools import require
from os import path

env.hosts = ['linkchecker2']
env.user = 'ubuntu'
BASE_PATH = '/home/ubuntu/apps'

env.use_ssh_config = True
env.ssh_config_path = './ssh_config'

APP_PATH = BASE_PATH + '/linkchecker'

LOGS_PATH = path.join(APP_PATH, 'logs')

SCRAPYD_PATH = path.join(APP_PATH, 'scrapyd_service')


@task
def setup():
    """Setup all server dependencies so that crawler can run"""

    if not exists(APP_PATH):
        run('mkdir -p %s' % APP_PATH)

    execute(copy_to_server)

    sudo('apt-get update')

    sudo('apt-get install python-setuptools python-mysqldb libmysqlclient-dev')
    sudo(
        'apt-get install python-dev libxml2-dev libxslt-dev lib32z1-dev libffi-dev supervisor zip')
    sudo('easy_install pip')

    execute(install_requirements)

    run('mkdir -p %s' % LOGS_PATH)


@task
def install_requirements():
    """Install specific python libraries used by the crawler"""

    with cd(APP_PATH):
        with cd('install'):
            sudo('pip install -r requirements.txt')


@task(alias='cs')
def copy_to_server():
    """Sync files from local to server"""

    exclude = (
    '.project', '.pydevproject', '.settings/*', '*.pyc', '.scrapy/', 'crawl_prod.sh', 'test.py',
    '.idea', '.git', '*.sqlite', 'build', '*egg*', 'dbs', 'logs', 'items', 'twistd.pid',
    'scrapyd.log',
    'test/*', '*.pem', 'data/*', '*.zip')

    rsync_project(remote_dir=APP_PATH, local_dir='./', exclude=exclude,
                  delete=False, extra_opts='')

    run('mkdir -p %s' % LOGS_PATH)

    sudo('chown -R ubuntu:ubuntu %s' % APP_PATH)

    execute(deploy_scrapy_config)


@task
def supervisor_setup():
    """Setup supervisor which is used to run scrapyd"""

    require.supervisor.process('linkchecker_scrapyd',
                               command='scrapyd',
                               directory=SCRAPYD_PATH,
                               user='root',
                               stdout_logfile=path.join(LOGS_PATH, 'linkchecker_scrapyd.log')
                               )


@task
def deploy_scrapy_config():
    """Make sure that on server we have the set the prod settings"""

    with cd(APP_PATH):
        run("sed -i 's/local/prod/g' scrapy.cfg")
        run("sed -i 's/local/prod/g' setup.py")


@task(alias='d')
def deploy():
    """Most important: perform:copy_to_server, deploy_scrapy_config, scrapyd_deploy and schedule  """

    execute(copy_to_server)
    execute(scrapyd_deploy)
    execute(schedule)


@task(alias='s')
def schedule():
    """Schedule the spider based on spider_id set in ./schedule file"""

    with cd(APP_PATH):
        run('./schedule')


@task(alias='sd')
def scrapyd_deploy():
    """Deploy spider to scrapyd(in case that you made any changes)"""

    with cd(APP_PATH):
        run('./deploy')


@task(alias='sr')
def scrapyd_restart():
    """Restart scrapyd service"""

    sudo('supervisorctl restart linkchecker_scrapyd')

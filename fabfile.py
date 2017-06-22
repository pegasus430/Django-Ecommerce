from fabric.api import env, task
from fabscripts.tasks import django, server

from os import path


#####################
### Host Settings ###
#####################
env.domain = 'mushroom.cooking'
env.ssl_email = 'sascha.dobblaere@gmail.com'
env.rolefs = {
	'web': ['host1', 'host2'],
	'mail': ['mailhost2'],
	'feature':[],
}
env.extra_packages = {
	'web': [],
	'mail': [],
	'feature':[],
}
env.user = 'someuser'
env.user_home = '/home/' + env.user + '/'
env.sudo_group = 'admin'
env.user_key_file = '/Users/sascha/.ssh/id_rsa.pub'


##############################
## Django related settings ### 
##############################
env.app_name = 'djangoapp'
env.django_dir = 'django_test'
env.requirements_file = 'requirements.txt'
env.setup_huey = False

env.venv_path =  'venv'
env.user_home = path.join('/home/', env.user) + '/'
env.venv_full_path = path.join(env.user_home, env.venv_path)

env.git_repo = 'git@bitbucket.org:somuser/somerepo.git'
env.git_branch_prod = 'master'
env.git_branch_staging = 'staging'
env.git_branch_dev = 'dev'
env.requirements_path = path.join(env.django_dir, 'requirements.txt')

env.db_type = 'postgresql' ## 'mysql' or 'postgresql'

env.db = 'db_name'
env.db_user = 'db_user'
env.db_passwd = 'db_pass'
env.db_root_password = 'test'

#############################
## Bitbucket  settings ### 
#############################
env.bitbucket = {
	'username': '',  ## Bitbucket username
	'password': '',  ## Bitbucket pass
	'repo_slug': '',  ## Bitbucket repo slug
	'repo_owner': None, ## Team name of the repo - name or None
}


#############################
## DigitalOcean  settings ### 
#############################
env.digitalocean_api_key = ''


#######################
### MkDocs settings ###
#######################
env.mkdocs_dir = path.join(env.user_home, env.django_dir, 'docs')


########################
### General settings ###
########################
env.colorize_errors = True
env.templates_dir = 'fab_templates'
env.dhparam_strength = 2048
env.nginx = {
	'user': '',
	'passwd': '', ## 8 char max
}

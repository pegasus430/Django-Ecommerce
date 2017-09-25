from fabric.api import env, task
from fabscripts.tasks import django, server

from os import path


#####################
### Host Settings ###
#####################
env.domain = 'sila.network'
env.ssl_email = 'sascha.dobblaere@gmail.com'
env.roledefs = {
	'web': [
            'www.sila.network',
            'dev.sila.network',
        ],
	'mail': [],
	'feature':[],
}
env.extra_packages = {
	'web': [],
	'mail': [],
	'feature':[],
}
env.user = 'sila'
env.user_home = '/home/' + env.user + '/'
env.sudo_group = 'admin'
env.user_key_file = '/Users/sascha/.ssh/id_rsa.pub'


##############################
## Django related settings ### 
##############################
env.app_name = 'Sila'
env.django_dir = 'sila'
env.requirements_file = 'requirements.txt'
env.setup_huey = False

env.venv_path =  'venv'
env.user_home = path.join('/home/', env.user) + '/'
env.venv_full_path = path.join(env.user_home, env.venv_path)

env.git_repo = 'git@bitbucket.org:saschadobbelaere/sila.git'
env.git_branch_prod = 'master'
env.git_branch_staging = 'staging'
env.git_branch_dev = 'dev'
env.requirements_path = path.join(env.django_dir, 'requirements.txt')

env.db_type = 'postgresql' ## 'mysql' or 'postgresql'

env.db = 'db_sila'
env.db_user = 'db_sila'
env.db_passwd = 'dkda!kda0daADwue22'
env.db_root_password = 'akd3ai3j2k20AD'

#############################
## Bitbucket  settings ### 
#############################
env.bitbucket = {
	'username': 'saschadobbelaere',  ## Bitbucket username
	'password': 'Q62v!3LuA',  ## Bitbucket pass
	'repo_slug': 'sila',  ## Bitbucket repo slug
	'repo_owner': None, ## Team name of the repo - name or None
}


#############################
## DigitalOcean  settings ### 
#############################
env.digitalocean_api_key = '8e5ceb3e062f58f6fc7fcb39d58fbfb91dcec960f0ca37e52a3ba23328ee0818'


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
	'user': 'dev',
	'passwd': 'sometest', ## 8 char max
}

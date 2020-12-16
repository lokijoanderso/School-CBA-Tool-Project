import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'team-kyq-rocks-and-cappers-rule'
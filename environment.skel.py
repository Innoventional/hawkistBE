import os

ROOT = os.path.abspath(os.path.dirname(__file__))


env = {
    'debug': True,
    'cookie_secret': '',
    'password_salt': '',
    'daemon': False,
    'listen': '0.0.0.0:8000',
    'logfile': os.path.join(ROOT, 'hawkist.log'),
    'pidfile': os.path.join(ROOT, 'pid'),
    'url_prefix': '',
    'db': 'postgresql://localhost/hawkist',
    'site_url': 'http://localhost:8000/',
    'static_url': 'http://localhost:8000/s/',
    'static_path': os.path.join(ROOT, 'static'),
    'serve_static': False,
    'mail': {
        'from': '',
        'subject': 'Hawkist Password',
        'server': '',
        'login': '',
        'password': ''
    },
}
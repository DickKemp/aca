import os
from flask import Flask
from flask_restx import Api

from werkzeug.middleware.proxy_fix import ProxyFix
from todo import ns as todo_ns

def create_app(test_config=None):
    app = Flask(__name__, static_url_path='', static_folder='static')
    app.wsgi_app = ProxyFix(app.wsgi_app)

    try:
        app.config["TEST_ENV_VARIABLE"] = os.environ['TEST_ENV_VARIABLE']
    except KeyError:
        print('variable not set')

    api = Api(
        etitle='TODO APIs',
        version='1.0',
        description='THese are some APIs for a todo list',
    )
    api.add_namespace(todo_ns)
    api.init_app(app)
    
    return app

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app = create_app()
    app.run(port=port)


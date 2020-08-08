from argparse import ArgumentParser

from dotenv import find_dotenv, load_dotenv
from werkzeug.serving import run_simple

from .app import app


def get_options():
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000)
    parser.add_argument('-b', '--bind', default='127.0.0.1')
    parser.add_argument('--debugger', action='store_true')
    parser.add_argument('--no-reload', dest='reloader', action='store_false')
    return parser.parse_args()


def serve():
    load_dotenv(find_dotenv())
    opts = get_options()
    run_simple(
        opts.bind, opts.port, app,
        use_reloader=opts.reloader, use_debugger=opts.debugger,
    )

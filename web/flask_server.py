import flask
import os

app = flask.Flask(__name__, static_url_path='')

@app.route('/<path>')
@app.route('/<path:subdir>/<path>')
def static_path(path, subdir=None):
    if subdir:
        path = os.path.join(subdir, path)
    return flask.send_from_directory(".", path)

@app.route('/')
def redirect():
    return static_path("index.html")

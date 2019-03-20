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

@app.route('/report_error', methods=["POST"])
def report_error():
    error_data = flask.request.get_json(silent=True)
    if error_data is None:
        print("Received invalid error data info:")
        print(request.data)
    else:
        print(
f"""JavaScript Error:
- message: "{ error_data.get("message") }"
- source: "{ error_data.get("source") }" (line: { error_data.get("line_number") }, char { error_data.get("column_number") })
""")
    return flask.Response("OK", mimetype="text/plain")
    
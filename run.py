from flask import Flask, render_template, Response

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.jinja2')


@app.route("/config.json")
def config():

    with open("config.json", "r") as json_file:
        resp = Response(json_file.read())
        resp.headers['Content-Type'] = 'Application/javascript'
        return resp
import os
import json

from flask import Flask
from flask_socketio import SocketIO
from flask_basicauth import BasicAuth

from reactstub import reactstub

app = Flask(__name__)
basic_auth = BasicAuth(app)

from api import api
from zorg import zorg
from socketapi import connect_socketio

app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(zorg, url_prefix="/zorg")

socketio = SocketIO(app)

if os.path.exists('/etc/config.json'):
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)

    app.config['SECRET_KEY'] = config.get('SECRET_KEY')
    app.config['BASIC_AUTH_USERNAME'] = config.get('BASIC_AUTH_USERNAME')
    app.config['BASIC_AUTH_PASSWORD'] = config.get('BASIC_AUTH_PASSWORD')
else:
    print("Warning, running without a secret")



@app.route("/", methods=['GET'])
@basic_auth.required
def index():
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": None}))


@app.route("/<session_id>", methods=['GET'], strict_slashes=False)
@basic_auth.required
def role_assignment(session_id):
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": session_id, "roleID": None}))


@app.route("/<session_id>/<role_id>", methods=['GET'], strict_slashes=False)
@basic_auth.required
def view(session_id, role_id):
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": session_id, "roleID": role_id}))

connect_socketio(socketio)

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0')

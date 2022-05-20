import os
import json

from flask import Flask
from flask_socketio import SocketIO
from flask_basicauth import BasicAuth

from reactstub import reactstub

from api import api
from socketapi import connect_socketio

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")

socketio = SocketIO(app)

if os.path.exists('/etc/config.json'):
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)

    app.config['SECRET_KEY'] = config.get('SECRET_KEY')
    app.config['BASIC_AUTH_USERNAME'] = config.get('BASIC_AUTH_USERNAME')
    app.config['BASIC_AUTH_PASSWORD'] = config.get('BASIC_AUTH_PASSWORD')
    app.config['BASIC_AUTH_FORCE'] = True
else:
    print("Warning, running without a secret")


back_auth = BasicAuth(app)

@app.route("/", methods=['GET'])
def index():
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": None}))


@app.route("/<session_id>", methods=['GET'], strict_slashes=False)
def role_assignment(session_id):
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": session_id, "roleID": None}))


@app.route("/<session_id>/<role_id>", methods=['GET'], strict_slashes=False)
def view(session_id, role_id):
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": session_id, "roleID": role_id}))

connect_socketio(socketio)

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0')

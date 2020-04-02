import os
import json

from flask import Flask

from reactstub import reactstub

from api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")

if os.path.exists('/etc/config.json'):
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)

    app.config['SECRET_KEY'] = config.get('SECRET_KEY')
else:
    print("Warning, running without a secret")


@app.route("/", methods=['GET'])
def index():
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": None}))


@app.route("/<session_id>", methods=['GET'], strict_slashes=False)
def role_assignment(session_id):
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": session_id, "roleID": None}))


@app.route("/<session_id>/<role_id>", methods=['GET'], strict_slashes=False)
def view(session_id, role_id):
    return reactstub("Shai-Hulud", ["app/css/styles.css", "app/css/slider.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": session_id, "roleID": role_id}))


if __name__ == "__main__":
    app.run(debug=True)

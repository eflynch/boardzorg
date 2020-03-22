import json

from flask import Flask

from reactstub import reactstub

from api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")


@app.route("/<session_id>/<faction>", methods=['GET'])
def view(session_id, faction):
    return reactstub("Shai-Hulud", ["app/css/styles.css"], ["app/main.js"], bootstrap=json.dumps({"sessionID": session_id, "faction": faction}))


if __name__ == "__main__":
    app.run(debug=True)

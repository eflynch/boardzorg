import json

from flask import Flask

from reactstub import reactstub

from api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")


@app.route("/faction/<faction>", methods=['GET'])
def view(faction):
    return reactstub("Shai-Hulud", [], ["app/main.js"], bootstrap=json.dumps({"faction": faction}))


if __name__ == "__main__":
    app.run(debug=True)

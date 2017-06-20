import json

from flask import Flask

from reactstub import reactstub

from api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")


@app.route("/", methods=['GET'])
def view():
    return reactstub("Shai-Hulud", ["app/css/styles.css"], ["app/main.js"], bootstrap=json.dumps({}))


if __name__ == "__main__":
    app.run(debug=True)

import json

from flask import Flask, Blueprint, request, jsonify

from dune import exceptions as de
from dune.session import Session

from reactstub import reactstub
from sessionwrapper import SessionWrapper


session_id = 1


app = Flask(__name__)

api = Blueprint("api", __name__)


@api.route("/sessions", methods=['POST'])
def insert():
    s = Session()
    session_id = SessionWrapper.insert(s)
    return jsonify({"id": session_id})


@api.route("/sessions/<session_id>", methods=['POST'])
def command(session_id):
    command = request.get_json()
    with SessionWrapper(session_id) as session:
        try:
            session.handle_cmd(command["faction"], command["cmd"])
        except de.IllegalAction as e:
            return jsonify({"IllegalAction": str(e)})
        except de.BadCommand as e:
            return jsonify({"BadCommand": str(e)})
        ret = {
            "state": session.get_visible_state(command["faction"]),
            "actions": list(session.get_valid_actions(command["faction"]).keys())
        }
        return jsonify(ret)


@api.route("/sessions/<session_id>", methods=['GET'])
def state(session_id):
    faction = request.args.get("faction")
    with SessionWrapper(session_id) as session:
        print("dude", session)
        ret = {
            "gamestate": session.get_visible_state(faction),
            "actions": list(session.get_valid_actions(faction).keys())
        }
        return jsonify(ret)


app.register_blueprint(api, url_prefix="/api")


@app.route("/faction/<faction>", methods=['GET'])
def view(faction):
    return reactstub("Shai-Hulud", [], ["app/main.js"], bootstrap=json.dumps({"faction": faction}))


if __name__ == "__main__":
    app.run(debug=True)

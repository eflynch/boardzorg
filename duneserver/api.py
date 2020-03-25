from flask import Blueprint, request, jsonify

from dune.exceptions import IllegalAction, BadCommand
from dune.session import Session

from sessionwrapper import SessionWrapper

api = Blueprint("api", __name__)


@api.route("/sessions", methods=['POST'])
def insert():
    s = Session.new_session()
    session_id = SessionWrapper.create(s)
    return jsonify({"id": session_id})


@api.route("/sessions/<session_id>", methods=['POST'])
def command(session_id):
    command = request.get_json()
    print(command)
    with SessionWrapper(session_id) as session:
        try:
            if command["cmd"] == "undo":
                session.undo()
            else:
                session.handle_cmd(command["faction"], command["cmd"])
        except IllegalAction as e:
            return jsonify({"IllegalAction": str(e)}), 400
        except BadCommand as e:
            return jsonify({"BadCommand": str(e)}), 400
        except Exception as e:
            return jsonify({"UnhandledError": str(e)}), 400

        actions = session.get_valid_actions(command["faction"])

        ret = {
            "state": session.get_visible_state(command["faction"]),
            "actions": {a: actions[a].get_arg_spec().to_dict() for a in actions},
            "history": session.get_visible_command_log(command["faction"]) 
        }

        return jsonify(ret)


@api.route("/sessions/<session_id>", methods=['GET'])
def state(session_id):
    faction = request.args.get("faction")
    with SessionWrapper(session_id) as session:
        actions = session.get_valid_actions(faction)
        return jsonify({
            "state": session.get_visible_state(faction),
            "actions": {a: actions[a].get_arg_spec().to_dict() for a in actions},
            "history": session.get_visible_command_log(faction) 
        })

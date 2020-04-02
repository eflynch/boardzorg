from flask import Blueprint, request, jsonify

from dune.exceptions import IllegalAction, BadCommand
from dune.session import Session

from sessionwrapper import SessionWrapper, SessionConflict
import rolewrapper

api = Blueprint("api", __name__)


@api.route("/sessions", methods=['POST'])
def insert():
    session_id = request.get_json()["session_id"]
    SessionWrapper.create(session_id)
    return jsonify({"id": session_id})


@api.errorhandler(IllegalAction)
def handle_illegal_action(error):
    response = jsonify({"IllegalAction": str(error)})
    response.status_code = 400
    return response


@api.errorhandler(BadCommand)
def handle_bad_command(error):
    response = jsonify({"BadCommand": str(error)})
    response.status_code = 400
    return response


@api.errorhandler(SessionConflict)
def handle_session_conflict(error):
    response = jsonify({"SessionConflict": str(error)})
    response.status_code = 400
    return response


@api.errorhandler(rolewrapper.RoleException)
def handle_role_exception(error):
    response = jsonify({"RoleException": str(error)})
    response.status_code = 400
    return response


@api.route("/sessions/<session_id>/roles", methods=['POST'])
def assign_role(session_id):
    pay_load = request.get_json()
    role = pay_load["role"]

    if role not in ('host', 'fremen', 'bene-gesserit', 'guild', 'harkonnen', 'emperor', 'atreides'):
        raise RoleException("{} is not a valid role".format(role))

    with SessionWrapper(session_id) as (session, roles):
        role_id = rolewrapper.assign(roles, role)
        ret = {
            "role": role,
            "role_id": role_id
        }
        return jsonify(ret)


@api.route("/sessions/<session_id>", methods=['POST'])
def command(session_id):
    pay_load = request.get_json()

    role_id = pay_load["role_id"].strip()
    cmd = pay_load["cmd"].strip()

    with SessionWrapper(session_id) as (session, roles):
        role = rolewrapper.look_up(roles, role_id)
        session.handle_cmd(role, cmd)

        actions = session.get_valid_actions(role)

        ret = {
            "role": role,
            "state": session.get_visible_state(role),
            "actions": {a: actions[a].get_arg_spec().to_dict() for a in actions},
            "history": session.get_visible_command_log(role)
        }

        return jsonify(ret)


@api.route("/sessions/<session_id>/roles", methods=['GET'])
def get_assigned_roles(session_id):
    with SessionWrapper(session_id) as (session, roles):
        assigned_roles = list(roles.values())
        return jsonify({
            "assigned_roles": assigned_roles
        })


@api.route("/sessions/<session_id>", methods=['GET'])
def state(session_id):
    role_id = request.args.get("role_id")
    with SessionWrapper(session_id) as (session, roles):
        role = rolewrapper.look_up(roles, role_id)
        actions = session.get_valid_actions(role)
        return jsonify({
            "role": role,
            "state": session.get_visible_state(role),
            "actions": {a: actions[a].get_arg_spec().to_dict() for a in actions},
            "history": session.get_visible_command_log(role)
        })

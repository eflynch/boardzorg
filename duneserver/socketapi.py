from dataclasses import dataclass
from flask_socketio import emit, join_room
from flask import request
from sessionwrapper import SessionWrapper, subscribe, unsubscribe
import rolewrapper


class UnknownSubscriptionType(Exception):
    pass


@dataclass
class _SubscriptionData:
    clients: any
    callback: any
    session_id: str


@dataclass
class _NamespaceInfo:
    name: str
    check_data: any
    serialize: any
    room_for_data: any


def connect_namespace(socketio, namespace_info):
    subs = {}

    @socketio.on('join', namespace=f"/{namespace_info.name}")
    def handle_join(data):
        namespace_info.check_data(data)
        room_id = namespace_info.room_for_data(data)
        session_id = data["session_id"]
        client_id = request.sid

        if session_id in subs:
            subs[room_id].clients.append(client_id)
        else:
            def _on_change(session, roles):
                emit(namespace_info.name,
                     namespace_info.serialize(session, roles, data),
                     room=room_id,
                     namespace=f"/{namespace_info.name}")
            subs[room_id] = _SubscriptionData(
                clients=[client_id],
                callback=_on_change,
                session_id=session_id)
            subscribe(session_id, subs[room_id].callback)
        with SessionWrapper(session_id, read_only=True) as (session, roles):
            emit(namespace_info.name, namespace_info.serialize(session, roles, data))
            join_room(room_id)

    @socketio.on('disconnect', namespace=f"/{namespace_info.name}")
    def handle_disconnect():
        client_id = request.sid
        for room_id in subs:
            if client_id in subs[room_id].clients:
                subs[room_id].clients.remove(client_id)
                if len(subs[room_id].clients) == 0:
                    unsubscribe(subs[room_id].session_id, subs[room_id].callback)
                    del subs[room_id]
                    break


def connect_socketio(socketio):
    def _check_state_data(data):
        with SessionWrapper(data["session_id"], read_only=True) as (_session, roles):
            rolewrapper.look_up(roles, data["role_id"])

    def _serialize_state_data(session, roles, data):
        role = rolewrapper.look_up(roles, data["role_id"])
        actions = session.get_valid_actions(role)
        return {
            "role": role,
            "state": session.get_visible_state(role),
            "actions": {a: actions[a].get_arg_spec(faction=role, game_state=session.game_log[-1]).to_dict() for a in actions},
            "history": session.get_visible_command_log(role)
        }

    connect_namespace(socketio, _NamespaceInfo(
        name="sessions",
        check_data=_check_state_data,
        serialize=_serialize_state_data,
        room_for_data=lambda data: f"{data['session_id']}/{data['role_id']}/session",
    ))

    def _serialize_roles(session, roles, data):
        assigned_roles = list(roles.values())
        all_roles = session.get_factions_in_play()
        all_roles.append("host")
        unassigned_roles = list(filter(lambda r: r not in assigned_roles, all_roles))
        return {
            "assigned_roles": assigned_roles,
            "unassigned_roles": unassigned_roles
        }

    connect_namespace(socketio, _NamespaceInfo(
        name="roles",
        check_data=lambda data: True,
        serialize=_serialize_roles,
        room_for_data=lambda data: f"{data['session_id']}/roles",
    ))

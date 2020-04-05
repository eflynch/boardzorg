from dataclasses import dataclass
from flask_socketio import emit, join_room
from sessionwrapper import SessionWrapper, subscribe, unsubscribe
from flask import request

class UnknownSubscriptionType(Exception):
    pass


@dataclass
class _SubscriptionData:
    clients: any
    callback: any

roles_subs = {}


def _serialize_roles(roles):
    return {
        "assigned_roles": list(roles.values())
    }


def _connect_roles(session_id, client_id):
    if session_id in roles_subs:
        roles_subs[session_id].clients.append(client_id)
    else:
        def _on_roles(_session, roles):
            emit('roles',
                 _serialize_roles(roles),
                 room=f"roles/{session_id}",
                 namespace="/roles")
        roles_subs[session_id] = _SubscriptionData(
            clients=[client_id],
            callback=_on_roles)
        subscribe(session_id, roles_subs[session_id].callback)


def _disconnect_roles(client_id):
    for session_id in roles_subs:
        roles_subs[session_id].clients.remove(client_id)
        if len(roles_subs[session_id].clients) == 0:
            unsubscribe(session_id, roles_subs[session_id].callback)
            del roles_subs[session_id]
            break


def connect_socketio(socketio):
    @socketio.on('join', namespace="/roles")
    def handle_join_roles(data):
        session_id = data["session_id"]

        _connect_roles(session_id, request.sid)
        with SessionWrapper(session_id) as (_session, roles):
            emit('roles', _serialize_roles(roles))
            join_room(f"roles/{session_id}")

    @socketio.on('disconnect', namespace="/roles")
    def handle_disconnect_roles():
        _disconnect_roles(request.sid)

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


@dataclass
class _NamespaceInfo:
    name: str
    serialize: any
    room_for_data: any

def connect_namespace(socketio, namespace_info):
    subs = {}

    def _connect(session_id, client_id, data):
        if session_id in subs:
            subs[session_id].clients.append(client_id)
        else:
            def _on_change(session, roles):
                emit(namespace_info.name,
                     namespace_info.serialize(session, roles, data),
                     room=room_for_data(data),
                     namespace=f"/{namespace_info.name}")
                subs[session_id] = _SubscriptionData(
                    clients=[client_id],
                    callback=_on_change)
                subscribe(session_id, subs[session_id].callback)

    def _disconnect(client_id):
        for session_id in subs:
            subs[session_id].clients.remove(client_id)
            if len(subs[session_id].clients) == 0:
                unsubscribe(session_id, subs[session_id].callback)
                del subs[session_id]
                break

    @socketio.on('join', namespace=f"/{namespace_info.name}")
    def handle_join(data):
        session_id = data["session_id"]
        _connect(session_id, request.sid, data)
        with SessionWrapper(session_id) as (session, roles):
            emit('roles', namespace_info.serialize(session, roles, data))
            join_room(namespace_info.room_for_data(data))

    @socketio.on('disconnect', namespace=f"/{namespace_info.name}")
    def handle_disconnect_roles():
        _disconnect(request.sid)

def connect_socketio(socketio):
    connect_namespace(socketio, _NamespaceInfo(
        name="roles",
        serialize=lambda _session, roles, _data: { "assigned_roles": list(roles.values()) },
        room_for_data=lambda data: f"{data['session_id']}/roles",
    ))
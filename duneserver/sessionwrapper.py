from dune.session import Session
import os
import rolewrapper

import psycopg2 as psql


class SessionConflict(Exception):
    pass


def _connect():
    if os.getenv("FLASK_ENV") == "docker":
        return psql.connect(host="postgres",
                            dbname=os.getenv("POSTGRES_DB"),
                            user=os.getenv("POSTGRES_USER"),
                            password=os.getenv("POSTGRES_PASSWORD"),)
    else:
        return psql.connect("dbname=shai-hulud")


session_change_subscriptions = {}


def subscribe(session_id, callback):
    """Calls `callback` with (session, roles) after any change"""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
            "SELECT 1 FROM sessions where name=%(name)s",
            {'name': session_id})
    if not cursor.fetchone():
        raise SessionConflict("No session found with name {}".format(session_id))

    if session_id not in session_change_subscriptions:
        session_change_subscriptions[session_id] = [callback]
    else:
        session_change_subscriptions[session_id].append(callback)


def unsubscribe(session_id, callback):
    """unsubscribes the callback from `session_id`"""
    if session_id not in session_change_subscriptions:
        session_change_subscriptions[session_id].remove(callback)
        if len(session_change_subscriptions[session_id]) == 0:
            del session_change_subscriptions[session_id]


class SessionWrapper:
    def __init__(self, session_id):
        self.session_id = session_id
        self.conn = _connect()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.conn.__enter__()
        self.cursor.__enter__()
        self.cursor.execute(
            "SELECT serialized, roles FROM sessions where name=%(name)s FOR UPDATE",
            {'name': self.session_id})
        ret = self.cursor.fetchone()
        if not ret:
            raise SessionConflict("No session found with name {}".format(self.session_id))
        self.session = Session.realize(ret[0])
        self.roles = ret[1]
        return self.session, self.roles

    def __exit__(self, *args):
        if self.session_id in session_change_subscriptions:
            for callback in session_change_subscriptions[self.session_id]:
                callback(self.session, self.roles)
        self.cursor.execute(
            "UPDATE sessions SET serialized=%(serialized)s, roles=%(roles)s WHERE name=%(name)s",
            {
                'serialized': Session.serialize(self.session),
                'roles': rolewrapper.serialize(self.roles),
                'name': self.session_id
            })
        self.conn.commit()
        self.conn.__exit__(*args)
        self.cursor.__exit__(*args)

    @staticmethod
    def create(name):
        conn = _connect()
        with conn.cursor() as cursor:
            cursor.execute("SELECT (id) from sessions where name=%(name)s", {"name": name})
            if cursor.rowcount != 0:
                raise SessionConflict("Session with this name already exists")

            cursor.execute(
                "INSERT INTO sessions (name, serialized, roles) VALUES (%(name)s, %(serialized)s, %(roles)s)",
                {
                    "name": name,
                    "serialized": Session.serialize(Session.new_session()),
                    "roles": rolewrapper.serialize(rolewrapper.new())
                })
        conn.commit()
        conn.close()
        return name

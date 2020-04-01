from dune.session import Session
import rolewrapper

import psycopg2 as psql


class SessionConflict(Exception):
    pass


class SessionWrapper:
    def __init__(self, session_id):
        self.session_id = session_id
        self.conn = psql.connect("dbname=shai-hulud")
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.conn.__enter__()
        self.cursor.__enter__()
        self.cursor.execute(
            "SELECT serialized, roles FROM sessions where name='{}' FOR UPDATE".format(
                self.session_id))
        ret = self.cursor.fetchone()
        self.session = Session.realize(ret[0])
        self.roles = ret[1]
        return self.session, self.roles

    def __exit__(self, *args):
        self.cursor.execute(
            "UPDATE sessions SET serialized='{}', roles='{}' WHERE name='{}'".format(
                Session.serialize(self.session), rolewrapper.serialize(self.roles),
                self.session_id))
        self.conn.commit()
        self.conn.__exit__(*args)
        self.cursor.__exit__(*args)

    @staticmethod
    def create(name):
        conn = psql.connect("dbname=shai-hulud")
        with conn.cursor() as cursor:
            cursor.execute("SELECT (id) from sessions where name='{}'".format(name))
            if (cursor.fetchone() is not None):
                raise SessionConflict("Session with this name already exists")

            cursor.execute(
                "INSERT INTO sessions (name, serialized, roles) VALUES ('{}', '{}', '{}')".format(
                    name, Session.serialize(Session.new_session()),
                    rolewrapper.serialize(rolewrapper.new())))
        conn.commit()
        conn.close()
        return name

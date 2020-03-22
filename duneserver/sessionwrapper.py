from dune.session import Session
import psycopg2 as psql


class SessionWrapper:
    def __init__(self, session_id):
        self.session_id = session_id
        self.conn = psql.connect("dbname=shai-hulud")
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.conn.__enter__()
        self.cursor.__enter__()
        self.cursor.execute("SELECT serialized FROM sessions where id={} FOR UPDATE".format(self.session_id))
        ret = self.cursor.fetchone()[0]
        self.session = Session.realize(ret)
        return self.session

    def __exit__(self, *args):
        self.cursor.execute(
"""UPDATE sessions SET serialized='{}' WHERE id={}
""".format(Session.serialize(self.session), self.session_id))
        self.conn.commit()
        self.conn.__exit__(*args)
        self.cursor.__exit__(*args)

    @staticmethod
    def create(session):
        conn = psql.connect("dbname=shai-hulud")
        with conn.cursor() as cursor:
            cursor.execute(
"""INSERT INTO sessions (serialized) VALUES ('{}') RETURNING id
""".format(Session.serialize(session)))
            session_id = cursor.fetchone()[0]
            cursor.execute("SELECT id from sessions WHERE id={}".format(session_id))
        conn.commit()
        conn.close()
        return session_id

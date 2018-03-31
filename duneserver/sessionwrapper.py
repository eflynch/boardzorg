from dune.session import Session
import pymysql as sql


class SessionWrapper:
    def __init__(self, session_id):
        self.session_id = session_id
        self.conn = sql.connect(host="localhost", user="shai", db="dune", cursorclass=sql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.conn.__enter__()
        self.cursor.__enter__()
        self.cursor.execute("SELECT serialized FROM sessions where id={} FOR UPDATE".format(self.session_id))
        ret = self.cursor.fetchone()
        self.session = Session.realize(ret["serialized"])
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
        conn = sql.connect(host="localhost", user="shai", db="dune", cursorclass=sql.cursors.DictCursor)
        with conn.cursor() as cursor:
            cursor.execute(
"""INSERT INTO sessions (serialized) VALUES ('{}')
""".format(Session.serialize(session)))
            cursor.execute("SELECT id from sessions WHERE id=LAST_INSERT_ID()")
            session_id = cursor.fetchone()["id"]
        conn.commit()
        conn.close()
        return session_id
